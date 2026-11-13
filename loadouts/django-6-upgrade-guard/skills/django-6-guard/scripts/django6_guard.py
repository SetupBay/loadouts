#!/usr/bin/env python3
"""Find Django code removed by 6.0 and 6.1 (and older removals agents still write) in a Django 6 project.

Usage: python3 django6_guard.py [PATH ...]        (default: the current folder)
       python3 django6_guard.py --list            (print every rule)

A "guard: ok" comment on a line silences its warnings (never its errors).
Prints one line per finding:  path:line: level [rule] what is wrong -> what to use
Exit 0 when nothing at "error" level is found, 1 when something is, 2 on bad usage.
Standard library only. Read-only: it never edits a file and makes no network calls.
"""
import fnmatch
import os
import re
import sys

# (rule id, level, regex, message, file patterns). Patterns run against each line with comments removed.
RULES = [
    ('check-constraint-check', 'error', 'CheckConstraint\\([^)]*\\bcheck\\s*=',
     'CheckConstraint(check=...) was removed in 6.0 -> CheckConstraint(condition=...)', ['*.py']),
    ('save-positional', 'error', '\\.save\\(\\s*(True|False)\\s*,',
     'Model.save() positional arguments were removed in 6.0 -> save(force_insert=..., force_update=...)', ['*.py']),
    ('format-html-no-args', 'error', 'format_html\\(\\s*[frbu]*(\\"[^\\"]*\\"|\'[^\']*\')\\s*\\)',
     'format_html() with no args or kwargs raises in 6.0 -> mark_safe() for fixed HTML, or pass the values as arguments', ['*.py']),
    ('staticfiles-find-all', 'error', 'finders\\.find\\([^)]*\\ball\\s*=',
     'finders.find(all=...) was removed in 6.1 -> find(..., find_all=True)', ['*.py']),
    ('pg-agg-ordering', 'error', '\\b(ArrayAgg|JSONBAgg|StringAgg)\\([^)]*\\bordering\\s*=',
     'ArrayAgg/JSONBAgg/StringAgg(ordering=...) was removed in 6.1 -> order_by=...', ['*.py']),
    ('choices-meta', 'error', '\\bChoicesMeta\\b',
     'ChoicesMeta was removed in 6.0 -> ChoicesType', ['*.py']),
    ('urlfield-assume', 'error', 'FORMS_URLFIELD_ASSUME_HTTPS',
     'FORMS_URLFIELD_ASSUME_HTTPS was removed; URLField now assumes https', ['*.py']),
    ('log-action', 'error', '\\.log_action\\(|\\.log_deletion\\(',
     'LogEntryManager.log_action() / ModelAdmin.log_deletion() were removed in 6.0 -> log_actions() / log_deletions()', ['*.py']),
    ('index-together', 'error', '\\bindex_together\\s*=',
     'Meta.index_together was removed in 5.1 -> indexes = [models.Index(fields=[...])]', ['*.py']),
    ('url-function', 'error', 'from\\s+django\\.conf\\.urls\\s+import\\s+[^#]*\\burl\\b|\\burl\\(\\s*r?[\\"\']\\^',
     'django.conf.urls.url() was removed in 4.0 -> path() or re_path()', ['*.py']),
    ('ugettext', 'error', '\\bu(gettext|gettext_lazy|ngettext|ngettext_lazy|pgettext)\\b',
     'ugettext* was removed in 4.0 -> gettext / gettext_lazy', ['*.py']),
    ('force-text', 'error', '\\b(force_text|smart_text)\\b',
     'force_text / smart_text were removed in 4.0 -> force_str / smart_str', ['*.py']),
    ('is-ajax', 'error', '\\.is_ajax\\(\\)',
     "request.is_ajax() was removed in 4.0 -> check request.headers.get('x-requested-with') or the Accept header", ['*.py']),
    ('timezone-utc', 'error', 'timezone\\.utc\\b(?!c)|import\\s+pytz|pytz\\.',
     'django.utils.timezone.utc and pytz support were removed -> datetime.UTC / zoneinfo.ZoneInfo', ['*.py']),
    ('use-l10n', 'error', '^\\s*USE_L10N\\s*=',
     'USE_L10N was removed in 5.0 (localisation is always on); delete the setting', ['*.py']),
    ('null-boolean', 'error', '\\bNullBooleanField\\(',
     'NullBooleanField is gone (system check fields.E903) -> BooleanField(null=True)', ['*.py']),
    ('staticfiles-tag', 'error', '\\{%\\s*load\\s+(staticfiles|admin_static)\\s*%\\}',
     '{% load staticfiles %} was removed -> {% load static %}', ['*.html', '*.txt']),
    ('login-user-none', 'warn', '\\b(a?login)\\(\\s*request\\s*,\\s*None\\b',
     'login(request, None) no longer falls back to request.user in 6.1 -> pass the user', ['*.py']),
    ('default-auto-field', 'warn', 'DEFAULT_AUTO_FIELD\\s*=\\s*[\\"\']django\\.db\\.models\\.AutoField[\\"\']',
     "Django 6.0 defaults to BigAutoField; keeping AutoField is fine for old apps, but new apps shouldn't set it", ['*.py']),
    ('mail-positional', 'warn', '\\b(send_mail|send_mass_mail|mail_admins|mail_managers|EmailMessage)\\(\\s*[^)=]+,\\s*[^)=]+,\\s*[^)=]+,\\s*[^)=]+,\\s*[^)=]+[,)]',
     'positional arguments past the first four in django.core.mail are deprecated in 6.0 -> keywords', ['*.py']),
    ('email-settings', 'warn', '^\\s*EMAIL_(BACKEND|HOST|HOST_USER|HOST_PASSWORD|PORT|USE_TLS|USE_SSL|TIMEOUT|SSL_CERTFILE|SSL_KEYFILE|FILE_PATH)\\s*=',
     'the EMAIL_* connection settings are deprecated in 6.1 (RemovedInDjango2028Warning) -> MAILERS = {"default": {"BACKEND": ..., "OPTIONS": {...}}}', ['*.py']),
    ('celery-for-simple-task', 'warn', '@shared_task\\b|from\\s+celery\\s+import',
     'Django 6.0 ships a Tasks framework (django.tasks); ask before adding Celery for simple background jobs', ['*.py']),
]
FILES = ['*.py', '*.html', '*.txt']
COMMENT = '#'
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".agents", ".claude", ".cursor", "dist", "build", "target", ".godot"}
COMPILED = [(rid, lvl, re.compile(rx), msg, globs) for rid, lvl, rx, msg, globs in RULES]


def strip_comment(line):
    """Drop a trailing comment, leaving string literals alone."""
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif line.startswith(COMMENT, i):
            return line[:i]
        i += 1
    return line


def wanted(name):
    return any(fnmatch.fnmatch(name, g) for g in FILES)


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if wanted(f):
                    yield os.path.join(root, f)


def scan(path):
    out = []
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        return [(path, 0, "error", "unreadable", str(e))]
    for n, raw in enumerate(lines, 1):
        code = strip_comment(raw)
        if not code.strip():
            continue
        accepted = "guard: ok" in raw  # a person accepted the warnings on this line
        for rid, lvl, rx, msg, globs in COMPILED:
            if accepted and lvl == "warn":
                continue
            if globs and not any(fnmatch.fnmatch(name, g) for g in globs):
                continue
            if rx.search(code):
                out.append((path, n, lvl, rid, msg))
    return out


def main(argv):
    if "--list" in argv:
        for rid, lvl, _, msg, globs in RULES:
            print(f"{lvl:5} [{rid}] {msg}" + (f"  (only {', '.join(globs)})" if globs else ""))
        return 0
    if any(a.startswith("-") for a in argv):
        print(__doc__)
        return 2
    paths = argv or ["."]
    for p in paths:
        if not os.path.exists(p):
            print(f"no such path: {p}", file=sys.stderr)
            return 2
    files = list(walk(paths))
    findings = []
    for f in files:
        findings.extend(scan(f))
    for path, n, lvl, rid, msg in findings:
        print(f"{os.path.relpath(path)}:{n}: {lvl} [{rid}] {msg}")
    errors = sum(1 for x in findings if x[2] == "error")
    warns = sum(1 for x in findings if x[2] == "warn")
    print(f"django6_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

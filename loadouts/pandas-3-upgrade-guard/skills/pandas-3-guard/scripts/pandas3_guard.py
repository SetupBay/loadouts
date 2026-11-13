#!/usr/bin/env python3
"""Find pandas 1.x/2.x code that pandas 3 removed, and code that copy-on-write or the str dtype quietly changed.

Usage: python3 pandas3_guard.py [PATH ...]        (default: the current folder)
       python3 pandas3_guard.py --list            (print every rule)

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
    ('applymap', 'error', '\\.applymap\\(',
     'DataFrame.applymap() was removed -> DataFrame.map()', []),
    ('append', 'error', '\\b(df\\w*|frame\\w*|data\\w*|result\\w*|out\\w*)\\.append\\(',
     'DataFrame.append() was removed (2.0) -> pd.concat([a, b], ignore_index=True)', []),
    ('iteritems', 'error', '\\.iteritems\\(',
     'iteritems() was removed (2.0) -> items()', []),
    ('fillna-method', 'error', '\\.fillna\\([^)]*\\bmethod\\s*=',
     "fillna(method='ffill') was removed -> .ffill() / .bfill()", []),
    ('replace-method', 'error', '\\.replace\\([^)]*\\b(method|limit)\\s*=',
     'replace(method=..., limit=...) was removed -> .ffill() / .bfill() after replacing with NA', []),
    ('interpolate-pad', 'error', '\\.interpolate\\([^)]*[\\"\'](pad|ffill|bfill|backfill)[\\"\']',
     "interpolate('ffill') was removed -> .ffill() / .bfill()", []),
    ('freq-alias', 'error', '\\b(freq|rule)\\s*=\\s*[\\"\'](\\d*)(H|BH|CBH|T|L|U|N|M|BM|SM|CBM|Q|BQ|Y|BY|A|BA|AS|BAS)(-[A-Z]{3})?[\\"\']',
     "old offset alias -> 'h', 'min', 'ms', 'us', 'ns', 'ME', 'QE', 'YE' (month/quarter/year END aliases)", []),
    ('resample-alias', 'error', '\\.(resample|asfreq)\\(\\s*[\\"\'](\\d*)(H|T|M|Q|Y|A)[\\"\']',
     "old offset alias in resample/asfreq -> 'h', 'min', 'ME', 'QE', 'YE'", []),
    ('delim-whitespace', 'error', '\\bdelim_whitespace\\s*=',
     'read_csv(delim_whitespace=True) was removed -> sep=r"\\s+"', []),
    ('date-parser', 'error', '\\b(date_parser|infer_datetime_format|keep_date_col)\\s*=',
     'read_csv date_parser / infer_datetime_format / keep_date_col were removed -> date_format=... or pd.to_datetime after reading', []),
    ('swapaxes', 'error', '\\.swapaxes\\(',
     'swapaxes() was removed -> .T or .transpose()', []),
    ('series-view', 'error', '\\]\\.view\\(|\\bseries\\w*\\.view\\(|\\bs\\.view\\(',
     'Series.view() was removed -> .astype(...)', []),
    ('groupby-axis', 'error', '\\.(groupby|rolling|resample)\\([^)]*\\baxis\\s*=',
     'the axis= argument was removed from groupby/rolling/resample -> transpose first', []),
    ('first-last', 'error', '\\.(first|last)\\(\\s*[\\"\']\\d',
     "DataFrame.first('3D') / last('3D') were removed -> df.loc[df.index < df.index[0] + pd.Timedelta('3D')]", []),
    ('errors-ignore', 'error', '\\bto_(numeric|datetime|timedelta)\\([^)]*errors\\s*=\\s*[\\"\']ignore[\\"\']',
     "errors='ignore' was removed -> errors='coerce' and handle NaN, or try/except", []),
    ('series-bool', 'error', '\\.bool\\(\\s*\\)',
     'Series.bool() / DataFrame.bool() were removed -> bool(s.item())', []),
    ('use-inf-as-na', 'error', 'use_inf_as_na',
     'mode.use_inf_as_na was removed -> df.replace([np.inf, -np.inf], np.nan)', []),
    ('copy-on-write-option', 'warn', 'mode\\.copy_on_write|copy_on_write\\s*=',
     'copy-on-write is always on in pandas 3; the option does nothing and will be removed', []),
    ('read-literal', 'error', 'pd\\.read_(json|html|xml|excel)\\(\\s*(f?[\\"\'][\\[{<]|response\\.text|r\\.text)',
     'read_json/read_html/read_xml no longer take literal text -> wrap it: pd.read_json(io.StringIO(text))', []),
    ('chained-assignment', 'error', '\\b(df\\w*|\\w+_df|frame\\w*|data)\\[[^\\]]+\\]\\[[^\\]]+\\]\\s*=[^=]',
     "chained assignment never writes back under copy-on-write -> df.loc[row, 'col'] = value", []),
    ('inplace-on-column', 'error', '\\b(df\\w*|\\w+_df|frame\\w*|data)\\[[^\\]]+\\]\\.\\w+\\([^)]*inplace\\s*=\\s*True',
     "df['col'].method(inplace=True) changes a copy, not df -> df['col'] = df['col'].method()", []),
    ('object-dtype-check', 'warn', 'dtype\\s*==\\s*(object|[\\"\']object[\\"\']|np\\.object_)|select_dtypes\\([^)]*[\\"\']object[\\"\']',
     "strings are now dtype 'str', not object -> pd.api.types.is_string_dtype(s) or select_dtypes(include=['str'])", []),
    ('setting-with-copy', 'warn', 'SettingWithCopyWarning|\\.copy\\(\\)\\s*#.*SettingWithCopy',
     'SettingWithCopyWarning is gone in pandas 3; the defensive .copy() is not needed for it', []),
    ('observed-default', 'warn', '\\.groupby\\((?![^)]*observed)[^)]*\\)(?=.*cat)',
     'groupby on categoricals now defaults to observed=True; pass observed=False to keep empty categories', []),
    ('future-stack', 'warn', '\\.stack\\([^)]*future_stack',
     'future_stack is the default in pandas 3; drop the argument', []),
    ('np-reduction-in-agg', 'warn', '\\.(agg|apply|transform)\\(\\s*(np\\.(sum|mean|max|min|std)|sum|max|min)\\s*[,)]',
     "agg(np.sum) is no longer swapped for pandas' own sum -> pass the string 'sum'", []),
]
FILES = ['*.py', '*.ipynb']
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
    print(f"pandas3_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

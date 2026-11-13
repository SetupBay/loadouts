#!/usr/bin/env python3
"""Find SQLAlchemy 1.x code (and the legacy Query API) in a project on SQLAlchemy 2.x.

Usage: python3 sqlalchemy2_guard.py [PATH ...]        (default: the current folder)
       python3 sqlalchemy2_guard.py --list            (print every rule)

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
    ('engine-execute', 'error', '\\b(engine|eng|db_engine|self\\.engine)\\.execute\\(',
     'Engine.execute() was removed in 2.0 -> with engine.begin() as conn: conn.execute(text(...))', []),
    ('select-list', 'error', '\\bselect\\(\\s*\\[',
     'select([a, b]) was removed -> select(a, b)', []),
    ('string-sql', 'error', '\\.execute\\(\\s*[frbu]*[\\"\']',
     'executing a plain SQL string was removed -> conn.execute(text("..."), {"name": value})', []),
    ('metadata-bind', 'error', '\\bMetaData\\([^)]*\\bbind\\s*=',
     'MetaData(bind=...) was removed -> pass the engine or connection explicitly', []),
    ('autocommit', 'error', '\\bautocommit\\s*=\\s*True',
     'Session/sessionmaker(autocommit=True) was removed -> with Session(engine) as s, s.begin(): ...', []),
    ('row-string-key', 'error', '\\b(row|r|result_row|record)\\[\\s*[\\"\']',
     "rows are tuples: row['name'] fails -> row.name or row._mapping['name']", []),
    ('ext-declarative', 'error', 'sqlalchemy\\.ext\\.declarative\\s+import\\s+[^#]*declarative_base',
     'sqlalchemy.ext.declarative.declarative_base moved -> class Base(DeclarativeBase): pass', []),
    ('query-get', 'error', '\\.query\\([^)]*\\)\\.get\\(',
     'Query.get() is legacy -> session.get(Model, pk)', []),
    ('legacy-query', 'error', '\\b(session|db|s|sess|self\\.session|db\\.session)\\.query\\(',
     'session.query() is the legacy Query API (still runs) -> session.scalars(select(Model).where(...))', []),
    ('orm-relation', 'error', '\\borm\\.relation\\(|\\brelation\\(',
     'relation() -> relationship()', []),
    ('declarative-base-fn', 'warn', '\\bdeclarative_base\\(\\s*\\)',
     'declarative_base() works but 2.0 style is class Base(DeclarativeBase): pass, with Mapped[] annotations', []),
    ('untyped-column', 'warn', '^\\s+\\w+\\s*=\\s*(sa\\.)?Column\\(',
     'Column() in a mapped class -> name: Mapped[str] = mapped_column(...) so types reach the type checker', []),
    ('backref', 'warn', '\\bbackref\\s*=',
     'backref= -> relationship(back_populates=...) on both sides, so both attributes are visible', []),
    ('future-flag', 'warn', '\\bfuture\\s*=\\s*True',
     'future=True does nothing on 2.x; remove it', []),
    ('dynamic-loader', 'warn', 'lazy\\s*=\\s*[\\"\']dynamic[\\"\']',
     "lazy='dynamic' is legacy -> WriteOnlyMapped[...] with lazy='write_only'", []),
    ('connect-then-write', 'warn', 'with\\s+\\w+\\.connect\\(\\)\\s+as\\s+\\w+\\s*:',
     'engine.connect() does not commit: writes are rolled back unless you call conn.commit() -> use engine.begin() for writes', []),
]
FILES = ['*.py']
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
    print(f"sqlalchemy2_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

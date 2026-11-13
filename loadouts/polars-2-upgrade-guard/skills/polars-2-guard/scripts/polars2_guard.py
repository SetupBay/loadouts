#!/usr/bin/env python3
"""Find Polars 1.x code that Polars 2 removed, and calls whose results changed silently in 2.0.

Usage: python3 polars2_guard.py [PATH ...]        (default: the current folder)
       python3 polars2_guard.py --list            (print every rule)

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
    ('melt', 'error', '\\.melt\\(',
     'melt() was removed -> unpivot(index=..., on=...) (id_vars -> index, value_vars -> on)', []),
    ('with-row-count', 'error', '\\.with_row_count\\(',
     "with_row_count() was removed -> with_row_index() (column is now 'index', not 'row_nr')", []),
    ('groupby-count', 'error', 'group_by\\([^)]*\\)\\s*\\.count\\(\\s*\\)',
     'group_by(...).count() was removed -> group_by(...).len()', []),
    ('groupby-old-name', 'error', '\\.groupby\\(',
     'groupby() -> group_by() (renamed in 0.19; also groupby_dynamic -> group_by_dynamic)', []),
    ('join-outer', 'error', 'how\\s*=\\s*[\\"\']outer(_coalesce)?[\\"\']',
     "join(how='outer') -> how='full' (outer_coalesce -> how='full', coalesce=True)", []),
    ('join-nulls', 'error', '\\bjoin_nulls\\s*=',
     'join_nulls= -> nulls_equal=', []),
    ('str-concat', 'error', '\\.str\\.concat\\(',
     'str.concat() was removed -> str.join() (default delimiter is now "", not "-")', []),
    ('lazy-fetch', 'error', '\\.fetch\\(\\s*\\d*\\s*\\)',
     'LazyFrame.fetch() was removed -> .head(n).collect()', []),
    ('lazy-profile', 'error', '\\.profile\\(\\s*\\)',
     'LazyFrame.profile() was removed (misleading on the streaming engine); time the collect() instead', []),
    ('streaming-flag', 'error', '\\bstreaming\\s*=\\s*(True|False)',
     "collect(streaming=...) was removed -> collect(engine='streaming' | 'in-memory')", []),
    ('csv-dtypes', 'error', '(read|scan)_csv\\([^)]*\\bdtypes\\s*=',
     'read_csv(dtypes=...) -> schema_overrides=... (a list must now cover every column)', []),
    ('min-periods', 'error', '\\bmin_periods\\s*=',
     'rolling_*(min_periods=...) -> min_samples=...', []),
    ('with-context', 'error', '\\.with_context\\(',
     "LazyFrame.with_context() was removed -> pl.concat([...], how='horizontal')", []),
    ('threadpool-size', 'error', 'pl\\.threadpool_size\\(',
     'pl.threadpool_size() -> pl.thread_pool_size()', []),
    ('expr-where', 'error', 'pl\\.col\\([^)]*\\)\\.where\\(',
     'Expr.where() was removed -> .filter()', []),
    ('apply', 'error', '\\.apply\\(',
     'apply() was removed in Polars 1.0 -> map_elements() (slow, last resort) or a native expression', []),
    ('map-dict', 'error', '\\.map_dict\\(',
     'map_dict() was removed -> replace() or replace_strict()', []),
    ('replace-default', 'error', '\\.replace\\([^)]*\\b(default|return_dtype)\\s*=',
     'replace(default=..., return_dtype=...) -> replace_strict(...)', []),
    ('missing-columns', 'error', '\\ballow_missing_columns\\s*=',
     "allow_missing_columns= -> missing_columns='insert' or 'raise'", []),
    ('read-rechunk', 'error', '(read|scan)_\\w+\\([^)]*\\brechunk\\s*=',
     'read_*/scan_*(rechunk=...) was removed -> call .rechunk() on the result', []),
    ('memory-map', 'error', '\\bmemory_map\\s*=',
     'read_ipc/scan_ipc(memory_map=...) was removed', []),
    ('hash-seeds', 'error', '\\bseed_[123]\\s*=|\\.hash\\(\\s*\\w+\\s*,\\s*\\w+',
     'hash(seed, seed_1, seed_2, seed_3) -> hash(seed) (one seed only)', []),
    ('categorical-ordering', 'error', 'pl\\.Categorical\\(\\s*(ordering\\s*=|[\\"\'](physical|lexical)[\\"\'])',
     'pl.Categorical(ordering=...) was removed; categoricals are always lexical now', []),
    ('to-struct-args', 'error', '\\.to_struct\\(\\s*\\)|\\b(upper_bound|n_field_strategy)\\s*=',
     "list.to_struct() needs the field names: list.to_struct(['a', 'b', 'c'])", []),
    ('concat-strict-false', 'error', 'how\\s*=\\s*[\\"\']horizontal[\\"\'][^)]*strict\\s*=\\s*False',
     "concat(how='horizontal', strict=False) now raises -> how='horizontal_extend' to pad", []),
    ('flatten', 'error', '\\.flatten\\(\\s*\\)',
     'Expr.flatten() was removed -> .list.explode(keep_nulls=False, empty_as_null=False)', []),
    ('top-k-descending', 'error', '(top|bottom)_k\\([^)]*\\bdescending\\s*=',
     'top_k/bottom_k(descending=...) -> reverse=...', []),
    ('pivot-columns', 'error', '\\.pivot\\([^)]*\\bcolumns\\s*=',
     'pivot(columns=...) -> pivot(on=...)', []),
    ('string-to-temporal-cast', 'warn', '\\.cast\\(\\s*pl\\.(Date|Datetime|Time)\\b',
     'casting a String column to Date/Datetime/Time now raises -> str.to_date() / str.to_datetime() / str.to_time()', []),
    ('concat-horizontal', 'warn', 'how\\s*=\\s*[\\"\']horizontal[\\"\'](?![^)]*_extend)',
     "horizontal concat now raises on different heights; use how='horizontal_extend' only if padding with nulls is intended", []),
    ('explode-empty', 'warn', '\\.explode\\((?![^)]*empty_as_null)',
     'explode(): empty lists now give zero rows, not one null row; pass empty_as_null=True if the old count matters', []),
    ('join-order', 'warn', '\\.join\\((?![^)]*maintain_order)(?=[^)]*\\bon\\s*=)',
     "lazy joins run on the streaming engine and don't keep row order; pass maintain_order='left' or sort if order matters", []),
    ('datetime-name', 'warn', 'pl\\.(datetime|repeat)\\((?!.*\\.alias\\()',
     "pl.datetime()/pl.repeat() are now named after their first argument; add .alias('...')", []),
    ('bytesio-seek', 'warn', 'BytesIO\\(\\s*\\)',
     'reading a BytesIO no longer rewinds it; call buf.seek(0) between write and read', []),
    ('cut-qcut', 'warn', '\\.q?cut\\(',
     'cut()/qcut() are deprecated -> bin_intervals() / bin_quantiles() (labels required, pass right_closed=True)', []),
    ('column-1', 'warn', '[\\"\']column_1[\\"\']',
     'headerless CSV columns now start at column_0, not column_1', []),
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
    print(f"polars2_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

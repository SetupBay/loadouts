#!/usr/bin/env python3
"""Find Roblox-only calls in Luau modules meant to be pure (no DataModel), so they run and test outside Studio. Run it on the pure folders only, such as src/shared.

Usage: python3 pure_luau_guard.py [PATH ...]        (default: the current folder)
       python3 pure_luau_guard.py --list            (print every rule)

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
    ('datamodel', 'error', '\\b(game|plugin)\\b\\s*[:.]|\\bworkspace\\b|\\bscript\\.(Parent|Name)\\b|\\bInstance\\.new\\(',
     "pure modules can't touch the DataModel (game, workspace, script, Instance) -> pass plain values in from the server or client script", []),
    ('instance-require', 'error', '\\brequire\\(\\s*(script|game)\\b',
     'Instance-path require only works in Studio -> require("./Sibling") or require("../Folder/Module"), which Roblox and the luau CLI both resolve', []),
    ('roblox-services', 'error', '\\b(Players|ReplicatedStorage|ServerStorage|RunService|DataStoreService|HttpService|TweenService|UserInputService|MarketplaceService|MemoryStoreService)\\b\\s*[:.]',
     'a Roblox service in a pure module -> keep services in the edge script and pass what you need in', []),
    ('task-library', 'error', '\\btask\\.(wait|spawn|delay|defer|cancel)\\(',
     'the task library is Roblox-only -> keep scheduling in the edge script; pure functions return values', []),
    ('deprecated-scheduler', 'error', '(?<![\\w.:])(wait|spawn|delay)\\(',
     'wait/spawn/delay are deprecated in Roblox and missing in the luau CLI -> task.wait/task.spawn/task.delay in edge scripts only', []),
    ('roblox-types', 'error', '\\b(Vector3|CFrame|Color3|UDim2|BrickColor|TweenInfo|Enum|Random|DateTime)\\b\\s*[.(]',
     'a Roblox datatype in a pure module -> use plain numbers and tables, or pass the value in', []),
    ('tick', 'error', '(?<![\\w.:])tick\\(\\)',
     'tick() is deprecated -> os.clock() for timing, or pass the time in', []),
    ('connect-lowercase', 'error', ':connect\\(',
     ':connect is deprecated -> :Connect, and only in edge scripts', []),
    ('math-random', 'warn', '\\bmath\\.random\\(',
     'random numbers make pure functions hard to test -> take an rng function or a seed as a parameter', []),
    ('os-time', 'warn', '\\bos\\.(time|clock)\\(',
     'reading the clock makes pure functions hard to test -> take the time as a parameter', []),
    ('print-in-module', 'warn', '(?<![\\w.:])(print|warn)\\(',
     'printing from a pure module -> return the value or an error and let the caller log', []),
]
FILES = ['*.luau', '*.lua']
COMMENT = '--'
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
    print(f"pure_luau_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

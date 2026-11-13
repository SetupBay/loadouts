#!/usr/bin/env python3
"""Read-only linter for Godot 4 headless test suites (tests/test_*.gd).

Finds tests that can't fail, tests that block or end the run, and timing that makes
headless runs slow or flaky. Prints findings and exits 1 if there are errors.

Usage: python3 gd_test_lint.py [path ...]   (default: tests)
A line ending in "# lint: ok" is skipped.
"""
import re
import sys
from pathlib import Path

ASSERT = re.compile(r"\bt\.(check|equal|fail)\s*\(")
LINE_RULES = [
    # (level, id, pattern, advice)
    ("error", "get-tree-in-suite", re.compile(r"(?<![.\w])get_tree\s*\("),
     "a RefCounted suite isn't in the tree; use t (the runner's SceneTree), e.g. t.root.add_child()"),
    ("error", "blocking-delay", re.compile(r"\bOS\.delay_(msec|usec)\s*\("),
     "blocks the main loop, so no frames run; await t.frames(n) instead"),
    ("error", "frames-without-await", re.compile(r"^(?!.*\bawait\b).*\bt\.frames\s*\("),
     "t.frames() is a coroutine; without await the test carries on at once"),
    ("error", "quit-in-test", re.compile(r"(\bt\.|get_tree\(\)\.)quit\s*\("),
     "ends the whole run early and hides the remaining results; let the runner quit"),
    ("error", "editor-only-api", re.compile(r"\b(EditorInterface|EditorPlugin|EditorScript)\b"),
     "the EditorInterface singleton and editor plugins are not available in a --script run; test the game code, not the plugin UI"),
    ("warn", "wall-clock-timer", re.compile(r"\bcreate_timer\s*\("),
     "real-time waits make headless runs slow and flaky; call the timeout handler or set Timer.wait_time tiny"),
    ("warn", "unseeded-random", re.compile(r"(?<![.\w])(randi|randf|randi_range|randf_range)\s*\("),
     "global RNG differs per run; use RandomNumberGenerator with a fixed seed"),
    ("warn", "print-as-check", re.compile(r"(?<![.\w])print\s*\("),
     "a printed value is not a check; use t.equal() so the run fails"),
    ("warn", "bare-assert", re.compile(r"(?<![.\w])assert\s*\("),
     "assert() is stripped from release builds and gives no expected/actual; use t.check() or t.equal()"),
]


def strip_comment(line: str) -> str:
    out, quote = [], ""
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


def lint(path: Path):
    findings = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    test_name, test_line, has_assert = None, 0, False

    def close_test():
        if test_name and not has_assert:
            findings.append(("error", "no-assertion", test_line,
                             f"{test_name}() has no t.check/t.equal/t.fail, so it can only pass"))

    for n, raw in enumerate(lines, 1):
        if raw.rstrip().endswith("# lint: ok"):
            continue
        code = strip_comment(raw)
        if not code.strip():
            continue
        m = re.match(r"^func\s+(\w+)\s*\(", code)
        if m or re.match(r"^\S", code):
            close_test()
            test_name = m.group(1) if m and m.group(1).startswith("test_") else None
            test_line, has_assert = n, False
        if test_name and ASSERT.search(code):
            has_assert = True
        for level, rid, pat, advice in LINE_RULES:
            if pat.search(code):
                findings.append((level, rid, n, advice))
    close_test()
    return sorted(findings, key=lambda f: f[2])


def main(argv):
    targets = [Path(a) for a in argv] or [Path("tests")]
    files = []
    for t in targets:
        if t.is_dir():
            files += sorted(p for p in t.rglob("test_*.gd") if ".godot" not in p.parts)
        elif t.is_file():
            files.append(t)
        else:
            print(f"gd_test_lint: no such path: {t}", file=sys.stderr)
            return 2
    errors = warnings = 0
    for f in files:
        for level, rid, line, advice in lint(f):
            print(f"{f}:{line}: {level} [{rid}] {advice}")
            if level == "error":
                errors += 1
            else:
                warnings += 1
    print(f"gd_test_lint: {len(files)} file(s), {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

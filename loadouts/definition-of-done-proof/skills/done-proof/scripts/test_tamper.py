#!/usr/bin/env python3
"""Find changes that make tests pass without fixing anything: weakened, skipped or deleted tests.

Usage: python3 test_tamper.py [--base REF] [--allow FILE]
  --base   compare the working tree (committed + uncommitted) with REF (default: HEAD; use main or origin/main for a branch)
  --allow  file listing test paths a human approved changing, one per line (default: .done-proof-allow if present)

Looks only at test files (tests/, test/, __tests__/, spec/, *_test.*, *.test.*, *.spec.*, test_*.py, *Tests.swift, *Test.java).
Reports, per file:
  removed-assert   a line with an assertion was deleted or changed
  changed-expect   an existing assertion now expects a different value
  added-skip       a skip / xfail / only / ignore marker was added
  deleted-test     a test function or case was removed
  snapshot         a snapshot file was changed
New tests and new assertions are fine and are only counted.
Exit 1 if anything is found outside the allow list, else 0. Read-only; needs git.
"""
import os
import re
import subprocess
import sys

TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|specs)/|(_test|\.test|\.spec|_spec)\.[a-z]+$|(^|/)test_[^/]*\.py$|Tests?\.(swift|java|kt|cs)$|_test\.go$")
SNAPSHOT = re.compile(r"(\.snap$|__snapshots__/|\.ambr$|snapshots?/)")
ASSERT = re.compile(r"\b(assert\w*|expect\s*\(|should\b|\.to(Be|Equal|Have|Match|Throw|Contain)\w*|XCTAssert\w*|#expect|#require|require\.\w+|t\.(Error|Fatal|Fail)\w*|assert_eq!|assert_ne!|assert!|refute\w*)", re.I)
SKIP = re.compile(r"(@pytest\.mark\.(skip|xfail)|pytest\.skip\(|@unittest\.skip|\b(it|test|describe|context)\.(skip|only|todo)\b|\bx(it|describe|test)\s*\(|\bf(it|describe)\s*\(|@Disabled\b|@Ignore\b|\bt\.Skip(Now|f)?\(|#\[ignore\]|\.disabled\(|skip\s*:\s*true|\bpending\s*\()")
TEST_DEF = re.compile(r"^\s*(def test_\w+|async def test_\w+|func Test\w+|fn test_\w+|#\[test\]|@Test\b|(it|test)\s*\(\s*['\"`])")


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def expected_value(line):
    """The value side of an assertion, roughly: what comes after ==, toBe(, toEqual(, assertEqual(x, ..."""
    m = re.search(r"(==|!=|\bis\b|\.to\w*\(|assert\w*\([^,]+,)\s*(.+)$", line)
    return m.group(2).strip().rstrip(")").strip() if m else None


def subject(line):
    m = re.search(r"(assert\w*\s*\(?|expect\s*\()\s*([^=,)]+)", line)
    return re.sub(r"\s+", "", m.group(2)) if m else None


def main(argv):
    base = "HEAD"
    allow_file = ".done-proof-allow"
    if "--base" in argv:
        base = argv[argv.index("--base") + 1]
    if "--allow" in argv:
        allow_file = argv[argv.index("--allow") + 1]
    allowed = set()
    if os.path.exists(allow_file):
        allowed = {l.strip() for l in open(allow_file) if l.strip() and not l.startswith("#")}
    git("rev-parse", "--verify", base)
    # Untracked test files count as new tests: add them to the diff with intent-to-add would change the index, so list them.
    untracked = [p for p in git("ls-files", "--others", "--exclude-standard").splitlines() if TEST_PATH.search(p)]
    diff = git("diff", "--no-color", "--unified=0", "--find-renames", base, "--")
    findings, new_tests, new_asserts = [], 0, 0
    path, removed, added = None, [], []

    def flush():
        nonlocal new_tests, new_asserts
        if not path or not TEST_PATH.search(path) and not SNAPSHOT.search(path):
            return
        if SNAPSHOT.search(path):
            if removed or added:
                findings.append((path, "snapshot", "snapshot changed; confirm the new output is right, not just accepted"))
            return
        rem_asserts = [l for l in removed if ASSERT.search(l)]
        add_asserts = [l for l in added if ASSERT.search(l)]
        add_by_subject = {}
        for l in add_asserts:
            add_by_subject.setdefault(subject(l), []).append(l)
        matched = set()
        for l in rem_asserts:
            s = subject(l)
            twins = add_by_subject.get(s) or []
            if twins:
                t = twins.pop(0)
                matched.add(id(t))
                if expected_value(l) != expected_value(t):
                    findings.append((path, "changed-expect", f"{l.strip()[:90]}  ->  {t.strip()[:90]}"))
            else:
                findings.append((path, "removed-assert", l.strip()[:120]))
        for l in added:
            if SKIP.search(l):
                findings.append((path, "added-skip", l.strip()[:120]))
        rem_defs = [l for l in removed if TEST_DEF.search(l)]
        norm = lambda l: re.sub(r"\.(skip|only|todo)\b|^x(?=(it|test|describe)\b)", "", l.strip())
        add_defs = {l.strip() for l in added if TEST_DEF.search(l) or SKIP.search(l)}
        add_norm = {norm(l) for l in add_defs}
        for l in rem_defs:
            if norm(l) not in add_norm:  # a test that was only marked skip is reported once, as added-skip
                findings.append((path, "deleted-test", l.strip()[:120]))
        new_tests += max(0, len([l for l in add_defs if TEST_DEF.search(l)]) - len(rem_defs))
        new_asserts += len([l for l in add_asserts if id(l) not in matched])

    for line in diff.splitlines():
        if line.startswith("diff --git"):
            flush()
            path, removed, added = None, [], []
        elif line.startswith("+++ "):
            p = line[4:]
            path = p[2:] if p.startswith("b/") else (None if p == "/dev/null" else p)
        elif line.startswith("--- ") and path is None:
            p = line[4:]
            if p != "/dev/null":
                path = p[2:] if p.startswith("a/") else p
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    flush()
    for p in untracked:
        text = open(p, encoding="utf-8", errors="replace").read().splitlines()
        new_tests += sum(1 for l in text if TEST_DEF.search(l))
        new_asserts += sum(1 for l in text if ASSERT.search(l))
        for l in text:
            if SKIP.search(l):
                findings.append((p, "added-skip", l.strip()[:120]))

    blocking = [f for f in findings if f[0] not in allowed]
    for p, kind, msg in findings:
        note = " (approved in allow list)" if p in allowed else ""
        print(f"{p}: {kind}: {msg}{note}")
    print(f"test-tamper: base {base}, {len(blocking)} finding(s) to explain, {len(findings) - len(blocking)} approved, {new_tests} new test(s), {new_asserts} new assertion(s)")
    if blocking:
        print("Not done: fix the code, not the test. If a test was wrong, say why and ask the human to add the file to .done-proof-allow.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

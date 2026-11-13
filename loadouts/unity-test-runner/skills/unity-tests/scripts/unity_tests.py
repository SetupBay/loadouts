#!/usr/bin/env python3
"""Run Unity Test Framework tests from the command line and read the NUnit results properly.

Usage:
  python3 unity_tests.py run [--platform EditMode|PlayMode] [--filter REGEX] [--category NAME] [--project .]
  python3 unity_tests.py read RESULTS.xml

`run` needs the Unity Editor binary in UNITY_PATH (for example
/Applications/Unity/Hub/Editor/6000.2.6f1/Unity.app/Contents/MacOS/Unity). The Editor must not have the project open.
It runs: Unity -batchmode -projectPath P -runTests -testPlatform X -testResults F -logFile L [-testFilter ...]
and leaves out -quit (the test run exits the Editor when it ends).

Why not trust the exit code alone: Unity exits 0 when every test passed and ALSO when no tests ran at all
(for example a -testFilter that matches nothing). 2 means tests failed, 3 a run error (often a compile error),
4 a platform that is not installed. This script fails on zero tests, lists each failure with its message,
and pulls compile errors out of the log.
Exit 0 only when at least one test ran and none failed. Standard library only.
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

CODES = {0: "run completed", 2: "one or more tests failed", 3: "run error (compile error, crash or no test callbacks)", 4: "test platform not found"}


def read(path):
    if not os.path.exists(path):
        print(f"unity-tests: no results file at {path}; the run did not get as far as tests")
        return 1
    root = ET.parse(path).getroot()
    run = root if root.tag == "test-run" else root.find(".//test-run")
    if run is None:
        print(f"unity-tests: {path} is not an NUnit 3 test-run file")
        return 1
    a = {k: run.get(k, "0") for k in ("total", "passed", "failed", "skipped", "inconclusive", "result", "duration")}
    total, failed = int(a["total"]), int(a["failed"])
    print(f"unity-tests: {a['total']} total, {a['passed']} passed, {a['failed']} failed, {a['skipped']} skipped, {a['inconclusive']} inconclusive ({a['result']})")
    for case in run.iter("test-case"):
        if case.get("result") == "Failed":
            msg = (case.findtext("failure/message") or "").strip().splitlines()
            where = (case.findtext("failure/stack-trace") or "").strip().splitlines()
            print(f"FAILED {case.get('fullname')}: {msg[0] if msg else '(no message)'}")
            if where:
                print(f"   at {where[0].strip()}")
    for case in run.iter("test-case"):
        if case.get("result") == "Skipped":
            reason = (case.findtext("reason/message") or "").strip()
            print(f"skipped {case.get('fullname')}{': ' + reason if reason else ''}")
    if total == 0:
        print("unity-tests: NO TESTS RAN. Unity still exits 0 here. Check -testFilter/-testCategory, the test assembly's .asmdef, and -testPlatform.")
        return 1
    return 1 if failed else 0


def compile_errors(log):
    if not os.path.exists(log):
        return []
    text = open(log, encoding="utf-8", errors="replace").read()
    errs = re.findall(r"^(Assets/[^\n(]+\(\d+,\d+\): error CS\d+: [^\n]+)", text, re.M)
    if "another Unity instance is running" in text or "It looks like another Unity instance" in text:
        errs.insert(0, "The project is open in another Unity Editor. Ask the human to close it, or run the tests in the Test Runner window.")
    return list(dict.fromkeys(errs))


def run(argv):
    unity = os.environ.get("UNITY_PATH")
    if not unity:
        print("unity-tests: set UNITY_PATH to the Unity Editor binary for this project's version (ProjectSettings/ProjectVersion.txt)")
        return 2
    opt = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
    project = os.path.abspath(opt("--project", "."))
    platform = opt("--platform", "EditMode")
    out = os.path.join(project, "TestResults")
    os.makedirs(out, exist_ok=True)
    results, log = os.path.join(out, f"{platform.lower()}.xml"), os.path.join(out, f"{platform.lower()}.log")
    for p in (results, log):
        if os.path.exists(p):
            os.remove(p)  # never read a stale file from an earlier run
    cmd = [unity, "-batchmode", "-projectPath", project, "-runTests", "-testPlatform", platform, "-testResults", results, "-logFile", log]
    if platform == "EditMode":
        cmd.insert(2, "-nographics")
    if opt("--filter"):
        cmd += ["-testFilter", opt("--filter")]
    if opt("--category"):
        cmd += ["-testCategory", opt("--category")]
    print("$ " + " ".join(cmd))
    code = subprocess.run(cmd).returncode
    print(f"unity exit {code}: {CODES.get(code, 'unknown')}")
    for e in compile_errors(log):
        print(f"COMPILE {e}")
    status = read(results)
    return status if code in (0, 2) else (code or 1)


def main(argv):
    if argv[:1] == ["read"] and len(argv) == 2:
        return read(argv[1])
    if argv[:1] == ["run"]:
        return run(argv[1:])
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

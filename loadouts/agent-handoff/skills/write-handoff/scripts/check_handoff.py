#!/usr/bin/env python3
"""Check a HANDOFF.md before a session ends or another agent picks it up.

Usage: python3 check_handoff.py [HANDOFF.md] [--max-lines 120]
Exit 0 when complete, 1 when something needs fixing. Standard library and git only; no network.
"""
import re
import subprocess
import sys
from pathlib import Path

REQUIRED = ["Goal", "Current state", "Files touched", "Decisions", "Failing or open", "Next step", "Verify with"]
SECRET = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|xox[abposr]-[A-Za-z0-9-]{10,})"
                    r"|-----BEGIN [A-Z ]*PRIVATE" r" KEY-----|\b(?:password|passwd|token|secret)\s*[:=]\s*\S{8,}", re.I)
PLACEHOLDER = re.compile(r"<[A-Za-z][A-Za-z0-9 ,/:\"'-]*>")


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv):
    path = Path(next((a for a in argv[1:] if not a.startswith("--")), "HANDOFF.md"))
    max_lines = int(argv[argv.index("--max-lines") + 1]) if "--max-lines" in argv else 120
    if not path.is_file():
        print(f"FAIL {path} not found")
        return 1
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    problems = []
    headings = {m.group(1).strip().lower(): i for i, l in enumerate(lines) if (m := re.match(r"^##\s+(.+)$", l))}
    for name in REQUIRED:
        if name.lower() not in headings:
            problems.append(f"missing section: ## {name}")
            continue
        start = headings[name.lower()] + 1
        body = []
        for l in lines[start:]:
            if l.startswith("## "):
                break
            if l.strip():
                body.append(l)
        if not body:
            problems.append(f"empty section: ## {name} (write 'none' if there is nothing)")
    if len(lines) > max_lines:
        problems.append(f"too long: {len(lines)} lines (max {max_lines}); link to files instead of pasting")
    for n, l in enumerate(lines, 1):
        if PLACEHOLDER.search(l):
            problems.append(f"line {n}: template placeholder left in: {PLACEHOLDER.search(l).group(0)}")
        if SECRET.search(l):
            problems.append(f"line {n}: looks like a secret; remove it")
    m = re.search(r"^- Commit:\s*([0-9a-f]{7,40})\b", text, re.M)
    head = git("rev-parse", "HEAD")
    if not m:
        problems.append("no '- Commit: <sha>' line")
    elif head and not head.startswith(m.group(1)):
        ahead = git("rev-list", "--count", f"{m.group(1)}..HEAD")
        problems.append(f"stale: written at {m.group(1)}, HEAD is {head[:7]}" + (f" ({ahead} commits later)" if ahead else "")
                        + "; re-check the state before trusting it")
    b = re.search(r"^- Branch:\s*(\S+)", text, re.M)
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if b and branch and b.group(1) != branch:
        problems.append(f"branch mismatch: handoff says {b.group(1)}, checkout is {branch}")
    for p in problems:
        print(f"FAIL {p}")
    if not problems:
        print(f"OK {path}: {len(REQUIRED)} sections, {len(lines)} lines, commit matches HEAD")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

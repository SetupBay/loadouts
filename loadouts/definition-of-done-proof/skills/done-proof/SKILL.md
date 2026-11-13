---
name: done-proof
description: Prove a coding task is done before saying so, with evidence the feature works and proof the tests were not weakened. Use before reporting any task as done, fixed or complete, when tests fail and it is tempting to change them, or when the user asks for proof.
---

# Done means proven

"Tests pass" was written for people, who also clicked through the feature. Agents read it literally, and changing an
assertion is cheaper than fixing a bug. This skill makes "done" mean three things: the behaviour works, a test shows
it, and no existing test was loosened to get there.

## 1. Before you change code
- Write down what done looks like for this task in one or two lines: the user-visible result, and the check that
  shows it (a command, a page, an output).
- For a bug: write or find a test that fails because of the bug. Run it and keep the failure output. That failure is
  half of your proof.

## 2. While you work
- Never edit an existing assertion's expected value, delete an assertion or a test, or add `skip`, `xfail`, `.only`,
  `@Disabled`, `t.Skip` or `#[ignore]` to get to green. Fix the code.
- If you believe a test is wrong (the spec changed, the test was buggy), stop and say so: which test, what it expects,
  why that is wrong. Change it only after the human agrees, and they add the file to `.done-proof-allow`.
- Never accept updated snapshots without reading the diff and saying why the new output is right.

## 3. Check the tests were not weakened
```bash
python3 .agents/skills/done-proof/scripts/test_tamper.py            # uncommitted changes
python3 .agents/skills/done-proof/scripts/test_tamper.py --base main  # the whole branch
```
(Claude Code installs the skill under `.claude/skills/`; use that path there.)
It must print `0 finding(s) to explain`. It reports changed expectations, removed assertions, added skip markers,
deleted tests and changed snapshots in test files. New tests and new assertions are counted, never blocked.

## 4. Show it works
- Run the full test command and keep the summary line (passed, failed, skipped).
- Run the feature itself: the CLI with real input, the endpoint with a real request, the page in a browser (screenshot or
  the visible text). Unit tests alone do not show a feature works end to end.
- Re-run the failing test from step 1: it passes now.

## 5. Report with evidence
Use `references/done-report.md`. Every claim has the command or observation behind it. Put what you could not check
under "Not checked". Never write "should work".

## Optional: make it a wall (Claude Code)
A rule asks; a hook enforces. `scripts/done-gate.sh` is a Stop hook that runs the tamper check and refuses to let
the session end while it has findings (exit 2, with `stop_hook_active` respected so it cannot loop). To install it,
merge `references/stop-hook.example.json` into `.claude/settings.json` (ask the human first; it changes their settings).

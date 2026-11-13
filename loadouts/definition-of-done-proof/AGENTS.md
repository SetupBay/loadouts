# AGENTS.md: definition of done for coding agents

"Done" is a claim the human will rely on. Make it only with evidence.

## Done means all of these
1. **It works.** You ran the behaviour that was asked for (command, request, page) and saw the right result.
2. **A test shows it.** New behaviour has a new test. A bug fix has a test that failed before the fix and passes now.
3. **No test was weakened.** You did not change an existing assertion's expected value, delete an assertion or test,
   add skip/xfail/only/ignore markers, or accept new snapshots unread. The `done-proof` skill's tamper check
   prints `0 finding(s) to explain`.
4. **The full suite passes**, with the summary line in your report (passed / failed / skipped).
5. **You said what you could not check.**

## When a test seems wrong
Stop. Name the test, what it expects, and why you think that is wrong. Change it only after the human agrees.
Approved test files are listed in `.done-proof-allow` by the human, never by you.

## Reporting
- End with the done report from the `done-proof` skill: what was asked, how you saw it work, tests (command and
  summary, new tests, changed tests), what was not checked, what needs the human.
- Never write "should work", "probably" or "done" without the evidence next to it.

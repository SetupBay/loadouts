# AGENTS.md: second-opinion review from another model

Before you call a non-trivial change done, get an independent read-only review from a different agent or model.
A different model misses different things; a reviewer that cannot edit cannot "fix" its way past a problem.

## When to ask
- The change touches three or more files, a public interface, auth, payments, data migrations or concurrency.
- You fixed a bug you could not reproduce with a test.
- You are about to tell the human the work is finished.

Skip it for typo fixes, formatting, dependency bumps with green CI, and changes the human will review line by line anyway.

## Rules
- Use the `cross-model-review` skill. The reviewer runs read-only (Codex: default `codex exec` sandbox; Claude Code: plan or
  dontAsk mode with read tools only).
- Give the reviewer the goal, the diff and the test command. Do not give it your reasoning; it should judge the code, not your story.
- Treat findings as claims. Verify each against the code before changing anything. Reject wrong findings with a one-line reason.
- Maximum two review rounds per change. If round two still finds blocking issues, stop and report to the human.
- Never paste secrets, `.env` contents or customer data into a review prompt.
- In the final report, list what the reviewer found and what you did about each finding.

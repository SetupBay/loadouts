---
name: ralph-loop
description: Set up and run a guarded Ralph-style loop (fresh agent process per pass, state in files, iteration and no-progress limits, independent check). Use when a task is a long list of similar, checkable steps.
---

# Guarded Ralph loop

A Ralph loop re-runs one prompt in a fresh agent process until the work is done. Fresh context each pass is the point:
state lives in files, not in the conversation. The guard rails stop the classic failures: endless loops, a pass that
"fixes" the tests, and quiet drift.

## When to use it
- Good fit: migrations, porting, test backfill, lint clean-up, one checklist item per pass, each provable by a command.
- Bad fit: design work, anything without a check command, anything touching production.

## Set up
1. Create a branch: `git switch -c ralph/<task>`. The runner refuses to start on main, master or a detached HEAD.
2. `mkdir -p .ralph` and copy `references/PROMPT.md` to `.ralph/prompt.md`. Fill in the goal, constraints and check command.
3. Write `.ralph/plan.md` as a checklist, one small item per line (`- [ ] ...`). Ask the human to approve it.
4. Copy `scripts/ralph.sh` into the repository (for example `scripts/ralph.sh`) and make it executable.
5. Add `.ralph/log/` to `.gitignore`. Keep `prompt.md`, `plan.md` and `progress.md` committed.

## Run
Set the agent command and the check, then start. The prompt file path is in `$RALPH_PROMPT`.

    AGENT_CMD='claude -p --permission-mode acceptEdits --max-budget-usd 3 < "$RALPH_PROMPT"' \
    CHECK_CMD='npm test' MAX_ITER=15 scripts/ralph.sh

Other agents (one process per pass in each case):
- Codex: `AGENT_CMD='codex exec --sandbox workspace-write - < "$RALPH_PROMPT"'`
- Antigravity CLI: `AGENT_CMD='agy -p "$(cat "$RALPH_PROMPT")" --cwd .'`

Limits (environment variables): `MAX_ITER` (default 10), `MAX_NO_PROGRESS` passes without a new commit or diff
(default 2), `PASS_TIMEOUT` seconds per pass (default 1800). Create `.ralph/STOP` to stop after the current pass.

Exit codes: 0 done and checks green, 2 iteration limit, 3 no progress, 4 stopped by `.ralph/STOP`, 5 refused to start.

## Guard rails the runner enforces
- `.ralph/DONE` only counts if `CHECK_CMD` passes after the pass. A false DONE is removed and logged.
- The check runs outside the agent, every pass. The agent cannot mark its own homework.
- `.ralph/prompt.md` is hashed at start; a pass that edits it ends the loop (exit 5).
- Each pass's output goes to `.ralph/log/pass-N.txt` for review.

## In-session alternatives
Claude Code `/goal` and Codex `/goal` keep one session working towards a condition, judged by a separate evaluator
(Claude) or the goal tracker (Codex). They are convenient, but the context is not cleared between turns. Use this runner
when you want a clean context per pass and limits enforced outside the agent; use `/goal` for shorter jobs.

## After the loop
Review `git log --oneline` and `.ralph/progress.md`, run the full test suite yourself, and open a pull request. Never let
the loop merge its own work.

Self-test: `bash scripts/selftest.sh` runs the runner against fake agents and checks every exit path.

---
name: night-shift
description: Queue coding tasks to run unattended overnight, each in its own git worktree with a dollar cap and a finish-line check, then read the morning report. Use when the user wants agents to work while they sleep, run a batch of tasks unattended, or asks what the overnight run did.
---

# Night shift

Unattended runs fail in two expensive ways: one stuck task eats the whole budget, or a usage limit leaves a request
hanging until morning with nothing to show. This skill gives every task a **finish line** (a command that exits 0
when it is done), its own worktree and branch, its own dollar cap inside a total for the night, and Claude Code's
unattended retry settings. Nothing is pushed or merged; the human reviews branches in the morning.

## 1. Write the plan with the human
Copy `references/night-shift.example.json` to `night-shift.json` at the repo root and fill it in together:
- **One task = one finish line.** "Make `pytest -q tests/test_dates.py` pass" is a task. "Improve the codebase" is not.
  If you cannot name the check command, the task is not ready for an unattended run.
- `budget_usd` per task and `budget_usd_total` for the night. The script never lets a task start with less than
  $0.50 left and passes Claude Code the smaller of the task budget and what is left as `--max-budget-usd`.
- Permissions: headless runs cannot answer prompts, so anything not allowed is refused. Allow only what the tasks
  need (`--allowedTools "Bash(pytest *)"`, `--permission-mode acceptEdits`). Never bypass permission checks
  (bypassPermissions mode or the "dangerously" flag) outside a container or VM; the script refuses both unless
  `NIGHT_SHIFT_SANDBOXED=1`.
- Keep `--max-turns` (it ends a run that loops) and `--output-format json` (the script reads the cost from it).

## 2. Start it
```bash
python3 .agents/skills/night-shift/scripts/night_shift.py run
```
(Claude Code installs the skill under `.claude/skills/`.) The main working tree must be committed first: each task
branches from `HEAD`. The script sets these unless they are already set:

| Variable | Value | Why |
|---|---|---|
| `CLAUDE_CODE_RETRY_WATCHDOG` | `1` | keep retrying 429 and 529 errors instead of failing the task |
| `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` | `1800000` | but end one request after 30 minutes of waiting (v2.1.295+) |
| `CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS` | `3600000` | end a request whose usage limit resets more than an hour away (v2.1.301+) |

The watchdog already fails at once on spend-limit and out-of-credits errors (v2.1.239+), so a hard limit stops the run.
For Codex, use `codex exec --json` as the agent and keep the budget in the spend-cap guard from the
`agent-spend-cap` loadout; Codex has no budget flag.

## 3. Read the morning report
`.night-shift/report.md` has one row per task: finish line, result, cost, turns, commits, branch, and the agent's last
line. `python3 .../night_shift.py report` rewrites it from `.night-shift/ledger.jsonl`. Then:
- For a passed task: review the diff (`git log -p main..night/<date>-<task>`), run the full suite, and only then merge.
  A passed finish line is not a review.
- For a task that did not reach the finish line: read its last note and the commits. Make the task smaller or the
  check clearer before queueing it again. Do not just raise the budget.
- Remove finished worktrees: `git worktree remove .night-shift/worktrees/<task>`.

## Never
- Push, merge, open PRs or delete branches from an unattended run.
- Queue tasks that need secrets, production access, or a human decision halfway through.
- Edit the plan's budget upwards during the night.

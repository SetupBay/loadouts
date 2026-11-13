# AGENTS.md: unattended overnight agent runs

Agents in this repo may run unattended (headless, overnight, in CI). Unattended work follows these rules, because
nobody is there to stop a loop or answer a question.

## Every unattended task
- Has a **finish line**: one command that exits 0 when the task is done. Run it yourself before you stop.
- Runs in its **own git worktree on its own branch** (`night/<date>-<task>`), never in the main working tree.
- Has a **dollar cap** (`--max-budget-usd`) and a **turn cap** (`--max-turns`), inside a total for the night.
- Commits its work to its branch, then ends with one line: done, or what is blocking.

## Never, when unattended
- Push, merge, open or close pull requests, delete branches, or touch other worktrees.
- Edit, skip or delete tests to reach a finish line.
- Change budgets, permissions, CI config or settings files.
- Use secrets, production systems or paid services the task did not name.
- Wait for a human: if a decision is needed, commit what you have and say what the decision is.

## Running a batch
Use the `night-shift` skill: it creates the worktrees, sets the budgets and Claude Code's unattended retry settings,
runs each task, checks its finish line, and writes `.night-shift/report.md`. A human reviews every branch before merging.

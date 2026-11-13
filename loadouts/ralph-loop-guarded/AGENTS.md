# AGENTS.md: guarded agent loop (Ralph style)

This repository may be worked on by an agent running in a loop: the same prompt, a fresh context each pass,
progress kept in files. These rules apply on every pass.

## Each pass
- Read `.ralph/prompt.md`, then `.ralph/plan.md` and the last 20 lines of `.ralph/progress.md`. Nothing else carries over.
- Pick ONE unchecked item from the plan. Do only that item.
- Run the check command from the prompt before you finish. Do not tick an item while checks fail.
- Tick the item in `.ralph/plan.md` and append one line to `.ralph/progress.md`: date, item, result, next step.
- Commit with a message naming the item. One item, one commit.
- When every item is ticked and checks pass, create `.ralph/DONE` containing one line of evidence (the check output summary).

## Never
- Never edit `.ralph/prompt.md`, the check command, CI config or tests you were not asked to change, to make a pass look green.
- Never delete or skip a failing test. Fix it, or write the blocker into `.ralph/progress.md` and stop.
- Never push, deploy, merge or touch the default branch. The loop runs on its own branch; a human lands it.
- Never install new dependencies unless the plan item says so.
- If the same item fails twice in a row, write `BLOCKED: <reason>` in `.ralph/progress.md` and stop without creating `.ralph/DONE`.

## Starting a loop
Use the `ralph-loop` skill. It sets up `.ralph/`, a branch and the guarded runner with limits.

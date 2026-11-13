# Loop prompt (copy to .ralph/prompt.md)

Goal: <one sentence: the end state>

Read first: AGENTS.md, .ralph/plan.md, the last 20 lines of .ralph/progress.md.

Each pass:
1. Pick the first unchecked item in .ralph/plan.md. Do only that item.
2. Run the check: <command, for example npm test>. It must pass before you tick the item.
3. Tick the item, append one line to .ralph/progress.md (date, item, result, next step) and commit.
4. If every item is ticked and the check passes, write the check summary to .ralph/DONE.

Constraints:
- Do not edit .ralph/prompt.md, tests you were not asked to change, CI config or lockfiles.
- No new dependencies unless the item says so. No pushes, deploys or merges.
- If the item fails twice, append "BLOCKED: <reason>" to .ralph/progress.md and stop.

---
name: cross-model-review
description: Ask a second agent (Codex from Claude Code, or Claude Code from Codex) for a read-only review of the current diff, then verify and act on its findings. Use before reporting a non-trivial change as done.
---

# Cross-model review

1. **Prepare.** Commit or stage the work. Pick the base (usually `origin/main`). Write the diff to a temporary file:
   `git diff origin/main...HEAD > "${TMPDIR:-/tmp}/review.diff"` (add `git diff` of uncommitted work if any).
   Check its size: over ~3,000 lines, review per directory instead.
2. **Write the prompt** from `references/review-prompt.md`: goal, test command, focus areas. No reasoning, no secrets.
3. **Run the reviewer**, read-only, from the repository root:
   - From Claude Code, ask Codex:
     `codex exec --ephemeral -o "${TMPDIR:-/tmp}/review.md" "$(cat "${TMPDIR:-/tmp}/review-prompt.txt")" < "${TMPDIR:-/tmp}/review.diff"`
     (`codex exec` is read-only unless you pass `--sandbox`; do not pass it.) `codex review` is an alternative for the current branch.
   - From Codex or another agent, ask Claude Code:
     `claude -p --permission-mode dontAsk --allowedTools "Read,Grep,Glob,Bash(git diff *),Bash(git log *)" "$(cat "${TMPDIR:-/tmp}/review-prompt.txt")" < "${TMPDIR:-/tmp}/review.diff" > "${TMPDIR:-/tmp}/review.md"`
   If the reviewer CLI is not installed or not logged in, stop and tell the human; do not substitute a different tool silently.
4. **Triage.** For each finding: open the cited code, decide valid / invalid / unsure. Fix valid ones. Write a reason for invalid ones.
5. **Round two** only if you changed code because of blocking findings. Same prompt plus "Previously reported: …". Never a third round.
6. **Report** a table: finding, verdict, action. Delete the temporary files.

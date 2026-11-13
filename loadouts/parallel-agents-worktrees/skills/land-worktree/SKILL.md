---
name: land-worktree
description: Rebase a finished worktree branch, run checks, open a pull request and clean up after merge. Use when a task in a worktree is done.
---

# Land a worktree

1. Commit everything. `git status` must be clean.
2. `git fetch origin && git rebase origin/<base>`. On conflicts in files you did not change, stop and ask; another agent's work may be landing.
3. Run the full check command (tests, lint, type-check). Fix failures you caused; report others.
4. Push the branch: `git push -u origin agent/<task>`. Never push to `<base>` directly, never force-push a shared branch.
   After a rebase of your own unshared branch, `git push --force-with-lease` is the only acceptable force.
5. Open a pull request (`gh pr create --fill` then edit the body): what changed, how it was tested, anything left.
6. Stop any dev server you started in this worktree.
7. After the human merges, clean up from the main checkout:
   `git worktree remove ../<repo>-<task>` then `git branch -d agent/<task>` and `git worktree prune`.
   `git branch -d` refuses unmerged branches. After a squash or rebase merge on GitHub it refuses too, because the
   commits differ: confirm with `gh pr view --json state` that the PR is merged, then ask the human before using `-D`.

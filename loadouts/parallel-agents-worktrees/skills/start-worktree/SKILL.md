---
name: start-worktree
description: Create a git worktree and branch for one task, install dependencies and pick a free port. Use before starting a task that will run alongside other agents.
---

# Start a worktree

Inputs: a short task name (kebab-case) and the base branch (default `main`; use the repo's default branch).

1. From the main checkout, update the base: `git fetch origin`.
2. Create the worktree next to the repository, never inside it:
   `git worktree add ../$(basename "$PWD")-<task> -b agent/<task> origin/<base>`
   If the branch exists already, stop and ask; another agent may own it.
3. `cd` into the new directory. Confirm with `git status` and `git branch --show-current`.
4. Install dependencies with the project's lockfile command (`npm ci`, `pnpm install --frozen-lockfile`, `uv sync`, …).
5. Environment files: list which ones the project needs (`ls ../<main-checkout>/.env*` names only) and ask the human to copy them.
6. Pick a port: `git worktree list` gives N; use `3000 + N` unless the human assigned one. Record it in your first report.
7. Run the test command once, before changing anything, so later failures are known to be yours.

Report: worktree path, branch, port, baseline test result.

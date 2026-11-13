# AGENTS.md: parallel agents in git worktrees

Several agents may work on this repository at once, each in its own git worktree on its own branch.
These rules keep them from colliding.

## Inside a worktree
- Work only inside your worktree directory. Never edit, check out or reset files in the main checkout or another worktree.
- One task per worktree, one branch per task: `agent/<short-task-name>`.
- Never switch branches inside a worktree; finish or abandon the task instead.
- Commit small and often. Uncommitted work in a worktree is easy to lose.
- Each worktree has its own `node_modules`, `.venv` and build output. Install dependencies in the worktree.
- Dev servers: use the port the human assigned, or `3000 + N` where N is your worktree number. Never kill a process you did not start.
- Shared resources (one local database, one emulator) are single-writer. Ask before migrating or seeding a shared database.
- Secrets: do not copy `.env` files between worktrees yourself. Ask the human to provide them.

## Starting and finishing
- Start with the `start-worktree` skill. Finish with the `land-worktree` skill.
- Do not delete a worktree or its branch until its pull request is merged, or the human says to drop it.

## Tool-specific notes
- Claude Code: `claude --worktree <name>` starts a session in a new worktree. A subagent with `isolation: worktree` gets a
  temporary worktree branched from the default branch, not from your current HEAD; commit and push what it needs first.
- Codex: the app and CLI can create managed worktrees (Codex 0.162+). Treat them the same way.
- GitHub CLI: `gh issue develop <number> --worktree` creates a linked branch and a worktree for an issue (gh 2.99+).

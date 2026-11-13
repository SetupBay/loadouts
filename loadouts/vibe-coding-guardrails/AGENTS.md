# AGENTS.md: working agreement

How to work in this repository, whatever the stack. Project-specific rules, if any, take precedence.

## Before you start
- Read the README and any `NOTES.md` handoff file first.
- For anything bigger than a small fix (more than ~3 files, a new feature, a refactor, a dependency change),
  use the `plan-then-build` skill: write a short plan and wait for the human to agree.
- If the request is ambiguous, ask one focused question rather than guessing big.

## While you work
- **Small steps.** Make one change that works, verify it, then the next. Prefer several small diffs to one huge one.
- **Stay in scope.** Do not reformat, rename or "tidy" code you were not asked to touch. Mention improvements instead.
- **Follow what is there.** Match the existing structure, naming, libraries and patterns before introducing new ones.
- **Check, don't guess, APIs.** If you are not certain a function or option exists in the installed version, look it up:
  check `package.json`/lockfile for the version, read the library's docs (the Context7 MCP server helps), or read the source in `node_modules`.
- **Commit after each working step** if the human uses git that way, with a message saying what and why.

## Hard rules
- Never delete, skip or weaken a test to make it pass. If a test is wrong, say so and explain why before changing it.
- Never silence errors to make something "work": no empty `catch`, no `// @ts-ignore`, no `# type: ignore`, no `eslint-disable` without a reason in the comment.
- Never add a dependency without saying so and why. Prefer what the platform or existing deps already provide.
- Never run destructive commands (`rm -rf`, `git reset --hard`, `git push --force`, dropping databases) without explicit permission.
- Never commit secrets or `.env` files.
- Never claim something works without running it. If you could not run it, say "not run" plainly.

## When you finish
- Run the project's checks (lint, type-check, tests, build — whatever exists).
- Summarise in a few lines: what changed, how you verified it, anything left undone or risky, and what the human should try.
- For long sessions, use `session-handoff` to update `NOTES.md`.

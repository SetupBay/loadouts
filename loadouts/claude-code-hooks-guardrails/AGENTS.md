# AGENTS.md: hooks and permissions guard rails

This project enforces its hard rules with hooks and permission rules, not with prose. Prose in this file guides you;
the hooks decide. Follow both.

## When a hook blocks you
- A blocked tool call comes back with a reason. Read it, then change approach. Do not retry the same command
  with different spelling, quoting, an env-var prefix, `sh -c`, a script file or another tool to get past it.
- If the block looks wrong for this task, stop and tell the human what you tried and the reason you got.
  Only a human edits the hook scripts or `.claude/settings.json`.
- A Stop hook that reports failing checks means you are not done. Fix the cause, not the check.

## Never, even if a hook would let it through
- Rewrite shared history: no `git push --force` to `main`/`master`, no `git reset --hard` on work you did not create.
- Skip verification: no `--no-verify`, no deleting or skipping tests to get green.
- Read or print secrets: `.env`, `.env.*` (except `.env.example`), key files, tokens in shell history.
- Delete outside the project folder, or delete the project folder itself.
- Run migrations, `DROP`, `TRUNCATE` or bulk `DELETE` against a database the human has not named as disposable.

## Keep the loop fast
- After each edit, the post-edit hook runs a quick check on the file you touched (syntax, lint or typecheck).
  Fix what it reports before moving to the next file.
- The full test suite runs once when you finish. Do not run it after every small edit unless the human asks.

## Changing the guard rails
- Use the `install-guard-hooks` skill to install, update or extend the hooks.
- Every new block needs a test: try the forbidden action once and confirm it is denied with a clear reason.

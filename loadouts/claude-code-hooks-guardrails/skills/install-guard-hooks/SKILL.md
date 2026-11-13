---
name: install-guard-hooks
description: Install, update or test the project's guard-rail hooks for Claude Code (with notes for Codex and Cursor). Use when asked to add hooks, block dangerous commands, run tests before finishing, or when a hook misbehaves.
---

# Install guard hooks

Installs three hooks and the matching permission rules, then proves each block works.
Requires `bash` and `jq` on the machine that runs the agent.

| Hook | Event | What it does |
|---|---|---|
| `scripts/guard-bash.sh` | PreToolUse, Bash | Denies force-push, `reset --hard`, `clean -f`, `--no-verify`, `.env` access, recursive deletes outside the project, DROP/TRUNCATE/unbounded DELETE, download-piped-to-shell. Prints a reason. |
| `scripts/post-edit-check.sh` | PostToolUse, Edit/Write | Fast check of the edited file: `bash -n`, `jq empty`, ruff or py_compile, eslint or `node --check`. Exit 2 shows the error to the agent. |
| `scripts/stop-gate.sh` | Stop | Runs the test command once if the tree has changes. Exit 2 keeps the agent working. Skips when `stop_hook_active` is true. |

## Install (Claude Code)

1. Copy the three scripts from this skill's `scripts/` folder to `.claude/hooks/` and make them executable:
   `mkdir -p .claude/hooks && cp <skill-dir>/scripts/{guard-bash,post-edit-check,stop-gate}.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh`
2. Merge `references/settings.example.json` into `.claude/settings.json`. Keep existing keys; append to existing
   `permissions.deny` and `hooks` arrays rather than replacing them. Validate with `jq empty .claude/settings.json`.
3. If the test command is not `npm test`, `pytest -q`, `cargo test -q` or `go test ./...`, write it on one line in
   `.claude/hooks/test-command`.
4. Tell the human to run `/hooks` and confirm the three hooks are listed with source "project settings".

## Install (Codex)

Codex reads hooks from `.codex/hooks.json` in the project (loaded only when the project is trusted) or from
`~/.codex/hooks.json` for the user, with the same event names and the same deny reply as Claude Code.

1. For the project, write `.codex/hooks.json` with a `PreToolUse` group, matcher `Bash`, and one `command` handler:
   `bash "$(git rev-parse --show-toplevel)/.claude/hooks/guard-bash.sh"`. Codex runs hooks from the session's working
   folder, so resolve the path from the git root. Timeouts are in seconds.
2. A `Stop` group running `stop-gate.sh` the same way also works: Codex sends `stop_hook_active`, and exit 2 keeps it going.
3. Leave the post-edit check out. Codex edits files through `apply_patch`, which sends the patch rather than a file path.
4. Codex's docs don't describe `args` or `onFailure` for command hooks, so a crashing guard lets the command through. Keep
   the script simple and keep the deny rules.
5. Tell the human to open `/hooks` in Codex and trust the new hooks. Codex skips new or changed hooks until they're trusted.

For user-level hooks, show the human the same block for `~/.codex/hooks.json` with an absolute script path and let them
add it. Do not edit files in their home folder yourself.

## Cursor

Cursor can load the Claude Code hooks straight from `.claude/settings.json` when "Include Third-Party Plugins, Skills, and
Other Configs" is on (the default). It maps `PreToolUse`, `PostToolUse` and `Stop`, and reads the guard's deny reply.
Its docs don't mention `args` or `onFailure`, so don't assume the hooks fail closed there.

- Ask the human to check Cursor's Hooks output channel, or the Hooks tab in Customize, to see that the hooks loaded,
  then try one forbidden command in Cursor. If it isn't refused, the always-on rule in `.cursor/rules/` is all Cursor has.
- For a native Cursor setup, Cursor's own hooks live in `.cursor/hooks.json` (`"version": 1`, events such as
  `beforeShellExecution` or `preToolUse` with matcher `Shell`, and `failClosed: true`). Confirm the guard's replies work
  there before relying on it: Cursor's docs say a permission hook with invalid output blocks the action.
- The Stop gate exits early once Cursor's `loop_count` reaches 2, because Cursor sets no loop limit on Claude Code hooks.

## Prove it

1. Run `bash <skill-dir>/scripts/selftest.sh`. It must print `ok:`.
2. In a live session, attempt one forbidden action (for example `git push --force origin scratch`). It must be
   denied with a reason that starts "Blocked by guard-bash". A hook you have not seen block something is not installed.
3. Report which checks were verified and which were skipped (for example, no eslint in the project).

## Extend

- Add a rule to `guard-bash.sh` as a `deny "<reason>"` line, then add a deny and an allow case to `selftest.sh`.
- Reasons must say what to do instead. The agent reads them.
- Keep the post-edit check under a few seconds. Slow checks belong in the Stop gate.
- Read `references/permissions.md` before changing permission rules: deny beats allow, exit 1 does not block,
  and deny rules alone are not a sandbox.

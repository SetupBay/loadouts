---
name: cursor-guard-hooks
description: Install, change or check this project's fail-closed Cursor hooks (.cursor/hooks.json with one Python guard for shell commands, file reads and MCP tools), then prove each decision with a self-test. Use when asked to add Cursor hooks, block a command, keep secrets out of the agent's context, restrict MCP servers, or when a hook doesn't fire or lets something through.
---

# Cursor guard hooks

One standard-library Python script answers Cursor's permission hooks. Every hook is set to fail closed.

| Hook | What `cursor_guard.py` decides |
|---|---|
| `beforeShellExecution` | **deny**: recursive deletes of the whole project or anything outside it, force or deleting pushes, `--no-verify`, a download piped into a shell, reading `.env`, key or credential files, `chmod 777`, `DROP`/`TRUNCATE`/unbounded `DELETE`. **ask**: `sudo`, `reset --hard`, `clean -f`, force-with-lease, publishing a package. |
| `beforeReadFile` | **deny**: `.env*` (except `.example`, `.sample`, `.template`, `.dist`), private keys, SSH and cloud credential folders, and any file whose content holds a private key or a known token format. |
| `beforeMCPExecution` | **deny** servers not in `mcp-policy.json` `allow_servers` (or a missing server name) and `deny_tools`; **ask** for `ask_tools`. |
| `preToolUse`, matcher `^MCP:` | The same tool lists for cloud agents, where `beforeMCPExecution` doesn't run. No server name is sent there, and `ask` isn't enforced, so `ask_tools` are denied. |

A malformed payload, a missing `mcp-policy.json` or an unknown event makes the script exit 1 with no output. With
`"failClosed": true` Cursor blocks the action, so a broken guard never reads as "allow".

## Install
1. Copy the guard and the policy into the project and the hooks file next to them:
   ```bash
   mkdir -p .cursor/hooks
   cp <skill-dir>/scripts/cursor_guard.py <skill-dir>/references/mcp-policy.json .cursor/hooks/
   cp <skill-dir>/references/hooks.json .cursor/hooks.json   # or merge its four entries into an existing file
   ```
   Merge rather than overwrite when `.cursor/hooks.json` already exists: keep other hooks, add these entries.
2. Edit `.cursor/hooks/mcp-policy.json`: list the `mcp.json` server keys the project uses in `allow_servers`. Use
   `server:tool` or a bare tool name in `deny_tools` and `ask_tools`. Ask the human which servers to allow; don't guess.
3. Check the config, then prove the decisions:
   ```bash
   python3 <skill-dir>/scripts/hooks_check.py .cursor/hooks.json
   python3 <skill-dir>/scripts/selftest.py .cursor/hooks/cursor_guard.py
   ```
   `hooks_check.py` must report 0 errors and no `fails-open` warning. `selftest.py` must end with `ok:`.
4. Ask the human to open the Hooks tab in Cursor's Customize view (or the Hooks output channel) and confirm the four
   hooks loaded, then try one blocked command, such as `git push --force`. A hook you haven't seen block something
   isn't working yet.

## Facts that decide the design
These are from Cursor's hooks docs; see `references/cursor-hooks-facts.md`.
- Exit 0 uses the JSON output, exit 2 blocks, and any other exit **fails open** unless `"failClosed": true`.
- A permission hook that prints invalid JSON blocks even without `failClosed`.
- Project hooks run from the project root, and they're the only hooks that run in cloud agents (not `~/.cursor/hooks.json`).
- Responses from every source merge: deny wins over ask, and ask over allow.
- Cursor also loads Claude Code hooks from `.claude/settings.json`; they run alongside these.

## Change a rule
- Shell rules live in `check_segment()` (per command, after splitting on `;`, `&&`, `|`) and in the two regexes for
  whole-command patterns. File rules live in `SECRET_NAMES`, `SECRET_DIRS` and `SECRET_CONTENT`.
- Reasons must say what to do instead. The agent reads them.
- Add a deny case and an allow case to `selftest.py`'s `CASES`, then run it and `hooks_check.py` again.

## Limits to tell the human
- This is a guard rail, not a sandbox. A determined command (an interpreter one-liner, an encoded string) can get past
  pattern checks. Keep Cursor's own sandbox and approval settings on.
- `beforeReadFile` covers the agent's read tool. Shell reads are caught only by the shell rules.

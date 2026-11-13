# AGENTS.md: Cursor project with fail-closed hooks

This project guards the agent with Cursor hooks in `.cursor/hooks.json`. One standard-library Python script,
`.cursor/hooks/cursor_guard.py`, answers four permission hooks: `beforeShellExecution`, `beforeReadFile`,
`beforeMCPExecution`, and `preToolUse` for MCP tools (which also covers cloud agents). Every hook has
`"failClosed": true`, so a crash or timeout blocks the action instead of letting it through.

## When a hook blocks you
- The reason starts with `Blocked by cursor_guard:` and says what to do instead. Do that, or ask the human.
- Don't retry the same action in another form (a different flag order, a script file, `bash -c`, another tool) to
  get round a block. A block is the answer.
- `ask` means the human approves or refuses in Cursor. Wait for them.

## Never
- Edit, disable or weaken `.cursor/hooks.json`, `.cursor/hooks/cursor_guard.py` or `.cursor/hooks/mcp-policy.json`
  unless the human asked for that exact change.
- Read `.env` files, keys or credentials, by any route. Use `.env.example` and ask for the values you need.
- Add an MCP server to `allow_servers` yourself.

## When you're asked to change the hooks
Use the `cursor-guard-hooks` skill. Before you say "done", run its `hooks_check.py` (0 errors, and no `fails-open`
warnings) and `selftest.py` (prints `ok:`), and add a selftest case for every new rule.

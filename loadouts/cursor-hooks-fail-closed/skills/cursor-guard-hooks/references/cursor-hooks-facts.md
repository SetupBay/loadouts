# Cursor hooks facts behind this setup

From Cursor's hooks documentation (https://cursor.com/docs/agent/hooks), read on 29 October 2026.

| Fact | What it means here |
|---|---|
| Exit 0: Cursor uses the JSON output. Exit 2: block. Any other exit: the hook failed and the action proceeds, unless the hook has `"failClosed": true`. | Every permission hook sets `failClosed: true`. The guard exits 1 on anything unexpected. |
| For permission hooks (`beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, `beforeTabFileRead`, `subagentStart`, `preToolUse`), invalid JSON or a response that doesn't match the schema blocks the action. | The guard prints exactly one JSON object, or nothing. |
| `failClosed` blocks on a crash, timeout, non-zero exit or no output. | A missing `mcp-policy.json` blocks MCP calls rather than allowing them. |
| Project hooks (`.cursor/hooks.json`) run from the project root, in any trusted workspace, and in cloud agents. User hooks (`~/.cursor/hooks.json`) don't run in cloud agents. | Commands are `python3 .cursor/hooks/cursor_guard.py`. The setup is project-level. |
| `beforeMCPExecution` and `afterMCPExecution` don't run in cloud agents. There, MCP tools reach `preToolUse` as `tool_name` `MCP:<tool_name>`. | A `preToolUse` hook with matcher `^MCP:` repeats the tool lists. |
| `preToolUse` accepts `"ask"` in its schema but doesn't enforce it. | `ask_tools` are denied in `preToolUse`. |
| `beforeMCPExecution` input has `tool_name`, `tool_input` (a JSON string) and `mcp_server_name` (the server's key in `mcp.json`). Cursor's docs advise that a hook should treat a missing or unexpected `mcp_server_name` as a deny. | Servers not in `allow_servers` are denied, including a missing name. |
| `beforeShellExecution` input has `command`, `cwd` and `sandbox`. `beforeReadFile` input has `file_path` and the full `content`. | The read guard checks both the path and the content. |
| Matchers are regexes. For `beforeShellExecution` the regex is matched against the full command. | The setup uses no shell matcher, so every command is checked. |
| All matching hooks from every source run, and their responses merge: deny over ask over allow. | Enterprise, team or user hooks can add blocks; none can undo a deny. |
| Hook scripts get `CURSOR_PROJECT_DIR` (and `CLAUDE_PROJECT_DIR` as an alias). | The guard resolves delete targets against the project root. |
| Cursor loads Claude Code hooks too. | If `.claude/settings.json` has hooks, they run as well. Check both. |

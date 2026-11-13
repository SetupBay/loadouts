# MCP config formats per agent

Source entry used in the examples:

```json
{ "mcpServers": {
  "docs": { "type": "http", "url": "https://mcp.example.com/mcp", "headers": { "Authorization": "Bearer ${DOCS_TOKEN}" } },
  "browser": { "command": "npx", "args": ["@playwright/mcp@0.0.83"] }
} }
```

| Agent | File | Shape |
|---|---|---|
| Claude Code | `.mcp.json` | Same as the source. `${VAR}` expands from the environment |
| Cursor | `.cursor/mcp.json` | Same as the source. Use `${env:VAR}` for environment variables |
| VS Code / Copilot | `.vscode/mcp.json` | Top-level key is `servers`, not `mcpServers`; each server keeps `type` (`stdio` or `http`) |
| Codex | `.codex/config.toml` (trusted projects) or `~/.codex/config.toml` | TOML tables, below |
| Gemini CLI | `.gemini/settings.json` | `mcpServers`; remote servers use `httpUrl` |
| Antigravity CLI | .agents/mcp_config.json | `mcpServers`; remote servers use `serverUrl` (not `url` or `httpUrl`). `agy plugin import gemini` migrates Gemini extensions |

Codex:

```toml
[mcp_servers.docs]
url = "https://mcp.example.com/mcp"
bearer_token_env_var = "DOCS_TOKEN"

[mcp_servers.browser]
command = "npx"
args = ["@playwright/mcp@0.0.83"]
```

Codex also has `codex mcp add <name> -- <command>` and `/mcp login` for servers that use OAuth.

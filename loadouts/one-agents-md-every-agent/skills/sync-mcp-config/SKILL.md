---
name: sync-mcp-config
description: Convert the single MCP server list in agents/mcp.servers.json into each agent's config file. Use when adding, removing or changing an MCP server for the team.
---

# Sync MCP config

The source of truth is `agents/mcp.servers.json`, an object `{ "mcpServers": { "<name>": {...} } }` in the
Claude/Cursor shape. Never edit generated files by hand; edit the source and re-run this skill.

1. Read the source. Each server is either stdio (`command`, `args`, `env`) or remote (`type: "http"`, `url`, `headers`).
2. Write only the files for agents the team uses (ask if unsure). Formats are in `references/formats.md`.
3. Secrets: never write a literal token. Use the agent's environment-variable syntax and tell the human which variable to set.
4. Pin package versions in `args` (for example `@playwright/mcp@0.0.83`), so an update is a reviewed diff.
5. Remove servers from generated files when they are removed from the source.
6. Show the human the diff. Each agent needs a restart or `/mcp` reconnect to pick up changes.

Keep the server list short: every server's tool descriptions cost context in every session. Prefer a CLI the
agent can already run (`gh`, `psql`, `supabase`) over an MCP server that wraps it.

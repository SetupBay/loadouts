# AGENTS.md: authoring agent plugins (Claude Code and Antigravity)

This repository builds a plugin that installs in Claude Code and in Antigravity from one source tree. A plugin runs
as the user in every session where it is enabled: its MCP servers start, its hooks fire and its skill descriptions
sit in context. Treat each change like a dependency release.

## How to work
- Use the `build-agent-plugin` skill to build both layouts and check them. Edit `plugin-src/`, never the built
  output.
- Claude Code and Antigravity differ: manifest location and fields, MCP file name, remote URL key, hook format and
  tool names. Keep shared skills and agents portable (frontmatter `name` and `description` only).
- Check facts against the official docs (code.claude.com/docs/en/plugins, antigravity.google/docs/plugins). Antigravity has no
  `plugin validate` command. Its manifest allows only `$schema`, `name` and `description`.

## Rules
- MCP servers are pinned to exact versions (`npx -y pkg@1.2.3`, `uvx pkg==1.2.3`); remote servers use https.
- No credentials in any plugin file. In Claude Code, use a sensitive `userConfig` option (`${user_config.KEY}`); in
  Antigravity, use an environment variable (`${VAR}`).
- Hooks are opt-in per agent and reviewed line by line. Never add a hook that sends data off the machine or edits
  agent settings.
- Do not name a plugin `claude-*`, `anthropic-*` or anything that passes as an official plugin.
- Do not install, enable or publish a plugin, or add a marketplace, without the user's go-ahead.

## Done means
- The skill's checker prints `plugins ok`, and `claude plugin validate --strict` passes for the plugin and the
  marketplace.
- `version` is bumped, the changelog says what changed, and the README lists every MCP server, hook and network
  call.

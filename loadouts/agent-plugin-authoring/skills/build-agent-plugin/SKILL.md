---
name: build-agent-plugin
description: Author one plugin that installs in both Claude Code and Antigravity from a single source tree (skills, subagents, MCP servers), build both layouts, and validate them before anyone installs. Use when creating, changing, versioning or publishing a Claude Code or Antigravity plugin or a plugin marketplace.
---

# Build a plugin for Claude Code and Antigravity

Both agents load a plugin as a folder of `skills/`, `agents/` and MCP config, but the manifests and file names differ:

| | Claude Code | Antigravity |
| --- | --- | --- |
| Manifest | `.claude-plugin/plugin.json` (`name` required; set `version`, `description`, `author`) | `plugin.json` at the root: only `$schema`, `name`, `description` (schema forbids other keys) |
| MCP servers | `.mcp.json`, remote: `"type": "http", "url"` | `mcp_config.json`, remote: `serverUrl` only |
| Skills | `skills/<name>/SKILL.md`, run as `/<plugin>:<skill>` | `skills/<name>/SKILL.md` |
| Subagents | `agents/<name>.md` (`name`, `description`, optional `model`, `tools`) | `agents/<name>.md` (`name` and `description` required; `tools` use Antigravity tool names) |
| Hooks | `hooks/hooks.json`, Claude Code tool names in matchers | `hooks.json` at the root, Antigravity tool names (`run_command`, `view_file`) in matchers |
| Validate | `claude plugin validate <dir> --strict` | No validate command: check against the documented schema |
| Plugin root variable | `${CLAUDE_PLUGIN_ROOT}` | None documented |

Keep shared files portable: frontmatter limited to `name` and `description`, no `${CLAUDE_PLUGIN_ROOT}`, and no
tool lists, because tool names differ between the agents. Write hooks separately for each agent, or leave them
out. A hook runs as the user on every matching event, so it needs its own review.

## Layout

```
plugin-src/
  plugin.json          name, version, description, author, license, repository, mcpServers
  skills/<skill>/SKILL.md
  agents/<agent>.md
```

`references/plugin-src/` is a complete example (`pr-tidy`: one skill, one reviewer subagent, one pinned MCP server).

## Build and check

```bash
node scripts/build_plugins.mjs plugin-src dist-plugins
node scripts/check_plugins.mjs dist-plugins
npx -y @anthropic-ai/claude-code@2.1.302 plugin validate dist-plugins/claude/<name> --strict
npx -y @anthropic-ai/claude-code@2.1.302 plugin validate dist-plugins/claude --strict
```

The build writes `dist-plugins/claude/<name>/`, `dist-plugins/antigravity/<name>/` and a one-plugin local marketplace
at `dist-plugins/claude/.claude-plugin/marketplace.json`. `check_plugins.mjs` catches:

- extra Antigravity manifest fields;
- names the Antigravity CLI rejects, and names reserved for Anthropic;
- missing `version`, `description` or `author`;
- a Claude instructions file at the plugin root, which Claude Code does not load;
- skills or agents without a usable description;
- MCP servers run with `npx` or `uvx` and no exact version;
- `url` where Antigravity needs `serverUrl`;
- non-https remotes, and literal credentials in `env` or `headers`;
- any difference between the two builds.

`claude plugin validate` is the authority for Claude Code. It runs without signing in, and it also checks the
marketplace file.

## Test an install locally (with the user's go-ahead)

Installing changes the user's agent configuration, so ask first.

- Claude Code: `claude --plugin-dir dist-plugins/claude/<name>` loads the plugin for one session without
  installing it. Then run `/plugin` and check the Errors tab.
- Antigravity: `agy plugin install ./dist-plugins/antigravity/<name>`, then `agy plugin list --json` to confirm
  the skills, agents and MCP servers it found. Remove it with `agy plugin uninstall <name>`.

## Versions and publishing

- Bump `version` in `plugin-src/plugin.json` for every release. Claude Code keeps users on a version until it
  changes.
- Set `version` in `plugin.json` only, not in the marketplace entry as well; `validate` warns when both are set.
- Credentials: Claude Code plugins take a sensitive `userConfig` option referenced as `${user_config.KEY}`. In
  Antigravity, reference an environment variable as `${VAR}`. Never commit a value.
- Publish by tagging a commit. Tell users to pin it: a Claude Code marketplace entry from GitHub takes
  `"source": {"source": "github", "repo": "owner/repo", "ref": "v1.2.0", "sha": "<40-char sha>"}`. `agy plugin
  install https://github.com/owner/repo` takes no pin, so give Antigravity users the commit to check out and install
  from a local path. Point reviewers at the `agent-extension-vetting` loadout.

## Done means

`check_plugins.mjs` prints `plugins ok`, and both `validate --strict` runs pass. The version is bumped, and the
README says what the plugin runs: MCP servers, hooks, and any network access.

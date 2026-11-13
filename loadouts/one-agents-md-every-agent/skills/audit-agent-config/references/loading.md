# What each agent loads (checked 16 October 2026)

| Agent | Instructions | Skills | MCP config (project) | Gotchas |
|---|---|---|---|---|
| Claude Code | CLAUDE.md (and `CLAUDE.local.md`); reads `AGENTS.md` natively since v2.1.277 only when no CLAUDE.md is on the path; setting "Project instructions" can read both | `.claude/skills/` | `.mcp.json` | Keep `@AGENTS.md` in CLAUDE.md. `/doctor prompt-audit` (v2.1.283+) lists what loaded |
| Codex | `AGENTS.md`, root to current folder, nearest last | `.agents/skills/` | `.codex/config.toml` `[mcp_servers.<name>]` | Untrusted projects do not supply project `AGENTS.md` or config; trust the project first |
| Cursor | `AGENTS.md`, `.cursor/rules/*.mdc` | `.agents/skills/`, `.cursor/skills/`, also `.claude/skills/` and `.codex/skills/` | `.cursor/mcp.json` | `.cursor/rules` does not apply to Bugbot; it reads `.cursor/BUGBOT.md` |
| GitHub Copilot | `AGENTS.md` (root and nested, nearest wins), `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` with `applyTo` | `.github/skills/`, `.claude/skills/` | `.vscode/mcp.json` (`servers`) | `excludeAgent` in front matter keeps an instruction file away from code review or the coding agent |
| Gemini CLI / Antigravity CLI | GEMINI.md (import `@AGENTS.md`); Antigravity also reads `AGENTS.md` | Gemini: `.gemini/skills/`; Antigravity: `.agents/skills/` | Gemini: `.gemini/settings.json`; Antigravity: .agents/mcp_config.json | Gemini CLI stopped serving personal Google accounts on 18 June 2026; Antigravity CLI replaces it and keeps GEMINI.md compatibility |

Sources: Claude Code changelog and memory docs, Codex AGENTS.md and skills docs, Cursor skills and Bugbot docs,
GitHub custom instructions docs, Google's Antigravity CLI announcement (19 May 2026). Re-check after major releases.

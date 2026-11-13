# AGENTS.md: one source of truth for every coding agent

This repository keeps agent instructions in one file, `AGENTS.md`, and generates or imports everything else.
Follow these rules whenever you add or change agent configuration.

## Where things go
- Project rules every agent needs: `AGENTS.md` at the root. Folder-specific rules: a nested `AGENTS.md` in that folder.
- Per-agent files hold only an import or that agent's genuine quirks:
  - CLAUDE.md contains `@AGENTS.md` plus Claude-only notes, if any.
  - GEMINI.md contains `@AGENTS.md`.
  - `.github/copilot-instructions.md` is optional; Copilot reads `AGENTS.md` itself.
- Workflows longer than ~15 lines go in a skill: `.agents/skills/<name>/SKILL.md` (also mirrored to `.claude/skills/` for Claude Code).
- MCP servers are declared once in `agents/mcp.servers.json` and converted per agent with the `sync-mcp-config` skill.

## Rules
- Never paste the same rule into two files. Move it to `AGENTS.md` and import.
- Keep root `AGENTS.md` under ~150 lines. Every line must change behaviour; delete lines an agent would follow anyway.
- Write commands exactly as they are run (`npm test -- --run`), not descriptions of them.
- When you change a build, test or lint command, update `AGENTS.md` in the same commit.
- Do not add a CLAUDE.md that lacks `@AGENTS.md`: since Claude Code v2.1.277, a CLAUDE.md on the path stops `AGENTS.md` loading natively.
- After any change to agent config, run the `audit-agent-config` skill.

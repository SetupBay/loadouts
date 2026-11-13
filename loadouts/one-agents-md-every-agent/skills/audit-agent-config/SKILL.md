---
name: audit-agent-config
description: Check that every coding agent in this repo actually loads the shared AGENTS.md, skills and MCP config, and find duplicated or shadowed rules. Use after changing agent config or when an agent ignores a rule.
---

# Audit agent config

Run from the repository root. Report findings as a table: agent, file, problem, fix. Fix only what the human approves.

1. **Inventory.**
   `git ls-files | grep -Ei '(^|/)(AGENTS|CLAUDE|GEMINI|CLAUDE\.local)\.md$|copilot-instructions|\.instructions\.md$|\.cursor/rules/|/SKILL\.md$|mcp'`
2. **Imports.** Every CLAUDE.md and GEMINI.md must contain `@AGENTS.md` (or the nested path). Flag any that do not.
3. **Shadowing.** Use `references/loading.md` to check each agent the team uses. Typical problems:
   - a CLAUDE.md without the import, which hides `AGENTS.md` from Claude Code;
   - a `.cursorrules` file (legacy) alongside `.cursor/rules/`;
   - skills only in `.claude/skills/` when Codex or Antigravity users need `.agents/skills/`.
4. **Duplicates.** Look for the same rule in more than one file:
   `grep -rhoE '^[-*] .{25,}' AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md .cursor/rules 2>/dev/null | sort | uniq -d`
5. **Size.** Report root instruction files over ~150 lines and skills whose description does not say when to use them.
6. **Live check.** Ask the human to start each agent and ask it "Which instruction files and skills did you load?" Record the answers.

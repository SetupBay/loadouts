---
name: agents-md-writer
description: Write or fix a repository's AGENTS.md from worked examples, then lint it against what Codex, Claude Code and the others actually load. Use when creating an AGENTS.md, when agents ignore or misread it, when adding a nested AGENTS.md in a monorepo, or when asked for AGENTS.md examples.
---

# Write an AGENTS.md that agents follow

AGENTS.md is read by Codex, Cursor, Copilot, Antigravity CLI and Claude Code (when no CLAUDE.md shadows it). It is
loaded into every session, so every line costs context and every wrong command wastes a run.

## 1. Pick the nearest example
`references/examples/` has seven, each 30–40 lines:

| File | For |
|---|---|
| `web-app.md` | Next.js / TypeScript app with a database |
| `python-library.md` | a published Python package (uv, pytest, ruff, mypy) |
| `monorepo-root.md` + `monorepo-api.md` | a root file plus a nested one for one app |
| `go-cli.md` | a Go command-line tool with golden files |
| `godot-game.md` | a Godot 4 game |
| `infra-opentofu.md` | OpenTofu / Terraform, plan only |

Copy the structure, not the content. Every example has the same five parts: one line on what the project is;
**Commands** (exact, copy-pasteable, including how to run one test); **Layout**; **Conventions** and **Never**;
**Done means**.

## 2. Fill it from the repository, not from memory
- Read `package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`, CI workflows. Use the commands that exist.
  Run each one once; if it fails, fix the command or leave it out.
- Write what an agent would get wrong here: the package manager, the test runner, generated folders, the database
  rule. Leave out what any agent already knows ("write clean code").
- Keep it under 150 lines. Longer procedures belong in skills.
- Monorepo: a short root file with rules for every package, and a nested `AGENTS.md` per app with its commands.
  Codex joins them root first and stops at 32 KiB in total.
- If the repo has a CLAUDE.md, make it import AGENTS.md (a line with `@AGENTS.md`). Otherwise Claude Code reads
  CLAUDE.md only and ignores AGENTS.md.

## 3. Lint it
```bash
python3 .agents/skills/agents-md-writer/scripts/agents_md_lint.py .
```
(Claude Code installs the skill under `.claude/skills/`.) Fix every error: a size over Codex's 32 KiB, a shadowing
CLAUDE.md, an `npm run` / `pnpm` / `make` / `just` command that does not exist. Fix or explain each warning: no
test command, no "Never" section, over 150 lines, a path that does not exist. The `info` lines show which files Codex
joins for each folder.

## 4. Report
Show the final file, the lint summary, and each command you ran to check it.

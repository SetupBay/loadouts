---
name: vet-agent-extension
description: Vet a skill, plugin or MCP server before it is installed or updated. Pins the source, checks the checkout matches the pin, scans every file for risky patterns and writes a short report for a human to approve.
---

# Vet an agent extension

Use this before installing or updating any skill, plugin, marketplace entry or MCP server, and when a teammate asks
"is this safe to add?". The output is a report for a human. You never install anything yourself.

## 1. Pin the source
- Git: resolve the full commit SHA you are about to review (`git ls-remote <url> <ref>`). Record it.
- npm: exact version (`npm view <pkg> version`, then `<pkg>@<version>`). PyPI: `<pkg>==<version>`.
- Claude Code marketplaces: plugin sources accept `ref` and `sha`; set `sha` to the full 40-character SHA.
- MCP servers: replace `@latest` and bare `uvx <pkg>` with exact versions in the config you propose.

## 2. Fetch without running anything
- Clone into a scratch directory, then detach at the pin and prove it:
  `scripts/check_pin.sh <dir> <sha>`. It fails if `HEAD` is not the pin or if a branch or tag is named like a SHA.
- Do not run install scripts, `npm install`, `make`, hooks or the server itself while reviewing.

## 3. Scan
- Run `python3 scripts/audit_extension.py <dir>`. It prints findings as `severity rule path:line` and exits 1 on any
  high finding. It checks hidden Unicode, pipe-to-shell, base64 execution, credential paths, env exfiltration,
  unpinned `npx`/`uvx`, hooks, auto-approve lists and agent-directed wording.
- Optional second opinion: NVIDIA SkillSpector, `skillspector scan <dir> --no-llm`, if the user already has it.
- A clean scan is not approval. Patterns miss things; it tells you where to read first.

## 4. Read
- Read every file the extension ships, in this order: hooks and scripts, MCP config, `SKILL.md` and rules, references.
- For each script note what it reads, what it writes, and what it sends over the network.
- Check validation passes: `claude plugin validate <dir> --strict` for Claude Code. Antigravity has no validate
  command, so check its `plugin.json` against the documented schema (`$schema`, `name`, `description` only).

## 5. Report
Use `references/report-template.md`. Recommend one of: install as pinned, install with changes (list them), or do not
install. Then stop and wait for the human.

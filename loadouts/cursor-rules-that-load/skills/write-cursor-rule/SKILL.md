---
name: write-cursor-rule
description: Add, split or fix a Cursor rule (.mdc) so it loads at the right time, and check it loads. Use when asked to write a rule, when a rule is ignored, or when converting .cursorrules.
---

# Write a Cursor rule

1. **Decide the container** with the table in AGENTS.md. If it belongs in `AGENTS.md`, a skill or a hook, do that instead and stop.
2. **Pick the type**: always, auto-attached (globs), agent-requested (description) or manual. Default to auto-attached.
3. **Write the file** at `.cursor/rules/<topic>.mdc`, using `references/examples.md` as the pattern. Topic names are kebab-case.
4. **Lint it**: `python3 .agents/skills/write-cursor-rule/scripts/rules_lint.py .` prints each rule's load type
   (always, auto, agent, manual) and must report `0 to fix`. It catches `.md` files Cursor ignores, missing front
   matter, globs written as a YAML list, `@file` mentions that don't exist, unknown keys, `alwaysApply: true` with
   globs, descriptions that don't say when, legacy `.cursorrules` and lines copied from `AGENTS.md`.
5. **Test it loads**: tell the human to open a file the globs match, start a new chat and ask "Which rules are attached?".
   For agent-requested rules, ask a question the description covers and check the rule is pulled in.
6. **Remove duplicates**: delete the same instruction from `AGENTS.md`, `.cursorrules` or other rules.

## Fixing an ignored rule
- A `.md` file in `.cursor/rules`: rename it to `.mdc` and add front matter, or move the text into `AGENTS.md`.
- `alwaysApply: true` with globs: globs do nothing. Pick one.
- Globs written as a YAML list: rewrite as one string, `src/**/*.ts, src/**/*.tsx`.
- Description that says what the rule is ("TypeScript rules") instead of when to use it ("Use when editing API handlers").
- Rule too long or contradicting `AGENTS.md`: shorten, and make `AGENTS.md` the single source.

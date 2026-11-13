# AGENTS.md: writing agent rules that actually load

Rules only help if the agent loads them at the right moment. Decide where each instruction goes before writing it.

## Pick the container
| Instruction | Put it in |
|---|---|
| Applies to every task (build/test commands, hard constraints) | `AGENTS.md` |
| Applies to some files (`*.tsx`, `migrations/**`) | Cursor rule with `globs`; Copilot `.instructions.md` with `applyTo`; or a nested `AGENTS.md` |
| A procedure used sometimes (release, migration, triage) | A skill: `.agents/skills/<name>/SKILL.md` |
| Must never happen (force-push, reading `.env`) | A hook or permission deny rule. Text rules are advice; hooks enforce |

## Cursor rule types (`.cursor/rules/*.mdc`)
Rules must be `.mdc` files; a plain `.md` file in `.cursor/rules` is ignored. Subfolders
inside it work too. Front matter has three keys only: `description`, `globs`, `alwaysApply`.
- Always: `alwaysApply: true`. Use for very few rules; each costs context in every chat.
- Auto-attached: `globs: src/**/*.tsx` and `alwaysApply: false`. Loads when a matching file is in context.
- Agent-requested: `description` set, no `globs`, `alwaysApply: false`. The agent reads the description and decides; write the description as "Use when …".
- Manual: no description, no globs. Loads only when someone types `@rule-name`.

## Writing rules
- One topic per rule file, under ~60 lines. Imperative sentences. Show the exact command or code shape.
- Say what to do, not only what to avoid. Pair each "never" with the alternative.
- Do not restate defaults the agent follows anyway.
- `.cursorrules` is legacy and no longer in Cursor's docs. Move its content into `.cursor/rules/` or `AGENTS.md`
  and delete it.
- Plain-markdown instructions for one folder can be a nested `AGENTS.md` in that folder; Cursor combines it with the
  parent ones, the more specific file winning.
- An `@path/to/file` mention in a rule is a pointer, not an include: the agent reads the file only if it decides to.
  Anything that must always be in context goes in the rule body.
- Cursor suggests keeping each rule under 500 lines; this loadout aims for far less.
- `.cursor/rules` does not apply to Bugbot code review; review rules go in `.cursor/BUGBOT.md`.
- Long rules that are really procedures become skills. Cursor's `/migrate-to-skills` converts agent-requested rules.

Use the `write-cursor-rule` skill to add or fix a rule, and test that it loads.

## Commands
- `python3 .agents/skills/write-cursor-rule/scripts/rules_lint.py .`: how each rule loads, and why some never will

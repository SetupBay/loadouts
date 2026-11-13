---
name: skill-listing-audit
description: Check that every skill's description fits the agent's skill listing and says when to use it. Use when adding, writing or renaming a skill, when a skill works with /name but never fires on its own, or when an agent warns that skill descriptions were truncated.
---

# Skill listing audit

Agents never read your skills up front. They read a **listing**: each skill's name and description, squeezed into a
fixed budget. If the listing overflows, descriptions get cut or dropped, and the keywords that would have matched
the user's request go with them. A skill that only works when typed as `/name` usually has this problem.

What the agents document:
- **Claude Code**: the listing budget is 1% of the model's context window. Each entry (`description` plus
  `when_to_use`) is cut at 1,536 characters. When the listing overflows, the least-used skills lose their
  descriptions first. Raise it with `skillListingBudgetFraction` or `SLASH_COMMAND_TOOL_CHAR_BUDGET`, or set a
  low-priority skill to `"name-only"` in `skillOverrides`. `/doctor` estimates the cost; `/skill-doctor` lists
  skills that are never used.
- **Codex**: the initial list uses at most 2% of the context window, or 8,000 characters when the window is unknown.
  Descriptions are shortened first, then skills are left out with a warning. `skills.max_context_tokens` changes it
  (up to 10,000 tokens). `name` and `description` are both required.

## 1. Run the audit
```bash
python3 .agents/skills/skill-listing-audit/scripts/skill_listing.py .claude/skills .agents/skills
```
Add `--context 1000000` for a 1M-token model. Point it at a plugin's `skills/` folder to check a plugin before
publishing. It only reads files.

## 2. Fix errors first
- **No description**: write one (step 3). Do not rely on the body's first line.
- **Over 1,536 characters**: the end is cut off in Claude Code. Move detail into the body; the description is a
  trigger, not documentation.
- **Front matter not valid**: an unquoted `: ` inside a value (for example `description: Triggers: X, Y`) makes YAML
  read a nested key, and some agents then skip the skill. Quote the whole value.

## 3. Then make each description trigger
Write it in this order, in plain words a user would type:
1. **What it does**, first sentence, under 200 characters. If the listing is cut, this is what survives.
2. **"Use when ..."** with the real triggers: the task, the file types, the error message, the words people use.
3. **What it is not for**, only when a neighbouring skill is easily confused with it.

See `references/description-examples.md` for before/after pairs. Fix overlap warnings by saying what makes each skill
different, or merge the two skills.

## 4. Check it fires
Seeing a skill trigger once is not proof. For each changed skill, write three realistic prompts that should use it
and one that should not. Try each in a fresh session with the skill on, then with it off, and compare. Keep the prompts
in the skill folder (for example `evals/triggers.md`) so the next edit can be checked the same way.

## 5. Report
List each skill you changed with its old and new length, the listing total against both budgets, and the trigger
prompts you tried, with what happened.

# AGENTS.md: skills that get used

This project keeps agent skills in `.agents/skills/` (and `.claude/skills/` for Claude Code). Agents choose a skill
from its `description` alone, inside a listing with a fixed budget. A skill with a weak or cut-off description
might as well not be installed.

## Rules for every SKILL.md
- Front matter has `name` (same as the folder) and `description`. Quote any value that contains `: `.
- The description starts with what the skill does, in one sentence under 200 characters, then "Use when ..." with
  the words a user would type. Keep `description` plus `when_to_use` well under 1,536 characters; 300–600 is plenty.
- Detail, steps, examples and history go in the body or in `references/`, never in the description.
- No two skills with overlapping descriptions. Merge them, or say what makes each different.
- Skills with side effects (deploy, publish, send) use `disable-model-invocation: true` where the agent supports it.
- The most important instructions go near the top of the body: after compaction, agents may keep only the start
  of a skill they already loaded.

## Before you say a skill change is done
1. Run the `skill-listing-audit` skill's audit on the skills folders. It must report `0 error(s)`; explain any warning
   you leave.
2. Try the changed skill on three prompts that should trigger it and one that should not, each in a fresh session.
3. Report the listing total against the budgets the audit prints.

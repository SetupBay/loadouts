# Skill descriptions: before and after

The description is read by the agent to decide whether to load the skill. It is a trigger, not a summary of the body.

## Too vague
Before: `description: Helps with database stuff.`
After: `description: Write and review Postgres migrations as SQL files. Use when adding a table, column or index, changing a constraint, or when a migration fails to apply.`

Why: "database stuff" matches nothing a user types. The after version names the task, the objects and the failure.

## Key use case buried
Before: `description: This skill was written after several incidents in which our team noticed that agents would sometimes produce release notes that did not match the actual changes, so it now gathers merged PRs and ...`
After: `description: Draft release notes from the PRs merged since the last tag. Use when the user asks for release notes, a changelog entry or "what shipped".`

Why: when the listing is cut, only the start survives. History belongs in the body, if anywhere.

## Missing the words people use
Before: `description: Performs Lighthouse-style auditing of web pages.`
After: `description: Measure page speed and fix slow loads with Chrome DevTools traces. Use when a page feels slow, LCP or CLS is poor, or the user mentions Core Web Vitals, PageSpeed or Lighthouse.`

## Two skills nobody can tell apart
Before:
- `review: Review code changes for problems.`
- `pr-check: Check pull requests for issues.`

After:
- `review: Review the uncommitted diff for bugs and risky changes before a commit. Use when the user asks to review, check or look over their changes.`
- `pr-check: Run the repository's PR checklist (tests, changelog, screenshots) on an open pull request. Use when preparing or updating a PR. Not for reviewing code itself.`

## Unquoted colon
Before: `description: Triggers: deploy, release, ship`
After: `description: "Deploy the app to staging or production. Triggers: deploy, release, ship."`

Why: YAML reads `Triggers:` as a nested key. Quote any value that contains `: `.

## A skill only a human should start
For deploys and other actions with side effects, set `disable-model-invocation: true` (Claude Code) so the
description stays out of the model's listing and the skill runs only when typed as `/name`. It then costs no budget.

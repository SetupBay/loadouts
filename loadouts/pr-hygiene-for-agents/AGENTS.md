# AGENTS.md: commits and pull requests made by agents

Review is the bottleneck. Make every commit and pull request cheap to review and safe to publish.

## Commits
- One logical change per commit. Message: imperative subject under 72 characters, blank line, why (not what).
- Never commit generated build output, lockfile churn you did not intend, `.env*` files, logs or editor folders.
- Never push to the default branch. Never force-push a branch someone else may have pulled.

## Pull requests
- Small: aim for under ~400 changed lines. Split refactors from behaviour changes.
- The body has four headings: **What**, **Why** (link the issue: `Fixes #123`), **How tested** (commands run and results), **Notes** (risks, follow-ups).
- UI changes include before/after screenshots. With gh 2.99+: `gh pr create --attach before.png#"Before: empty state" --attach after.png#"After"`.
- Open as draft until checks pass and you have reviewed your own diff once.
- Answer every review comment, with a commit or a reason.

## Attribution and leaks
- Follow the repository's policy on AI disclosure (CONTRIBUTING.md, PR template). If it asks for disclosure, disclose plainly.
- Never put private links in public places: agent session URLs, internal dashboards, local file paths, customer names.
- Before pushing, run the leak check in the `open-pull-request` skill.
- Claude Code users: `attribution.sessionUrl: false` in settings stops session links being added to commits from cloud and
  Remote Control sessions (snippet in the `open-pull-request` skill).

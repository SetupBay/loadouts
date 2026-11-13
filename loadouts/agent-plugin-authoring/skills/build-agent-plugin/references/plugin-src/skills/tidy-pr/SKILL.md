---
name: tidy-pr
description: Tidy a branch before opening or updating a pull request. Use when asked to prepare a PR, clean up commits or write a PR description.
---

# Tidy a pull request

1. Run `git status` and `git log --oneline origin/HEAD..` to see what the branch holds.
2. Name anything unrelated to the PR's purpose and ask before moving it to another branch.
3. Run the project's formatter, linter and tests. Fix failures caused by this branch; report others.
4. Write the description: what changed, why, how it was tested, and what a reviewer should look at first.
5. Check library calls against current docs with the plugin's `context7` MCP server when a version changed.

Never force-push a branch someone else has pushed to. Ask first.

---
name: add-ci-agent-job
description: Add a GitHub Actions job that runs Claude Code or Codex headless with least privilege, a budget and pinned versions. Use when asked to automate review, triage, docs updates or other agent work in CI.
---

# Add a CI agent job

1. **Define the job**: trigger, task, read-only or write, output (PR comment, artefact, commit on a branch). Prefer read-only
   jobs that comment; jobs that write should open a PR, never push to the default branch.
2. **Start from** `references/agent-review.yml`. Keep its permissions block, `pull_request` trigger, pinned install,
   `--bare`, budget and timeout.
3. **Prompt file**: write `.github/prompts/<job>.md` with task, scope, output format and the stop rule.
4. **Untrusted input**: pass PR or issue text via files written by `gh` (`gh pr diff "$PR" > pr.diff`), never via
   `${{ github.event.* }}` inside `run:`.
5. **Secrets**: tell the human which repository secret to add (`ANTHROPIC_API_KEY` or `CODEX_API_KEY`). Do not create it.
6. **Test** on a branch: open a small PR against it, check the job's output, cost line and failure handling
   (temporarily set a tiny budget to see the job fail).
7. **Document** the job in `AGENTS.md` or the README: what it does, what it may touch, how to turn it off.

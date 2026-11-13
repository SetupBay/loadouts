# AGENTS.md: GitHub Actions hardening

Rules for writing or changing anything under `.github/workflows/`, including workflows that run AI agents on issues
and pull requests. A workflow is code that runs with the repository's tokens and secrets; review it like code.

## Every workflow
- Pin every third-party action to a full commit SHA with the version in a comment:
  `uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`. Tags and branches can be moved.
  Keep pins current with Dependabot (`package-ecosystem: github-actions`), not by switching back to tags.
- `permissions: {}` at the top, then grant each job only what it needs (`contents: read`, `issues: write`, ...).
- `actions/checkout` with `persist-credentials: false` unless a later step must push.
- Never write `${{ github.event.* }}`, `${{ github.head_ref }}` or other attacker-controllable values inside `run:`.
  Pass them through `env:` and quote the variable: `TITLE: ${{ github.event.issue.title }}` then `"$TITLE"`.
- Secrets only in the steps that need them, through `env:` or `with:`. Never echo them or write them to files that
  are uploaded as artifacts.
- Pin runner images (`ubuntu-24.04`, not `ubuntu-latest`) when reproducibility matters.

## Triggers
- Avoid `pull_request_target` and `workflow_run`. If one is unavoidable, never check out or run the pull request's
  code in that job, and never give it secrets.
- Code from forks runs under `pull_request`, with a read-only token and no secrets. Keep it that way.

## Workflows that run AI agents
- Issue and PR text is untrusted input to the agent. Run the agent job with a read-only token and no write secrets.
- Split "think" from "act": the agent job writes its proposal to an artifact or output; a separate job with narrow
  write permission applies it after checks (labels from a fixed list, comments only, no pushes to default branches).
- Pin agent actions and CLIs to exact versions, and cap spend and turns where the tool supports it.

## Before finishing
- Run the `harden-workflow` skill: `uvx zizmor@1.31.1 --offline .github/workflows` must report no findings, or each
  remaining finding is justified in a comment and the PR description.
- Do not push workflow changes to the default branch or re-run workflows with secrets unless the user asks.

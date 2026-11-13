---
name: harden-workflow
description: Audit and fix GitHub Actions workflows with zizmor before they are committed. Pins actions to commit SHAs, narrows permissions, removes template injection and unsafe triggers. Use for any change under .github/workflows.
---

# Harden a workflow

Example of the target shape: `references/issue-triage.yml`.

1. Audit offline (no token needed): `uvx zizmor@1.31.1 --offline .github/workflows`. Exit code 0 means no findings.
   With a `GH_TOKEN`, drop `--offline` to enable the online audits (known-vulnerable actions, impostor commits).
2. Fix by audit name:
   - `unpinned-uses`: resolve the SHA for the tag you want with
     `gh api repos/OWNER/REPO/git/ref/tags/TAG --jq .object.sha`. If `.object.type` is `tag` (annotated),
     follow it once more with `gh api repos/OWNER/REPO/git/tags/SHA --jq .object.sha`. Write
     `uses: OWNER/REPO@SHA # TAG`.
   - `template-injection`: move the expression into `env:` and reference `"$VAR"` in the script.
   - `excessive-permissions`: add `permissions: {}` at the top and per-job grants.
   - `artipacked`: set `persist-credentials: false` on checkout.
   - `dangerous-triggers`: switch `pull_request_target` to `pull_request`, or split privileged work into a job that
     never touches PR code.
3. Re-run zizmor until clean. If you must keep a finding, add an inline `# zizmor: ignore[audit-name]` comment with
   the reason, and mention it to the user.
4. Check the workflow still parses: `gh workflow view <file>` on a pushed branch, or `actionlint` if installed.
5. Summarise the changes for the user. Do not push to the default branch yourself.

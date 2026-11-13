---
name: open-pull-request
description: Prepare and open a reviewable pull request with gh, including a leak check, a structured body and screenshots for UI changes. Use when work on a branch is ready for review.
---

# Open a pull request

1. **Self-review.** `git diff origin/<base>...HEAD --stat`, then read the full diff once. Remove debug output and stray files.
2. **Checks.** Run the project's test, lint and type-check commands. Note the results for the body.
3. **Leak check.** Inspect commit messages and the diff for things that must not go public:
   ```sh
   git log origin/<base>..HEAD --format='%H %s%n%b' | grep -niE 'session|claude\.ai/code|chatgpt\.com|localhost:|/Users/|/home/' || echo "messages clean"
   git diff origin/<base>...HEAD | grep -nE '^\+.*(api[_-]?key|secret|password|token)\s*[:=]' || echo "diff clean"
   ```
   Matches are not always problems; read each one. Rewrite messages of unpushed commits with `git commit --amend` or an
   interactive rebase only on your own unpushed branch. If something sensitive was already pushed, stop and tell the human.
4. **Screenshots** for UI changes: capture before and after (same viewport), save outside the repo, attach with `--attach`.
5. **Create.** Write the body from `references/pr-body.md` into a temporary file, then:
   `gh pr create --draft --base <base> --title "<subject>" --body-file <file> [--attach <img>#"<alt text>"]`
6. **Mark ready** with `gh pr ready` once checks are green. Report the PR URL.

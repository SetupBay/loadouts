---
name: set-up-review-rules
description: Create or tune review-only instruction files for Claude Code Review, Cursor Bugbot and Copilot code review from one rule list. Use when setting up AI code review or when reviews are noisy or miss team rules.
---

# Set up review rules

1. **Collect evidence.** Read the last 10–20 AI review comments if available (`gh pr list --state merged --limit 20`,
   then `gh pr view <n> --comments`). Note false positives, noise categories and real misses.
2. **Write one rule list** with four sections: severity definitions, nit cap, do not report, always check.
   Start from `references/review-rules-template.md`. Every rule must come from evidence or a known team requirement.
3. **Generate the files** for the reviewers the team uses:
   - Claude Code Review: root `REVIEW.md`; subdirectory `REVIEW.md` only for path-specific checks.
   - Cursor Bugbot: `.cursor/BUGBOT.md` with the same content.
   - Copilot: `.github/instructions/code-review.instructions.md` using `references/copilot-review-instructions.md`.
4. **Keep coding rules out.** Rules that also apply while writing code belong in `AGENTS.md`, not in review files.
5. **Land it.** Open a PR with only these files. Remind the human that Claude Code Review reads `REVIEW.md` from the
   default branch, so the new rules apply to PRs opened after the merge, and that branch protection is needed for
   subdirectory files and severity overrides to count.
6. **Re-check** after a week of reviews: delete rules that never fired, sharpen rules that were misapplied.

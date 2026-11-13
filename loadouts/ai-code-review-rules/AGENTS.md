# AGENTS.md: rules for AI code reviewers

This repository is reviewed by AI reviewers (Claude Code Review, Cursor Bugbot, GitHub Copilot code review) as well as people.
Review rules live in review-only files, separate from coding instructions, and are kept short and testable.

## Which file each reviewer reads
| Reviewer | Reads | Notes |
|---|---|---|
| Claude Code Review (service) | `REVIEW.md` (root, plus subdirectory files) and CLAUDE.md files | Read from the base or default branch, never from the PR. Merge rule changes first. Protect the default branch or subdirectory files and severity overrides are ignored |
| Claude Code `/code-review` (local) | CLAUDE.md only | Does not read `REVIEW.md` |
| Cursor Bugbot | `.cursor/BUGBOT.md` (root always; nested ones for changed paths) | `.cursor/rules` does not apply to Bugbot |
| Copilot code review | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | Use `excludeAgent: "coding-agent"` for review-only instruction files |

## Writing review rules
- Define severity for this repo: what counts as blocking (wrong behaviour, data leak, unsafe migration) and what is a nit at most.
- Cap nits (for example "at most five per review").
- List what not to report: anything CI enforces (lint, format, types), generated paths, lockfiles, vendored code.
- List what to always check, as concrete, checkable rules ("new API routes have an integration test").
- Require evidence: behaviour claims must cite `path:line`, not infer from names.
- One rule per line. No style essays. Under ~60 lines per file.
- When a reviewer is repeatedly wrong about something, add a rule; when a rule never fires, delete it.

## When you are the author
Before opening a PR, read the review files above and check your diff against the "always check" rules yourself.
Use the `set-up-review-rules` skill to create or change these files.

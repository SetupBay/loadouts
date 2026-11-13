---
name: plain-prose
description: Rewrite or check prose so it does not read as machine-written. Use for READMEs, docs, release notes, PR descriptions, commit messages and UI copy, before showing them to the user.
---

# Plain prose

1. Lint first: `python3 scripts/prose_lint.py <file> [<file> ...]`. It skips fenced code, inline code and block
   quotes, and prints `path:line rule "match" -> suggestion`. Exit code 1 means there are findings.
2. Fix each finding by rewriting the sentence, not by swapping in a synonym. Most findings mean the sentence has no
   content: delete it, or replace it with the specific fact it was gesturing at.
3. Read `references/word-list.md` for the patterns and the plain alternatives.
4. Re-run the lint until it is clean, or until every remaining finding is deliberate (a quotation, a product name).
   Pass `--allow word` for a deliberate exception and say why in your reply.
5. Read the result aloud in your head. If a sentence would sound odd said to a colleague, rewrite it.

## Before and after
- Before: "This powerful tool seamlessly empowers teams to unlock their full potential."
  After: "Runs the test suite on every push and posts failures to the PR."
- Before: "It's not just a linter, it's a complete quality journey."
  After: "It lints Markdown and checks links."
- Before: "Trusted by 10,000+ developers worldwide."
  After: cut it, or "Downloaded 12,400 times last month (npm, October 2026)."

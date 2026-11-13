---
name: write-handoff
description: Write HANDOFF.md so a fresh session or a different agent can continue without the old context. Use before clearing or compacting context, at the end of a long session, or when switching agents or people.
---

# Write a handoff

1. Gather facts, do not summarise from memory alone:
   - `git rev-parse --abbrev-ref HEAD` and `git rev-parse --short HEAD`
   - `git status --short` and `git diff --stat` for files touched
   - Run the project's test command once and copy the first failing test and its exact error line.
2. Fill in `references/HANDOFF.template.md` and save it as `HANDOFF.md` at the repository root. Keep every heading.
   Write "none" rather than deleting a section.
3. Check it: `python3 scripts/check_handoff.py HANDOFF.md`. Fix everything it reports. It checks the required
   sections, the recorded commit against `HEAD`, length, leftover placeholders and secret-shaped strings.
4. Tell the user where the file is and the single next step. Do not commit it unless the user asks.

## Writing well
- Goal: one sentence on what "done" means, in the user's words.
- Decisions: what you chose, the alternative you rejected, and why. These are what compaction loses first.
- Failing or open: exact test name, command and error. "Tests flaky" is not useful; `test_refund_rounding: expected
  10.00, got 9.99` is.
- Next step: one concrete action the next session can start on without asking.

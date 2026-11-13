---
name: implement-spec
description: Build an approved SPEC.md ticket by ticket with tests for each acceptance criterion, in parallel where tickets are independent, then review against the spec. Use after a spec has been approved.
---

# Implement a spec

1. **Check approval.** `SPEC.md` status must be `approved` and open questions empty. Otherwise stop.
2. **Plan waves.** From `TASKS.md`, group tickets with no dependencies and no shared files into waves.
3. **Per ticket** (yourself, or one subagent or worktree per ticket in a wave):
   - Write the test for the ticket's acceptance criteria first and see it fail.
   - Implement until it passes; run the full test suite.
   - Tick the ticket in `TASKS.md` and commit: `feat(<slug>): T<n> <title>`.
4. **Between waves** pull in finished work and run the full suite before starting the next wave.
5. **Spec drift.** If a ticket cannot meet its criterion as written, stop that ticket, propose a spec change to the human,
   and continue only with unaffected tickets.
6. **Final review** against the spec, by a reviewer that did not write the code: every AC has a passing test, nothing out of
   scope was built. Set `Status: done` in `SPEC.md`.

Heavier frameworks exist if the team wants more structure: GitHub Spec Kit (`specify` CLI) and OpenSpec
(`npx @fission-ai/openspec`). Use them only if the repository already does; do not mix formats.

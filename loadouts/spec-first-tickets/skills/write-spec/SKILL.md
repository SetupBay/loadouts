---
name: write-spec
description: Interview the human and research the codebase to write SPEC.md and TASKS.md for a feature before any code. Use when asked to plan or build a non-trivial feature.
---

# Write a spec

1. **Research first, quietly.** Read the relevant code (delegate broad reading to a read-only subagent where available).
   Note existing patterns, data models and tests the feature must fit.
2. **Interview.** Ask the human at most five questions at a time, only ones the code cannot answer: users, edge cases,
   limits, what is out of scope. Offer a recommended answer with each question.
3. **Draft** `specs/<date>-<slug>/SPEC.md` from `references/spec-template.md`. Every acceptance criterion must be testable.
4. **Split into tickets** in `TASKS.md` (format in the template): small, file-scoped, mapped to criteria, dependencies marked.
5. **Review with the human.** Show the spec and tickets; list open questions. Change nothing in source code until the human
   approves the spec.
6. **Commit** the spec folder on its own: `docs(spec): <slug>`.

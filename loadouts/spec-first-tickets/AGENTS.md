# AGENTS.md: spec first, then tickets, then code

For any change bigger than a small fix, agree a written spec with the human before writing code, then implement it
as small tickets with checkable acceptance criteria.

## When a spec is required
- New feature, new endpoint or screen, schema change, cross-module refactor, or anything estimated over ~200 lines.
- Not required: bug fixes with a failing test, copy changes, dependency bumps, one-file refactors.

## Files
- Specs: `specs/<yyyy-mm-dd>-<slug>/SPEC.md`. Tickets: `TASKS.md` in the same folder. Both committed.
- The spec is the source of truth. If implementation reveals the spec is wrong, stop, update the spec and tell the human.

## Spec rules
- Problem and goal first; the solution second. Name what is out of scope.
- Acceptance criteria are observable and testable: "GET /api/orders?status=open returns only open orders, newest first".
  Not "orders are filtered correctly".
- List open questions instead of guessing. Do not start implementation while any are unanswered.
- Keep it short: one to two screens.

## Ticket rules
- Each ticket is independently testable and small (under ~200 changed lines), lists the files it touches, and maps to
  one or more acceptance criteria.
- Mark dependencies. Tickets with no shared files and no dependency can run in parallel.
- A ticket is done when its criteria pass in a test, not when the code compiles.

Use the `write-spec` skill to draft the spec and tickets, and the `implement-spec` skill to build them.

---
name: polars-2-guard
description: Check Python for Polars 1.x APIs that Polars 2 removed, and for calls whose results changed silently in 2.0, before saying a Polars change is done. Use after writing or editing Polars code, when Polars raises AttributeRemovedError or ArgumentRemovedError, or when porting older Polars or pandas snippets.
---

# Polars 2 guard

Polars 2.0 (6 October 2026) removed most names deprecated during 0.20 and 1.x, and changed defaults: lazy
queries now run on the streaming engine, which doesn't keep row order, `explode()` drops empty lists, and
horizontal `concat` refuses frames of different heights. Removed names fail loudly. The changed defaults don't.

## 1. Confirm the version
- `uv run python -c "import polars; print(polars.__version__)"` must print `2.x`. If it prints `1.x`, stop and ask
  whether the project is meant to move to Polars 2 before changing anything.

## 2. Scan
```bash
python3 .agents/skills/polars-2-guard/scripts/polars2_guard.py src tests
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.
With no arguments it scans the current folder, skipping virtualenvs and agent folders.)

- Every `error` line is an API Polars 2 removed. Fix it with the replacement the line gives;
  `references/rename-table.md` has the table with examples.
- `warn` lines are calls that still run but may now give a different answer. Decide for each one:
  - join or unpivot where order matters → add `maintain_order="left"` or `.sort(...)`;
  - `explode` where the row count matters → `empty_as_null=True`, or accept the new count;
  - a `BytesIO` round trip → `buf.seek(0)` before reading.
  If the current behaviour is what you want, add a `# guard: ok` comment to that line. That silences warnings,
  never errors.
- Run it again until it prints `0 error(s)`.

## 3. Let Polars check it
- Run the tests or the script with the pinned version: `uv run pytest -q` or `uv run python <script>.py`.
- An `AttributeRemovedError` or `ArgumentRemovedError` names the replacement. Use it.
- For pipelines whose output is compared elsewhere, compare row counts and a sorted sample before and after.

## 4. Report
Say how many Polars 1 calls you replaced, which silent changes you checked (order, counts, names) and how, and that
the scanner and tests were clean.

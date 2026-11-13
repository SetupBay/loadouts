# AGENTS.md: Polars 2 project (Polars 1 guard)

This project uses **Polars 2** (`polars>=2.1,<3`). Most Polars code you have seen is Polars 0.19–1.x. Polars 2
removed many of those names, and changed some results without raising, so treat remembered Polars as suspect.

## Version facts
- Check the pinned version first: `uv pip show polars` or the `polars` line in `pyproject.toml`/`uv.lock`.
- Lazy queries default to the **streaming engine** in 2.0. It does not keep row order for joins, `group_by` or
  `unpivot` unless you ask (`maintain_order=...`) or sort.
- Removed APIs raise `AttributeRemovedError` or `ArgumentRemovedError` with a hint. Read the hint; don't guess.
- If you are unsure an API exists in Polars 2, look it up in the API reference (https://docs.pola.rs/api/python/stable/)
  or the upgrade guide (https://docs.pola.rs/releases/upgrade/2/). Never copy Polars 1 answers or pandas idioms.

## Rules
- Write Polars 2 only. The `polars-2-guard` skill has the full table; the common traps are:
  `unpivot` (not `melt`), `with_row_index` (not `with_row_count`), `group_by(...).len()` (not `.count()`),
  `how="full"` (not `"outer"`), `nulls_equal=` (not `join_nulls=`), `str.join` (not `str.concat`),
  `engine="streaming"` (not `streaming=True`), `min_samples=` (not `min_periods=`), `str.to_date()` (not `.cast(pl.Date)` on strings).
- Prefer expressions over `map_elements`. Never use pandas methods on a Polars frame.
- If row order matters, say so in code: `.sort(...)` or `maintain_order="left"` on joins.
- Don't upgrade or downgrade Polars, and don't set `POLARS_ENGINE_AFFINITY`, without asking the human.

## Before you say "done"
1. Run the `polars-2-guard` scanner on the files you touched; it must report `0 error(s)`. Read every `warn`.
2. Run the code or its tests against the pinned Polars (`uv run pytest`, `uv run python <script>.py`).
3. If you changed a query whose row order or row count could differ in Polars 2, say which and how you checked it.

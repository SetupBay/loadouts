# Polars 1 → Polars 2 table

From the Polars 2.0 upgrade guide (https://docs.pola.rs/releases/upgrade/2/). Checked against polars 2.1.0.

## Removed: raises in Polars 2

| Polars 1.x (or older) | Polars 2 |
|---|---|
| `df.melt(id_vars="a", value_vars=["b"])` | `df.unpivot(index="a", on=["b"])` |
| `df.with_row_count()` (column `row_nr`) | `df.with_row_index()` (column `index`) |
| `df.group_by("k").count()` | `df.group_by("k").len()` |
| `df.groupby("k")` | `df.group_by("k")` |
| `join(how="outer")` / `"outer_coalesce"` | `join(how="full")` / `how="full", coalesce=True` |
| `join(join_nulls=True)` | `join(nulls_equal=True)` |
| `pl.col("s").str.concat("-")` | `pl.col("s").str.join("-")` (default delimiter is now `""`) |
| `lf.fetch(5)` | `lf.head(5).collect()` |
| `lf.profile()` | none; time `collect()` instead |
| `collect(streaming=True)` | `collect(engine="streaming")` |
| `read_csv(dtypes={...})` | `read_csv(schema_overrides={...})` |
| `rolling_mean(3, min_periods=1)` | `rolling_mean(3, min_samples=1)` |
| `lf.with_context(other)` | `pl.concat([lf, other], how="horizontal")` |
| `pl.threadpool_size()` | `pl.thread_pool_size()` |
| `pl.col("a").where(cond)` | `pl.col("a").filter(cond)` |
| `.apply(f)` (removed in 1.0) | a native expression; `map_elements(f)` as a last resort |
| `.map_dict(d)` | `.replace(d)` or `.replace_strict(d)` |
| `.replace(d, default=x)` | `.replace_strict(d, default=x)` |
| `read_parquet(allow_missing_columns=True)` | `read_parquet(missing_columns="insert")` |
| `read_*(rechunk=True)` | `read_*(...).rechunk()` |
| `read_ipc(memory_map=True)` | `read_ipc(...)` |
| `hash(1, 2, 3, 4)` | `hash(1)` |
| `pl.Categorical(ordering="lexical")` | `pl.Categorical()` (always lexical) |
| `list.to_struct(upper_bound=3)` | `list.to_struct(["a", "b", "c"])` |
| `concat(how="horizontal", strict=False)` | `concat(how="horizontal_extend")` |
| `Expr.flatten()` | `list.explode(keep_nulls=False, empty_as_null=False)` |
| `top_k(k, by=..., descending=True)` | `top_k(k, by=..., reverse=True)` |
| `pivot(columns="c")` | `pivot(on="c")` |
| `pl.Series(["2026-10-01"]).cast(pl.Date)` | `pl.Series(["2026-10-01"]).str.to_date()` |

## Changed silently: same code, different answer

| Change in 2.0 | What to do |
|---|---|
| Lazy `collect()` runs on the streaming engine; joins, `group_by`, `unpivot` don't keep row order | `.sort(...)`, or `join(..., maintain_order="left")` |
| `explode()` turns an empty list into zero rows (was one null row) | `explode(..., empty_as_null=True)` for the old count |
| `concat(how="horizontal")` raises on different heights (used to pad) | pad on purpose with `how="horizontal_extend"` |
| `pl.datetime(...)` / `pl.repeat(...)` named after their first argument | `.alias("datetime")` |
| Reading a `BytesIO` starts at its current position | `buf.seek(0)` after writing |
| Signed int + `UInt64` gives `Int128`, not `Float64` | cast if a float was expected |
| Headerless CSV columns are `column_0, column_1, ...` | update names that started at `column_1` |
| Map columns from Arrow/Parquet load as `pl.Map` | `.map.entries()` for the old list-of-structs shape |
| `cut()` / `qcut()` deprecated | `bin_intervals(...)` / `bin_quantiles(...)`, `right_closed=True`, labels required |

To restore the in-memory engine for one query: `lf.collect(engine="in-memory")`. Ask before doing it project-wide.

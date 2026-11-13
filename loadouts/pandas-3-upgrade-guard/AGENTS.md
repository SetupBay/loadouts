# AGENTS.md: pandas 3 project (pandas 1 and 2 guard)

This project uses **pandas 3** (`pandas>=3.1,<4`). Most pandas code you have seen predates it. pandas 3 removed a
long list of deprecated APIs and changed two things that make old code wrong without an error:
**copy-on-write is always on**, and **strings are the `str` dtype, not `object`**.

## Version facts
- Check the pin first: `uv pip show pandas` or the `pandas` line in `pyproject.toml`/`uv.lock`.
- Copy-on-write: every indexing result behaves as a copy. Chained assignment (`df["a"][0] = 1`) and
  `df["a"].fillna(0, inplace=True)` change a temporary copy and leave `df` alone. pandas only warns.
- `pd.Series(["a"]).dtype` is `str`. `dtype == object` checks are now false for string columns, and a
  string column refuses non-string values.
- Offset aliases: `h`, `min`, `s`, `ms`, `us`, `ns`; month, quarter and year ends are `ME`, `QE`, `YE`.
- If you are unsure an API exists in pandas 3, check the API reference (https://pandas.pydata.org/docs/reference/)
  or the 3.0 release notes (https://pandas.pydata.org/docs/whatsnew/v3.0.0.html). Don't copy pandas 1 answers.

## Rules
- Write pandas 3 only. The `pandas-3-guard` skill has the full table; the common traps are:
  `DataFrame.map` (not `applymap`), `pd.concat` (not `append`), `.ffill()` (not `fillna(method=)`),
  `sep=r"\s+"` (not `delim_whitespace`), `date_format=` (not `date_parser`), `freq="h"`/`"ME"` (not `"H"`/`"M"`),
  `errors="coerce"` (not `"ignore"`), `pd.read_json(io.StringIO(text))` (not literal JSON).
- Assign with one `.loc` call: `df.loc[mask, "col"] = value`. Never chain `[...][...] =`.
- Reassign instead of `inplace=True` on a column: `df["col"] = df["col"].fillna(0)`.
- Test for strings with `pd.api.types.is_string_dtype(s)`, not `dtype == object`.
- Don't upgrade or downgrade pandas without asking the human.

## Before you say "done"
1. Run the `pandas-3-guard` scanner on the files you touched; it must report `0 error(s)`. Read every `warn`.
2. Run the tests with warnings as errors for pandas' own warnings:
   `uv run pytest -W error::pandas.errors.ChainedAssignmentError`.
3. Say which silent changes (copy-on-write writes, string dtype checks) you looked for and where.

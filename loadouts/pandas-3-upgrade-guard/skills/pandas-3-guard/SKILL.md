---
name: pandas-3-guard
description: Check Python for pandas APIs removed in 3.0, chained assignment that copy-on-write ignores, and object-dtype string checks, before saying a pandas change is done. Use after writing or editing pandas code, when pandas raises an unexpected keyword or attribute error, warns ChainedAssignmentError, or when porting older pandas snippets.
---

# pandas 3 guard

pandas 3.0 (21 January 2026; 3.1 on 22 October 2026) removed what 2.x deprecated and turned on two behaviour
changes for good. Copy-on-write means a chained write such as `df["v"][0] = 1` changes a copy and leaves `df`
alone, with only a warning. The `str` dtype means string columns are no longer `object`. Removed names fail loudly.
Those two changes don't fail at all.

## 1. Confirm the version
- `uv run python -c "import pandas; print(pandas.__version__)"` must print `3.x`. If it prints `2.x`, stop and ask
  whether the project is moving to pandas 3. The pandas docs suggest getting clean on 2.3 first.

## 2. Scan
```bash
python3 .agents/skills/pandas-3-guard/scripts/pandas3_guard.py src tests notebooks
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- Every `error` line is either an API pandas 3 removed or a write that copy-on-write throws away. Fix it with the
  replacement the line gives; `references/rename-table.md` has the table.
- The chained-assignment rules only look at names like `df`, `*_df`, `frame*` and `data`, so a frame called
  something else can slip through. The test run below catches those.
- `warn` lines still run but may mean something different now: `dtype == object` checks, `agg(np.sum)`,
  groupby on categoricals. Fix them, or add `# guard: ok` to a line where the new behaviour is what you want.
  That silences warnings, never errors.

## 3. Let pandas check it
```bash
uv run pytest -q -W error::pandas.errors.ChainedAssignmentError
```
- `ChainedAssignmentError` is a warning by default. Turning it into an error makes every lost write fail a test.
- `TypeError: ... got an unexpected keyword argument` and `AttributeError: 'DataFrame' object has no attribute`
  mean a removed API. The release notes name each replacement.
- `TypeError: Invalid value ... for dtype 'str'` means code put a non-string into a string column. Convert on purpose
  (`astype(object)`) only if mixed values are really wanted.

## 4. Report
Say how many removed calls and chained writes you replaced, which dtype checks you changed, and that the scanner and
the tests (with ChainedAssignmentError as an error) were clean.

# AGENTS.md: Python data scripts

## Folders
```
data/raw/        inputs exactly as received — never modified, often git-ignored
data/interim/    intermediate files written by scripts
output/          final CSVs, charts, reports
scripts/         one script per job, numbered if they run in order: 01_clean.py, 02_report.py
```

## Every script is runnable with one command
- Use PEP 723 inline metadata so `uv run scripts/01_clean.py` installs what it needs:
  ```python
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["polars>=1.0", "matplotlib"]
  # ///
  ```
- Add dependencies with `uv add --script scripts/01_clean.py <package>` rather than editing by hand.
- Paths come from CLI arguments (`argparse`) with sensible defaults, built with `pathlib.Path`. No hard-coded absolute paths.
- Put the work in `main()` and end with `if __name__ == "__main__": main()`.

## Data handling
- Prefer **polars** for new scripts (fast, strict types); use pandas if the project already does.
- Read with explicit types for IDs, postcodes and phone numbers (strings, so leading zeros survive) and explicit date parsing.
- Never overwrite files in `data/raw/`. Write outputs to new files.
- After each major step (load, filter, join, dedupe), log the row count. A join that changes the row count unexpectedly is a bug until proven otherwise.
- State assumptions in code comments next to the line that makes them ("drops refunds: amount < 0").
- Money: keep as integer pence/cents or `Decimal`, not floats, when sums must reconcile.
- Dates: be explicit about time zones and day-first formats (UK data is usually DD/MM/YYYY).

## Output
- Print a short summary at the end: rows in, rows out, files written.
- Charts: label axes with units, title says what the chart shows, save as PNG and SVG to `output/`.
- Do not print or commit personal data. If the data contains names, emails or addresses, keep outputs aggregated unless asked otherwise.

## Style
- Type hints on functions. Small functions per step (`load`, `clean`, `summarise`), each returning a dataframe.
- `ruff format` and `ruff check` clean (`uvx ruff check .`).

## Before you say "done"
Run the script end to end on the real input (or a sample), show the summary output, and mention any rows dropped and why.

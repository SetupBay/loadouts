# AGENTS.md

`tidyparse`: a pure-Python library for parsing messy CSV exports. Supports Python 3.11 and later. Published to PyPI.

## Commands
- Set up: `uv sync`
- Tests: `uv run pytest -q` · one test: `uv run pytest -q tests/test_dates.py::test_iso_week`
- Lint and format: `uv run ruff check --fix` then `uv run ruff format`
- Types: `uv run mypy src`
- Docs preview: `uv run mkdocs serve`

## Layout
- `src/tidyparse/` the package; public API is exactly what `__init__.py` exports
- `tests/` mirrors `src/`; fixtures (sample CSVs) in `tests/data/`

## Conventions
- No new runtime dependencies without asking; dev dependencies go in the `dev` group
- Every public function has type hints and a docstring with one example
- Changes to public behaviour get a line in `CHANGELOG.md` under "Unreleased"
- Keep Python 3.11 compatible: no `type` statements or 3.12+ only syntax

## Never
- Change the public API (names, arguments, return types) without saying so first; it breaks users
- Bump the version or publish; releases are done by a maintainer
- Edit `tests/data/` files to make a test pass

## Done means
`uv run pytest -q`, `uv run ruff check` and `uv run mypy src` pass, new behaviour has a test, and `CHANGELOG.md` is updated.

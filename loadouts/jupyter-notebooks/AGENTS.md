# AGENTS.md: Jupyter notebooks

Data and ML work in Jupyter notebooks, managed with uv. Notebooks are paired with plain Python files by Jupytext and
committed without outputs.

## Editing notebooks
- Edit the paired `.py` file (Jupytext percent format, cells start with `# %%`), not the `.ipynb` JSON. Then sync:
  `uv run jupytext --sync notebooks/<name>.py`. Never hand-edit cell JSON, outputs or execution counts.
- New notebook: write `notebooks/<name>.py` in percent format and pair it:
  `uv run jupytext --set-formats ipynb,py:percent notebooks/<name>.py`.
- Keep outputs out of git: `nbstripout` is installed as a git filter (`uv run nbstripout --install`). Do not remove it.

## Done means it runs top to bottom
- Execute from a fresh kernel before reporting: `uv run jupytext --to ipynb --execute notebooks/<name>.py`
  (or `uv run jupyter nbconvert --to notebook --execute --inplace notebooks/<name>.ipynb`).
- A notebook that only works after running cells out of order is broken. Fix the order; no hidden state.
- Report the key numbers or the figure you produced, not just "it ran".

## Reproducibility
- Dependencies in `pyproject.toml` via `uv add`; no `!pip install` cells. Dev tools: `uv add --dev jupytext nbconvert
  ipykernel nbstripout` (executing needs nbconvert and ipykernel).
- One parameters cell near the top (paths, dates, sample sizes, seeds). No magic numbers further down.
- Seed every source of randomness (`numpy.random.default_rng(seed)`, framework seeds) and say so in the notebook.
- Paths relative to the project root; raw data in `data/raw/` is read-only and gitignored. Write outputs to
  `data/processed/` or `reports/`.
- Long training or heavy queries: move the code into a module in `src/` and import it; keep the notebook for narrative,
  checks and plots.

## Data care
- Look at the data before modelling: shape, dtypes, missing values, duplicates, a few rows. Use the
  `notebook-change` skill.
- Never print or commit personal data, credentials or full raw tables. Use `.head()` on synthetic or anonymised data.
- Split train and test before any fitting or scaling. Never tune on the test set.

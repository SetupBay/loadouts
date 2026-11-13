---
name: notebook-change
description: Change or add a Jupyter notebook through its Jupytext-paired .py file, check the data first, run it top to bottom in a fresh kernel and keep outputs out of git. Use for any notebook work.
---

# Notebook change

1. Find the paired `.py` file for the notebook (`jupytext --paired-paths notebooks/<name>.ipynb` if unsure). If the
   notebook is not paired yet, pair it first and commit that as its own change.
2. Read the parameters cell and the cells you will change. Edit the `.py` file only, keeping `# %%` cell markers and
   `# %% [markdown]` cells for narrative.
3. When data is involved, add or keep a check cell like the one in `references/analysis.py`: shape, dtypes, missing
   values and duplicates, with `assert` lines for what the rest of the notebook relies on.
4. Sync and execute from a fresh kernel: `uv run jupytext --sync notebooks/<name>.py` then
   `uv run jupytext --to ipynb --execute notebooks/<name>.py`. Fix any error and run again from the top.
5. Check git sees no outputs: `git diff --stat` shows the `.py` and a small `.ipynb` change; if outputs appear, run
   `uv run nbstripout notebooks/<name>.ipynb` and check the filter is installed.
6. Report: what changed, the key result (numbers or a figure described in words), and the run time.

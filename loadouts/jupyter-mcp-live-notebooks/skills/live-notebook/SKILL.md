---
name: live-notebook
description: Explore data, fix or extend a Jupyter notebook through the Jupyter MCP server (jupyter-mcp-server) on a JupyterLab the human started, keeping kernel state honest and proving the notebook reruns from a fresh kernel. Use when the user asks to work in a notebook, analyse data in JupyterLab, or a notebook breaks on Restart & Run All.
---

# Live notebook work with Jupyter MCP

Server: `uvx jupyter-mcp-server==2.2.4` (MCP Python SDK 2), talking to JupyterLab with real-time collaboration.
Tools come in four groups (full list: https://jupyter-mcp-server.datalayer.tech/mcp):

| Group | Tools you'll use |
|---|---|
| Server | `list_files`, `list_kernels` |
| Notebooks | `use_notebook`, `read_notebook`, `restart_notebook` |
| Cells | `read_cell`, `insert_cell`, `edit_cell_source`, `overwrite_cell_source`, `move_cell`, `delete_cell`, `clear_cell_output` |
| Execution | `insert_execute_code_cell`, `execute_cell`, `execute_code` |

## Before you start
If the server isn't connected, ask the human to start JupyterLab themselves (see `references/setup.md`):
```bash
export JUPYTER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
uv run --with jupyterlab==4.6.4 --with jupyter-collaboration==5.0.4 --with ipykernel==7.4.0 \
  jupyter lab --ip 127.0.0.1 --port 8888 --IdentityProvider.token "$JUPYTER_TOKEN" --no-browser
```
and to start the agent from the same shell so the MCP server gets `JUPYTER_TOKEN`.

## Work loop
1. `use_notebook` on the notebook, then `read_notebook`. Note the execution counts: gaps or out-of-order numbers
   mean the live kernel state may not match the cells.
2. Look before you change anything: `execute_code` for read-only peeks (`df.shape`, `df.dtypes`, `df.head()`).
3. Make changes as saved cells: `insert_execute_code_cell` for new steps, `edit_cell_source` then `execute_cell` for
   fixes. One idea per cell, a markdown cell above each section saying what it does.
4. Check results in the notebook itself: an `assert` on row counts, totals or ranges after each transformation.
5. Images are on (`ALLOW_IMG_OUTPUT=true`), so look at the plot you made before you describe it.

## Prove it reruns
1. `restart_notebook`, then `execute_cell` on each code cell from the top, in order. Stop at the first failure and fix
   the cell, not the kernel.
2. Save, then run `python3 <skill-dir>/scripts/nb_check.py <notebook>`. It fails on counts that aren't 1..n in order,
   saved errors and secrets in sources or outputs. It warns on `%pip install`, absolute home paths and outputs over
   500 KB.
3. Without a running server (or in CI), `uv run <skill-dir>/scripts/run_fresh.py <notebook>` does the same
   restart-and-run-all with nbclient and saves the outputs.

If a cell only worked because of something you ran with `execute_code`, the fresh run fails with a `NameError`.
Move that code into a cell.

## Done means
The fresh run passes, `nb_check.py` passes, and your summary names the notebook, what changed, the checks the
notebook asserts and anything you could not verify. Pair with Jupytext (`.py` files next to each notebook) if the
project uses it, and clear large outputs before a commit.

# /// script
# requires-python = ">=3.11"
# dependencies = ["nbclient==0.11.0", "nbformat==5.11.1", "ipykernel==7.4.0"]
# ///
"""Restart-and-run-all without a Jupyter server: execute a notebook top to bottom in a fresh kernel, in place.

  uv run run_fresh.py NOTEBOOK [--timeout 600]

Exits 1 on the first failing cell (the notebook is still saved, with the error in it, so you can see where).
The kernel runs in the same environment as this script; for a project's own packages run it with
`uv run --with nbclient==0.11.0 --with ipykernel==7.4.0 python run_fresh.py NOTEBOOK` from the project.
"""
import sys

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

path = sys.argv[1]
timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600
nb = nbformat.read(path, as_version=4)
client = NotebookClient(nb, timeout=timeout, kernel_name="python3", resources={"metadata": {"path": "."}})
try:
    client.execute()
    ok = True
except CellExecutionError as e:
    ok = False
    print(f"failed: {str(e).strip().splitlines()[-1][:200]}")
nbformat.write(nb, path)
n = sum(1 for c in nb.cells if c.cell_type == "code")
print(f"{'ran' if ok else 'stopped'}: {path} ({n} code cells, fresh kernel)")
sys.exit(0 if ok else 1)

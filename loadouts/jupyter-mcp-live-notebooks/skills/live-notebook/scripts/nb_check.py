#!/usr/bin/env python3
"""Check saved notebooks before you call notebook work done. Standard library only; reads .ipynb JSON.

  python3 nb_check.py NOTEBOOK_OR_FOLDER [...]

fix:  code cells not run once, top to bottom, in one kernel (execution counts must be 1, 2, 3, ... in order),
      error outputs, secrets in sources or outputs.
warn: %pip / !pip installs inside the notebook, absolute home paths, outputs over 500 KB.
Exit 1 if anything needs fixing.
"""
import json
import os
import re
import sys

SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abp]-[A-Za-z0-9-]{10,}|"
                    r"(?:api[_-]?key|token|secret|password)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,})", re.I)
INSTALL = re.compile(r"^\s*[%!]\s*(pip|uv\s+pip|conda|mamba)\s+install\b", re.M)
ABS_PATH = re.compile(r"(/Users/[^/\s'\"]+|/home/[^/\s'\"]+|[A-Z]:\\\\Users\\\\[^\\\s'\"]+)")


def text_of(out):
    if out.get("output_type") == "stream":
        t = out.get("text", "")
    elif out.get("output_type") == "error":
        t = "\n".join(out.get("traceback", [])) or f"{out.get('ename')}: {out.get('evalue')}"
    else:
        t = (out.get("data") or {}).get("text/plain", "")
    return "".join(t) if isinstance(t, list) else str(t)


def check(path):
    found = []
    try:
        nb = json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [("fix", f"not a readable notebook ({e})")]
    code = [(i, c) for i, c in enumerate(nb.get("cells", [])) if c.get("cell_type") == "code" and "".join(c.get("source", "")).strip()]
    counts = [c.get("execution_count") for _, c in code]
    if code and all(n is None for n in counts):
        found.append(("fix", "never executed: restart the kernel and run all cells before saving"))
    elif counts != list(range(1, len(counts) + 1)):
        shown = ", ".join("-" if n is None else str(n) for n in counts[:12])
        found.append(("fix", f"execution counts are [{shown}], not 1..{len(counts)} in order: the saved outputs did not come from one top-to-bottom run. Restart and run all"))
    size = 0
    for i, c in code:
        src = "".join(c.get("source", ""))
        if INSTALL.search(src):
            found.append(("warn", f"cell {i}: installs packages from inside the notebook; add them to the project (uv add) and restart the kernel instead"))
        if SECRET.search(src):
            found.append(("fix", f"cell {i}: source looks like it contains a secret; read it from the environment instead"))
        if ABS_PATH.search(src):
            found.append(("warn", f"cell {i}: absolute home path {ABS_PATH.search(src).group(0)}; use a path relative to the project"))
        for out in c.get("outputs", []):
            t = text_of(out)
            size += len(json.dumps(out))
            if out.get("output_type") == "error":
                found.append(("fix", f"cell {i}: saved with an error ({out.get('ename')}: {str(out.get('evalue'))[:80]})"))
            if SECRET.search(t):
                found.append(("fix", f"cell {i}: an output looks like it contains a secret; clear it, rotate the secret, and stop printing it"))
    if size > 500_000:
        found.append(("warn", f"outputs are {size // 1000} KB; clear large outputs before committing"))
    return found


def main(argv):
    paths = []
    for a in argv or ["."]:
        if os.path.isdir(a):
            for root, dirs, files in os.walk(a):
                dirs[:] = [d for d in dirs if d not in (".ipynb_checkpoints", ".venv", "node_modules", ".git")]
                paths += [os.path.join(root, f) for f in sorted(files) if f.endswith(".ipynb")]
        else:
            paths.append(a)
    fixes = warns = 0
    for p in paths:
        for level, msg in check(p):
            print(f"{level:<4} {p}: {msg}")
            fixes += level == "fix"
            warns += level == "warn"
    print(f"notebooks: {len(paths)}; {fixes} to fix, {warns} warnings")
    return 1 if fixes or not paths else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

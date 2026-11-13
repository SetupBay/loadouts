#!/usr/bin/env python3
"""Show how each Cursor project rule will load, and catch the ones that never will.

Standard library only.  python3 rules_lint.py [project dir]

Prints one line per rule: its load type (always, auto, agent, manual) and its globs or description. Then:
fix:  a .md file in .cursor/rules (ignored: rules must be .mdc), an .mdc with no front matter, globs written as a
      YAML list, an @file mention that doesn't exist
warn: unknown front matter keys, alwaysApply: true alongside globs or a description (they're ignored), an
      agent-requested rule whose description doesn't say when to use it, a rule over 500 lines, a legacy
      .cursorrules file, a line repeated word for word in AGENTS.md
"""
import re
import sys
from pathlib import Path

KEYS = {"description", "globs", "alwaysApply"}
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
rules_dir = root / ".cursor" / "rules"
out, rows = [], []


def add(level, rel, msg):
    out.append((level, rel, msg))


agents_lines = set()
if (root / "AGENTS.md").exists():
    agents_lines = {l.strip().lstrip("-* ").strip() for l in (root / "AGENTS.md").read_text().splitlines()}
    agents_lines = {l for l in agents_lines if len(l) >= 30}

files = sorted(rules_dir.rglob("*")) if rules_dir.exists() else []
for f in files:
    if not f.is_file():
        continue
    rel = f.relative_to(root).as_posix()
    if f.suffix == ".md":
        add("fix", rel, "plain .md files in .cursor/rules are ignored; rename to .mdc with front matter, or move it to AGENTS.md")
        continue
    if f.suffix != ".mdc":
        continue
    text = f.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        add("fix", rel, "no front matter, so Cursor can't tell when to load it")
        continue
    fm_text, body = m.group(1), m.group(2)
    fm, list_keys = {}, set()
    lines = fm_text.splitlines()
    for i, line in enumerate(lines):
        km = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if key not in KEYS:
            add("warn", rel, f"front matter key '{key}' is not read by Cursor (only description, globs, alwaysApply)")
        if val.startswith("[") or (val == "" and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("- ")):
            list_keys.add(key)
        fm[key] = val.strip("\"'")
    if "globs" in list_keys:
        add("fix", rel, "globs is a YAML list; write one comma-separated string, e.g. globs: src/**/*.ts, src/**/*.tsx")
    always = fm.get("alwaysApply", "false").lower() == "true"
    desc, globs = fm.get("description", ""), fm.get("globs", "")
    if always:
        kind = "always"
        if globs or desc:
            add("warn", rel, "alwaysApply: true, so its globs and description are ignored")
    elif globs or "globs" in list_keys:
        kind = "auto"
    elif desc:
        kind = "agent"
        if not re.search(r"\b(use when|when |whenever|for (editing|writing|changing|adding))", desc, re.I):
            add("warn", rel, f"description '{desc}' says what the rule is, not when to use it; start with 'Use when'")
    else:
        kind = "manual"
    shown = {"always": "every chat", "auto": globs or "(globs written as a YAML list)", "agent": desc, "manual": "only when @-mentioned"}[kind]
    rows.append((kind, rel, shown))
    n = text.count("\n") + 1
    if n > 500:
        add("warn", rel, f"{n} lines; Cursor suggests under 500, and long procedures work better as skills")
    for ref in re.findall(r"(?<![\w`])@([\w./-]+\.\w+)", body):
        if not (root / ref).exists() and not any(root.rglob(Path(ref).name)):
            add("fix", rel, f"mentions @{ref}, which doesn't exist")
    for line in body.splitlines():
        s = line.strip().lstrip("-* ").strip()
        if len(s) >= 30 and s in agents_lines:
            add("warn", rel, f"repeats AGENTS.md word for word: '{s[:60]}'")

if (root / ".cursorrules").exists():
    add("warn", ".cursorrules", "legacy file; move its content into .cursor/rules/*.mdc or AGENTS.md, then delete it")

for kind, rel, what in rows:
    print(f"{kind:<6} {rel}: {what}")
for level, rel, msg in out:
    print(f"{level:<6} {rel}: {msg}")
fixes = sum(1 for o in out if o[0] == "fix")
print(f"rules: {len(rows)} loadable; {fixes} to fix, {len(out) - fixes} warnings")
sys.exit(1 if fixes else 0)

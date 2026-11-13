#!/usr/bin/env python3
"""Lint the AGENTS.md files in a repository against what agents actually load.

Usage: python3 agents_md_lint.py [REPO_DIR]     (default: the current folder)

For every AGENTS.md (root and nested; skips node_modules, .git, vendor, dist, build, .venv):
  error  combined size of the AGENTS.md chain is over Codex's default 32 KiB project_doc_max_bytes (the rest is not read)
  error  a CLAUDE.md or CLAUDE.local.md sits beside it without importing it (@AGENTS.md), so Claude Code reads only CLAUDE.md
  error  a referenced script does not exist: `npm run X` / `pnpm X` / `yarn X` (package.json scripts), `make X` (Makefile targets),
         `just X` (justfile recipes)
  warn   no section that tells the agent how to test or check its work
  warn   no "never" / "don't" section (the agent has no boundaries)
  warn   over 150 lines (agents follow short files better; move procedures into skills)
  warn   a backticked path such as `src/lib/` that does not exist
  info   files Codex would read for each nested AGENTS.md, root first
Exit 1 if any error, else 0. Standard library only; read-only.
"""
import json
import os
import re
import sys

SKIP = {"node_modules", ".git", "vendor", "dist", "build", ".venv", "venv", "target", ".next", ".godot", "__pycache__"}
CODEX_MAX = 32 * 1024
TEST_HINT = re.compile(r"^#+.*\b(test|tests|testing|check|checks|verify|done)\b|`[^`]*\b(test|pytest|vitest|jest|check|validate|lint)\b[^`]*`", re.I | re.M)
NEVER_HINT = re.compile(r"^#+\s*(never|don'?t|do not|boundaries|off limits|ask first)\b|^\s*[-*]\s*(never|do not|don'?t)\b", re.I | re.M)
CODE_SPAN = re.compile(r"`([^`\n]+)`")
RUN_SCRIPT = re.compile(r"\b(?:npm run|pnpm(?: run)?|yarn(?: run)?|bun run)\s+([A-Za-z0-9:_-]+)")
PNPM_BUILTINS = {"install", "i", "add", "remove", "exec", "dlx", "turbo", "--filter", "-r", "why", "update", "outdated", "audit", "store", "run", "x", "create", "init"}
MAKE = re.compile(r"^make\s+([A-Za-z0-9_.-]+)")
JUST = re.compile(r"^just\s+([A-Za-z0-9_-]+)")
PATHLIKE = re.compile(r"^((?:\.?[A-Za-z0-9_-]+/)+(?:[A-Za-z0-9_.-]+)?)$")
GENERATED = (".next/", "dist/", "build/", "node_modules/", ".godot/", "target/", ".venv/", "coverage/")


def find_agents(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP and not x.startswith(".") or x in (".github",))
        if "AGENTS.md" in files:
            yield os.path.join(d, "AGENTS.md")


def nearest(start, root, name):
    d = start
    while True:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
        if os.path.abspath(d) == os.path.abspath(root):
            return None
        d = os.path.dirname(d)


def scripts_for(dirpath, root):
    pj = nearest(dirpath, root, "package.json")
    if not pj:
        return None, None
    try:
        return set(json.load(open(pj)).get("scripts", {})), pj
    except ValueError:
        return set(), pj


def make_targets(dirpath, root):
    mk = nearest(dirpath, root, "Makefile")
    if not mk:
        return None
    return set(re.findall(r"^([A-Za-z0-9_.-]+)\s*:(?!=)", open(mk).read(), re.M))


def just_recipes(dirpath, root):
    jf = nearest(dirpath, root, "justfile") or nearest(dirpath, root, "Justfile")
    if not jf:
        return None
    return set(re.findall(r"^@?([A-Za-z0-9_-]+)[^:\n]*:(?!=)", open(jf).read(), re.M))


def chain(path, root):
    """AGENTS.md files Codex concatenates when started in path's folder: root first."""
    out, d = [], os.path.dirname(path)
    while True:
        p = os.path.join(d, "AGENTS.md")
        o = os.path.join(d, "AGENTS.override.md")
        if os.path.isfile(o):
            out.append(o)
        elif os.path.isfile(p):
            out.append(p)
        if os.path.abspath(d) == os.path.abspath(root):
            break
        d = os.path.dirname(d)
    return list(reversed(out))


def main(argv):
    root = argv[0] if argv else "."
    files = list(find_agents(root))
    if not files:
        print("agents-md-lint: no AGENTS.md found")
        return 1
    errors = warns = 0

    def report(level, path, msg):
        nonlocal errors, warns
        errors += level == "error"
        warns += level == "warn"
        print(f"{level:5} {os.path.relpath(path, root)}: {msg}")

    for path in files:
        d = os.path.dirname(path)
        text = open(path, encoding="utf-8").read()
        lines = text.count("\n") + 1
        ch = chain(path, root)
        size = sum(os.path.getsize(p) for p in ch)
        if size > CODEX_MAX:
            report("error", path, f"AGENTS.md chain is {size} bytes; Codex stops reading at {CODEX_MAX} (project_doc_max_bytes)")
        for cname in ("CLAUDE.md", "CLAUDE.local.md"):
            c = os.path.join(d, cname)
            if os.path.isfile(c) and not re.search(r"^\s*@(\./)?AGENTS\.md\s*$", open(c).read(), re.M):
                report("error", path, f"{cname} next to it does not import it with @AGENTS.md, so Claude Code reads {cname} only")
        scripts, pj = scripts_for(d, root)
        spans = [m.group(1).strip() for m in CODE_SPAN.finditer(text)]
        cmds = [c for sp in spans for c in re.split(r"\s*(?:&&|\|\||;|\bthen\b)\s*", sp)]
        for m in (x for c in cmds for x in RUN_SCRIPT.finditer(c)):
            name = m.group(1)
            if name in PNPM_BUILTINS or name.startswith("-"):
                continue
            if scripts is None:
                report("warn", path, f"mentions script '{name}' but no package.json was found")
            elif name not in scripts:
                report("error", path, f"script '{name}' is not in {os.path.relpath(pj, root)} scripts")
        targets = make_targets(d, root)
        for m in (x for c in cmds for x in [MAKE.match(c)] if x):
            if targets is not None and m.group(1) not in targets:
                report("error", path, f"make target '{m.group(1)}' is not in the Makefile")
        recipes = just_recipes(d, root)
        for m in (x for c in cmds for x in [JUST.match(c)] if x):
            if recipes is not None and m.group(1) not in recipes:
                report("error", path, f"just recipe '{m.group(1)}' is not in the justfile")
        if not TEST_HINT.search(text):
            report("warn", path, "nothing says how to test or check work (add the exact test command and what done means)")
        if not NEVER_HINT.search(text):
            report("warn", path, "no 'Never' section; list what the agent must not touch or run")
        if lines > 150:
            report("warn", path, f"{lines} lines; keep it short and move procedures into skills")
        for m in (x for sp in spans for x in [PATHLIKE.match(sp)] if x):
            rel = m.group(1)
            if "<" in rel or "*" in rel or rel.startswith(("http", "~", "/")) or rel.startswith(GENERATED):
                continue
            if not (os.path.exists(os.path.join(d, rel)) or os.path.exists(os.path.join(root, rel))):
                report("warn", path, f"path `{rel}` does not exist")
        print(f"info  {os.path.relpath(path, root)}: {lines} lines, {len(text.encode())} bytes; Codex reads: {' + '.join(os.path.relpath(p, root) for p in ch)}")
    print(f"agents-md-lint: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

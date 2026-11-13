#!/usr/bin/env python3
"""Before starting a coding agent in a folder: say whether the folder is one the web can write to, list every
instruction and agent-config file the agent will read there (this folder and its parents up to the git root or
home), and flag files that tell an agent to install, fetch, reconfigure itself or keep quiet. Read-only, stdlib only.

  python3 start_check.py [FOLDER] [--home DIR] [--json]

Exit 0: nothing found. Exit 1: don't start here until a human has read the files listed under "fix".
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

INSTRUCTION_FILES = ["AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md", "GEMINI.md", ".cursorrules",
                     ".windsurfrules", ".github/copilot-instructions.md"]
CONFIG_FILES = [".mcp.json", ".claude/settings.json", ".claude/settings.local.json", ".codex/config.toml", ".codex/hooks.json",
                ".cursor/mcp.json", ".cursor/hooks.json", ".gemini/settings.json", ".agents/mcp_config.json", ".vscode/mcp.json"]
GLOB_DIRS = [(".cursor/rules", (".mdc", ".md")), (".claude/skills", ("SKILL.md",)), (".agents/skills", ("SKILL.md",)),
             (".github/instructions", (".instructions.md",)), (".claude/agents", (".md",)), (".claude/commands", (".md",))]
# Folders a browser, mail client or chat app can drop files into without asking.
DROP_ZONES = ["Downloads", "Desktop", "Library/Mobile Documents", "tmp"]

RED_FLAGS = [
    ("installs packages", re.compile(r"\b(npm\s+(i|install|add)|npx\s+(-y\s+)?[\w@]|pnpm\s+(add|dlx)|yarn\s+(add|dlx)|bunx?\s+(add|x)\b|pip3?\s+install|uv\s+(add|pip\s+install|tool\s+install)|uvx\s+\w|gem\s+install|cargo\s+install|go\s+install|brew\s+install)", re.I)),
    ("downloads and runs code", re.compile(r"(curl|wget|iwr|Invoke-WebRequest)[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b|\b(bash|sh)\s+<\(\s*curl|base64\s+(-d|--decode)[^\n]*\|\s*(ba)?sh", re.I)),
    ("changes the agent's own config", re.compile(r"(\.codex/config\.toml|~/\.codex|mcp_servers|\.mcp\.json|mcpServers|\.claude/settings|~/\.claude|\.cursor/mcp\.json|\.gemini/settings|mcp_config\.json|claude\s+mcp\s+add|codex\s+mcp\s+add)", re.I)),
    ("redirects API traffic or credentials", re.compile(r"\b(ANTHROPIC_BASE_URL|OPENAI_BASE_URL|ANTHROPIC_AUTH_TOKEN|ANTHROPIC_API_KEY|OPENAI_API_KEY|apiKeyHelper|HTTPS?_PROXY|NODE_EXTRA_CA_CERTS|base_url\s*=)", re.I)),
    ("turns off safety", re.compile(r"(--dangerously[-\w]*|bypassPermissions|danger-full-access|approval_policy\s*=\s*\"?never|--yo" r"lo\b|--no-sandbox|sandbox_mode\s*=\s*\"?danger|disableAllHooks)", re.I)),
    ("asks the agent to hide what it does", re.compile(r"(do not|don't|never)\s+(tell|mention|inform|show|alert)\s+(the\s+)?(user|human|developer)|without\s+(asking|telling)\s+(the\s+)?(user|human)|silently|before\s+(doing|starting)\s+(anything|the\s+(user'?s\s+)?task)", re.I)),
    ("reads secrets", re.compile(r"(~|\$HOME)/\.(ssh|aws|config/gh|netrc|npmrc)|\bid_(rsa|ed25519)\b|\.env\b|keychain|credentials\.json|auth\.json", re.I)),
]
INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\U000e0000-\U000e007f]")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)

findings, files_seen = [], []


def git(args, cwd):
    try:
        r = subprocess.run(["git", "-C", cwd] + args, capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    except FileNotFoundError:
        return 1, ""


def chain(folder, home):
    code, top = git(["rev-parse", "--show-toplevel"], folder)
    stop = os.path.realpath(top) if code == 0 and top else None
    out, d = [], folder
    while True:
        out.append(d)
        if stop and d == stop:
            break
        parent = os.path.dirname(d)
        if parent == d or d == home:
            break
        d = parent
    return out, stop


def candidates(d):
    for name in INSTRUCTION_FILES + CONFIG_FILES:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            yield p
    for sub, ends in GLOB_DIRS:
        base = os.path.join(d, sub)
        if os.path.isdir(base):
            for root, _, names in os.walk(base):
                for n in sorted(names):
                    if n.endswith(ends):
                        yield os.path.join(root, n)


def scan(p, d, gitroot):
    text = open(p, encoding="utf-8", errors="replace").read()
    tracked = None
    if gitroot and os.path.realpath(p).startswith(gitroot + os.sep):
        code, _ = git(["ls-files", "--error-unmatch", os.path.relpath(p, gitroot)], gitroot)
        tracked = code == 0
        if tracked:
            code2, _ = git(["diff", "--quiet", "HEAD", "--", os.path.relpath(p, gitroot)], gitroot)
            if code2 != 0:
                tracked = "modified"
    files_seen.append({"path": p, "tracked": tracked})
    hits = []
    for label, rx in RED_FLAGS:
        m = rx.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            hits.append(f"{label} (line {line}: {text.splitlines()[line - 1].strip()[:90]})")
    if INVISIBLE.search(text):
        hits.append("contains invisible Unicode characters")
    for c in COMMENT.findall(text):
        if re.search(r"\b(agent|assistant|claude|codex|you must|ignore|instruction)", c, re.I):
            hits.append("has an HTML comment addressed to the agent (hidden when the file is rendered)")
            break
    return tracked, hits


def main(argv):
    as_json = "--json" in argv
    home = os.path.realpath(os.path.expanduser("~"))
    args = [a for a in argv if not a.startswith("--")]
    if "--home" in argv:
        home = os.path.realpath(argv[argv.index("--home") + 1])
        args = [a for a in args if os.path.realpath(a) != home]
    folder = os.path.realpath(args[0] if args else ".")

    rel_home = os.path.relpath(folder, home)
    in_drop = None
    for z in DROP_ZONES:
        zp = os.path.realpath(os.path.join(home, z)) if z != "tmp" else None
        if (zp and (folder == zp or folder.startswith(zp + os.sep))) or (z == "tmp" and not folder.startswith(home + os.sep) and re.match(r"^/(tmp|var/tmp|private/tmp)(/|$)", folder)):
            in_drop = z
            break
    if in_drop:
        findings.append(("fix", folder, f"this is inside {in_drop}, a folder websites and apps can write to without asking. Don't start an agent here: move the project into its own folder first"))
    if folder == home:
        findings.append(("fix", folder, "this is your home folder; start the agent in a project folder instead"))

    dirs, gitroot = chain(folder, home)
    if not gitroot:
        findings.append(("warn", folder, "not inside a git repository, so nothing here has a history you can check"))
    for d in dirs:
        for p in candidates(d):
            tracked, hits = scan(p, d, gitroot)
            state = {True: "tracked", "modified": "modified since last commit", False: "not tracked by git", None: "outside any repo"}[tracked]
            for h in hits:
                level = "warn" if tracked is True else "fix"
                findings.append((level, p, f"{h} [{state}]"))
            if tracked is not True and not hits:
                findings.append(("info", p, f"{state}: read it before the agent does"))

    rel = lambda p: os.path.relpath(p, folder) if p.startswith(folder) and p != folder else p
    if as_json:
        print(json.dumps({"folder": folder, "git_root": gitroot, "files": files_seen,
                          "findings": [{"level": l, "path": p, "message": m} for l, p, m in findings]}, indent=2))
    else:
        print(f"folder: {folder}")
        print(f"git root: {gitroot or 'none'}")
        for f in files_seen:
            print(f"reads {rel(f['path'])}")
        order = {"fix": 0, "warn": 1, "info": 2}
        for l, p, m in sorted(findings, key=lambda x: order[x[0]]):
            print(f"{l:<4} {rel(p)}: {m}")
        n = lambda lv: sum(1 for f in findings if f[0] == lv)
        verdict = "do not start an agent here yet" if n("fix") else "ok to start"
        print(f"{len(files_seen)} file(s) the agent will read; {n('fix')} to fix, {n('warn')} warnings: {verdict}")
    return 1 if any(f[0] == "fix" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

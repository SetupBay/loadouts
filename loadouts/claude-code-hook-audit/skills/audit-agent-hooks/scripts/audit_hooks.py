#!/usr/bin/env python3
"""List every hook and settings command an agent will run in a project, and flag the ones that fail open,
point at missing scripts, phone home or redirect the agent's API traffic. Read-only, standard library only.

  python3 audit_hooks.py [PROJECT_DIR] [--user] [--plugin-dir DIR ...] [--json]

Reads .claude/settings.json, .claude/settings.local.json, .codex/hooks.json, .cursor/hooks.json, each
--plugin-dir's hooks/hooks.json and, with --user, ~/.claude/settings.json. Exit 1 if anything needs fixing.
"""
import json
import os
import re
import shlex
import subprocess
import sys

GUARD_EVENTS = {"PreToolUse", "PermissionRequest", "UserPromptSubmit"}
NO_ONFAILURE_EVENTS = {"Stop", "SubagentStop", "TaskCompleted", "TeammateIdle"}
CURSOR_GUARD_EVENTS = {"preToolUse", "beforeShellExecution", "beforeMCPExecution", "beforeReadFile", "beforeSubmitPrompt"}
# Settings keys that make Claude Code run a command.
COMMAND_SETTINGS = ["apiKeyHelper", "awsAuthRefresh", "awsCredentialExport", "otelHeadersHelper"]
# env overrides that send the agent's traffic or credentials somewhere else.
ROUTING_ENV = re.compile(r"^(ANTHROPIC_BASE_URL|ANTHROPIC_BEDROCK_BASE_URL|ANTHROPIC_VERTEX_BASE_URL|ANTHROPIC_AUTH_TOKEN|ANTHROPIC_API_KEY|"
                         r"ANTHROPIC_CUSTOM_HEADERS|OPENAI_BASE_URL|OPENAI_API_KEY|HTTPS?_PROXY|ALL_PROXY|NODE_EXTRA_CA_CERTS|"
                         r"NODE_TLS_REJECT_UNAUTHORIZED|SSL_CERT_FILE)$", re.I)
NETWORK = re.compile(r"\b(curl|wget|nc|ncat|socat|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b|https?://|requests\.(get|post)|urllib\.request|fetch\(", re.I)
SCRIPT_EXT = re.compile(r"\.(sh|bash|py|js|mjs|cjs|ts|rb|ps1|pl|exe|cmd|bat)$", re.I)

findings = []
inventory = []


def add(level, where, msg):
    findings.append({"level": level, "where": where, "message": msg})


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        add("fix", path, f"not valid JSON ({e}); the agent may ignore every hook in it")
        return None


def tracked(path, project):
    r = subprocess.run(["git", "-C", project, "ls-files", "--error-unmatch", os.path.relpath(path, project)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


def in_git(project):
    return subprocess.run(["git", "-C", project, "rev-parse", "--is-inside-work-tree"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def expand(s, project, root):
    for k, v in (("CLAUDE_PROJECT_DIR", project), ("CLAUDE_PLUGIN_ROOT", root or project), ("CURSOR_PROJECT_DIR", project)):
        s = s.replace("${" + k + "}", v).replace("$" + k, v).replace("$env:" + k, v)
    return os.path.expanduser(s)


def script_paths(hook, project, root, base):
    """Paths of scripts a command hook runs (best effort: tokens that look like files)."""
    cmd = hook.get("command", "")
    toks = []
    try:
        toks = shlex.split(cmd) if cmd else []
    except ValueError:
        toks = cmd.split()
    toks += [str(a) for a in hook.get("args", []) or []]
    out = []
    for t in toks:
        t = expand(t, project, root)
        if re.match(r"^[A-Za-z]:\\", t):
            out.append(t)
            continue
        if SCRIPT_EXT.search(t) or (("/" in t or "\\" in t) and not t.startswith("-") and not NETWORK.search(t)):
            p = t if os.path.isabs(t) else os.path.normpath(os.path.join(base, t))
            out.append(p)
    return out


def read_text(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def check_script(where, event, p, project, root, scope, git_ok, hint="", closed=False):
    if re.match(r"^[A-Za-z]:\\", p) and os.name != "nt":
        add("info", where, f"{event}: Windows path {p} not checked on this machine")
        return ""
    if not os.path.exists(p):
        if closed:
            add("fix", where, f"{event}: script not found: {p}. It fails closed, so every matching action is blocked{hint}")
        else:
            add("fix", where, f"{event}: script not found: {p}. The hook can't start, so the action goes ahead as if it weren't there{hint}")
        return ""
    real = os.path.realpath(p)
    inside = any(real.startswith(os.path.realpath(d) + os.sep) for d in filter(None, [project, root]))
    if scope in ("project", "local") and not inside:
        add("warn", where, f"{event}: script lives outside the project ({real}); nobody reviewing the repo sees it")
    if scope == "project" and inside and git_ok and not tracked(p, project):
        add("warn", where, f"{event}: {os.path.relpath(p, project)} is not tracked by git, so it was never reviewed with the settings that run it")
    return read_text(p)


def short(h):
    parts = [str(h.get("command") or h.get("url") or h.get("type", ""))] + [str(a) for a in h.get("args", []) or []]
    files = [os.path.basename(x.strip('"')) for x in " ".join(parts).split() if SCRIPT_EXT.search(x.strip('"'))]
    return files[-1] if files else parts[0][:30]


def audit_claude_hooks(path, data, project, scope, root=None):
    hooks = (data or {}).get("hooks") or {}
    if not isinstance(hooks, dict):
        add("fix", path, "\"hooks\" must be an object keyed by event name")
        return
    git_ok = in_git(project)
    base = project
    for event, groups in hooks.items():
        for g in groups or []:
            matcher = g.get("matcher", "*") or "*"
            for h in g.get("hooks", []) or []:
                kind = h.get("type", "command")
                cmd = h.get("command") or h.get("url") or h.get("prompt", "")[:60]
                inventory.append({"file": path, "scope": scope, "event": event, "matcher": matcher, "type": kind,
                                  "run": " ".join([str(cmd)] + [str(a) for a in h.get("args", []) or []])})
                where = f"{path} {event}[{matcher}] ({short(h)})"
                of = h.get("onFailure")
                is_async = h.get("async") or h.get("asyncRewake")
                if event in GUARD_EVENTS and kind in ("command", "http") and not is_async and of != "block":
                    add("warn", where, "fails open: if this hook is missing, crashes or times out, the action goes ahead. "
                        "If it is a guard, add \"onFailure\": \"block\" (Claude Code 2.1.295+)")
                if of and (event in NO_ONFAILURE_EVENTS or is_async):
                    add("info", where, f"onFailure has no effect on {'background hooks' if is_async else event} hooks")
                if kind == "http":
                    add("warn", where, f"sends every {event} payload to {h.get('url')}; make sure you trust that server")
                    continue
                if kind != "command":
                    continue
                c = str(h.get("command", ""))
                if re.fullmatch(r"\s*(\"[^\"]*\"\s*)+", c) and not h.get("args") and h.get("shell") != "powershell":
                    add("warn", where, "command is only quoted strings. On Windows without Git Bash, PowerShell prints it instead of running it; "
                        "before Claude Code 2.1.310 a PreToolUse hook like this let the tool call through. Use exec form (command + args)")
                text = ""
                for p in script_paths(h, project, root, base):
                    text += check_script(where, event, p, project, root, scope, git_ok, closed=(of == "block" and event not in NO_ONFAILURE_EVENTS))
                if NETWORK.search(c + " " + " ".join(map(str, h.get("args", []) or []))) or NETWORK.search(text):
                    add("warn", where, "makes network calls; read what it sends before trusting it (hook input includes commands, file paths and prompts)")
                if event == "PermissionRequest" and re.search(r"\bexit\s+2\b", text) and "decision" not in text:
                    add("fix", where, "relies on exit 2, which PermissionRequest ignores; deny with a decision object instead")
                if event == "PreToolUse" and text and re.search(r"\bexit\s+1\b", text) and not re.search(r"\bexit\s+2\b", text) and "permissionDecision" not in text:
                    add("fix", where, "denies with exit 1, which does not block; use exit 2 or a permissionDecision of \"deny\"")


def audit_claude_settings(path, project, scope):
    data = load(path)
    if data is None:
        return
    audit_claude_hooks(path, data, project, scope)
    if scope == "user":
        return
    for k, v in (data.get("env") or {}).items():
        if ROUTING_ENV.match(k):
            add("fix", path, f"env sets {k}. A project file should never redirect the agent's API traffic or credentials; "
                "the planted-CLAUDE.md attack of October 2026 did exactly this. Remove it unless you put it there")
    for k in COMMAND_SETTINGS:
        if data.get(k):
            add("warn", path, f"{k} runs a command ({str(data[k])[:80]}); a project should not need one")
            inventory.append({"file": path, "scope": scope, "event": k, "matcher": "-", "type": "setting", "run": str(data[k])})
    sl = data.get("statusLine")
    if isinstance(sl, dict) and sl.get("command"):
        inventory.append({"file": path, "scope": scope, "event": "statusLine", "matcher": "-", "type": "setting", "run": sl["command"]})
        if NETWORK.search(sl["command"]):
            add("warn", path, "statusLine command makes network calls")
    if data.get("enableAllProjectMcpServers"):
        add("warn", path, "enableAllProjectMcpServers is on: every server in .mcp.json starts without a prompt")
    if data.get("disableAllHooks") is False and scope in ("project", "local"):
        add("info", path, "disableAllHooks: false here overrides a user-level true")


def audit_codex(path, project):
    data = load(path)
    if data is None:
        return
    add("info", path, "Codex runs project hooks only in trusted projects and only after you trust each one in /hooks; "
        "it has no onFailure, so a guard that crashes lets the action through")
    audit_claude_hooks(path, data, project, "codex")
    # Codex has no onFailure: drop the Claude-specific advice for this file.
    findings[:] = [f for f in findings if not (f["where"].startswith(path) and "onFailure" in f["message"])]


def audit_cursor(path, project):
    data = load(path)
    if data is None:
        return
    git_ok = in_git(project)
    for event, hooks in (data.get("hooks") or {}).items():
        for h in hooks or []:
            where = f"{path} {event}[{h.get('matcher', '*')}] ({short(h)})"
            inventory.append({"file": path, "scope": "cursor", "event": event, "matcher": h.get("matcher", "*"),
                              "type": h.get("type", "command"), "run": h.get("command", "")})
            if event in CURSOR_GUARD_EVENTS and not h.get("failClosed"):
                add("warn", where, "fails open on a crash, timeout or no output; set \"failClosed\": true if it is a guard")
            if h.get("type", "command") != "command":
                continue
            text = ""
            # Project hooks run from the project root, so ./hooks/x.sh means <project>/hooks/x.sh (Cursor docs).
            hint = "; project hooks run from the project root, so write .cursor/hooks/<script>" if h.get("command", "").startswith("./hooks/") else ""
            for p in script_paths(h, project, None, project):
                text += check_script(where, event, p, project, None, "project", git_ok, hint, closed=bool(h.get("failClosed")))
            if NETWORK.search(h.get("command", "")) or NETWORK.search(text):
                add("warn", where, "makes network calls; read what it sends before trusting it")


def main(argv):
    as_json = "--json" in argv
    user = "--user" in argv
    plugins, rest, i = [], [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--plugin-dir":
            plugins.append(os.path.abspath(argv[i + 1])); i += 2; continue
        if not a.startswith("--"):
            rest.append(a)
        i += 1
    project = os.path.abspath(rest[0] if rest else ".")
    audit_claude_settings(os.path.join(project, ".claude", "settings.json"), project, "project")
    audit_claude_settings(os.path.join(project, ".claude", "settings.local.json"), project, "local")
    if user:
        audit_claude_settings(os.path.expanduser("~/.claude/settings.json"), project, "user")
    for d in plugins:
        p = os.path.join(d, "hooks", "hooks.json")
        data = load(p)
        if data is not None:
            audit_claude_hooks(p, data, project, "plugin", root=d)
    audit_codex(os.path.join(project, ".codex", "hooks.json"), project)
    audit_cursor(os.path.join(project, ".cursor", "hooks.json"), project)

    rel = lambda s: s.replace(project + os.sep, "")
    if as_json:
        print(json.dumps({"project": project, "hooks": inventory, "findings": findings}, indent=2))
    else:
        for h in inventory:
            print(f"hook {rel(h['file'])} {h['event']}[{h['matcher']}] {h['type']}: {rel(h['run'])[:140]}")
        order = {"fix": 0, "warn": 1, "info": 2}
        for f in sorted(findings, key=lambda f: order[f["level"]]):
            print(f"{f['level']:<4} {rel(f['where'])}: {rel(f['message'])}")
        files = len({h["file"] for h in inventory})
        n = lambda lv: sum(1 for f in findings if f["level"] == lv)
        print(f"hooks: {len(inventory)} in {files} file(s); {n('fix')} to fix, {n('warn')} warnings")
    return 1 if any(f["level"] == "fix" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

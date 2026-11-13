#!/usr/bin/env python3
"""Cursor permission hook: one script for beforeShellExecution, beforeReadFile, beforeMCPExecution and preToolUse.

Reads the hook's JSON from stdin and prints a JSON decision. Standard library only, makes no network calls.
Configure it in .cursor/hooks.json with "failClosed": true, so a crash or timeout blocks instead of allowing.
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_FILE = HERE / "mcp-policy.json"

SAFE_ENV_SUFFIXES = (".example", ".sample", ".template", ".dist")
SECRET_NAMES = re.compile(r"(^|/)(\.env(\.[\w.-]+)?|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?|credentials(\.json)?|\.netrc|\.pgpass|[\w.-]+\.(pem|key|p12|pfx|keystore))$")
SECRET_DIRS = re.compile(r"(^|/)(\.ssh|\.aws|\.gnupg|\.config/gcloud|\.docker)(/|$)")
SECRET_CONTENT = re.compile(r"-----BEGIN ([A-Z]+ )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\b(ghp|github_pat|glpat|xox[abp])_[A-Za-z0-9_]{16,}|//registry\.npmjs\.org/:_authToken=\S+")


def is_secret_path(path: str) -> bool:
    p = path.replace("\\", "/")
    if p.endswith(SAFE_ENV_SUFFIXES):
        return False
    return bool(SECRET_NAMES.search(p) or SECRET_DIRS.search(p))


def decide(permission: str, reason: str = "") -> dict:
    out = {"permission": permission}
    if reason:
        out["user_message"] = f"Blocked by cursor_guard: {reason}" if permission == "deny" else f"cursor_guard: {reason}"
        out["agent_message"] = out["user_message"]
    return out


# --- shell ---------------------------------------------------------------------------------------------------------

def project_dir() -> Path:
    return Path(os.environ.get("CURSOR_PROJECT_DIR") or os.getcwd()).resolve()


def whole_project_or_outside(target: str, cwd: Path) -> bool:
    if target in ("/", "~", "$HOME", "${HOME}", "*", "/*", "~/*", "..", "../*"):
        return True
    expanded = os.path.expanduser(os.path.expandvars(target))
    resolved = Path(expanded).resolve() if os.path.isabs(expanded) else (cwd / expanded).resolve()
    root = project_dir()
    return resolved == root or root not in resolved.parents


def check_segment(words: list, cwd: Path):
    if not words:
        return None
    cmd = os.path.basename(words[0])
    args = words[1:]
    flags = {a for a in args if a.startswith("-")}
    if cmd == "sudo":
        return ("ask", "sudo needs the human's approval")
    if cmd == "rm" and any(f.startswith("-") and "r" in f.lower() for f in flags):
        for target in (a for a in args if not a.startswith("-")):
            if whole_project_or_outside(target, cwd):
                return ("deny", f"recursive delete of {target!r} is the whole project or outside it; delete specific paths inside the project")
    if cmd == "git":
        while args and args[0] in ("-C", "-c", "--git-dir", "--work-tree"):
            args = args[2:]
        flags = {a for a in args if a.startswith("-")}
        if args:
            sub = args[0]
            if "--no-verify" in args or (sub == "commit" and "-n" in args):
                return ("deny", "--no-verify skips the project's checks; fix what the hook reports instead")
            if sub == "push" and ({"--force", "-f", "--mirror", "--delete", "-d"} & flags or any(a.startswith("+") for a in args[1:])):
                return ("deny", "force or deleting pushes rewrite shared history; push normally, or ask the human")
            if sub == "push" and any(f.startswith("--force-with-lease") for f in flags):
                return ("ask", "force-with-lease rewrites the remote branch")
            if sub == "reset" and "--hard" in args:
                return ("ask", "reset --hard throws away uncommitted work")
            if sub == "clean" and any(f.startswith("-") and not f.startswith("--") and "f" in f for f in flags):
                return ("ask", "git clean -f deletes untracked files")
    if (cmd in ("npm", "pnpm", "yarn", "cargo", "gem") and "publish" in args) or (cmd == "twine" and "upload" in args):
        return ("ask", f"{cmd} publishes a package; the human decides when")
    if cmd in ("cat", "less", "more", "head", "tail", "bat", "grep", "rg", "source", ".", "cp", "scp", "base64", "xxd", "strings", "open"):
        for a in args:
            if not a.startswith("-") and is_secret_path(a):
                return ("deny", f"{a} holds secrets; read .env.example or ask the human for the value you need")
    if cmd == "chmod" and any(a in ("777", "a+rwx") for a in args):
        return ("deny", "chmod 777 makes files world-writable; use the narrowest mode that works")
    return None


SQL_DESTRUCTIVE = re.compile(r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+(TABLE\s+)?\w|DELETE\s+FROM\s+\w+\s*(;|$|\"|'))", re.I)
PIPE_TO_SHELL = re.compile(r"\b(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(ba|z|da)?sh\b|\b(curl|wget)\b[^|;&]*\|\s*python3?\b")


def check_shell(data: dict) -> dict:
    command = data.get("command") or ""
    cwd = Path(data.get("cwd") or project_dir())
    if PIPE_TO_SHELL.search(command):
        return decide("deny", "piping a download into a shell runs unreviewed code; download it, read it, then run it")
    if SQL_DESTRUCTIVE.search(command):
        return decide("deny", "DROP, TRUNCATE or an unbounded DELETE; write a migration or add a WHERE clause, and ask the human")
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return decide("ask", "the command couldn't be parsed")
    worst = None
    segment = []
    for tok in tokens + [";"]:
        if tok and set(tok) <= set(";&|()"):
            result = check_segment(segment, cwd)
            if result and (worst is None or (result[0] == "deny" and worst[0] != "deny")):
                worst = result
            segment = []
        else:
            segment.append(tok)
    return decide(*worst) if worst else decide("allow")


# --- file reads ----------------------------------------------------------------------------------------------------

def check_read(data: dict) -> dict:
    path = data.get("file_path") or ""
    if is_secret_path(path):
        return decide("deny", f"{os.path.basename(path)} holds secrets; use .env.example, or ask the human")
    if SECRET_CONTENT.search(data.get("content") or ""):
        return decide("deny", f"{os.path.basename(path)} contains a private key or token; it stays out of the model's context")
    return decide("allow")


# --- MCP -----------------------------------------------------------------------------------------------------------

def load_policy() -> dict:
    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    return {k: set(policy.get(k, [])) for k in ("allow_servers", "deny_tools", "ask_tools")}


def check_mcp(data: dict) -> dict:
    policy = load_policy()
    server = data.get("mcp_server_name")
    tool = data.get("tool_name") or ""
    if not server or server not in policy["allow_servers"]:
        return decide("deny", f"MCP server {server!r} isn't in .cursor/hooks/mcp-policy.json allow_servers")
    if tool in policy["deny_tools"] or f"{server}:{tool}" in policy["deny_tools"]:
        return decide("deny", f"MCP tool {tool} is denied by mcp-policy.json")
    if tool in policy["ask_tools"] or f"{server}:{tool}" in policy["ask_tools"]:
        return decide("ask", f"MCP tool {tool} needs the human's approval")
    return decide("allow")


def check_pre_tool(data: dict) -> dict:
    name = data.get("tool_name") or ""
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    if name.startswith("MCP:"):
        # preToolUse also runs in cloud agents, where beforeMCPExecution doesn't. It sends no server name and
        # doesn't enforce "ask", so ask_tools are denied here.
        policy = load_policy()
        tool = name[4:]
        listed = {t.split(":", 1)[-1] for t in policy["deny_tools"] | policy["ask_tools"]}
        if tool in listed:
            return decide("deny", f"MCP tool {tool} is denied or needs approval (mcp-policy.json); ask the human")
        return decide("allow")
    if name == "Shell":
        return check_shell({"command": tool_input.get("command", ""), "cwd": tool_input.get("working_directory") or data.get("cwd")})
    if name == "Read":
        path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("target_file") or ""
        return check_read({"file_path": path})
    return decide("allow")


HANDLERS = {
    "beforeShellExecution": check_shell,
    "beforeReadFile": check_read,
    "beforeMCPExecution": check_mcp,
    "preToolUse": check_pre_tool,
}


def main() -> int:
    data = json.loads(sys.stdin.read())
    event = data.get("hook_event_name") or (sys.argv[1] if len(sys.argv) > 1 else "")
    handler = HANDLERS.get(event)
    if handler is None:
        print(f"cursor_guard: no handler for {event!r}", file=sys.stderr)
        return 1  # with failClosed this blocks: a guard wired to the wrong event shouldn't pass silently
    print(json.dumps(handler(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check a Cursor hooks.json for hooks that fail open, wrong paths, bad matchers and cloud-agent gaps.

Usage: hooks_check.py [path/to/.cursor/hooks.json]   (default: .cursor/hooks.json)
Read-only, standard library only. Exit 1 on errors, 2 on bad usage.
"""
import json
import re
import shlex
import sys
from pathlib import Path

EVENTS = {
    "sessionStart", "sessionEnd", "preToolUse", "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop",
    "beforeShellExecution", "afterShellExecution", "beforeMCPExecution", "afterMCPExecution", "beforeReadFile",
    "afterFileEdit", "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse", "afterAgentThought",
    "beforeTabFileRead", "afterTabFileEdit", "workspaceOpen",
}
PERMISSION = {"beforeShellExecution", "beforeMCPExecution", "beforeReadFile", "beforeTabFileRead", "subagentStart", "preToolUse"}
NOT_IN_CLOUD = {"sessionStart", "sessionEnd", "beforeTabFileRead", "afterTabFileEdit", "workspaceOpen"}
OPTIONS = {"command", "type", "prompt", "model", "timeout", "loop_limit", "failClosed", "matcher"}
INTERPRETERS = {"python", "python3", "node", "bash", "sh", "bun", "deno", "uv", "ruby", "pwsh"}

findings = []


def report(level, rule, msg):
    findings.append((level, rule, msg))


def script_path(command):
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    if words and words[0] in INTERPRETERS:
        words = [w for w in words[1:] if not w.startswith("-") and w != "run"]
    if not words:
        return None
    first = words[0]
    return first if ("/" in first or first.endswith((".py", ".sh", ".js", ".ts", ".mjs"))) else None


def main(argv):
    if len(argv) > 2 or (len(argv) == 2 and argv[1] in ("-h", "--help")):
        print(__doc__.strip())
        return 2
    path = Path(argv[1] if len(argv) == 2 else ".cursor/hooks.json")
    if not path.is_file():
        print(f"hooks_check: {path} not found", file=sys.stderr)
        return 2
    project_level = path.parent.name == ".cursor"
    root = path.parent.parent if project_level else path.parent
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"{path}: error [json] invalid JSON: {exc}")
        print("hooks_check: 0 hook(s), 1 error(s), 0 warning(s)")
        return 1
    version = config.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        report("error", "version", 'top-level "version" must be a positive integer (use 1)')
    hooks = config.get("hooks")
    if not isinstance(hooks, dict):
        report("error", "hooks", 'top-level "hooks" must map event names to arrays')
        hooks = {}
    count = 0
    mcp_pre_tool = False
    for event, entries in hooks.items():
        if event not in EVENTS:
            near = [e for e in EVENTS if e.lower() == event.lower()]
            report("error", "unknown-event", f"{event}: not a Cursor hook event" + (f" (did you mean {near[0]}?)" if near else ""))
            continue
        if not isinstance(entries, list):
            report("error", "entries", f"{event}: must be an array of hook definitions")
            continue
        for i, h in enumerate(entries):
            count += 1
            where = f"{event}[{i}]"
            if not isinstance(h, dict):
                report("error", "entry", f"{where}: must be an object")
                continue
            for key in sorted(set(h) - OPTIONS):
                report("warn", "unknown-option", f"{where}: unknown option {key!r} (ignored by Cursor)")
            kind = h.get("type", "command")
            if kind == "prompt":
                if not h.get("prompt"):
                    report("error", "prompt", f'{where}: prompt hooks need a "prompt"')
                report("warn", "prompt-hook-cloud", f"{where}: prompt hooks don't run in cloud agents; keep a command hook for anything that must block")
            elif not h.get("command"):
                report("error", "command", f'{where}: needs a "command"')
            else:
                cmd = h["command"]
                if project_level and re.match(r"^\.?/?hooks/", cmd):
                    report("error", "project-path", f"{where}: project hooks run from the project root -> use .cursor/hooks/..., not {cmd.split()[0]}")
                sp = script_path(cmd)
                if sp and not sp.startswith(("$", "~")) and not Path(sp).is_absolute() and not (root / sp).exists():
                    report("error", "missing-script", f"{where}: {sp} doesn't exist (relative to {root})")
            if "matcher" in h:
                try:
                    re.compile(h["matcher"])
                except re.error as exc:
                    report("error", "matcher", f"{where}: matcher isn't a valid regex: {exc}")
                if event == "preToolUse" and "MCP" in str(h["matcher"]) or h.get("matcher") in ("", "*"):
                    mcp_pre_tool = mcp_pre_tool or event == "preToolUse"
            elif event == "preToolUse":
                mcp_pre_tool = True
            if event in PERMISSION and kind == "command" and h.get("failClosed") is not True:
                report("warn", "fails-open", f'{where}: a crash, timeout or exit code other than 2 lets the action through -> add "failClosed": true')
            if event in ("stop", "subagentStop") and "loop_limit" in h and h["loop_limit"] is None:
                report("warn", "loop-limit", f"{where}: loop_limit null removes the follow-up cap; keep a number")
            if "timeout" in h and not (isinstance(h["timeout"], (int, float)) and h["timeout"] > 0):
                report("error", "timeout", f"{where}: timeout must be a positive number of seconds")
            if event in NOT_IN_CLOUD and project_level:
                report("warn", "not-in-cloud", f"{where}: {event} doesn't run in cloud agents")
    if "beforeMCPExecution" in hooks and not mcp_pre_tool:
        report("warn", "mcp-cloud-gap", 'beforeMCPExecution doesn\'t run in cloud agents -> also add a preToolUse hook with matcher "^MCP:"')
    order = {"error": 0, "warn": 1}
    for level, rule, msg in sorted(findings, key=lambda f: order[f[0]]):
        print(f"{path}: {level} [{rule}] {msg}")
    errors = sum(1 for f in findings if f[0] == "error")
    print(f"hooks_check: {count} hook(s), {errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

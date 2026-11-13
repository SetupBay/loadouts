---
name: audit-agent-hooks
description: List and check every hook and settings command Claude Code, Codex or Cursor will run in a project, and flag guards that fail open, missing scripts, wrong exit codes, network calls and settings that redirect API traffic. Use before trusting a cloned repo, after adding or changing hooks, or when a hook seems not to fire.
---

# Audit agent hooks

`scripts/audit_hooks.py` is read-only and uses only the Python standard library. It reads:

| File | Agent | Notes |
|---|---|---|
| `.claude/settings.json`, `.claude/settings.local.json` | Claude Code | hooks, `env`, `apiKeyHelper`, `statusLine`, `enableAllProjectMcpServers` |
| `~/.claude/settings.json` (with `--user`) | Claude Code | hooks only |
| `<plugin>/hooks/hooks.json` (with `--plugin-dir`) | Claude Code plugins | `${CLAUDE_PLUGIN_ROOT}` resolved |
| `.codex/hooks.json` | Codex | runs only in trusted projects, after you trust each hook |
| `.cursor/hooks.json` | Cursor | commands run from the project root |

## Run it
```bash
python3 .agents/skills/audit-agent-hooks/scripts/audit_hooks.py .
```
(Claude Code: `.claude/skills/...`.) It prints one `hook` line per hook or settings command, then findings:

- `fix`: a script that doesn't exist, a PreToolUse guard that denies with `exit 1` (only exit 2 or a deny
  decision blocks), a PermissionRequest hook relying on exit 2 (ignored there), invalid JSON, or project `env`
  that sets `ANTHROPIC_BASE_URL`, API keys, proxies or CA certificates. Exit code 1.
- `warn`: a PreToolUse, PermissionRequest or UserPromptSubmit hook without `"onFailure": "block"`, a Cursor guard
  without `"failClosed": true`, network calls in a hook or its script, HTTP hooks, scripts outside the project or
  not tracked by git, `apiKeyHelper` and similar commands in project settings, `enableAllProjectMcpServers`, and
  commands that are only a quoted path (PowerShell prints them instead of running them on Windows without Git Bash).
- `info`: things that are fine but often misunderstood, such as `onFailure` on a Stop hook (no effect there).

## Then
1. Read every script the audit lists, in full, before you say the hooks are safe. The audit finds patterns; it
   doesn't prove a script is harmless.
2. For each `fix`, propose the smallest change (see `references/what-runs.md`) and let the human apply it.
3. Ask the human to open `/hooks` (Claude Code or Codex) or Cursor's Hooks output channel to confirm what loaded.
4. For each guard, try the forbidden action once in a live session and confirm it is denied with the guard's reason.

## Report
List the hooks found (file, event, matcher, what runs), the findings with your proposed fixes, which guards you
proved by trying the blocked action, and anything you could not check (Windows paths on Linux, user-level files
you were not allowed to read, Gemini CLI hooks).

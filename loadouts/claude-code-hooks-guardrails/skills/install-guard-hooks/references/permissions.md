# Permissions and hooks: what actually holds (Claude Code, Codex and Cursor, October 2026)

Facts from the Claude Code permissions and hooks reference, and the Codex and Cursor hooks docs. Check `claude --version` before relying on a version-gated item.

## Order of evaluation
- Deny rules beat allow rules. An allow rule cannot carve an exception out of a deny rule.
- A PreToolUse hook that denies, or exits 2, blocks the call even if an allow rule matches.
- A hook that returns "allow" does not bypass a matching deny or ask rule.
- Exception: an installed mod that handles `tool.check` answers after rules and hooks and can replace their answer.
  Review mods before installing them; a mod can switch your guard rails off.

## Exit codes
- Exit 0: success. JSON on stdout is applied.
- Exit 2: blocking error. stderr is the reason shown to the agent.
- Any other exit code: non-blocking error. The tool call goes ahead. Do not use `exit 1` to enforce a policy.
- `onFailure: "block"` (v2.1.295+) makes a crash, a missing script, invalid JSON or a timeout block the call.
  Use it on every policy hook. It has no effect on Stop hooks.

## Matching
- Deny and ask rules match past any leading `VAR=value` assignment (fixed in v2.1.289).
- Allow rules only skip a short built-in list of safe variables, so `FOO=bar npm test` is not covered by `Bash(npm test *)`.
- Environment runners (`npx`, `docker exec`, `devbox run`, `mise exec`) run whatever follows them. Allow the exact inner command.
- Hook `if` filters are best-effort. Enforce hard rules with permission rules or with a hook that inspects the whole command.

## Deny rules are not a sandbox
- `Read(./.env)` stops the Read tool. A shell command, a script, or an `@import` can still reach the file.
  Pair Read deny rules with the Bash guard hook, and with the sandbox's denied read paths where available.
- Cover `.env`, `.env.*` and any secrets folder. Carve out `.env.example` with a `!` rule in the same file.

## Settings files merge
- Permission rules merge across user, project and local settings. An allow rule in `~/.claude/settings.json` applies in every repo.
- Hooks merge too; the same handler defined twice runs once.
- Project `.claude/settings.json` hooks run in `claude -p` sessions without a trust prompt. Use `--bare` for scripted runs in repos you do not control.

## Stop hooks
- The Stop input has `stop_hook_active: true` when the agent is already continuing because of a Stop hook. Exit 0 then, or the agent can loop.
- Claude Code also caps consecutive Stop-hook continuations at 8.

## Codex
- Codex reads hooks from `.codex/hooks.json` in a trusted project, from `~/.codex/hooks.json`, or from a `[hooks]` table
  in either `config.toml`, with the same event names. Hooks from every layer run.
- New or changed hooks don't run until you trust them in `/hooks`.
- A PreToolUse hook blocks with exit 2 or `permissionDecision: "deny"`. Test the Bash input shape with one harmless call before relying on it.
- The docs don't describe `onFailure` for Codex command hooks, and they call tool hooks "a useful guardrail, not a complete
  enforcement boundary".

## Cursor
- Cursor's own hooks live in `.cursor/hooks.json` (project) or `~/.cursor/hooks.json` (user). Project hooks run only in a trusted workspace.
- With third-party import on (the default), Cursor also loads hooks from `.claude/settings.local.json`, `.claude/settings.json`
  and `~/.claude/settings.json`. It supports `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`,
  `PreCompact` and `UserPromptSubmit`, but not `Notification` or `PermissionRequest`. `Bash` maps to `Shell` and `Edit` to `Write`.
- Exit 2 blocks. Other exit codes fail open unless the native hook sets `failClosed: true`. Its docs don't mention `onFailure`.
- Cursor sets no loop limit on Stop hooks it loads from Claude Code settings, and its stop input has `loop_count`, not `stop_hook_active`.

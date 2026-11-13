# What runs from agent settings, and how it fails

Checked against the vendor docs on 29 October 2026.

## Claude Code
- Hook sources merge: user (`~/.claude/settings.json`), project (`.claude/settings.json`), local
  (`.claude/settings.local.json`, gitignored), managed policy, enabled plugins (`hooks/hooks.json`) and skill or agent
  front matter. None replaces another. `/hooks` lists them with their source.
- Only exit code 2 (or a JSON decision with exit 0) blocks. Any other exit code, a script that can't start (exit 127),
  a timeout or invalid JSON is a non-blocking error: the action goes ahead.
- `"onFailure": "block"` (2.1.295+) on a `command` or `http` hook makes those failures block. It has no effect on
  Stop, SubagentStop, TaskCompleted, TeammateIdle or background (`async`) hooks.
- PermissionRequest ignores exit 2. Deny there with the `decision` object.
- Windows: without Git Bash, a shell-form hook runs in PowerShell. A `command` that is only a quoted path is printed,
  not run. Before 2.1.310, a PreToolUse or PermissionRequest hook like that let the tool call through. Use exec form
  (`command` plus `args`) and `"onFailure": "block"`.
- Since 2.1.312, prompt and agent hooks run at most 24 at a time per session.
- Other settings that run commands: `apiKeyHelper`, `awsAuthRefresh`, `awsCredentialExport`, `otelHeadersHelper`,
  `statusLine.command`. `env` sets environment variables for the session, including `ANTHROPIC_BASE_URL`.
- `disableAllHooks: true` turns hooks off; a project `false` overrides a user `true`. Pass
  `--settings '{"disableAllHooks": true}'` to run once without project hooks.

## Codex
- Hooks come from `~/.codex/hooks.json`, `~/.codex/config.toml`, `<repo>/.codex/hooks.json` and
  `<repo>/.codex/config.toml`. Project hooks load only when the project's `.codex/` layer is trusted.
- Every non-managed hook must be reviewed and trusted in `/hooks`; trust is tied to the hook's hash, so a changed
  hook is skipped until trusted again. `--dangerously-bypass-hook-trust` skips that check: don't use it on repos you
  didn't write.
- There is no `onFailure`. A guard that crashes lets the action through.

## Cursor
- Project hooks live in `.cursor/hooks.json` (`"version": 1`) and run from the project root: write
  `.cursor/hooks/check.sh`, not `./hooks/check.sh`.
- `"failClosed": true` makes a crash, timeout, non-zero exit or missing output block. Permission hooks block on
  invalid JSON even without it.
- Cursor can also load Claude Code hooks from `.claude/settings.json` (third-party configs setting). Its docs don't
  mention `onFailure` there.

## The October 2026 planted-file attack
Forever Security found an AGENTS.md planted in a user's Downloads folder that told Codex to add an MCP server and
install a malicious npm package. In their tests a CLAUDE.md variant had Claude Code write `ANTHROPIC_BASE_URL` into
`.claude/settings.json`, sending its traffic and OAuth token to the attacker. The audit's `env` check is for that.

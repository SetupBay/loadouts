# AGENTS.md: Tauri 2 desktop app

Tauri 2 app: a web frontend (in `src/`) and a Rust core (in `src-tauri/`). The frontend is untrusted; the Rust side
decides what it may do.

## Commands
- Dev: `npm run tauri dev` (or the project's package manager). Build: `npm run tauri build`.
- Rust checks, from `src-tauri/`: `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test`.
- Frontend checks: the project's lint, type-check and test scripts.
- Permissions check after any change to capabilities or `tauri.conf.json`:
  `node <skills dir>/tauri-permissions/scripts/check-capabilities.mjs src-tauri`.

## Security model
- Capabilities in `src-tauri/capabilities/` grant permissions to named windows. Grant the minimum; use the
  `tauri-permissions` skill for any change.
- Never `"windows": ["*"]` on a capability that grants file system, shell or HTTP access. Name the windows.
- File system and HTTP permissions always carry a scope (`allow` paths such as `$APPDATA/**`, or exact URLs).
- No `shell:allow-execute` or `shell:allow-spawn` unless the human asks; prefer `shell:allow-open` or the opener plugin.
- Keep a Content Security Policy in `app.security.csp`. Never set it to null to make something load.
- Remote URLs (`remote.urls`) get no command access unless the human approves each one.

## Commands (Rust)
- `#[tauri::command]` functions validate every argument. Paths from the frontend are resolved and checked against an
  allowed base directory before use. Return `Result<T, String>` or a serialisable error type, never panic.
- Long work runs async or on a background thread; the UI must not freeze.
- Secrets live in the Rust side or the OS keychain, never in frontend code or `localStorage`.

## Changes
- Adding a plugin: `npm run tauri add <plugin>`, then grant only the permissions you use and justify each in the report.
- Do not upgrade Tauri, plugins or the webview target as part of another change.

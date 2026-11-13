# AGENTS.md: Tauri 2 app (Tauri 1 API guard)

This desktop app runs **Tauri 2** (`tauri` crate 2.12, `@tauri-apps/api` 2.12). Tauri 2 came out in October 2024,
but much of what you learnt is Tauri 1: `@tauri-apps/api/tauri`, `appWindow`, `@tauri-apps/api/fs`, the
`allowlist`, `get_window`, `emit_all` and `SystemTray`. None of those work in Tauri 2.

## Version facts
- Check the pins first: `src-tauri/Cargo.toml` (`tauri = "2..."`) and `package.json` (`@tauri-apps/api` 2.x).
  If either says 1.x, stop and ask; don't mix the two.
- Front end: `invoke` comes from `@tauri-apps/api/core`. The current window is `getCurrentWebviewWindow()` from
  `@tauri-apps/api/webviewWindow`. fs, dialog, shell, http, clipboard, notification, os, process and the updater are
  plugins: a JS package `@tauri-apps/plugin-<name>`, a Rust crate `tauri-plugin-<name>` registered with
  `.plugin(...)`, and a permission in `src-tauri/capabilities/`.
- Opening URLs and files is `openUrl` / `openPath` from `@tauri-apps/plugin-opener`, not shell `open`.
- **Command arguments are camelCase from JS.** A Rust `fn save_note(note_title: String)` is called with
  `invoke("save_note", { noteTitle })`. Sending `note_title` fails with a missing-argument error. (Return values and
  struct fields keep their serde names.)
- Config: there's no `tauri` or `package` key. `productName`, `version` and `identifier` are top level, the window
  list and security settings live under `app`, `build.devPath` is `build.devUrl` and `build.distDir` is
  `build.frontendDist`. Validate against the schema in `node_modules/@tauri-apps/cli/config.schema.json`.
- Rust: `get_webview_window`, `emit` (the `Emitter` trait), `app.path()`, `tauri::tray::TrayIconBuilder`,
  `tauri::menu::MenuBuilder`, `WebviewWindowBuilder`. The builder goes in `lib.rs` as `pub fn run()` with
  `#[cfg_attr(mobile, tauri::mobile_entry_point)]`, and `main.rs` only calls it.
- Docs for this version: https://v2.tauri.app/ (the migration guide is
  https://v2.tauri.app/start/migrate/from-tauri-1/). Ignore tauri.app/v1 pages.

## Rules
- Write Tauri 2 code only. The `tauri-2-guard` skill has the full table.
- Every plugin needs all three parts: the npm package, the crate plus `.plugin(...)`, and the narrowest permission
  that works. Never add `"fs:default"`-style wide grants to make an error go away; ask.
- Keep `app.security.csp`. Don't turn on `withGlobalTauri` to use `window.__TAURI__`; import from `@tauri-apps/api`.
- Don't change the Tauri version without asking.

## Before you say "done"
1. Run the `tauri-2-guard` scanner on `src`, `src-tauri` and `package.json`. It must report `0 error(s)`.
2. Type-check the front end (`npx tsc --noEmit`) and run its tests, mocking the IPC with `@tauri-apps/api/mocks`.
3. Validate `src-tauri/tauri.conf.json` against the CLI's config schema.
4. Run `cargo check --manifest-path src-tauri/Cargo.toml` where the system has the WebView libraries, and
   `npm run tauri dev` if you changed windows, menus or the tray.

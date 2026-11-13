# Tauri 1 to Tauri 2, the code agents get wrong

From the official guide (https://v2.tauri.app/start/migrate/from-tauri-1/). Checked against `@tauri-apps/api` 2.12.4,
`@tauri-apps/cli` 2.12.4 (config schema 2.12.5) and the `tauri` 2.12.5 crate source.

## Front end
| Tauri 1 | Tauri 2 |
|---|---|
| `import { invoke, convertFileSrc } from "@tauri-apps/api/tauri"` | `from "@tauri-apps/api/core"` |
| `import { appWindow } from "@tauri-apps/api/window"` | `getCurrentWebviewWindow()` from `@tauri-apps/api/webviewWindow` (or `getCurrentWindow()` from `/window`) |
| `WebviewWindow` from `@tauri-apps/api/window` | from `@tauri-apps/api/webviewWindow` |
| `@tauri-apps/api/fs` (`readTextFile(p, { dir })`) | `@tauri-apps/plugin-fs` (`readTextFile(p, { baseDir })`) |
| `@tauri-apps/api/dialog` | `@tauri-apps/plugin-dialog` |
| `@tauri-apps/api/shell` `open(url)` | `openUrl(url)` from `@tauri-apps/plugin-opener`; `Command` from `@tauri-apps/plugin-shell` |
| `@tauri-apps/api/http` | `@tauri-apps/plugin-http` (`fetch`) |
| `clipboard`, `notification`, `globalShortcut`, `os`, `process`, `updater`, `cli` | `@tauri-apps/plugin-clipboard-manager`, `-notification`, `-global-shortcut`, `-os`, `-process`, `-updater`, `-cli` |
| `invoke("cmd", { note_title })` | `invoke("cmd", { noteTitle })`: arguments are camelCase by default |
| `window.__TAURI__.*` | imports from `@tauri-apps/api` (the global needs `app.withGlobalTauri: true`) |

## tauri.conf.json
| Tauri 1 | Tauri 2 |
|---|---|
| `package.productName`, `package.version` | top-level `productName`, `version` |
| `tauri.bundle.identifier` | top-level `identifier` |
| `tauri` | `app` (windows, security, trayIcon); `bundle` moves to the top level |
| `tauri.allowlist` | `src-tauri/capabilities/*.json` with plugin permissions |
| `build.devPath` / `build.distDir` | `build.devUrl` / `build.frontendDist` |
| `build.withGlobalTauri` | `app.withGlobalTauri` |
| `tauri.systemTray` | `app.trayIcon` |
| `tauri.updater` | `plugins.updater` and `tauri-plugin-updater` |

## Rust
| Tauri 1 | Tauri 2 |
|---|---|
| `app.get_window("main")` | `app.get_webview_window("main")` (`get_window` needs the `unstable` feature) |
| `window.emit_all(event, payload)` | `window.emit(event, payload)` with `use tauri::Emitter` |
| `window: tauri::Window` in a command | `window: tauri::WebviewWindow` |
| `app.path_resolver().app_data_dir()` (Option) | `app.path().app_data_dir()` (Result) |
| `SystemTray::new().with_menu(...)` | `tauri::tray::TrayIconBuilder::new().menu(&menu).build(app)?` (feature `tray-icon`) |
| `Menu::new().add_item(CustomMenuItem::new(id, text))` | `MenuBuilder::new(app).item(&MenuItemBuilder::with_id(id, text).build(app)?).build()?` |
| `WindowBuilder::new(app, label, WindowUrl::App(..))` | `WebviewWindowBuilder::new(app, label, WebviewUrl::App(..))` |
| `tauri::api::shell::open`, `tauri::api::dialog` | the plugin crates |
| builder in `main.rs` | `pub fn run()` in `lib.rs` with `#[cfg_attr(mobile, tauri::mobile_entry_point)]` |
| `tauri = { version = "1", features = ["shell-open", ...] }` | `tauri = "2"` plus plugin crates; allowlist features are gone |

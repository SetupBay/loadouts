---
name: tauri-2-guard
description: Check a Tauri 2 app for Tauri 1 code in the front end, the Rust side and tauri.conf.json (api/tauri imports, appWindow, the allowlist, get_window, emit_all, SystemTray) and for snake_case invoke arguments, then type-check, test with mocked IPC and validate the config schema. Use after writing or editing Tauri code, when invoke reports a missing argument, or when porting a Tauri 1 example.
---

# Tauri 2 guard

Most Tauri examples online are Tauri 1, and Tauri 2 changed the import paths, moved fs/dialog/shell/http into
plugins, replaced the allowlist with capabilities, renamed config keys and renamed core Rust APIs. One change bites
even in pure Tauri 2 code: JS must send command arguments in camelCase.

## 1. Confirm the version
- `src-tauri/Cargo.toml` must say `tauri = "2..."` and `package.json` `@tauri-apps/api` 2.x. If not, stop and ask.

## 2. Scan
```bash
python3 .agents/skills/tauri-2-guard/scripts/tauri2_guard.py src src-tauri package.json
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- Each `error` is Tauri 1 code. Fix it with the replacement on the line, or look it up in `references/v1-to-v2.md`.
- `warn [invoke-snake-args]`: rename the keys to camelCase, unless the Rust command has
  `#[tauri::command(rename_all = "snake_case")]`. Then add `// guard: ok rename_all` to the line.
- `warn [global-tauri]`: import from `@tauri-apps/api` instead of using `window.__TAURI__`.
- When a plugin import is reported, add all three parts: the npm package, the crate plus `.plugin(...)`, and a
  narrow permission in `src-tauri/capabilities/`.

## 3. Check the front end
```bash
npx tsc --noEmit
```
Test calls to Rust without running the app, using the mocks that ship with `@tauri-apps/api`:
```js
globalThis.window ??= globalThis; // only when the test runs in Node
const { mockIPC, mockWindows } = await import("@tauri-apps/api/mocks");
mockWindows("main");
mockIPC((cmd, args) => (cmd === "save_note" ? `saved ${args.noteTitle}` : null));
```
Assert on the command name and the argument keys, so a snake_case key fails the test.

## 4. Validate the config
`node_modules/@tauri-apps/cli/config.schema.json` is the schema for this exact CLI version, and it rejects unknown
keys. Validate `src-tauri/tauri.conf.json` against it with any JSON Schema (draft-07) validator. With Ajv, pass
`unicodeRegExp: false`, because the schema has a pattern that isn't valid as a Unicode regex.

## 5. Check the Rust side
`cargo check --manifest-path src-tauri/Cargo.toml` needs the platform WebView libraries (on Linux, webkit2gtk-4.1).
Where they aren't installed, say so in your report rather than claiming the Rust side compiles.

## 6. Report
Say which Tauri 1 calls and keys you replaced, which plugins and permissions you added, and which checks ran
(scanner, tsc, tests, schema, cargo check).

---
name: godot-jam-ship
description: Export a Godot 4 project to the web and publish it to itch.io. Use when the user wants to build, export, upload, publish or submit their game jam entry.
---

# Ship a Godot 4 jam build to itch.io

## 0. Preconditions (check, then tell the human what is missing)
- Godot 4 is on the PATH (`godot --version`) and the **export templates for that exact version** are installed
  (Editor → Manage Export Templates). Headless export fails without them.
- `export_presets.cfg` contains a preset named `Web`. If not, ask the human to add one in Project → Export
  (Add… → Web) and save; do not invent the file from scratch.
- `butler` is installed and logged in (`butler login`, or `BUTLER_API_KEY` set) if publishing.
- The itch.io project page exists (it can be a draft). You need `user/game-slug`.

## 1. Pick threading
- **Thread Support off** (default for Godot 4.3+ Web preset): works anywhere, including itch.io, with no special headers. Use this unless the human needs threads.
- **Thread Support on**: needs cross-origin isolation (SharedArrayBuffer). On itch.io tick
  "SharedArrayBuffer support" in the embed options, or the game shows a blank screen.

## 2. Export
```sh
mkdir -p build/web
godot --headless --export-release "Web" build/web/index.html
```
- The entry file must be `index.html` for itch.io.
- Check `build/web` contains `index.html`, `.js`, `.wasm` and `.pck` files. If the `.pck` is huge, look for
  uncompressed audio or unused assets and mention it.

## 3. Smoke test locally
```sh
npx serve build/web   # or: python3 -m http.server -d build/web 8000
```
Ask the human to open it and play for 30 seconds. Web builds can behave differently from the editor
(audio needs a click to start; mouse capture needs a user gesture).

## 4. Publish
```sh
butler push build/web user/game-slug:html5 --userversion "jam-$(date +%Y%m%d-%H%M)"
butler status user/game-slug:html5
```
- First push only: the human must set "Kind of project" to HTML on the itch page and tick
  "This file will be played in the browser" for the html5 upload, and set the viewport size to the project's window size.

## 5. Optional desktop builds
If presets exist: `godot --headless --export-release "Windows Desktop" build/win/game.exe` then
`butler push build/win user/game-slug:windows`. Same for `Linux` and `macOS` (macOS builds are unsigned — tell the human players will need to right-click → Open).

## 6. Report
Tell the human: the itch.io URL, the channel(s) pushed, the build version string, and anything that still needs a click on the itch dashboard. Do not submit to the jam itself — that is the human's button.

# AGENTS.md: Chrome extension (Manifest V3)

## Ground rules
- This is a **Manifest V3** extension (`"manifest_version": 3`). Do not use MV2 APIs: no `background.page`,
  no `background.persistent`, no `chrome.browserAction`/`pageAction` (use `chrome.action`), no blocking `webRequest` (use `declarativeNetRequest`).
- **No remotely hosted code.** Every script the extension runs ships in the package. No `eval`, no `new Function`,
  no `<script src="https://...">`, no loading JS from a CDN. Fetching *data* (JSON) is fine.

## Layout
```
manifest.json
src/background.ts    service worker
src/content/*.ts     content scripts (run in web pages, isolated world)
src/popup/           popup UI (popup.html + script)
src/options/         options page
icons/               16, 32, 48, 128 px PNGs
```

## Service worker lifecycle
- The service worker stops when idle (after about 30 seconds) and restarts on events. **Global variables are lost.**
  Persist state in `chrome.storage.local` (or `session` for per-browser-session data).
- Register all event listeners synchronously at the top level of the worker, not inside `await`s or callbacks,
  or they will be missed when the worker wakes.
- Use `chrome.alarms` instead of `setInterval`/`setTimeout` for anything longer than a few seconds.
- No DOM in the service worker (`document`, `window`, `localStorage` do not exist). Use an offscreen document if you truly need DOM APIs.

## Permissions (least privilege — reviewers check this)
- Prefer `activeTab` + `scripting` over broad host permissions: the extension gets access to the current tab only when the user clicks it.
- If host access is needed, list specific origins, and prefer `optional_host_permissions` requested at the moment of use
  with `chrome.permissions.request`.
- Never add `<all_urls>`, `tabs`, `history`, `cookies` or `webRequest` "just in case". Every permission needs a one-line reason in `PERMISSIONS.md`.

## Messaging
- Content script ↔ service worker: `chrome.runtime.sendMessage` / `chrome.runtime.onMessage`. Popup → tab: `chrome.tabs.sendMessage(tabId, ...)`.
- Messages are typed objects with a `type` field. Validate the shape on receipt; treat messages from content scripts as untrusted
  (web pages can influence them).
- To respond asynchronously from `onMessage`, `return true` from the listener and call `sendResponse` later.

## Content scripts
- Do not trust page data. Never insert page-controlled strings with `innerHTML`; use `textContent` or build elements.
- Scope `matches` as narrowly as possible. Avoid running on every page if the feature is for one site.
- Style injected UI in a Shadow DOM so page CSS cannot break it (and vice versa).

## Dev loop
- `npm run build` outputs to `dist/`. The human loads it at `chrome://extensions` → Developer mode → Load unpacked → `dist/`.
- After changing `manifest.json` or the service worker, the extension must be reloaded on that page. Remind the human.
- Debug the worker from `chrome://extensions` → "service worker" link; debug content scripts in the page's DevTools.

## Testing
- Use the `extension-e2e` skill. Tests load `dist/` in Playwright's bundled Chromium (`channel: "chromium"`), since
  branded Chrome and Edge removed the flags for side-loading extensions. They check the loaded manifest, the popup,
  message handling and storage.
- `node .agents/skills/extension-e2e/scripts/manifest_check.mjs dist PERMISSIONS.md` checks the built package:
  MV3 keys, files present, risky or unjustified permissions, CSP, no eval or remote code.
- Don't widen permissions to make a test easier.

## Before you say "done"
`npm run build` passes, `manifest_check.mjs` prints `ok:`, `npx playwright test` passes, there are no new
permissions you have not justified, and you have said what the human should reload and click through by hand.

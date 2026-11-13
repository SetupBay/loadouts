# AGENTS.md: Chrome extension, Manifest V3 service worker guard

This extension is **Manifest V3**. Its background script is a **service worker**, not a background page. Chrome
starts it for an event and stops it after about 30 seconds without events. Manifest V2 no longer runs in
Chrome, but much of the extension code you learnt from is MV2.

## What a service worker is not
- It has no DOM: no `document`, `window`, `localStorage`, `sessionStorage`, `XMLHttpRequest` or `alert()`. Use
  `chrome.storage`, `fetch`, and an offscreen document (`chrome.offscreen`) for work that needs a DOM.
- It doesn't keep globals. A `let count = 0` at the top of the worker goes back to `0` every time Chrome stops and
  restarts it. Keep state in `chrome.storage.session` (in memory, cleared when the browser closes) or
  `chrome.storage.local`.
- It doesn't keep timers. Use `chrome.alarms` for anything that should happen later than a few seconds from now.
- Chrome wakes it only for listeners it already knows about. Register every `chrome.*.on*.addListener` call
  synchronously at the top level of the worker, not inside a callback, a function or after an `await`.
- There is no background page to reach into: `chrome.extension.getBackgroundPage()` and
  `chrome.runtime.getBackgroundPage()` don't exist in MV3. Send messages.

## API replacements
- `chrome.browserAction` / `chrome.pageAction` → `chrome.action`
- `chrome.tabs.executeScript` / `insertCSS` → `chrome.scripting.executeScript` / `insertCSS` (permission `scripting`)
- `chrome.extension.sendRequest` / `onRequest` / `getURL` → `chrome.runtime.sendMessage` / `onMessage` / `getURL`
- `chrome.tabs.getSelected` → `chrome.tabs.query({ active: true, currentWindow: true })`
- blocking `webRequest` → `chrome.declarativeNetRequest` rules
- No `eval`, `new Function` or remotely hosted scripts: everything runs from the package.

## Before you say "done"
1. Run the `mv3-worker-guard` scanner on the extension source and `manifest.json`. It must report `0 error(s)`; any
   warning you keep needs a `// guard: ok <reason>` comment.
2. Load the extension, stop its service worker (chrome://serviceworker-internals, or the CDP command
   `ServiceWorker.stopAllWorkers` in a test), then use the feature again. It must behave the same.

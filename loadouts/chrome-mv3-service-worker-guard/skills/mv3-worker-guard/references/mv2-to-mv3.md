# MV2 background page to MV3 service worker

From the Chrome docs: "Migrate to a service worker" and "Replace blocking web request listeners"
(https://developer.chrome.com/docs/extensions/develop/migrate). Checked in Playwright's Chromium (@playwright/test 1.64.1).

| MV2 | MV3 |
|---|---|
| `"background": { "scripts": [...], "persistent": false }` | `"background": { "service_worker": "sw.js", "type": "module" }` |
| `"browser_action"` / `"page_action"` | `"action"` |
| `chrome.browserAction.*` / `chrome.pageAction.*` | `chrome.action.*` |
| `chrome.tabs.executeScript(tabId, { code })` | `chrome.scripting.executeScript({ target: { tabId }, func })` |
| `chrome.tabs.insertCSS` / `removeCSS` | `chrome.scripting.insertCSS` / `removeCSS` |
| `chrome.extension.getBackgroundPage()` / `getViews()` | message the worker: `chrome.runtime.sendMessage` |
| `chrome.extension.sendRequest` / `onRequest` | `chrome.runtime.sendMessage` / `onMessage` |
| `chrome.extension.getURL` | `chrome.runtime.getURL` |
| `chrome.tabs.getSelected(null, cb)` | `chrome.tabs.query({ active: true, currentWindow: true })` |
| `webRequest.onBeforeRequest` with `["blocking"]` + `webRequestBlocking` | `declarativeNetRequest` rules (static `rule_resources` or `updateDynamicRules`) |
| `localStorage` in the background | `chrome.storage.local` (or `storage.session` for in-memory state) |
| globals as state | `chrome.storage.session` |
| `setTimeout` / `setInterval` for minutes or hours | `chrome.alarms` |
| `XMLHttpRequest` | `fetch` |
| DOM work in the background (`DOMParser`, audio, clipboard) | `chrome.offscreen.createDocument({ url, reasons, justification })` |
| `eval`, `new Function`, remote scripts | not allowed; ship the code in the package |

## Service worker lifecycle facts
- Chrome stops the worker after 30 seconds without events; a single request taking longer than 5 minutes is also stopped.
- Events reset the idle timer, and extension API calls do too.
- Register listeners at the top level, synchronously, so they exist when Chrome restarts the worker for an event.
- `chrome.storage.session` keeps data in memory for the browser session (about 10 MB) and survives worker restarts.

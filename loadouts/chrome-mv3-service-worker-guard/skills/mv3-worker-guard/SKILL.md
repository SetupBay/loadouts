---
name: mv3-worker-guard
description: Check a Chrome extension's Manifest V3 service worker and scripts for MV2 APIs (browserAction, tabs.executeScript, getBackgroundPage, blocking webRequest) and for code that breaks when Chrome stops the worker (globals as state, long timers, nested listeners, DOM and localStorage), then prove state survives a worker restart. Use after writing or editing extension background code, when a feature works at first and then stops, or when porting an MV2 extension.
---

# MV3 service worker guard

Chrome stops an MV3 service worker after about 30 seconds without events and starts it again for the next one.
Code written for an MV2 background page assumes it runs forever, so it works while you click around and breaks
later: counts reset to zero, timers never fire, and `document` or `localStorage` throw. This skill finds those
patterns and the removed MV2 APIs, then checks the behaviour by restarting the worker.

## 1. Scan
```bash
python3 .agents/skills/mv3-worker-guard/scripts/mv3_worker_guard.py src manifest.json
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- The worker rules apply to files named like a background script (`sw.js`, `service-worker.js`, `background.js`,
  `*-worker.js` and the `.ts` versions). Other files get the API rules only.
- `error` lines are MV2 APIs or things a worker can't do. Fix each with the replacement on the line; see
  `references/mv2-to-mv3.md`.
- `warn` lines are lifecycle risks: a mutable global, a long timer, a listener registered below the top level,
  a keep-alive hack. Fix them, or add `// guard: ok <reason>` (for example, a constant cache that's fine to rebuild).

## 2. Restart the worker and use the feature again
The bug only shows after a restart, so test that directly. With Playwright and a persistent context that loads the
unpacked extension, stop every service worker through CDP and send the next message:
```js
const cdp = await context.newCDPSession(page);   // page: an extension page such as popup.html
await cdp.send("ServiceWorker.enable");
const stopped = new Promise((resolve) => cdp.on("ServiceWorker.workerVersionUpdated", (e) => {
  if (e.versions.some((v) => v.runningStatus === "stopped")) resolve();
}));
await cdp.send("ServiceWorker.stopAllWorkers");
await stopped;
// now sendMessage again and assert the state is unchanged
```
`references/worker-restart.spec.mjs` is a complete test that does this. By hand, use chrome://serviceworker-internals
and click **Stop**.

## 3. Report
Say which MV2 APIs you replaced, where state now lives (`storage.session` or `storage.local`), which timers became
alarms, and that the scanner was clean and the feature still worked after a worker restart.

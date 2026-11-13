---
name: electron-e2e-test
description: Write and run Playwright end-to-end tests that drive the real Electron app - main process, preload and renderer together - including security assertions on webPreferences, the preload API, IPC validation and blocked navigation. Use when adding a feature that crosses IPC, changing window or preload settings, or setting up Electron tests in CI.
---

# Electron end-to-end tests with Playwright

Unit tests of the renderer miss the bugs that matter in Electron: a preload that leaks `ipcRenderer`, a
handler that trusts its input, a window that someone set to `sandbox: false`. Playwright's Electron support
launches the real app and lets a test reach both sides: `page` for the renderer, `app.evaluate` for the main
process.

## Setup

- Dev dependencies, pinned: `@playwright/test` and `electron`. No browser download is needed for Electron
  tests (`npx playwright install` is not required).
- `references/playwright.config.js`: one worker, traces kept on failure, one retry on CI only.
- `references/electron-fixture.js`: `test.extend` fixtures. Every test gets a fresh `userData` folder,
  its own app instance (`app.current`), its first window (`page`), and `app.relaunch()` for restart tests.
  The main process must honour `E2E_USER_DATA`:

  ```js
  if (process.env.E2E_USER_DATA) app.setPath("userData", process.env.E2E_USER_DATA);
  ```

- Run: `npx playwright test`. On Linux without a display: `xvfb-run -a npx playwright test`.

## What every app's suite covers

`references/app.spec.js` is a complete example. Adapt these to your app:

1. Secure defaults, read from the main process:
   `webContents.getLastWebPreferences()` has `contextIsolation: true`, `sandbox: true`,
   `nodeIntegration: false`. A change that weakens one fails here, not in a security review.
2. The renderer sees only the preload API: `typeof window.require`, `window.process` and
   `window.ipcRenderer` are `"undefined"`, and the exposed object has exactly the functions you expect.
3. Each IPC feature end to end: act in the UI, assert the UI, then assert the main-process effect (a file
   in `userData`, a value from `app.evaluate`). Restart with `app.relaunch()` when persistence matters.
4. Each handler's validation: send bad input through the UI and assert the error and that nothing was written.
5. `window.open` and navigation away are denied, and there is still one window.

## Rules

- Locate by role and label (`getByRole`, `getByLabel`), never by CSS classes or XPath.
- Wait with web-first assertions (`expect(locator).toHaveText`, `expect.poll`), never `waitForTimeout`.
- One app per test via the fixture. No shared state between tests, no real home-directory data.
- Never trigger `shell.openExternal` from a test (use a URL your handler denies outright); on CI it can hang shutdown.
- Never pass `--no-sandbox`, `--disable-web-security` or similar flags to make a test pass. If the app only
  starts with them, report it as a bug.
- Do not stub `ipcRenderer` or the preload in e2e tests. That is what the test is for.
- A failing test gets fixed or reported, not skipped. `test.fixme` only with a linked issue.

## CI

`references/electron-e2e.yml`: Ubuntu runner, `npm ci`, a step that downloads the Electron binary
(`node -e "require('electron')"`, verified against Electron's checksums), then
`xvfb-run -a npx playwright test`. Traces upload on failure.

## Done means

The suite passes locally or under `xvfb-run`, the new behaviour has a test from the list above, and the
summary names any security assertion you changed and why.

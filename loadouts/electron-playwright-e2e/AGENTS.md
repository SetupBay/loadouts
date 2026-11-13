# AGENTS.md: Electron app tested end to end with Playwright

An Electron desktop app with a sandboxed, context-isolated renderer and a narrow preload API. End-to-end tests
use Playwright's Electron support to drive the real app. Check `package.json` for the Electron and Playwright
versions before using an API.

## Commands

- Start: `npm start`.
- End-to-end tests: `npx playwright test` (Linux without a display: `xvfb-run -a npx playwright test`).
- One test: `npx playwright test -g "rejects an empty title"`. Traces: `npx playwright show-trace test-results/.../trace.zip`.
- Done means: the suite passes and the behaviour you changed has an end-to-end test.

## Rules

- Use the `electron-e2e-test` skill for any change that crosses IPC, touches `webPreferences`, the preload or
  window handlers, or adds tests.
- Keep `contextIsolation: true`, `sandbox: true` and `nodeIntegration: false`, and keep the tests that assert
  them. Never weaken a security assertion to make a test pass.
- The renderer reaches main only through named preload functions. Every `ipcMain.handle` checks the sender
  frame and validates its arguments, and has a test for bad input.
- Tests use the shared fixture: a fresh app and `userData` per test. No `waitForTimeout`, no CSS selectors.
- Never add `--no-sandbox`, `--disable-web-security` or `ELECTRON_RUN_AS_NODE` to scripts or CI.

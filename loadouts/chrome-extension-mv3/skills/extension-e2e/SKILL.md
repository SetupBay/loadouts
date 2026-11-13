---
name: extension-e2e
description: Prove a Manifest V3 Chrome extension works by loading the built package in Playwright's bundled Chromium - service worker, popup, messaging and storage - and checking the manifest and package rules. Use after any change to the manifest, service worker, popup or messages, and before store submission.
---

# Test the extension in a real browser

Branded Chrome and Edge no longer accept the command-line flags that side-load an unpacked extension, so tests use
the Chromium that Playwright bundles (`channel: "chromium"`), which does, and which runs extensions headless.

## Set up once (ask before adding dependencies)
1. `npm install -D @playwright/test@1.64.1`, then `npx playwright install chromium` (downloads the browser).
2. Copy `references/playwright.config.mjs` to the project root and `references/fixtures.mjs` to `e2e/`.
3. Start from `references/extension.spec.mjs` in `e2e/` and adapt it: the permissions you expect, your popup's
   controls, your message types.

## What the fixtures give you
- `context`: a persistent Chromium context with only `dist/` loaded (`EXTENSION_DIR` overrides the folder).
- `serviceWorker`: the extension's MV3 worker; `serviceWorker.evaluate(() => chrome.storage.local.get())` runs code
  inside it.
- `extensionId`: from the worker URL, for opening `chrome-extension://<id>/popup/popup.html` as a normal page.

## Tests worth having
- The manifest Chrome actually loaded (`chrome.runtime.getManifest()`) has exactly the permissions you expect and no
  host permissions you didn't justify.
- The popup renders its controls (query by role and name).
- Messages: a valid message gets the right reply; a malformed one gets no reply. Content scripts and pages are
  untrusted senders.
- State comes back from `chrome.storage`, not from a global that dies when the worker stops after about 30 s idle.

## Run it
```sh
npm run build
node .agents/skills/extension-e2e/scripts/manifest_check.mjs dist PERMISSIONS.md
npx playwright test
```
`manifest_check.mjs` must print `ok:` and every test must pass. Report the counts. If Chromium can't be downloaded
(offline, locked-down CI), say so and run only the manifest check; don't claim the extension was tested in a browser.

## Limits
- Toolbar clicks, `activeTab` grants and the real popup window can't be driven from Playwright. Test the popup as
  a page and leave the click-through to the human's manual check at `chrome://extensions`.
- Don't add host permissions or `tabs` just to make a test easier.

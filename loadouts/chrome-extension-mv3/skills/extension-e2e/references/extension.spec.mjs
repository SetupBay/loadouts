// Example smoke tests for an unpacked MV3 extension. Adapt the names, permissions and messages to your extension.
import { test, expect } from "./fixtures.mjs";

test("loads as a Manifest V3 service worker", async ({ serviceWorker, extensionId }) => {
  expect(extensionId).toMatch(/^[a-p]{32}$/);
  const manifest = await serviceWorker.evaluate(() => chrome.runtime.getManifest());
  expect(manifest.manifest_version).toBe(3);
  expect(manifest.permissions).toEqual(["activeTab", "scripting", "storage"]);
  expect(manifest.host_permissions ?? []).toEqual([]);
});

test("popup renders its controls", async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/popup/popup.html`);
  await expect(page.getByRole("button", { name: "Count words" })).toBeVisible();
});

test("state survives in chrome.storage, not globals", async ({ page, extensionId, serviceWorker }) => {
  await page.goto(`chrome-extension://${extensionId}/popup/popup.html`);
  expect(await page.evaluate(() => chrome.runtime.sendMessage({ type: "get-last-count" }))).toBeNull();
  await serviceWorker.evaluate(() => chrome.storage.local.set({ lastCount: { words: 42, url: "https://example.com/" } }));
  expect(await page.evaluate(() => chrome.runtime.sendMessage({ type: "get-last-count" }))).toEqual({ words: 42, url: "https://example.com/" });
});

test("malformed messages get no answer", async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/popup/popup.html`);
  const reply = await page.evaluate(() =>
    chrome.runtime.sendMessage({ type: "count-words", tabId: "1; drop" }).then((r) => ({ r }), (e) => ({ e: String(e.message) })),
  );
  expect(reply.r).toBeUndefined();
});

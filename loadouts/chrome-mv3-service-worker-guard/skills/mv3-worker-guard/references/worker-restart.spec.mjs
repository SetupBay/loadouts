// Stop the MV3 service worker the way Chrome does when it's idle, then talk to it again.
import { test as base, chromium, expect } from "@playwright/test";
import path from "node:path";

const withExtension = (dir) => {
  const EXT = path.resolve(dir);
  return base.extend({
    context: async ({}, use) => {
      const context = await chromium.launchPersistentContext("", {
        channel: "chromium",
        args: [`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`],
      });
      await use(context);
      await context.close();
    },
    serviceWorker: async ({ context }, use) => {
      let [worker] = context.serviceWorkers();
      if (!worker) worker = await context.waitForEvent("serviceworker");
      await use(worker);
    },
    extensionId: async ({ serviceWorker }, use) => use(serviceWorker.url().split("/")[2]),
  });
};

async function countAcrossRestart(context, extensionId) {
  const page = await context.newPage();
  await page.goto(`chrome-extension://${extensionId}/popup.html`);
  const send = (type) => page.evaluate((t) => chrome.runtime.sendMessage({ type: t }), type);
  await send("count");
  await send("count");
  const before = (await send("get")).count;
  const cdp = await context.newCDPSession(page);
  await cdp.send("ServiceWorker.enable");
  const stopped = new Promise((resolve) =>
    cdp.on("ServiceWorker.workerVersionUpdated", (e) => {
      if (e.versions.some((v) => v.runningStatus === "stopped")) resolve();
    }),
  );
  await cdp.send("ServiceWorker.stopAllWorkers");
  await stopped;
  const after = (await send("get")).count;
  return { before, after };
}

const good = withExtension("extension");
const globals = withExtension("globals-extension");

good("the MV3 worker has no DOM, localStorage, XMLHttpRequest or MV2 APIs", async ({ serviceWorker }) => {
  const seen = await serviceWorker.evaluate(() => ({
    document: typeof document,
    localStorage: typeof localStorage,
    XMLHttpRequest: typeof XMLHttpRequest,
    browserAction: typeof chrome.browserAction,
    executeScript: typeof chrome.tabs.executeScript,
    getBackgroundPage: typeof chrome.extension?.getBackgroundPage,
    action: typeof chrome.action,
    alarms: typeof chrome.alarms,
  }));
  console.log(`worker globals ${JSON.stringify(seen)}`);
  expect(seen).toEqual({
    document: "undefined", localStorage: "undefined", XMLHttpRequest: "undefined",
    browserAction: "undefined", executeScript: "undefined", getBackgroundPage: "undefined",
    action: "object", alarms: "object",
  });
});

good("state in chrome.storage.session survives a worker restart", async ({ context, extensionId }) => {
  const { before, after } = await countAcrossRestart(context, extensionId);
  console.log(`storage.session before=${before} after=${after}`);
  expect(before).toBe(2);
  expect(after).toBe(2);
});

good("the alarm is registered with chrome.alarms, not a timer", async ({ serviceWorker }) => {
  // onInstalled creates the alarm asynchronously, so wait for it rather than racing it.
  await expect.poll(() => serviceWorker.evaluate(async () => Boolean(await chrome.alarms.get("tidy")))).toBe(true);
  const alarm = await serviceWorker.evaluate(() => chrome.alarms.get("tidy"));
  console.log(`alarm ${alarm.name} every ${alarm.periodInMinutes} min`);
  expect(alarm.periodInMinutes).toBe(30);
});

globals("state in a global is lost when Chrome stops the worker", async ({ context, extensionId }) => {
  const { before, after } = await countAcrossRestart(context, extensionId);
  console.log(`global before=${before} after=${after}`);
  expect(before).toBe(2);
  expect(after).toBe(0);
});

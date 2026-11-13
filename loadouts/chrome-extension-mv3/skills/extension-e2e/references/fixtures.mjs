// Playwright fixtures for an unpacked Manifest V3 extension (see the Playwright "Chrome extensions" guide).
import { test as base, chromium } from "@playwright/test";
import path from "node:path";

const EXTENSION_DIR = path.resolve(process.env.EXTENSION_DIR ?? "dist");

export const test = base.extend({
  // A persistent context is required for extensions. channel "chromium" uses Playwright's bundled Chromium, which
  // still accepts --load-extension (branded Chrome and Edge dropped it) and supports extensions in headless mode.
  context: async ({}, use) => {
    const context = await chromium.launchPersistentContext("", {
      channel: "chromium",
      args: [`--disable-extensions-except=${EXTENSION_DIR}`, `--load-extension=${EXTENSION_DIR}`],
    });
    await use(context);
    await context.close();
  },
  serviceWorker: async ({ context }, use) => {
    let [worker] = context.serviceWorkers();
    if (!worker) worker = await context.waitForEvent("serviceworker");
    await use(worker);
  },
  extensionId: async ({ serviceWorker }, use) => {
    await use(serviceWorker.url().split("/")[2]);
  },
});
export const expect = test.expect;

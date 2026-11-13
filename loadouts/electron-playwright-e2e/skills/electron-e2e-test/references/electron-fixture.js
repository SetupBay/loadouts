// Playwright fixtures for Electron: every test gets its own app instance and an empty userData folder.
// `relaunch()` closes and restarts the app on the same userData, for persistence tests.
const base = require("@playwright/test");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const launch = (userData) =>
  base._electron.launch({
    args: ["."],
    env: { ...process.env, E2E_USER_DATA: userData, ELECTRON_ENABLE_LOGGING: "1" },
  });

exports.test = base.test.extend({
  userData: async ({}, use) => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "electron-e2e-"));
    await use(dir);
    fs.rmSync(dir, { recursive: true, force: true });
  },
  app: async ({ userData }, use) => {
    const holder = { current: await launch(userData) };
    holder.relaunch = async () => {
      await holder.current.close();
      holder.current = await launch(userData);
      return holder.current;
    };
    await use(holder);
    // Close normally, but never let a stuck app hang the run: kill it after 10 seconds.
    const proc = holder.current.process();
    const timer = setTimeout(() => proc.kill("SIGKILL"), 10_000);
    await holder.current.close().catch(() => {});
    clearTimeout(timer);
  },
  page: async ({ app }, use) => {
    const page = await app.current.firstWindow();
    await page.waitForLoadState("domcontentloaded");
    await use(page);
  },
});

exports.expect = base.expect;

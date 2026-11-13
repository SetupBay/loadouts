// Drives the real Electron app: main process, preload and renderer together.
const fs = require("node:fs");
const path = require("node:path");
const { test, expect } = require("./electron-fixture");

test("window opens with the secure web preferences", async ({ app, page }) => {
  await expect(page).toHaveTitle("Notes");
  const prefs = await app.current.evaluate(({ BrowserWindow }) => {
    const p = BrowserWindow.getAllWindows()[0].webContents.getLastWebPreferences();
    return { contextIsolation: p.contextIsolation, sandbox: p.sandbox, nodeIntegration: p.nodeIntegration };
  });
  expect(prefs).toEqual({ contextIsolation: true, sandbox: true, nodeIntegration: false });
});

test("the renderer has the preload API and no Node", async ({ page }) => {
  const globals = await page.evaluate(() => ({
    require: typeof window.require,
    process: typeof window.process,
    ipcRenderer: typeof window.ipcRenderer,
    notes: Object.keys(window.notes).sort(),
  }));
  expect(globals).toEqual({ require: "undefined", process: "undefined", ipcRenderer: "undefined", notes: ["add", "list"] });
});

test("adding a note goes through IPC, is saved by main, and survives a restart", async ({ app, page, userData }) => {
  await page.getByLabel("Title").fill("  Buy milk  ");
  await page.getByRole("button", { name: "Add note" }).click();
  await expect(page.getByRole("list", { name: "Notes" }).getByRole("listitem")).toHaveText(["Buy milk"]);

  const saved = JSON.parse(fs.readFileSync(path.join(userData, "notes.json"), "utf8"));
  expect(saved.map((n) => n.title)).toEqual(["Buy milk"]);

  const again = await (await app.relaunch()).firstWindow();
  await expect(again.getByRole("listitem")).toHaveText(["Buy milk"]);
});

test("the main process rejects an empty title", async ({ page, userData }) => {
  await page.getByLabel("Title").fill("   ");
  await page.getByRole("button", { name: "Add note" }).click();
  await expect(page.getByRole("alert")).toHaveText("Title must be 1-120 characters");
  expect(fs.existsSync(path.join(userData, "notes.json"))).toBe(false);
});

test("window.open and navigation away are denied", async ({ app, page }) => {
  // http:// is denied without being handed to the OS browser; https:// would go to shell.openExternal,
  // which a test must never trigger (on CI it can leave xdg-open hanging and block shutdown).
  expect(await page.evaluate(() => window.open("http://example.com") === null)).toBe(true);
  await page.evaluate(() => {
    window.location.href = "https://example.com";
  });
  await expect.poll(() => page.url()).toMatch(/index\.html$/);
  expect(app.current.windows()).toHaveLength(1);
});

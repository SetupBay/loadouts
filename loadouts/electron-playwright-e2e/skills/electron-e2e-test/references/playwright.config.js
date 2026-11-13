// Electron end-to-end tests. One worker: each test launches its own app instance.
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "e2e",
  timeout: 30_000,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: { trace: "retain-on-failure" },
});

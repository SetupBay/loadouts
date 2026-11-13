// Extensions need a persistent context, so tests run one at a time.
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "e2e",
  testMatch: /.*\.spec\.mjs/,
  workers: 1,
  retries: 0,
  reporter: "list",
});

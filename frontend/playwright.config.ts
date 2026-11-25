import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:18401",
    headless: true,
  },
  reporter: "list",
  timeout: 60000,
});

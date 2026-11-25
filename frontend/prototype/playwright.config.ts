import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests/e2e",
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "evidence/playwright-report" }],
    ["json", { outputFile: "evidence/playwright-results.json" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:18767",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: {
    command: "npm run preview -- --port 18767",
    url: "http://127.0.0.1:18767",
    reuseExistingServer: false,
  },
});

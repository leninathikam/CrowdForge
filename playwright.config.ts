import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests/e2e",
  timeout: 60000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://127.0.0.1:8000",
    viewport: { width: 1920, height: 1080 },
    trace: "retain-on-failure",
  },
  reporter: [["list"], ["json", { outputFile: "artifacts/e2e-results.json" }]],
});

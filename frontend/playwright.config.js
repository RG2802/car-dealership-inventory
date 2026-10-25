import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:5173",
    launchOptions: process.env.CHROMIUM_PATH
      ? { executablePath: process.env.CHROMIUM_PATH }
      : {},
    viewport: { width: 1440, height: 1050 },
  },
  webServer: [
    {
      command: ".venv/bin/python -m backend.e2e_server",
      cwd: "..",
      url: "http://127.0.0.1:8000/docs",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5173",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: false,
    },
  ],
  reporter: [
    ["list"],
    ["json", { outputFile: "../docs/browser-results.json" }],
  ],
});

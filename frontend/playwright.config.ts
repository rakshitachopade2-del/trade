import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './browser',
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  outputDir: '../artifacts/browser',
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:15173',
    channel: 'chrome',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } },
    { name: 'tablet', use: { viewport: { width: 768, height: 1024 } } },
    { name: 'mobile', use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
    { name: 'narrow', use: { viewport: { width: 320, height: 740 }, isMobile: true, hasTouch: true } },
  ],
  webServer: {
    command: 'npm run dev -- --port 15173 --strictPort',
    url: 'http://127.0.0.1:15173',
    reuseExistingServer: false,
  },
});

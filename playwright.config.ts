import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://127.0.0.1:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /e2e\/.*/,
    },
    {
      name: 'api',
      use: {
        baseURL: 'http://127.0.0.1:8000',
      },
      testMatch: /api\/.*/,
    },
  ],
  webServer: process.env.CI
    ? undefined
    : [
        {
          command: 'cd frontend && npm run dev',
          url: 'http://localhost:3000',
          reuseExistingServer: true,
          timeout: 30000,
        },
        {
          command:
            'cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000',
          url: 'http://localhost:8000/health',
          reuseExistingServer: true,
          timeout: 30000,
        },
      ],
});

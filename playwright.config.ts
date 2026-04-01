import { defineConfig, devices } from '@playwright/test';

const frontendBaseURL =
  process.env.PLAYWRIGHT_FRONTEND_URL || (process.env.CI ? 'http://127.0.0.1:3000' : 'http://127.0.0.1:3100');
const backendApiURL =
  process.env.PLAYWRIGHT_BACKEND_URL || (process.env.CI ? 'http://127.0.0.1:8000/api' : 'http://127.0.0.1:8010/api');
const backendOriginURL = backendApiURL.replace(/\/api$/, '');

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
    baseURL: frontendBaseURL,
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
        baseURL: backendOriginURL,
      },
      testMatch: /api\/.*/,
    },
  ],
  webServer: process.env.CI
    ? undefined
    : [
        {
          command:
            `cd frontend && NEXT_PUBLIC_ENABLE_EMAIL_LOGIN=true NEXT_PUBLIC_API_URL=${backendApiURL} NEXT_PUBLIC_APP_URL=${frontendBaseURL} npm run dev -- --port 3100`,
          url: frontendBaseURL,
          reuseExistingServer: false,
          timeout: 30000,
        },
        {
          command:
            'cd backend && source venv/bin/activate && ENABLE_TEST_LOGIN=true uvicorn app.main:app --host 0.0.0.0 --port 8010',
          url: `${backendOriginURL}/health`,
          reuseExistingServer: false,
          timeout: 30000,
        },
      ],
});

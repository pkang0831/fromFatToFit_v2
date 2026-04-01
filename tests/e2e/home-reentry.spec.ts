import { test, expect, type APIRequestContext, type Page } from '@playwright/test';

const BACKEND_URL = process.env.PLAYWRIGHT_BACKEND_URL || 'http://127.0.0.1:8010/api';
const FRONTEND_URL = process.env.PLAYWRIGHT_FRONTEND_URL || 'http://127.0.0.1:3100';

async function bootstrapAuthenticatedSession(page: Page, request: APIRequestContext) {
  const res = await request.post(`${BACKEND_URL}/auth/test-login`);
  expect(res.status()).toBe(200);

  const body = await res.json();
  expect(body.access_token).toBeTruthy();
  expect(body.refresh_token).toBeTruthy();

  await page.context().addCookies([
    { name: 'access_token', value: body.access_token, url: FRONTEND_URL },
    { name: 'refresh_token', value: body.refresh_token, url: FRONTEND_URL },
  ]);

  await page.addInitScript(
    ({ accessToken, refreshToken }) => {
      window.localStorage.setItem('access_token', accessToken);
      window.localStorage.setItem('refresh_token', refreshToken);
    },
    {
      accessToken: body.access_token as string,
      refreshToken: body.refresh_token as string,
    },
  );
}

test.describe('Home Re-entry Surface @regression', () => {
  test('shows a server-backed primary CTA and state cards for an authenticated user', async ({ page, request }) => {
    await bootstrapAuthenticatedSession(page, request);

    const summaryResponse = page.waitForResponse(
      (res) => res.url().includes('/api/home/summary') && res.status() === 200,
    );

    await page.goto('/home', { waitUntil: 'domcontentloaded' });
    await summaryResponse;

    await expect(page).toHaveURL(/\/home/);
    await expect(page.getByText(/next action/i)).toBeVisible();
    await expect(
      page.getByRole('button', {
        name: /save your plan|check in today|start first scan|do weekly check-in|upload progress proof|review your proof/i,
      }),
    ).toBeVisible();
    await expect(page.getByText(/current goal/i)).toBeVisible();
    await expect(page.getByText(/^journey$/i)).toBeVisible();
    await expect(page.getByText(/^progress proof$/i)).toBeVisible();
  });
});

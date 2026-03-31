import { test, expect } from '@playwright/test';

/**
 * Full dashboard smoke after email login (Google OAuth bypass for QA).
 * Requires:
 * - Backend + Supabase with a real user
 * - NEXT_PUBLIC_ENABLE_EMAIL_LOGIN=true (Playwright webServer sets this)
 * - E2E_EMAIL, E2E_PASSWORD in the environment
 */
const email = process.env.E2E_EMAIL?.trim();
const password = process.env.E2E_PASSWORD;
const canRun = Boolean(email && password);

test.describe('Dashboard QA @regression', () => {
  test.skip(!canRun, 'Set E2E_EMAIL and E2E_PASSWORD (Supabase email/password user)');

  test('email login → home → navigate core routes without hard errors', async ({ page }) => {
    test.setTimeout(180000);
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    const failedResponses: { url: string; status: number }[] = [];
    page.on('response', (res) => {
      const u = res.url();
      if (res.status() >= 500 && u.includes('/api/')) {
        failedResponses.push({ url: u, status: res.status() });
      }
    });

    const t0 = Date.now();

    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    const emailField = page.getByTestId('email-login-email');
    await expect(emailField).toBeVisible({ timeout: 15000 });

    await emailField.fill(email!);
    await page.getByTestId('email-login-password').fill(password!);
    await page.getByTestId('email-login-submit').click();

    await page.waitForURL(/\/(home|onboarding)/, { timeout: 60000 });
    if (page.url().includes('/onboarding')) {
      test.info().annotations.push({
        type: 'note',
        description: 'User landed on /onboarding — complete profile in app; skipping deep nav.',
      });
      expect(Date.now() - t0).toBeLessThan(120000);
      return;
    }

    await expect(page).toHaveURL(/\/home/);
    await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

    const routes = [
      '/calories',
      '/progress',
      '/food-camera',
      '/workouts',
      '/fasting',
      '/body-scan',
      '/beauty-scan',
      '/fashion',
      '/chat',
      '/profile',
      '/profile/notifications',
      '/profile/preferences',
      '/upgrade',
      '/mask-editor',
      '/body-editor',
    ];

    for (const path of routes) {
      const navStart = Date.now();
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      await expect(page).toHaveURL(new RegExp(`${path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
      await expect(page.locator('main')).toBeVisible({ timeout: 20000 });
      expect(Date.now() - navStart, `slow navigation to ${path}`).toBeLessThan(45000);
    }

    const badConsole = consoleErrors.filter(
      (e) =>
        !e.includes('favicon') &&
        !e.includes('DevTools') &&
        !e.includes('ResizeObserver') &&
        !e.includes('data-cursor'),
    );
    expect(badConsole.length, `Console errors:\n${badConsole.join('\n')}`).toBe(0);

    expect(failedResponses.length, JSON.stringify(failedResponses)).toBe(0);

    expect(Date.now() - t0).toBeLessThan(300000);
  });
});

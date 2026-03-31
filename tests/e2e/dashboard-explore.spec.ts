import { test, expect } from '@playwright/test';

/**
 * Logged-in UX smoke: click through desktop sidebar (core + Extras) and open
 * a few routes not in the nav. Safe for CI — no payments, no file uploads.
 *
 * Requires: E2E_EMAIL, E2E_PASSWORD, backend + frontend, viewport ≥ lg (sidebar).
 */
const email = process.env.E2E_EMAIL?.trim();
const password = process.env.E2E_PASSWORD;
const canRun = Boolean(email && password);

test.describe('Dashboard explore (sidebar clicks) @regression', () => {
  test.skip(!canRun, 'Set E2E_EMAIL and E2E_PASSWORD');

  test('login → click core nav → Extras → more routes; main visible', async ({ page }) => {
    test.setTimeout(180000);

    await page.setViewportSize({ width: 1440, height: 900 });

    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.getByTestId('email-login-email')).toBeVisible({ timeout: 15000 });
    await page.getByTestId('email-login-email').fill(email!);
    await page.getByTestId('email-login-password').fill(password!);
    await page.getByTestId('email-login-submit').click();

    await page.waitForURL(/\/(home|onboarding)/, { timeout: 60000 });
    if (page.url().includes('/onboarding')) {
      await page.goto('/home', { waitUntil: 'domcontentloaded' });
      await page.waitForURL(/\/(home|onboarding)/, { timeout: 15000 });
    }
    if (page.url().includes('/onboarding')) {
      test.skip(true, 'Still on /onboarding — set user_profiles.onboarding_completed or finish onboarding');
    }

    await expect(page).toHaveURL(/\/home/);
    const aside = page.locator('aside').first();
    /** Dashboard uses <main>; standalone pages (mask-editor, body-editor) may not — #root-app is always present. */
    const appShell = page.locator('#root-app');

    const navClick = async (href: string) => {
      const link = aside.locator(`a[href="${href}"]`).first();
      await expect(link).toBeVisible({ timeout: 10000 });
      await link.click();
      await expect(page).toHaveURL(new RegExp(`${href.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
      await expect(appShell).toBeVisible({ timeout: 20000 });
    };

    await test.step('Core nav', async () => {
      for (const href of ['/home', '/body-scan', '/chat', '/profile'] as const) {
        await navClick(href);
      }
    });

    await test.step('Extras submenu', async () => {
      const extrasBtn = aside.getByRole('button', { name: /extras/i });
      await extrasBtn.click();
      for (const href of ['/progress', '/calories', '/food-camera', '/workouts', '/fasting'] as const) {
        await navClick(href);
      }
    });

    await test.step('Other dashboard routes (direct)', async () => {
      for (const href of [
        '/upgrade',
        '/beauty-scan',
        '/fashion',
        '/mask-editor',
        '/body-editor',
        '/profile/notifications',
        '/profile/preferences',
      ] as const) {
        await page.goto(href, { waitUntil: 'domcontentloaded' });
        await expect(page).toHaveURL(new RegExp(`${href.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
        await expect(appShell).toBeVisible({ timeout: 20000 });
      }
    });
  });
});

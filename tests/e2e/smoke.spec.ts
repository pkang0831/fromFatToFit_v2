import { test, expect } from '@playwright/test';

test.describe('Smoke Tests @smoke', () => {

  test.describe('Landing Page', () => {
    test('renders all major sections', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveURL('/');

      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('[data-testid="hero-cta"]')).toBeVisible();

      const headings = await page.locator('h2').allTextContents();
      expect(headings.length).toBeGreaterThanOrEqual(5);
    });

    test('has no fatal console errors', async ({ page }) => {
      const errors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') errors.push(msg.text());
      });
      await page.goto('/');
      await page.waitForTimeout(2000);

      const fatalErrors = errors.filter(e =>
        !e.includes('favicon') && !e.includes('DevTools') && !e.includes('data-cursor')
      );
      expect(fatalErrors).toHaveLength(0);
    });

    test('has no 5xx network errors', async ({ page }) => {
      const serverErrors: { url: string; status: number }[] = [];
      page.on('response', res => {
        if (res.status() >= 500) {
          serverErrors.push({ url: res.url(), status: res.status() });
        }
      });
      await page.goto('/');
      await page.waitForTimeout(2000);
      expect(serverErrors).toHaveLength(0);
    });

    test('FAQ accordion opens and closes', async ({ page }) => {
      await page.goto('/');
      await page.waitForTimeout(1500);
      const firstFaq = page.locator('button').filter({ hasText: /photos|사진/i }).first();
      await firstFaq.waitFor({ state: 'attached', timeout: 5000 });
      await firstFaq.scrollIntoViewIfNeeded();
      await firstFaq.click();
      await page.waitForTimeout(500);
      await firstFaq.click();
    });

    test('footer links navigate correctly', async ({ page }) => {
      await page.goto('/');
      await page.waitForTimeout(1500);
      const privacyLink = page.getByRole('link', { name: /privacy policy|개인정보/i }).first();
      await privacyLink.waitFor({ state: 'attached', timeout: 5000 });
      await privacyLink.scrollIntoViewIfNeeded();
      await privacyLink.click();
      await expect(page).toHaveURL('/privacy');
    });
  });

  test.describe('Login Page', () => {
    test('renders login page with Google OAuth', async ({ page }) => {
      await page.goto('/login');
      await expect(page.locator('h1')).toContainText(/Devenira/);
      await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
    });
  });

  test.describe('Register Page', () => {
    test('renders register page with Google OAuth', async ({ page }) => {
      await page.goto('/register');
      await expect(page.locator('h1')).toContainText(/Devenira/);
      await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
    });

    test('has link back to login', async ({ page }) => {
      await page.goto('/register');
      const signInLink = page.getByRole('link', { name: /sign in|로그인/i });
      await expect(signInLink).toBeVisible();
      await signInLink.click();
      await expect(page).toHaveURL('/login');
    });
  });

  test.describe('Legal Pages', () => {
    for (const route of ['/terms', '/privacy', '/disclaimer']) {
      test(`${route} renders content`, async ({ page }) => {
        await page.goto(route);
        await expect(page.locator('h1')).toBeVisible();
        await expect(page.locator('article')).toBeVisible();

        const navLinks = page.locator('header nav a');
        await expect(navLinks).toHaveCount(3);
      });
    }
  });

  test.describe('Language Switching', () => {
    test('switches from English to Korean and back', async ({ page }) => {
      await page.goto('/');
      await page.waitForTimeout(1000);

      const langButton = page.getByRole('button', { name: /change language/i }).first();
      await langButton.scrollIntoViewIfNeeded();
      await langButton.click();

      const koButton = page.getByRole('button', { name: '한국어' });
      await koButton.click();
      await page.waitForTimeout(500);

      await expect(page.locator('h1')).toContainText(/미래 몸/);

      await langButton.scrollIntoViewIfNeeded();
      await langButton.click();
      const enButton = page.getByRole('button', { name: 'English' });
      await enButton.click();
      await page.waitForTimeout(500);

      await expect(page.locator('h1')).toContainText(/Future Body/);
    });
  });

  test.describe('Middleware Protection', () => {
    test('unauthenticated user redirected from /home to /login', async ({ page }) => {
      await page.goto('/home');
      await expect(page).toHaveURL('/login');
    });

    test('unauthenticated user redirected from /calories to /login', async ({ page }) => {
      await page.goto('/calories');
      await expect(page).toHaveURL('/login');
    });

    test('unauthenticated user redirected from /body-scan to /login', async ({ page }) => {
      await page.goto('/body-scan');
      await expect(page).toHaveURL('/login');
    });

    test('unauthenticated user on /fasting eventually redirects to /login', async ({ page }) => {
      await page.goto('/fasting');
      await page.waitForURL('/login', { timeout: 10000 });
      await expect(page).toHaveURL('/login');
    });

    test('unauthenticated user on /chat eventually redirects to /login', async ({ page }) => {
      await page.goto('/chat');
      await page.waitForURL('/login', { timeout: 10000 });
      await expect(page).toHaveURL('/login');
    });
  });
});

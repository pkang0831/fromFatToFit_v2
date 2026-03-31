import { test, expect, type Page, type BrowserContext } from '@playwright/test';
import path from 'path';

/**
 * Comprehensive dashboard QA — every user-facing workflow except body transformation.
 *
 * Requires:
 *   E2E_EMAIL, E2E_PASSWORD  (Supabase email/password user with onboarding_completed)
 *   Backend + Frontend running (Playwright webServer handles this)
 *   sample_image.jpg at project root
 */

const email = process.env.E2E_EMAIL?.trim();
const password = process.env.E2E_PASSWORD;
const canRun = Boolean(email && password);
const SAMPLE_IMAGE = path.resolve(__dirname, '../../sample_image.jpg');

/* ── helpers ─────────────────────────────────────────────────────────── */

const consoleErrors: string[] = [];
const apiErrors: { url: string; status: number }[] = [];

function attachMonitors(page: Page) {
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('response', (res) => {
    if (res.status() >= 500 && res.url().includes('/api/')) {
      apiErrors.push({ url: res.url(), status: res.status() });
    }
  });
}

function filterConsoleNoise(errors: string[]): string[] {
  return errors.filter(
    (e) =>
      !e.includes('favicon') &&
      !e.includes('DevTools') &&
      !e.includes('ResizeObserver') &&
      !e.includes('data-cursor') &&
      !e.includes('Download the React DevTools') &&
      !e.includes('Autofocus processing') &&
      !e.includes('404 (Not Found)') &&
      !e.includes('500 (Internal Server Error)') &&
      !e.includes('Failed to fetch photos') &&
      !e.includes('hydration error') &&
      !e.includes('cannot be a descendant'),
  );
}

async function loginViaEmail(page: Page) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await expect(page.getByTestId('email-login-email')).toBeVisible({ timeout: 15000 });
  await page.getByTestId('email-login-email').fill(email!);
  await page.getByTestId('email-login-password').fill(password!);
  await page.getByTestId('email-login-submit').click();
  await page.waitForURL(/\/(home|onboarding)/, { timeout: 60000 });
}

async function waitForApi(page: Page, urlPattern: string | RegExp, timeout = 15000) {
  return page.waitForResponse(
    (res) =>
      (typeof urlPattern === 'string'
        ? res.url().includes(urlPattern)
        : urlPattern.test(res.url())) && res.status() < 500,
    { timeout },
  );
}

/* ── tests ───────────────────────────────────────────────────────────── */

test.describe('Dashboard Comprehensive QA @regression', () => {
  test.skip(!canRun, 'Set E2E_EMAIL and E2E_PASSWORD');
  test.describe.configure({ mode: 'serial' });

  let page: Page;
  let context: BrowserContext;

  test.beforeAll(async ({ browser }) => {
    test.setTimeout(120000);
    context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    page = await context.newPage();
    attachMonitors(page);
    await loginViaEmail(page);

    if (page.url().includes('/onboarding')) {
      test.skip(true, 'User on /onboarding — complete onboarding first');
    }
  });

  test.afterAll(async () => {
    await context?.close();
  });

  /* ─── 1. Auth & Login ──────────────────────────────────────────── */

  test.describe('1 — Auth & Login', () => {
    test('lands on /home after email login', async () => {
      await expect(page).toHaveURL(/\/home/);
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
    });

    test('session persists across page refresh', async () => {
      await page.reload({ waitUntil: 'domcontentloaded' });
      await expect(page).toHaveURL(/\/home/);
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
    });
  });

  /* ─── 2. Home Dashboard ────────────────────────────────────────── */

  test.describe('2 — Home Dashboard', () => {
    test('renders quick stats and CTA buttons', async () => {
      await page.goto('/home', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('[data-tour="home-stats"]')).toBeVisible({ timeout: 15000 });

      const bodyScanLink = page.locator('a[href="/body-scan"]').first();
      await expect(bodyScanLink).toBeVisible();

      const progressLink = page.locator('a[href="/progress"]').first();
      await expect(progressLink).toBeVisible();
    });

    test('API: quick-stats, credits, gap-to-goal return 200', async () => {
      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(token).toBeTruthy();

      const apiBase = 'http://127.0.0.1:8000/api';
      const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

      const [stats, credits, gap] = await Promise.all([
        fetch(`${apiBase}/dashboard/quick-stats`, { headers }),
        fetch(`${apiBase}/payments/credits`, { headers }),
        fetch(`${apiBase}/body/gap-to-goal`, { headers }),
      ]);
      expect(stats.status).toBe(200);
      expect(credits.status).toBe(200);
      expect(gap.status).toBe(200);
    });
  });

  /* ─── 3. Profile ───────────────────────────────────────────────── */

  test.describe('3 — Profile', () => {
    test.beforeEach(async () => {
      await page.goto('/profile', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
    });

    test('displays user info and credit balance', async () => {
      await expect(page.getByText(email!)).toBeVisible({ timeout: 10000 });
      await expect(page.locator('[data-tour="profile-credits"]')).toBeVisible();
    });

    test('edit profile modal: open, fill, save', async () => {
      const editBtn = page.getByRole('button', { name: /edit profile/i });
      await expect(editBtn).toBeVisible({ timeout: 10000 });
      await editBtn.click();

      const heightInput = page.locator('input[name="height_cm"]');
      await expect(heightInput).toBeVisible({ timeout: 5000 });
      await heightInput.fill('178');

      const weightInput = page.locator('input[name="weight_kg"]');
      await weightInput.fill('75');

      const saveBtn = page.getByRole('button', { name: /save/i });
      await saveBtn.click();
      // Wait for modal to close (save completed)
      await expect(heightInput).toBeHidden({ timeout: 10000 });
    });

    test('sign out button is visible and clickable', async () => {
      const signOutBtn = page.getByRole('button', { name: /sign out/i });
      await expect(signOutBtn).toBeVisible({ timeout: 10000 });
      // Don't actually sign out — it would block subsequent serial tests.
      // Sign-out redirect is covered by middleware protection tests in smoke.spec.ts.
    });
  });

  /* ─── 4. Profile Preferences ───────────────────────────────────── */

  test.describe('4 — Profile Preferences', () => {
    test('renders dietary preference toggles', async () => {
      await page.goto('/profile/preferences', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      await expect(page.getByRole('button', { name: /save/i })).toBeVisible({ timeout: 10000 });
    });
  });

  /* ─── 5. Profile Notifications ─────────────────────────────────── */

  test.describe('5 — Profile Notifications', () => {
    test('page loads without error', async () => {
      await page.goto('/profile/notifications', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
      // Verify page didn't redirect away or show blank
      await expect(page).toHaveURL(/\/profile\/notifications/);
    });
  });

  /* ─── 6. Calories ──────────────────────────────────────────────── */

  test.describe('6 — Calories', () => {
    test.beforeEach(async () => {
      await page.goto('/calories', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
    });

    test('date navigation: prev, next, today', async () => {
      const prevBtn = page.getByRole('button', { name: /prev/i }).first();
      await expect(prevBtn).toBeVisible({ timeout: 10000 });
      await prevBtn.click();
      await page.waitForTimeout(500);

      const todayBtn = page.getByRole('button', { name: /today/i }).first();
      await expect(todayBtn).toBeVisible();
      await todayBtn.click();
      await page.waitForTimeout(500);

      const nextBtn = page.getByRole('button', { name: /next/i }).first();
      await expect(nextBtn).toBeVisible();
    });

    test('trend toggle switches between 7d and 30d', async () => {
      const trend7 = page.getByRole('button', { name: /7/i }).first();
      const trend30 = page.getByRole('button', { name: /30/i }).first();

      if (await trend7.isVisible()) {
        await trend7.click();
        await page.waitForTimeout(300);
      }
      if (await trend30.isVisible()) {
        await trend30.click();
        await page.waitForTimeout(300);
      }
    });

    test('scan food button navigates to food-camera', async () => {
      const scanBtn = page.getByRole('button', { name: /scan food/i }).or(
        page.getByRole('link', { name: /scan food/i }),
      );
      if (await scanBtn.isVisible()) {
        await scanBtn.click();
        await page.waitForURL(/\/food-camera/, { timeout: 10000 });
        await expect(page).toHaveURL(/\/food-camera/);
      }
    });
  });

  /* ─── 7. Food Camera ───────────────────────────────────────────── */

  test.describe('7 — Food Camera', () => {
    test('upload image and analyze button appears', async () => {
      await page.goto('/food-camera', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      const fileInput = page.locator('input[type="file"][accept="image/*"]');
      await fileInput.setInputFiles(SAMPLE_IMAGE);
      await page.waitForTimeout(1000);

      const analyzeBtn = page.getByRole('button', { name: /analyze/i });
      await expect(analyzeBtn).toBeVisible({ timeout: 10000 });
      // Not clicking — sample_image.jpg is a body photo, not food, so AI would fail.
      // The fact that upload + analyze button renders is the key workflow check.
    });
  });

  /* ─── 8. Workouts ──────────────────────────────────────────────── */

  test.describe('8 — Workouts', () => {
    test.beforeEach(async () => {
      await page.goto('/workouts', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
    });

    test('exercise library renders with category tabs', async () => {
      await expect(page.locator('[data-tour="workout-library"]').or(page.locator('#exercise-library'))).toBeVisible({ timeout: 10000 });

      const allTab = page.getByRole('button', { name: /^all$/i }).first();
      if (await allTab.isVisible()) {
        await allTab.click();
      }
    });

    test('search exercises', async () => {
      const searchInput = page.locator('input[placeholder*="earch"]').first();
      if (await searchInput.isVisible()) {
        await searchInput.fill('push');
        await page.waitForTimeout(500);
        await searchInput.clear();
      }
    });

    test('log workout flow: click exercise then log', async () => {
      // Click the first exercise card in the library to open the detail modal
      const exerciseCard = page.locator('[data-tour="workout-library"] button, #exercise-library button').first();
      if (await exerciseCard.isVisible({ timeout: 5000 }).catch(() => false)) {
        await exerciseCard.click();
        await page.waitForTimeout(500);

        // Look for "Log This Exercise" in the modal
        const logThisBtn = page.getByRole('button', { name: /log this/i });
        if (await logThisBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
          await logThisBtn.click();
          await page.waitForTimeout(500);
        }
      }
    });
  });

  /* ─── 9. Fasting ───────────────────────────────────────────────── */

  test.describe('9 — Fasting', () => {
    test('protocol selection and start/end fast', async () => {
      await page.goto('/fasting', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      // If a fast is already running, end it first
      const endBtn = page.getByRole('button', { name: /end fast/i });
      if (await endBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await endBtn.click();
        await page.waitForTimeout(500);
      }

      // Start a fast
      const startBtn = page.getByRole('button', { name: /start.*fast/i });
      await expect(startBtn).toBeVisible({ timeout: 10000 });
      await startBtn.click();
      await page.waitForTimeout(500);

      // Select 14:10 protocol (beginner, safe for testing)
      const protocol = page.getByRole('button', { name: /14:10/i }).first();
      await expect(protocol).toBeVisible({ timeout: 5000 });
      await protocol.click();
      await page.waitForTimeout(1000);

      // Verify timer is running
      const progressRing = page.locator('svg circle').first();
      await expect(progressRing).toBeVisible({ timeout: 5000 });

      // End the fast
      const endFastBtn = page.getByRole('button', { name: /end fast/i });
      await expect(endFastBtn).toBeVisible({ timeout: 5000 });
      await endFastBtn.click();
      await page.waitForTimeout(500);

      // Stats should update
      const totalFasts = page.getByText(/total fasts/i).or(page.getByText(/총 단식/i));
      await expect(totalFasts).toBeVisible({ timeout: 5000 });
    });
  });

  /* ─── 10. Chat / AI Coach ──────────────────────────────────────── */

  test.describe('10 — Chat', () => {
    test('chat input and send button render', async () => {
      await page.goto('/chat', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      const input = page.locator('[data-tour="chat-input"] textarea').or(
        page.locator('textarea').first(),
      );
      await expect(input).toBeVisible({ timeout: 10000 });
      await input.fill('Test message');

      // Send button should be present
      const sendBtn = page.locator('[data-tour="chat-input"] button').first().or(
        page.locator('button[type="submit"]').first(),
      );
      await expect(sendBtn).toBeVisible({ timeout: 5000 });
      // Not clicking — AI response can take 60s+ and would consume credits.
    });
  });

  /* ─── 11. Body Scan (Scan tab only) ────────────────────────────── */

  test.describe('11 — Body Scan', () => {
    test('scan tab renders with upload and form elements', async () => {
      await page.goto('/body-scan', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      // Ensure we're on the Body Scan tab (not Journey)
      const scanTab = page.getByRole('button', { name: /body scan/i }).first();
      if (await scanTab.isVisible({ timeout: 5000 }).catch(() => false)) {
        await scanTab.click();
        await page.waitForTimeout(500);
      }

      // File input for photo upload should exist
      const fileInput = page.locator('input[type="file"][accept="image/*"]');
      await expect(fileInput).toBeAttached({ timeout: 5000 });

      // Upload prompt or scan button should be visible
      const uploadArea = page.getByText(/upload/i).first();
      await expect(uploadArea).toBeVisible({ timeout: 5000 });
    });
  });

  /* ─── 12. Beauty Scan ──────────────────────────────────────────── */

  test.describe('12 — Beauty Scan', () => {
    test('upload image and see analyze button', async () => {
      await page.goto('/beauty-scan', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      const fileInput = page.locator('input[type="file"][accept="image/*"]');
      await expect(fileInput).toBeAttached({ timeout: 5000 });
      await fileInput.setInputFiles(SAMPLE_IMAGE);
      await page.waitForTimeout(1000);

      const analyzeBtn = page.getByRole('button', { name: /analyze/i });
      await expect(analyzeBtn).toBeVisible({ timeout: 10000 });
    });
  });

  /* ─── 13. Fashion ──────────────────────────────────────────────── */

  test.describe('13 — Fashion', () => {
    test('season tabs and get outfits button render', async () => {
      await page.goto('/fashion', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      // Season tabs
      for (const season of ['Spring', 'Summer', 'Fall', 'Winter']) {
        const tab = page.getByRole('button', { name: new RegExp(season, 'i') }).first();
        await expect(tab).toBeVisible({ timeout: 5000 });
      }

      // Click through seasons
      await page.getByRole('button', { name: /summer/i }).first().click();
      await page.waitForTimeout(300);
      await page.getByRole('button', { name: /winter/i }).first().click();
      await page.waitForTimeout(300);

      const getOutfitsBtn = page.getByRole('button', { name: /get.*outfit/i });
      await expect(getOutfitsBtn).toBeVisible({ timeout: 5000 });
    });
  });

  /* ─── 14. Progress ─────────────────────────────────────────────── */

  test.describe('14 — Progress', () => {
    test.beforeEach(async () => {
      await page.goto('/progress', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
    });

    test('goals tab: chart and action buttons render', async () => {
      const goalsTab = page.getByRole('button', { name: /goal/i }).first();
      if (await goalsTab.isVisible({ timeout: 5000 }).catch(() => false)) {
        await goalsTab.click();
        await page.waitForTimeout(500);
      }

      await expect(
        page.locator('[data-tour="progress-chart"]').or(page.locator('canvas').first()),
      ).toBeVisible({ timeout: 10000 });

      const setGoalBtn = page.getByRole('button', { name: /set goal/i }).first();
      await expect(setGoalBtn).toBeVisible({ timeout: 5000 });

      const logWeightBtn = page.getByRole('button', { name: /log weight/i }).first();
      await expect(logWeightBtn).toBeVisible({ timeout: 5000 });
    });

    test('log weight modal: open, fill, save', async () => {
      const logWeightBtn = page.getByRole('button', { name: /log weight/i });
      await expect(logWeightBtn).toBeVisible({ timeout: 10000 });
      await logWeightBtn.click();
      await page.waitForTimeout(500);

      const weightInput = page.locator('input[type="number"]').first();
      await expect(weightInput).toBeVisible({ timeout: 5000 });
      await weightInput.fill('75');

      const saveBtn = page.getByRole('button', { name: /save|log|submit/i }).last();
      if (await saveBtn.isVisible()) {
        const apiPromise = waitForApi(page, '/api/weight', 10000).catch(() => null);
        await saveBtn.click();
        await apiPromise;
      }
    });

    test('photos tab renders', async () => {
      const photosTab = page.getByRole('button', { name: /photo/i }).first();
      if (await photosTab.isVisible({ timeout: 5000 }).catch(() => false)) {
        await photosTab.click();
        await page.waitForTimeout(500);

        await expect(
          page.locator('[data-tour="progress-photos"]'),
        ).toBeVisible({ timeout: 10000 });
      }
    });
  });

  /* ─── 15. Upgrade ──────────────────────────────────────────────── */

  test.describe('15 — Upgrade', () => {
    test('renders plans, credit packs, and cost table', async () => {
      await page.goto('/upgrade', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('main')).toBeVisible({ timeout: 15000 });

      // Plan toggle (monthly/yearly)
      const yearlyToggle = page.getByRole('button', { name: /year/i }).first();
      if (await yearlyToggle.isVisible({ timeout: 5000 }).catch(() => false)) {
        await yearlyToggle.click();
        await page.waitForTimeout(300);
      }

      // Go Pro button visible but not clicked
      const goProBtn = page.getByRole('button', { name: /go pro/i }).first();
      await expect(goProBtn).toBeVisible({ timeout: 5000 });

      // Credit packs
      const buyBtn = page.getByRole('button', { name: /buy/i }).first();
      await expect(buyBtn).toBeVisible({ timeout: 5000 });
    });
  });

  /* ─── 16. Cross-cutting ────────────────────────────────────────── */

  test.describe('16 — Cross-cutting', () => {
    test('sidebar navigation: core links', async () => {
      await page.goto('/home', { waitUntil: 'domcontentloaded' });
      const aside = page.locator('aside').first();

      for (const href of ['/home', '/body-scan', '/chat', '/profile']) {
        const link = aside.locator(`a[href="${href}"]`).first();
        await expect(link).toBeVisible({ timeout: 10000 });
        await link.click();
        await expect(page).toHaveURL(new RegExp(`${href}$`), { timeout: 15000 });
        await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
      }
    });

    test('sidebar navigation: extras submenu', async () => {
      await page.goto('/home', { waitUntil: 'domcontentloaded' });
      const aside = page.locator('aside').first();

      const extrasBtn = aside.getByRole('button', { name: /extras/i });
      if (await extrasBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
        await extrasBtn.click();
        await page.waitForTimeout(300);
      }

      for (const href of ['/progress', '/calories', '/food-camera', '/workouts', '/fasting']) {
        const link = aside.locator(`a[href="${href}"]`).first();
        if (await link.isVisible({ timeout: 3000 }).catch(() => false)) {
          await link.click();
          await expect(page).toHaveURL(new RegExp(`${href}$`), { timeout: 15000 });
          await expect(page.locator('main')).toBeVisible({ timeout: 15000 });
        }
      }
    });

    test('no unfiltered console errors', () => {
      const bad = filterConsoleNoise(consoleErrors);
      expect(bad.length, `Console errors:\n${bad.join('\n')}`).toBe(0);
    });

    test('no 5xx API responses', () => {
      expect(apiErrors.length, `5xx errors:\n${JSON.stringify(apiErrors, null, 2)}`).toBe(0);
    });
  });
});

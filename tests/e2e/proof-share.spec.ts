import { test, expect, type APIRequestContext, type Page, type Route } from '@playwright/test';

const BACKEND_URL = 'http://127.0.0.1:8000/api';
const FRONTEND_URL = 'http://127.0.0.1:3000';
const DATA_URL =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn4m0QAAAAASUVORK5CYII=';
const TINY_PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn4m0QAAAAASUVORK5CYII=',
  'base64',
);

async function bootstrapAuthenticatedSession(page: Page, request: APIRequestContext) {
  const res = await request.post(`${BACKEND_URL}/auth/test-login`);
  expect(res.status()).toBe(200);

  const body = await res.json();
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

function json(route: Route, data: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(data),
  });
}

async function mockAuthenticatedShell(page: Page) {
  await page.route('**/api/auth/me', (route) =>
    json(route, {
      id: 'user-e2e',
      email: 'e2e@devenira.test',
      full_name: 'Devenira E2E',
      gender: 'male',
      age: 30,
      height_cm: 180,
      weight_kg: 82,
      activity_level: 'moderate',
      premium_status: true,
      onboarding_completed: true,
      created_at: '2026-03-01T12:00:00+00:00',
    }),
  );

  await page.route('**/api/payments/usage-limits', (route) =>
    json(route, {
      is_premium: true,
      limits: {
        food_scan: { current_count: 0, limit: -1, remaining: -1, is_premium: true },
        body_fat_scan: { current_count: 0, limit: -1, remaining: -1, is_premium: true },
        percentile_scan: { current_count: 0, limit: -1, remaining: -1, is_premium: true },
        form_check: { current_count: 0, limit: -1, remaining: -1, is_premium: true },
        transformation: { current_count: 0, limit: -1, remaining: -1, is_premium: true },
        enhancement: { current_count: 0, limit: -1, remaining: -1, is_premium: true },
      },
    }),
  );

  await page.route('**/api/payments/credits', (route) =>
    json(route, { total_credits: 120 }),
  );
}

test.describe('Public-safe proof share @regression', () => {
  test('renders an anonymous public share without exposing private URLs', async ({ page }) => {
    await page.route('**/api/proof-shares/public/public-token*', (route) =>
      json(route, {
        token: 'public-token',
        public_url: 'http://127.0.0.1:3000/proof/public-token',
        image_url: `${BACKEND_URL}/proof-shares/public/public-token/image`,
        referred_try_url: `${BACKEND_URL}/proof-shares/public/public-token/try`,
        week_marker: 6,
        goal_summary: {
          current_bf: 18.4,
          target_bf: 14.0,
          gap: 4.4,
        },
        photo_summary: {
          progress_photo_id: 'photo-1',
          taken_at: '2026-03-31T12:00:00+00:00',
          weight_kg: 81.2,
          body_fat_pct: 18.1,
        },
      }),
    );
    await page.route('**/api/proof-shares/public/public-token/image', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'image/png',
        body: TINY_PNG,
      }),
    );

    await page.goto('/proof/public-token', { waitUntil: 'domcontentloaded' });

    await expect(page.getByText('Public-safe proof card')).toBeVisible();
    await expect(page.getByTestId('public-proof-share-image')).toBeVisible();
    await expect(page.getByTestId('proof-share-try-link')).toHaveAttribute(
      'href',
      /\/proof-shares\/public\/public-token\/try\?session_id=/,
    );
    await expect(page.locator('body')).not.toContainText('signed.example');
  });

  test('denies anonymous access for revoked shares', async ({ page }) => {
    await page.route('**/api/proof-shares/public/revoked-token*', (route) =>
      json(route, { detail: 'Share not found' }, 404),
    );

    await page.goto('/proof/revoked-token', { waitUntil: 'domcontentloaded' });

    await expect(page.getByText('This proof card is no longer public.')).toBeVisible();
  });

  test('creates and revokes a public proof card from progress surface', async ({ page, request }) => {
    await bootstrapAuthenticatedSession(page, request);
    await mockAuthenticatedShell(page);

    let shares = [] as Array<{
      id: string;
      token: string;
      progress_photo_id: string;
      week_marker: number | null;
      status: 'active' | 'revoked';
      created_at: string;
      revoked_at: string | null;
      public_url: string;
      image_url: string;
      referred_try_url: string;
      goal_summary: { current_bf: number | null; target_bf: number | null; gap: number | null };
      photo_summary: { progress_photo_id: string; taken_at: string | null; weight_kg: number | null; body_fat_pct: number | null };
    }>;

    await page.route('**/api/home/summary', (route) =>
      json(route, {
        entry_state: 'progress_proof',
        reentry_state: 'progress_proof',
        surface_state: 'progress_proof',
        goal_summary: {
          has_saved_plan: true,
          plan_updated_at: '2026-03-28T12:00:00+00:00',
          current_bf: 18.4,
          target_bf: 14.0,
          goal_image_url: null,
          gap: 4.4,
          selected_tier_calories: 2100,
        },
        scan_summary: {
          scan_count: 3,
          last_scan_date: '2026-03-30T12:00:00+00:00',
          prompt_state: 'too_early',
          latest_transformation: {
            id: 'transform-1',
            date: '2026-03-29T12:00:00+00:00',
            result_summary: 'Transformation: -4%',
            image_url: DATA_URL,
          },
          next_check_in_label: '5 days',
        },
        challenge_summary: {
          is_active: false,
          checked_in_today: false,
          day_index: null,
        },
        progress_summary: {
          photo_count: 1,
          latest_photo_date: '2026-03-31T12:00:00+00:00',
          compare_ready: false,
        },
        primary_cta: {
          state: 'progress_proof',
          href: '/progress?tab=photos&focus=upload&from=home_progress_proof',
          label: 'Upload progress proof',
          title: 'You have data, but no proof yet',
          description: 'Add a progress photo so this is not just a scan result.',
        },
      }),
    );

    await page.route('**/api/progress-photos', (route) =>
      json(route, [
        {
          id: 'photo-1',
          notes: 'Week 1',
          weight_kg: 81.2,
          body_fat_pct: 18.1,
          taken_at: '2026-03-31T12:00:00+00:00',
          created_at: '2026-03-31T12:00:00+00:00',
          image_url: DATA_URL,
        },
      ]),
    );

    await page.route('**/api/proof-shares**', async (route) => {
      if (route.request().method() === 'GET') {
        return json(route, shares);
      }

      const payload = route.request().postDataJSON() as { progress_photo_id: string; week_marker?: number; session_id?: string };
      const created = {
        id: 'share-1',
        token: 'public-token',
        progress_photo_id: payload.progress_photo_id,
        week_marker: payload.week_marker ?? null,
        status: 'active' as const,
        created_at: '2026-03-31T12:30:00+00:00',
        revoked_at: null,
        public_url: `${FRONTEND_URL}/proof/public-token`,
        image_url: `${BACKEND_URL}/proof-shares/public/public-token/image`,
        referred_try_url: `${BACKEND_URL}/proof-shares/public/public-token/try`,
        goal_summary: { current_bf: 18.4, target_bf: 14.0, gap: 4.4 },
        photo_summary: {
          progress_photo_id: payload.progress_photo_id,
          taken_at: '2026-03-31T12:00:00+00:00',
          weight_kg: 81.2,
          body_fat_pct: 18.1,
        },
      };
      shares = [created];
      return json(route, created);
    });

    await page.route('**/api/proof-shares/share-1', async (route) => {
      shares = shares.map((share) =>
        share.id === 'share-1'
          ? { ...share, status: 'revoked', revoked_at: '2026-03-31T12:45:00+00:00' }
          : share,
      );
      return json(route, { message: 'Share revoked' });
    });

    page.on('dialog', dialog => dialog.accept());

    await page.goto('/progress?tab=photos', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('open-proof-share-modal').click();
    await page.getByTestId('proof-share-week-marker-input').fill('6');
    await page.getByTestId('create-proof-share-button').click();

    await expect(page.getByTestId('proof-share-public-url')).toContainText('/proof/public-token');

    await page.getByRole('button', { name: 'Revoke' }).click();
    await expect(page.getByTestId('open-proof-share-modal')).toBeVisible();
  });
});

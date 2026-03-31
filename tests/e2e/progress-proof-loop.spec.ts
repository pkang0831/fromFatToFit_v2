import { test, expect, type APIRequestContext, type Page, type Route } from '@playwright/test';

const BACKEND_URL = 'http://127.0.0.1:8000/api';
const FRONTEND_URL = 'http://127.0.0.1:3000';
const TINY_PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn4m0QAAAAASUVORK5CYII=',
  'base64',
);
const DATA_URL =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn4m0QAAAAASUVORK5CYII=';

type ProgressPhoto = {
  id: string;
  notes: string;
  weight_kg: number | null;
  body_fat_pct: number | null;
  taken_at: string;
  created_at: string;
  image_url: string;
};

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

function json(route: Route, data: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(data),
  });
}

function buildHomeSummary(photoCount: number) {
  const compareReady = photoCount >= 2;
  const latestPhotoDate = photoCount > 0 ? '2026-03-31T12:00:00+00:00' : null;

  return {
    entry_state: compareReady ? 'review_progress' : 'progress_proof',
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
      prompt_state: compareReady ? 'ready' : 'too_early',
      latest_transformation: {
        id: 'transform-1',
        date: '2026-03-29T12:00:00+00:00',
        result_summary: 'Transformation: -4%',
        image_url: DATA_URL,
      },
      next_check_in_label: compareReady ? 'Now' : '5 days',
    },
    challenge_summary: {
      is_active: false,
      checked_in_today: false,
      day_index: null,
    },
    progress_summary: {
      photo_count: photoCount,
      latest_photo_date: latestPhotoDate,
      compare_ready: compareReady,
    },
    primary_cta: compareReady
      ? {
          state: 'review_progress',
          href: '/progress?tab=photos&focus=compare&from=home_review_progress',
          label: 'Review your proof',
          title: 'Your proof loop is active',
          description: 'Review the evidence before your next check-in.',
        }
      : {
          state: 'progress_proof',
          href: '/progress?tab=photos&focus=upload&from=home_progress_proof',
          label: 'Upload progress proof',
          title: 'You have data, but no proof yet',
          description: 'Add a progress photo so this is not just a scan result.',
        },
  };
}

async function mockAuthenticatedShell(page: Page) {
  await page.route('**/api/auth/me', (route) =>
    json(route, {
      id: 'user-e2e',
      email: 'e2e@denevira.test',
      full_name: 'Denevira E2E',
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

async function mockProgressLoopApis(page: Page, initialPhotos: ProgressPhoto[], analyticsEvents?: string[]) {
  let photos = [...initialPhotos];

  await page.route('**/api/home/summary', (route) =>
    json(route, buildHomeSummary(photos.length)),
  );

  await page.route('**/api/analytics/retention', async (route) => {
    if (analyticsEvents) {
      const payload = route.request().postDataJSON() as { event_name?: string };
      if (payload.event_name) analyticsEvents.push(payload.event_name);
    }
    return json(route, { status: 'ok' });
  });

  await page.route('**/api/progress-photos/compare/**', (route) => {
    const path = new URL(route.request().url()).pathname;
    const [, ids] = path.split('/compare/');
    const [beforeId, afterId] = ids.split('/');
    const selected = photos
      .filter((photo) => photo.id === beforeId || photo.id === afterId)
      .sort((a, b) => new Date(a.taken_at).getTime() - new Date(b.taken_at).getTime());

    if (selected.length < 2) {
      return json(route, { detail: 'One or both photos not found' }, 404);
    }

    return json(route, {
      before: selected[0],
      after: selected[1],
      days_between: Math.round(
        (new Date(selected[1].taken_at).getTime() - new Date(selected[0].taken_at).getTime()) / (1000 * 60 * 60 * 24),
      ),
      weight_change:
        selected[0].weight_kg != null && selected[1].weight_kg != null
          ? Number((selected[1].weight_kg - selected[0].weight_kg).toFixed(1))
          : null,
      bf_change:
        selected[0].body_fat_pct != null && selected[1].body_fat_pct != null
          ? Number((selected[1].body_fat_pct - selected[0].body_fat_pct).toFixed(1))
          : null,
    });
  });

  await page.route('**/api/progress-photos', async (route) => {
    if (route.request().method() === 'GET') {
      return json(route, photos);
    }

    const body = route.request().postDataJSON() as {
      notes?: string;
      weight_kg?: number;
      body_fat_pct?: number;
    };
    const newPhoto: ProgressPhoto = {
      id: `photo-${photos.length + 1}`,
      notes: body.notes || '',
      weight_kg: body.weight_kg ?? null,
      body_fat_pct: body.body_fat_pct ?? null,
      taken_at: '2026-03-31T12:00:00+00:00',
      created_at: '2026-03-31T12:00:00+00:00',
      image_url: DATA_URL,
    };
    photos = [newPhoto, ...photos];
    return json(route, newPhoto);
  });
}

test.describe('Progress Proof Loop @regression', () => {
  test('offers a proof-upload CTA after a successful scan', async ({ page, request }) => {
    await bootstrapAuthenticatedSession(page, request);
    await mockAuthenticatedShell(page);
    await mockProgressLoopApis(page, []);

    await page.route('**/api/body/gap-to-goal', (route) =>
      json(route, {
        current_bf: 18.4,
        target_bf: 14.0,
        goal_image_url: null,
        gap: 4.4,
        scan_count: 3,
        last_scan_date: '2026-03-30T12:00:00+00:00',
        scan_history: [
          { date: '2026-03-16T12:00:00+00:00', bf: 20.1 },
          { date: '2026-03-23T12:00:00+00:00', bf: 19.2 },
          { date: '2026-03-30T12:00:00+00:00', bf: 18.4 },
        ],
      }),
    );
    await page.route('**/api/body/validate-photo', (route) =>
      json(route, { ok: true, messages: [], failure_codes: [] }),
    );
    await page.route('**/api/body/percentile', (route) =>
      json(route, {
        percentile_data: {
          percentile: 72,
          rank_text: 'Above average',
          comparison_group: 'Men 25-34',
          body_fat_percentage: 18.4,
        },
        distribution_data: {
          mean: 20.1,
          std: 3.2,
          user_value: 18.4,
          better_than_percent: 72,
        },
        scan_id: 'scan-1',
        usage_remaining: 99,
      }),
    );

    await page.goto('/body-scan?tab=scan', { waitUntil: 'domcontentloaded' });
    await page.locator('input[type="file"]').first().setInputFiles({
      name: 'scan.png',
      mimeType: 'image/png',
      buffer: TINY_PNG,
    });
    await page.locator('select[name="gender"]').selectOption('male');
    await page.locator('input[name="age"]').fill('30');
    await page.locator('#scanConfirm').check();
    await page.locator('form').getByRole('button', { name: /scan/i }).click();

    await expect(page.getByTestId('scan-to-proof-cta')).toBeVisible();
    await page.getByTestId('scan-to-proof-cta').click();

    await expect(page).toHaveURL(/\/progress\?tab=photos&focus=upload&from=scan_result/);
    await expect(page.getByTestId('progress-upload-modal')).toBeVisible();
  });

  test('renders the empty proof branch honestly when no progress photos exist', async ({ page, request }) => {
    await bootstrapAuthenticatedSession(page, request);
    await mockAuthenticatedShell(page);
    await mockProgressLoopApis(page, []);

    await page.goto('/progress?tab=photos', { waitUntil: 'domcontentloaded' });

    await expect(page.getByTestId('progress-proof-branch-empty')).toBeVisible();
    await expect(page.getByTestId('progress-proof-primary-action')).toContainText(/upload progress proof/i);
    await expect(page.getByTestId('progress-proof-loop')).toHaveAttribute('data-proof-branch', 'empty');
    await expect(page.getByTestId('progress-compare-surface')).toHaveCount(0);
  });

  test('renders the single-proof branch before compare is available', async ({ page, request }) => {
    await bootstrapAuthenticatedSession(page, request);
    await mockAuthenticatedShell(page);
    await mockProgressLoopApis(page, [
      {
        id: 'photo-1',
        notes: 'Week 1',
        weight_kg: 82.1,
        body_fat_pct: 19.8,
        taken_at: '2026-03-24T12:00:00+00:00',
        created_at: '2026-03-24T12:00:00+00:00',
        image_url: DATA_URL,
      },
    ]);

    await page.goto('/progress?tab=photos', { waitUntil: 'domcontentloaded' });

    await expect(page.getByTestId('progress-proof-branch-single')).toBeVisible();
    await expect(page.getByTestId('progress-proof-primary-action')).toContainText(/upload next proof/i);
    await expect(page.getByTestId('progress-proof-loop')).toHaveAttribute('data-proof-branch', 'single');
    await expect(page.getByTestId('progress-compare-surface')).toHaveCount(0);
  });

  test('uploads proof, renders compare, and fires retention analytics', async ({ page, request }) => {
    const analyticsEvents: string[] = [];

    await bootstrapAuthenticatedSession(page, request);
    await mockAuthenticatedShell(page);
    await mockProgressLoopApis(
      page,
      [
        {
          id: 'photo-1',
          notes: 'Week 1',
          weight_kg: 82.1,
          body_fat_pct: 19.8,
          taken_at: '2026-03-24T12:00:00+00:00',
          created_at: '2026-03-24T12:00:00+00:00',
          image_url: DATA_URL,
        },
      ],
      analyticsEvents,
    );

    await page.goto('/progress?tab=photos&focus=upload&from=test_progress_loop', { waitUntil: 'domcontentloaded' });

    await expect(page.getByTestId('progress-upload-modal')).toBeVisible();
    await page.locator('[data-testid="progress-upload-modal"] input[type="file"]').setInputFiles({
      name: 'proof.png',
      mimeType: 'image/png',
      buffer: TINY_PNG,
    });
    await page.locator('[data-testid="progress-upload-modal"] input[placeholder="e.g. 75.5"]').fill('80.4');
    await page.locator('[data-testid="progress-upload-modal"] input[placeholder="e.g. 18.5"]').fill('18.2');
    await page.locator('[data-testid="progress-upload-modal"] textarea').fill('Week 2 proof');
    await page.getByRole('button', { name: /^upload$/i }).click();

    await expect(page.getByTestId('progress-proof-branch-compare')).toBeVisible();
    await expect(page.getByTestId('progress-compare-surface')).toBeVisible();
    await expect(page.getByText(/elapsed/i)).toBeVisible();
    await expect(page.getByTestId('progress-compare-surface').getByText(/next recommended action/i)).toBeVisible();

    await expect.poll(() => analyticsEvents).toEqual(
      expect.arrayContaining([
        'history_viewed',
        'progress_proof_started',
        'progress_proof_completed',
        'progress_compare_viewed',
      ]),
    );
  });
});

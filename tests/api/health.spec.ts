import { test, expect } from '@playwright/test';

test.describe('API Tests @api', () => {

  test.describe('Health & Root', () => {
    test('GET /health returns 200 with valid schema', async ({ request }) => {
      const res = await request.get('/health');
      expect(res.status()).toBe(200);
      const body = await res.json();
      expect(body).toHaveProperty('status');
      expect(body).toHaveProperty('version');
      expect(body.status).toBe('healthy');
    });

    test('GET / returns 200', async ({ request }) => {
      const res = await request.get('/');
      expect(res.status()).toBe(200);
    });
  });

  test.describe('Auth Endpoints', () => {
    test('GET /api/auth/me without token returns 401', async ({ request }) => {
      const res = await request.get('/api/auth/me');
      expect(res.status()).toBe(401);
    });

    test('POST /api/auth/register with missing consent returns 400', async ({ request }) => {
      const res = await request.post('/api/auth/register', {
        data: {
          email: 'qa-noconsent@test.com',
          password: 'TestPass123!',
          consent_terms: false,
          consent_privacy: false,
          consent_sensitive_data: false,
          consent_age_verification: false,
        },
      });
      expect(res.status()).toBe(400);
      const body = await res.json();
      expect(body.detail).toContain('consent');
    });

    test('POST /api/auth/register with age < 18 returns 400', async ({ request }) => {
      const res = await request.post('/api/auth/register', {
        data: {
          email: 'qa-underage@test.com',
          password: 'TestPass123!',
          age: 15,
          consent_terms: true,
          consent_privacy: true,
          consent_sensitive_data: true,
          consent_age_verification: true,
        },
      });
      expect(res.status()).toBe(400);
      const body = await res.json();
      expect(body.detail).toContain('18');
    });

    test('POST /api/auth/login with invalid credentials returns 401', async ({ request }) => {
      const res = await request.post('/api/auth/login', {
        data: {
          email: 'nonexistent@test.com',
          password: 'WrongPassword123!',
        },
      });
      expect(res.status()).toBe(401);
    });
  });

  test.describe('Protected Endpoints — Unauthenticated Access', () => {
    const protectedEndpoints = [
      { method: 'GET', path: '/api/dashboard/quick-stats' },
      { method: 'GET', path: '/api/food/daily/2026-01-01' },
      { method: 'GET', path: '/api/food/trends' },
      { method: 'GET', path: '/api/food/recent' },
      { method: 'GET', path: '/api/workout/exercises/library' },
      { method: 'GET', path: '/api/workout/trends' },
      { method: 'GET', path: '/api/body/scans/history' },
      { method: 'GET', path: '/api/payments/subscription' },
      { method: 'GET', path: '/api/payments/usage-limits' },
      { method: 'GET', path: '/api/payments/credits' },
      { method: 'GET', path: '/api/weight/logs' },
      { method: 'GET', path: '/api/weight/projection' },
      { method: 'GET', path: '/api/chat/status' },
      { method: 'GET', path: '/api/chat/history' },
      { method: 'GET', path: '/api/notifications/preferences' },
      { method: 'GET', path: '/api/dashboard/calorie-balance-trend' },
    ];

    for (const endpoint of protectedEndpoints) {
      test(`${endpoint.method} ${endpoint.path} returns 401`, async ({ request }) => {
        const res = await request.get(endpoint.path);
        expect(res.status()).toBe(401);
      });
    }
  });

  test.describe('Public Endpoints', () => {
    test('GET /api/food-database/search returns valid response', async ({ request }) => {
      const res = await request.get('/api/food-database/search?q=chicken&limit=5');
      expect(res.status()).toBe(200);
      const body = await res.json();
      expect(body).toHaveProperty('results');
      expect(body).toHaveProperty('count');
      expect(Array.isArray(body.results)).toBe(true);

      if (body.results.length > 0) {
        const firstResult = body.results[0];
        expect(firstResult).toHaveProperty('id');
        expect(firstResult).toHaveProperty('name');
        expect(firstResult).toHaveProperty('nutrition_per_100g');
        expect(firstResult.nutrition_per_100g).toHaveProperty('calories');
        expect(firstResult.nutrition_per_100g).toHaveProperty('protein');
      }
    });

    test('GET /api/food-database/categories returns categories', async ({ request }) => {
      const res = await request.get('/api/food-database/categories');
      expect(res.status()).toBe(200);
      const body = await res.json();
      expect(Array.isArray(body.categories || body)).toBe(true);
    });

    test('GET /api/food-database/search with empty query', async ({ request }) => {
      const res = await request.get('/api/food-database/search?q=');
      expect([200, 400, 422]).toContain(res.status());
    });

    test('GET /api/food-database/search with special characters', async ({ request }) => {
      const res = await request.get('/api/food-database/search?q=<script>alert(1)</script>');
      expect(res.status()).toBeLessThan(500);
    });
  });
});

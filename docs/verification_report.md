# Verification Report

## Executive Summary
- 승인된 구현 범위에 대해서는 activation/trust contract가 눈에 띄게 개선됐다.
- 새 계정 생성은 strong password 기준으로 `201`을 반환했고, weak password는 generic `500` 대신 `400`으로 바뀌었다.
- fresh user notification preferences load/save는 더 이상 `500`을 내지 않고 `200`으로 응답했다.
- `activity_level=athlete`는 이제 DB `500`이 아니라 schema-level `422`로 막히고, `very_active`는 `200`으로 저장됐다.

## Commands Run
```bash
cd backend && python -m pytest tests/test_auth_register.py tests/test_notification_service.py tests/test_payment_service.py tests/test_transformation_endpoint.py

npx playwright test tests/api/health.spec.ts --grep "guest/body-scan|register"

npx playwright test tests/e2e/smoke.spec.ts --grep "Register Page"

npm --prefix frontend run lint -- --file 'src/app/(auth)/register/page.tsx' --file 'src/app/try/page.tsx' --file 'src/app/(dashboard)/profile/notifications/page.tsx' --file 'src/app/(auth)/onboarding/page.tsx' --file 'src/app/(dashboard)/profile/page.tsx' --file 'src/types/api.ts'
```

## Results
- `pytest`: `17 passed`
- API Playwright subset: `3 passed`
- E2E smoke subset: `2 passed`
- targeted frontend lint: `No ESLint warnings or errors`

## Direct Runtime Reproduction
### 1. Registration
- Before: `POST /api/auth/register` with weak password returned generic `500`
- After:
  - strong password `Codex12345!` -> `201`
  - weak password `Codex12345A` -> `400` with actionable password-strength detail

### 2. Notification Preferences
- Before: fresh user `GET /api/notifications/preferences` -> `500`
- After:
  - fresh user `GET /api/notifications/preferences` -> `200`
  - fresh user `PUT /api/notifications/preferences` -> `200`
  - returned payload:
```json
{
  "email_weekly_summary": false,
  "email_inactivity_reminder": true,
  "email_credit_low": true,
  "push_meal_reminder": true,
  "push_workout_reminder": true,
  "push_daily_summary": false,
  "push_weekly_body_scan": false,
  "meal_reminder_time": "12:00",
  "workout_reminder_days": ["monday", "wednesday", "friday"]
}
```

### 3. Activity Level Contract
- `PUT /api/auth/profile` with `activity_level=athlete` -> `422`
- `PUT /api/auth/profile` with `activity_level=very_active` -> `200`

### 4. Guest Age Gate
- `POST /api/guest/body-scan` with `age=17` -> `422`

## Remaining Risks
- `progress_photos` still stores raw `image_base64`; this is the highest unresolved privacy risk.
- notification fallback currently prioritizes uptime over guaranteed persistence when the backing table is absent; migration still needs to be applied for durable storage.
- push reminders are still not a real retention system. This pass only stopped the broken subscribe path from pretending to work without config.
- registration still depends on Supabase signup policy. If email confirmation mode changes, the endpoint’s `response_model=TokenResponse` path needs a follow-up redesign.

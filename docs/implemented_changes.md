# Implemented Changes

## Executive Summary
- 이번 패스는 Agent 4가 승인한 작은 P0/P1만 구현했다.
- 목표는 구조 리라이트가 아니라, activation과 trust를 바로 깨던 계약 문제를 닫는 것이었다.

## Implemented Fixes
| Problem | What changed | Files |
|---|---|---|
| `/register` non-Google dead end | email signup form, consent checkboxes, next-path preservation, stronger password floor added behind `NEXT_PUBLIC_ENABLE_EMAIL_LOGIN` | `frontend/src/app/(auth)/register/page.tsx:11-237` |
| `register` profile insert fragile across schema drift | legacy-safe profile insert helper added; `register` now uses fresh data client instead of auth singleton for PostgREST | `backend/app/routers/auth.py:19-165` |
| weak password surfaced as generic 500 | Supabase auth validation errors now return actionable `400` instead of generic `500` | `backend/app/routers/auth.py:148-165` |
| notification settings fresh user `500` | notification service now normalizes legacy schema, retries legacy columns, and falls back to defaults when table/schema is unavailable | `backend/app/services/notification_service.py:9-171` |
| broken push subscribe UI | push toggle now requires `NEXT_PUBLIC_WEB_PUSH_PUBLIC_KEY`; without it, push is treated as unconfigured instead of attempting `applicationServerKey: undefined` | `frontend/src/app/(dashboard)/profile/notifications/page.tsx:10-89` |
| guest age policy mismatch | guest scan UI and schema now enforce `18+` instead of allowing `10+` | `frontend/src/app/try/page.tsx:233-255`, `backend/app/schemas/body_schemas.py:241-245` |
| `activity_level` save failures | canonical enum aligned to `sedentary/light/moderate/active/very_active`; onboarding/profile option values updated to match backend validation | `backend/app/schemas/auth_schemas.py:1-21,37-51`, `backend/app/schemas/body_schemas.py:5-29,284-292`, `frontend/src/app/(auth)/onboarding/page.tsx:312-319`, `frontend/src/app/(dashboard)/profile/page.tsx:282-292`, `frontend/src/types/api.ts:1-38` |
| misleading free-tier promise on guest result | copy now states free plan includes 1 body scan; AI goal previews require Pro or paid credits | `frontend/src/app/try/page.tsx:351-385` |
| stale migration doc for notifications | `FIX_RLS_MISSING_TABLES.sql` updated to runtime notification preference columns | `docs/sql/FIX_RLS_MISSING_TABLES.sql:35-48` |

## Tests Added Or Updated
| Test | Purpose |
|---|---|
| `backend/tests/test_auth_register.py` | legacy-safe profile insert retry |
| `backend/tests/test_notification_service.py` | notification legacy schema normalization and update fallback |
| `tests/api/health.spec.ts` | guest under-18 rejection contract |
| `tests/e2e/smoke.spec.ts` | register page smoke remains stable and recognizes optional email form |

## Not Implemented In This Pass
- `progress_photos` raw image storage refactor
- explicit delete-account / delete-data flow
- public-safe share route
- Stripe customer linkage / entitlement reconciliation
- first-party moderation before vendor upload
- real push delivery + scheduler

## Remaining Risks
- notification fallback now keeps the page alive even if the table is missing, but durable persistence still depends on applying the matching migration.
- push remains disabled unless `NEXT_PUBLIC_WEB_PUSH_PUBLIC_KEY` and backend delivery infrastructure are actually provided.
- progress photo privacy risk remains the biggest unresolved trust problem.

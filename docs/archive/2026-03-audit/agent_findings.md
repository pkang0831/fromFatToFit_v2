# Denevira Strike Team Findings

## Executive Summary
- [Evidence] 지금 Denevira의 가장 큰 문제는 기능 부족이 아니라 계약 위반이다. 민감한 body image 제품인데 trust copy, guest age policy, notification promise, registration path, billing-language가 실제 동작과 자주 어긋난다.
- [Evidence] 이번 점검에서 즉시 재현된 운영 문제는 세 가지였다. `POST /api/auth/register`가 weak password에서 generic `500`을 내던 문제, fresh user의 `GET /api/notifications/preferences`가 `500`이던 문제, `activity_level` 값 불일치로 `PUT /api/auth/profile`이 `500` 나던 문제였다.
- [Inference] 제품 방향은 여전히 `AI transformation demo` 쪽으로 기울어 있지만, 실제로 돈과 재방문을 만들 수 있는 자산은 `Goal Planner`, `gap-to-goal`, `weekly check-in`, `challenge` 쪽이다.
- [Risk] 더 큰 구조 리스크는 아직 남아 있다. `progress_photos` raw `image_base64` 저장, deletion truthfulness 부재, Stripe customer linkage drift, public-safe share route 부재, real push/scheduler 부재는 이번 슬라이스에서 해결하지 않았다.

## Top 10 Problems
| Rank | Problem | Reproduction | User impact | Severity | Likely root cause | Affected files / routes / services | Suggested fix | Tests needed |
|---|---|---|---|---:|---|---|---|---|
| 1 | Raw body images stored directly in DB | `POST /api/progress-photos` 후 `GET /api/progress-photos/{id}` / `compare` 호출 | 민감 이미지 저장 부담, payload 비대화, privacy/support risk | 5 | object storage 없이 `image_base64`를 row에 직접 저장 | `backend/app/routers/progress_photos.py:11-37,57-123`, `frontend/src/app/(dashboard)/progress/page.tsx:107-176,326-380,596-604` | DB에는 storage key / signed URL만 저장 | upload/get/delete integration, payload-size regression |
| 2 | Privacy promise and deletion truth diverge | guest/landing copy와 profile/legal 확인 | trust collapse, refund/legal risk | 5 | copy가 구현보다 앞서감, delete/export lifecycle 부재 | `frontend/src/app/try/page.tsx:196-199`, `frontend/src/components/landing/HeroSection.tsx:117-120`, `frontend/src/app/(legal)/privacy/page.tsx:173-187,220-244`, `frontend/src/app/(dashboard)/profile/page.tsx:16-320` | marketing/legal copy 정렬, auditable deletion flow 추가 | account deletion e2e, storage cleanup test |
| 3 | Notification loop is mostly theatrical | notifications page, weekly reminder code, no scheduler | retention promise가 UI-only로 남음 | 5 | VAPID/service worker/scheduler/delivery telemetry 없음 | `frontend/src/app/(dashboard)/profile/notifications/page.tsx:10-89`, `backend/app/services/notification_service.py:107-220`, `backend/app/main.py:24-32,123-141` | real path 하나만 남기기: disable or fully wire push | push subscription roundtrip, reminder job integration |
| 4 | Non-Google signup was a dead end | `/try -> /register` 또는 `/register` 직접 접근 | high-intent 신규 유저 즉시 이탈 | 5 | register page가 OAuth only | `frontend/src/app/(auth)/register/page.tsx:11-237`, `frontend/src/components/features/SocialLoginButtons.tsx:19-145` | email signup + consent path 노출 | register smoke, onboarding e2e |
| 5 | Guest age gate conflicted with legal policy | `/try` age input, guest schema | minors가 guest funnel로 body image 업로드 가능 | 5 | guest UI/schema가 18+ 정책과 분리 | `frontend/src/app/try/page.tsx:233-255`, `backend/app/schemas/body_schemas.py:241-245`, `backend/app/routers/auth.py:67-71` | guest UI + schema 둘 다 `18+` 강제 | guest API validation, E2E age-gate |
| 6 | `activity_level` contract mismatch caused save failures | `PUT /api/auth/profile` with `athlete` or `heavy` | onboarding/profile 저장 실패, generic error | 4 | UI enum과 DB/schema enum 불일치 | `backend/app/schemas/auth_schemas.py:5-21,37-51`, `backend/app/schemas/body_schemas.py:5-29,284-292`, `frontend/src/app/(auth)/onboarding/page.tsx:312-319`, `frontend/src/app/(dashboard)/profile/page.tsx:282-292` | canonical enum one-source | schema validation, profile update integration |
| 7 | Registration error contract was wrong | weak password registration | user sees `500`, not actionable fix | 4 | Supabase auth validation error를 generic 500으로 포장 | `backend/app/routers/auth.py:73-165` | auth validation errors -> 400 passthrough | register unit + API tests |
| 8 | Stripe lifecycle can drift from entitlements | subscription created/updated/deleted code inspection | cancellation mismatch, support burden, refund risk | 4 | checkout completed는 처리하지만 customer linkage가 약함 | `backend/app/services/payment_service.py:21-33,116-214`, `backend/supabase_schema.sql:20-21` | precreate/persist customer + reconcile all webhooks | mocked webhook lifecycle tests |
| 9 | Share loop is not a public acquisition loop | share buttons on result/progress | private URL 공유 or download-only, virality weak | 3 | tokenized public share artifact 없음 | `frontend/src/components/ui/ShareButtons.tsx:11-35`, `frontend/src/components/features/ShareableResultCard.tsx:48-93` | public-safe share route + tokenized asset | anonymous share e2e, privacy regression |
| 10 | Product loop still ends too early after wow moment | home/challenge/progress usage | repeat value 약함, paywall feels output-based | 3 | state-driven home and accountability loop weak | `frontend/src/app/(dashboard)/home/page.tsx:25-179`, `frontend/src/app/(dashboard)/challenge/page.tsx:84-101`, `frontend/src/app/(dashboard)/goal-planner/page.tsx`, `frontend/src/components/features/WeeklyRescanPrompt.tsx:40-233` | default thesis를 planner/check-in/progress proof로 전환 | state-based home tests, challenge re-entry e2e |

## Agent 1 — New Beta User
- [Evidence] `/register`는 원래 Google only라 비-Google 유저가 막혔다. `frontend/src/app/(auth)/register/page.tsx:11-237`
- [Evidence] `/try`의 locked transformation copy는 free entitlement보다 더 많은 것을 약속했다. `frontend/src/app/try/page.tsx:351-385`
- [Inference] 첫 wow 뒤 account creation 계약이 흐리면 conversion보다 distrust가 먼저 온다.

## Agent 2 — Power User / Churn Risk
- [Evidence] 실제로 연결된 반복 자산은 `body-scan -> gap-to-goal -> planner -> challenge`뿐이다.
- [Inference] 돈을 내게 만드는 것은 더 많은 이미지가 아니라 `weekly proof + accountability + reminder`다.
- [Evidence] `notifications`, `home`, `challenge`는 현재 default return path를 충분히 만들지 못한다. `frontend/src/app/(dashboard)/home/page.tsx:76-176`, `frontend/src/app/(dashboard)/challenge/page.tsx:84-101`

## Agent 3 — Principal Engineer
- [Evidence] raw image storage, deletion mismatch, under-18 guest acceptance, vendor moderation gap, Stripe lifecycle drift가 구조 리스크다.
- [Evidence] 이번 승인 범위 밖이라 미구현으로 남긴 핵심 리스크는 `progress_photos` storage refactor, explicit deletion flow, Stripe customer linkage, first-party moderation gate다.

## Agent 5 — Growth & Marketing
- [Evidence] growth blocker는 계측 부재보다 loop 부재다.
- [Evidence] trust copy와 policy mismatch가 paid scale 전에 정리돼야 한다. `frontend/src/components/landing/HeroSection.tsx:117-120`, `frontend/src/app/(legal)/privacy/page.tsx:173-244`
- [Inference] acquire with wow, retain with proof loop.

## Kill / Keep / Delay
### Kill
- push를 real infra 없이 retention feature처럼 파는 것
- private URL share를 viral loop처럼 취급하는 것
- `more generations`를 product core value처럼 파는 copy

### Keep
- guest `try` wow moment
- `gap-to-goal` framing
- `Goal Planner`, `7-day challenge`, weekly check-in direction

### Delay
- mobile parity 확대
- extra generator modes
- paywall variant proliferation

## 5 Ranked Growth Experiments
| Rank | Experiment | Target audience | Channel | Hook | Landing | Success metric | Dependencies |
|---|---|---|---|---|---|---|---|
| 1 | Warm retargeting to `upgrade` | transformation/paywall viewers | Meta, Google retargeting | “Your gap-to-goal is already calculated.” | `/upgrade` | `purchase_completed / paywall_viewed` | pricing narrative cleanup |
| 2 | Short-form UGC into guest `try` | summer-cut / wedding / recomposition seekers | TikTok, IG Reels | “See your future body in 60 seconds.” | `/try` | `photo_upload_started`, register conversion | trust/legal cleanup |
| 3 | Creator-led weekly proof challenge | coaches, creators | influencer whitelisting | “Week 1 to week 8 proof” | `/register?next=/body-scan?tab=journey` | onboarding completion, week-2 return | challenge + reminders |
| 4 | High-intent SEO into body scan | search intent users | SEO / content | “Estimate + preview in one flow” | `/try` | organic -> upload rate | trust/legal alignment |
| 5 | Public-safe share/referral card | existing users with visible progress | in-product share | “Share your proof card” | public share route | share CTR, referred uploads | tokenized public share infra |

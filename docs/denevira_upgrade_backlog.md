# Denevira Upgrade Backlog

[Inference] Primary thesis for execution ordering: `progress proof/check-in coach`.

[Evidence] 이 백로그는 `docs/denevira_product_audit.md`의 confirmed defects와 connected loop analysis를 실행 순서로 재배열한 것이다. 증거 우선순위는 `runtime code > routes > services > DB schema/migrations > tests > configs > QA docs > transcripts > competitive docs`를 유지한다.

## P0

### P0-1. Fix `gap-to-goal` / `save-goal` profile key contract

- Readiness: `Ready`
- Goal: weekly proof loop의 핵심 상태인 `goal_image_url`, `target_body_fat_percentage`, `gap`을 정상화한다.
- Owner: `engineering`
- Evidence: [Evidence] body router가 `user_profiles.eq("id", current_user["id"])`를 사용하고, auth middleware는 `current_user["id"] = auth.users.id`를 준다. `user_profiles`는 별도 PK `id`와 FK `user_id`를 가진다 (`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/app/middleware/auth_middleware.py:67-91`; `backend/supabase_schema.sql:8-10`).
- Scope: `backend/app/routers/body.py:477-483, 690-777` 수정, shared profile lookup helper 도입, any related read/write path audit.
- Dependencies: 없음.
- Flag: 없음. 바로 고쳐야 하는 defect.
- Tests needed: `save-goal` integration test, `gap-to-goal` authenticated read test, journey auto-save regression test.
- Expected impact: home proof loop 복구, saved goal consistency 회복, trust loss 감소.

### P0-2. Repair purchase credit contract and `user_credits` schema alignment

- Readiness: `Ready`
- Goal: purchase completion 이후 credit 지급과 subscription upgrade path를 deterministic하게 만든다.
- Owner: `engineering`
- Evidence: [Evidence] backend payment service가 `add_credits`, `PRO_MONTHLY_CREDITS`, `FREE_MONTHLY_CREDITS`를 import하지만 usage limiter에는 없다 (`backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220`). Runtime은 `monthly_credits`, `bonus_credits`, `reset_date`를 기대하지만 doc migration은 `balance`만 정의한다 (`backend/app/services/payment_service.py:264-276`; `backend/app/services/usage_limiter.py:169-211`; `backend/supabase_credit_rpc.sql:1-50`; `docs/sql/FIX_RLS_MISSING_TABLES.sql:15-21`).
- Scope: payment/credit contract 단일화, migration cleanup, webhook path verification, copy sync precondition 마련.
- Dependencies: 없음.
- Flag: 없음. business-critical.
- Tests needed: webhook purchase-complete test, credit-pack award test, Pro upgrade credit delta test, schema smoke test.
- Expected impact: revenue leakage 감소, refund/support risk 감소, monetization trust 회복.

### P0-3. Ship analytics taxonomy v1 across acquisition, activation, retention, and billing

- Readiness: `Ready`
- Goal: product decision을 가능하게 하는 최소 event backbone을 만든다.
- Owner: `data + engineering`
- Evidence: [Evidence] `GoogleAnalytics` wrapper exists but `trackEvent` callsite가 없다 (`frontend/src/components/Analytics.tsx:30-38`; repo-wide `rg -n "trackEvent\\(" frontend/src` 결과 `frontend/src/components/Analytics.tsx:30`만 존재). Server telemetry/cost tracking도 in-memory only다 (`backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36`).
- Scope: common client event helper, server event emitter, identity stitching (`anonymous_id -> user_id`), core dashboard.
- Dependencies: analytics sink/vendor 선택.
- Flag: `ff_event_taxonomy_v1`
- Tests needed: event emission unit tests, purchase event contract tests, no-PII leakage review.
- Expected impact: funnel blindness 제거, pricing/onboarding/paywall decision 가능.

### P0-4. Patch activation dead ends in the web funnel

- Readiness: `Ready`
- Goal: wow-to-account-to-first-value 전환에서 새는 구간을 한 번에 줄인다.
- Owner: `product + engineering`
- Evidence: [Evidence] `Goal Preview` links to `/body-scan#transformation` but body-scan ignores hash (`frontend/src/app/(dashboard)/home/page.tsx:120-135`; `frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`). OAuth callback restores only `/home` or `/onboarding` (`frontend/src/app/(auth)/auth/callback/page.tsx:120-136`). `target_weight` is collected but never saved (`frontend/src/app/(auth)/onboarding/page.tsx:63-79, 333-368`). `/upgrade?success=true` and `?credits=purchased` are not consumed (`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`).
- Scope: hash/query routing, `next` param preservation, onboarding payload repair, upgrade success banner/state refresh.
- Dependencies: none.
- Flag: `ff_activation_path_repairs`
- Tests needed: deep-link Playwright test, OAuth callback redirect test, onboarding persistence test, upgrade success-state test.
- Expected impact: activation conversion 개선, purchase reassurance 개선.

### P0-5. Align trust/privacy copy with runtime truth and add data controls requirements

- Readiness: `Blocked by trust/legal`
- Goal: body-image product에 맞는 truth-aligned promise set을 확정한다.
- Owner: `trust/legal + product`
- Evidence: [Evidence] trust/FAQ says third parties never store and deletion is immediate (`frontend/src/lib/i18n/en.json:95-99, 803-806`). Privacy says third-party retention cannot be guaranteed, originals may be stored, deletion is by request/email (`frontend/src/app/(legal)/privacy/page.tsx:109-176, 181-187, 206-223`). Profile hub lacks explicit delete/export surface (`frontend/src/app/(dashboard)/profile/page.tsx:108-124`).
- Scope: copy audit, privacy copy scoping (guest vs authenticated), in-product delete/export/settings requirements, consent surface updates.
- Dependencies: legal review, data retention decision, support workflow design.
- Flag: `ff_trust_copy_refresh`
- Tests needed: content QA checklist, policy/legal approval, privacy UX smoke tests once built.
- Expected impact: trust conversion 개선, compliance risk 감소.

### P0-6. Make weekly reminders real or remove the promise

- Readiness: `Ready`
- Goal: re-engagement를 실제로 동작시키거나, 최소한 허위 약속을 제거한다.
- Owner: `engineering + infra + product`
- Evidence: [Evidence] notification preferences and push subscriptions persist (`backend/app/services/notification_service.py:22-93`; `frontend/src/app/(dashboard)/profile/notifications/page.tsx:33-214`), but `send_push_notification` only logs `[DEV]` and repo에는 scheduler가 없다 (`backend/app/services/notification_service.py:96-148`).
- Scope: actual push sender, scheduled job, delivery/open analytics, fallback copy if not shipping immediately.
- Dependencies: push provider/VAPID or equivalent infra.
- Flag: `ff_weekly_reminder_v1`
- Tests needed: scheduler dry-run test, push subscription integration test, notification event tests.
- Expected impact: D7/D30 reactivation 기반 마련.

## P1

### P1-1. Turn home into a connected “next best action” proof loop

- Readiness: `Ready`
- Goal: home를 static dashboard가 아니라 weekly check-in control center로 바꾼다.
- Owner: `product + design + engineering`
- Evidence: [Evidence] home already leads with `WeeklyRescanPrompt`, `Gap to Goal`, `Goal Preview`, `Progress Timeline` (`frontend/src/app/(dashboard)/home/page.tsx:76-176`). Full prompt is non-clickable (`frontend/src/components/features/WeeklyRescanPrompt.tsx:106-220`).
- Scope: due-state based CTA ordering, full prompt actionability, next-best action card orchestration.
- Dependencies: P0-1, P0-4.
- Flag: `ff_home_proof_loop`
- Tests needed: home CTA state test, due/not-due prompt test, clickthrough analytics validation.
- Expected impact: repeat session action rate 상승.

### P1-2. Connect transformation result and planner summary to challenge start

- Readiness: `Ready`
- Goal: `Goal Planner`와 `7-day challenge`를 side feature가 아니라 main loop step으로 만든다.
- Owner: `product + engineering`
- Evidence: [Evidence] journey result already promotes planner and challenge (`frontend/src/components/features/JourneyResult.tsx:172-239`). Challenge API and DB are real (`backend/app/routers/seven_day_challenge.py:64-223`; `docs/sql/ADD_SEVEN_DAY_CHALLENGE.sql:4-81`). Planner summary has no challenge-start action (`frontend/src/app/(dashboard)/goal-planner/page.tsx:835-849`).
- Scope: planner summary CTA, journey result default action tuning, challenge-start analytics.
- Dependencies: P0-3 instrumentation.
- Flag: `ff_planner_to_challenge`
- Tests needed: CTA routing test, challenge start integration test, duplicate start behavior test.
- Expected impact: week-1 retention loop 연결.

### P1-3. Surface scan history and make progress photos visually useful

- Readiness: `Blocked by architecture`
- Goal: proof assets가 “저장만 되는 상태”를 끝내고 실제로 소비되게 만든다.
- Owner: `engineering + design`
- Evidence: [Evidence] scan history API exists with no frontend callsite (`frontend/src/lib/api/services.ts:158-171`; `backend/app/routers/body.py:649-683`). Progress photo list returns no image data, so UI shows placeholders (`backend/app/routers/progress_photos.py:40-54`; `frontend/src/app/(dashboard)/progress/page.tsx:421-424`). Compare metrics are `None` (`backend/app/routers/progress_photos.py:117-123`).
- Scope: scan history UI, photo thumbnails or object storage references, compare metrics computation.
- Dependencies: storage approach decision, possibly thumbnail generation infra.
- Flag: `ff_progress_proof_v1`
- Tests needed: photo list render test, compare metrics test, history load test.
- Expected impact: proof consumption 및 repeat motivation 상승.

### P1-4. Repackage monetization around subscription for proof loop, credits for extra generation

- Readiness: `Blocked by data`
- Goal: pricing logic를 product thesis와 일치시킨다.
- Owner: `product + growth + data`
- Evidence: [Evidence] runtime scan/journey costs (`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`) conflict with marketing/FAQ claims (`frontend/src/lib/i18n/en.json:101-109, 819-822`). Home already says Pro includes unlimited weekly scans and credits are only for premium AI previews (`frontend/src/app/(dashboard)/home/page.tsx:155-176`).
- Scope: paywall copy, FAQ, profile credit cost display, upgrade offer hierarchy.
- Dependencies: P0-3 analytics to measure impact.
- Flag: `ff_packaging_progress_proof`
- Tests needed: copy QA, paywall event QA, checkout attribution tests.
- Expected impact: conversion clarity와 retention fit 동시 개선.

### P1-5. Wire or retire the stranded `streak` system

- Readiness: `Ready`
- Goal: fake gamification을 제거하거나 real compliance signal로 승격한다.
- Owner: `product + engineering`
- Evidence: [Evidence] `StreakBadge` reads streak only (`frontend/src/components/features/StreakBadge.tsx:12-24`), while `streakApi.checkIn()` exists with no UI callsite (`frontend/src/lib/api/services.ts:327-330`; `backend/app/routers/streaks.py:52-120`).
- Scope: streak trigger on meaningful actions (`progress_checkin`, weekly scan, weight log) or hide badge until connected.
- Dependencies: action taxonomy decisions.
- Flag: `ff_streak_connected`
- Tests needed: streak increment test, no-double-check-in test, hidden-state UI test if retired.
- Expected impact: badge trustworthiness and habit loop clarity 개선.

### P1-6. Make a hard mobile product decision

- Readiness: `Ready`
- Goal: mobile을 product surface로 인정할지, 임시로 축소할지 결정한다.
- Owner: `product + engineering`
- Evidence: [Evidence] mobile navigation exists (`mobile/src/navigation/RootNavigator.tsx:107-143`), but body scan and paywall are static (`mobile/src/screens/BodyScanScreen.tsx:11-24`; `mobile/src/screens/PaywallScreen.tsx:36-58`). API layer exists but UI wiring is absent (`mobile/src/services/api.ts:131-157`).
- Scope: either hide unfinished surfaces / mark beta, or fully wire scan and purchase.
- Dependencies: business channel priority decision.
- Flag: `ff_mobile_surface_gate`
- Tests needed: mobile navigation smoke, purchase flow test if shipped, hidden-surface smoke if gated.
- Expected impact: support burden 감소, channel clarity 상승.

## P2

### P2-1. Build a public-safe share landing for proof assets

- Readiness: `Blocked by trust/legal`
- Goal: external share를 growth loop로 바꾸되 body-image risk를 통제한다.
- Owner: `growth + design + engineering + trust/legal`
- Evidence: [Evidence] current share logic uses protected current URL (`frontend/src/components/ui/ShareButtons.tsx:13-25`; `frontend/src/components/features/ShareableResultCard.tsx:89-93`; `frontend/src/middleware.ts:39-42`).
- Scope: public tokenized landing, safe metadata set, consent-aware share permissions, revoke/delete behavior.
- Dependencies: trust/legal approval, privacy policy updates, analytics foundation.
- Flag: `ff_public_share_page`
- Tests needed: token auth test, revocation test, SEO/social preview QA, abuse review.
- Expected impact: virality 가능성 확보, broken share 제거.

### P2-2. Add durable cost, failure, and support operations dashboards

- Readiness: `Blocked by data`
- Goal: inference-heavy product의 운영 지표를 durable하게 본다.
- Owner: `data + infra`
- Evidence: [Evidence] journey telemetry and cost tracking are in-process only (`backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36`). Guest validate cold start can take 1–3+ minutes (`backend/app/main.py:24-30`).
- Scope: warehouse tables, failure dashboards, latency dashboards, cost dashboards, support tags.
- Dependencies: P0-3 analytics sink.
- Flag: `ff_ops_dashboards`
- Tests needed: data pipeline validation, dashboard sanity checks, alert threshold dry runs.
- Expected impact: gross margin/quality/support control 향상.

### P2-3. Introduce sensitive-image safety and moderation pipeline

- Readiness: `Blocked by trust/legal`
- Goal: minors, non-consensual uploads, sexualized outputs, dysmorphia risk에 대한 최소 운영 장치를 만든다.
- Owner: `trust/legal + engineering`
- Evidence: [Evidence] auth path has 18+ gating (`backend/app/routers/auth.py:32-36`), but guest path allows age 10+ (`frontend/src/app/try/page.tsx:233-242`). Local diffusion backends disable `safety_checker` (`backend/app/services/diffusion/sd15_cpu.py:56-61`; `backend/app/services/diffusion/sd2_cpu.py:56-61`).
- Scope: guest 18+ gate, non-self-photo escalation path, moderation checks, crisis copy/guardrails, vendor policy mapping.
- Dependencies: trust/legal policy decisions, moderation vendor choice if external.
- Flag: `ff_sensitive_image_safety`
- Tests needed: age-gate tests, refusal/moderation tests, escalation-path QA.
- Expected impact: compliance/trust risk 대폭 감소.

### P2-4. Run pricing and offer experiments only after instrumentation is live

- Readiness: `Blocked by data`
- Goal: subscription/credit pack pricing과 paywall timing을 measured way로 바꾼다.
- Owner: `growth + product + data`
- Evidence: [Evidence] current pricing is inconsistent across surfaces (`frontend/src/app/(dashboard)/upgrade/page.tsx:51-54`; `mobile/src/screens/PaywallScreen.tsx:46-48`; `frontend/src/lib/i18n/en.json:819-822`), while event measurement is absent (`frontend/src/components/Analytics.tsx:30-38`).
- Scope: paywall timing tests, plan framing tests, free allowance tests, annual vs monthly tests.
- Dependencies: P0-3 analytics, P0-2 payment contract repair.
- Flag: `ff_paywall_experiments`
- Tests needed: event integrity QA, revenue attribution QA, offer assignment consistency tests.
- Expected impact: monetization efficiency 개선 without blind guessing.

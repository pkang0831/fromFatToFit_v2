# Denevira Product Audit

[Evidence] 감사 기준일은 `2026-03-30`이며, 이 문서는 현재 저장소의 런타임 코드와 라우트, 서비스, 스키마, 테스트, 설정을 우선순위대로 읽고 작성했다. 충돌 시 증거 우선순위는 `runtime code > routes > services > DB schema/migrations > tests > configs > QA docs > transcripts > competitive docs`를 적용했다.

## 0. Repo Inspection Summary

- [Evidence] 먼저 본 web 진입점과 구조는 `frontend/src/app/layout.tsx:24-102`, `frontend/src/middleware.ts:4-49`, `frontend/src/components/landing/HeroSection.tsx:47-120`, `frontend/src/components/landing/WhyReturnSection.tsx:32-79`, `frontend/src/app/try/page.tsx:35-114, 345-383`였다. 여기서 landing, guest funnel, auth gating, 전역 provider, `GoogleAnalytics` mount를 확인했다.
- [Evidence] 그다음 core dashboard와 retention 표면은 `frontend/src/app/(dashboard)/home/page.tsx:25-177`, `frontend/src/components/features/WeeklyRescanPrompt.tsx:40-220`, `frontend/src/app/(dashboard)/body-scan/page.tsx:29-415`, `frontend/src/app/(dashboard)/progress/page.tsx:193-590`, `frontend/src/app/(dashboard)/challenge/page.tsx:18-176`, `frontend/src/app/(dashboard)/goal-planner/page.tsx:40-98, 265-358, 698-849`, `frontend/src/app/(dashboard)/chat/page.tsx:18-286`, `frontend/src/app/(dashboard)/upgrade/page.tsx:37-290`에서 확인했다.
- [Evidence] auth, onboarding, consent, OAuth continuity는 `frontend/src/components/features/SocialLoginButtons.tsx:19-145`, `frontend/src/app/(auth)/auth/callback/page.tsx:114-136`, `frontend/src/app/(auth)/onboarding/page.tsx:63-92, 139-241, 326-369`, `backend/app/routers/auth.py:20-107`에서 확인했다.
- [Evidence] backend product surface는 `backend/app/main.py:24-150`, `backend/app/routers/guest.py:50-145`, `backend/app/routers/body.py:355-558, 649-777`, `backend/app/routers/goal_planner.py:202-264`, `backend/app/routers/seven_day_challenge.py:64-223`, `backend/app/routers/streaks.py:10-120`, `backend/app/routers/progress_photos.py:11-123`, `backend/app/routers/weight.py:17-104`, `backend/app/services/notification_service.py:22-148`, `backend/app/routers/chat.py:53-143`, `backend/app/services/payment_service.py:116-290`, `backend/app/services/usage_limiter.py:1-220`를 기준으로 읽었다.
- [Evidence] DB와 migration 증거는 `backend/supabase_schema.sql:8-24, 122-205`, `backend/supabase_credit_rpc.sql:1-50`, `backend/supabase_progress_photos.sql:1-17`, `docs/sql/ADD_SAVED_GOAL_PLANS.sql:4-30`, `docs/sql/ADD_SEVEN_DAY_CHALLENGE.sql:4-81`, `docs/sql/FIX_RLS_MISSING_TABLES.sql:13-41`를 기준으로 사용했다.
- [Evidence] 실험/운영/품질 증거는 `frontend/src/components/Analytics.tsx:5-38`, repo-wide search `rg -n "trackEvent\\(" frontend/src` 결과 `frontend/src/components/Analytics.tsx:30`만 존재, `backend/app/services/journey_telemetry.py:1-90`, `backend/app/services/cost_tracker.py:7-36`, `.github/workflows/ci.yml:9-127`, `tests/e2e/smoke.spec.ts:5-154`, `tests/api/health.spec.ts:5-134`에서 확인했다.
- [Evidence] mobile 상태는 `mobile/src/navigation/RootNavigator.tsx:23-143`, `mobile/src/screens/BodyScanScreen.tsx:5-25`, `mobile/src/screens/PaywallScreen.tsx:36-58`, `mobile/src/services/api.ts:131-157`, `mobile/src/contexts/AuthContext.tsx:75-148`를 기준으로 판단했다.

- [Evidence] 현재 앱 구조는 `Next.js App Router` 기반 web front end 위에 `AuthProvider`, `SubscriptionProvider`, `ThemeProvider`, `LanguageProvider`를 올리고(`frontend/src/app/layout.tsx:71-99`), `FastAPI` 단일 앱이 router-per-feature로 `guest`, `body`, `payments`, `goal_planner`, `challenge`, `streaks`, `progress_photos`, `notifications`, `chat`, `weight`를 붙이는 구조다(`backend/app/main.py:35-41, 123-141`).
- [Evidence] 인증은 Supabase token/cookie 기반이고, web은 middleware와 client redirect가 이중으로 dashboard를 보호한다(`frontend/src/middleware.ts:8-44`; `frontend/src/app/(dashboard)/layout.tsx:18-22, 35-44`).
- [Inference] 상태관리는 domain store 중심이 아니라 page-local `useState` + API fetch + 일부 `localStorage` 의존에 가깝다. `WeeklyRescanPrompt`와 `BodyScanPage`가 `localStorage`를 직접 건드리고 있고(`frontend/src/components/features/WeeklyRescanPrompt.tsx:23-33`; `frontend/src/app/(dashboard)/body-scan/page.tsx:241-248`), 중앙 이벤트/실험 계층은 사실상 없다(`frontend/src/components/Analytics.tsx:30-38`).
- [Evidence] 실질 제품은 web-first다. mobile은 modal shell과 static screen이 있는 수준이며, purchase/scan UI wiring이 연결되지 않았다(`mobile/src/navigation/RootNavigator.tsx:107-143`; `mobile/src/screens/BodyScanScreen.tsx:11-24`; `mobile/src/screens/PaywallScreen.tsx:36-58`).

## 1. Brutal Diagnosis

- [Evidence] 지금 가장 잘 되는 것은 retention이 아니라 activation이다. `/try` guest scan은 sign-up 없이 바로 들어가고, 결과 직후 locked teaser로 계정을 만들게 한다(`frontend/src/app/try/page.tsx:35-114, 345-383`; `backend/app/routers/guest.py:106-145`).
- [Evidence] 제품이 파는 약속은 “주간 재방문과 visual proof”인데, 실제 연결은 끊겨 있다. landing이 weekly return을 팔고(`frontend/src/components/landing/WhyReturnSection.tsx:32-79`), home도 weekly rescan을 맨 위에 두지만(`frontend/src/app/(dashboard)/home/page.tsx:76-99`), full `WeeklyRescanPrompt`는 눌리지 않고(`frontend/src/components/features/WeeklyRescanPrompt.tsx:106-220`), push는 dev log만 찍으며(`backend/app/services/notification_service.py:134-145`), scheduler는 저장소에 없다.
- [Evidence] retention의 핵심 데이터 경로 자체가 깨져 있다. `goal_image_url`, `target_body_fat_percentage`, `gap-to-goal`은 `user_profiles.id`로 읽고 쓰는데, auth middleware가 주는 `current_user["id"]`는 `auth.users.id`다(`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/app/middleware/auth_middleware.py:67-91`; `backend/supabase_schema.sql:8-10`).
- [Evidence] monetization은 UI는 있지만 운영 신뢰도가 낮다. checkout completion은 `usage_limiter`에 존재하지 않는 `add_credits`, `PRO_MONTHLY_CREDITS`, `FREE_MONTHLY_CREDITS`를 import한다(`backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220`).
- [Evidence] 가격과 credit narrative가 서로 모순된다. runtime은 scan 10 credits, journey 30 credits인데(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`), marketing/FAQ는 free 10 credits로 body scan과 transformation preview 둘 다 된다고 말한다(`frontend/src/lib/i18n/en.json:101-109, 819-822`).
- [Evidence] trust copy가 구현보다 공격적이다. landing/FAQ는 “never stored by third parties”, “delete anytime”, “no backups retained”라고 말하지만(`frontend/src/lib/i18n/en.json:95-99, 803-806`; `frontend/src/components/landing/HeroSection.tsx:117-120`), privacy policy는 third-party retention 보장 불가, originals may be stored, deletion by request/email이라고 쓴다(`frontend/src/app/(legal)/privacy/page.tsx:109-176, 181-187, 206-223`).
- [Evidence] authenticated body scan은 capture guidance에서 full-body를 요구하면서 실제 validation은 `upper_body`로 보내고 있다(`frontend/src/app/(dashboard)/body-scan/page.tsx:118-163, 207-288, 382-415`). 이건 copy inconsistency가 아니라 measurement contract inconsistency다.
- [Evidence] repo에는 retention asset이 많다. `Goal Planner`, `7-day challenge`, `progress photos`, `weight projection`, `chat`, `streaks`가 모두 있다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:40-98, 265-358, 698-849`; `backend/app/routers/goal_planner.py:202-264`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`; `backend/app/routers/seven_day_challenge.py:64-223`; `frontend/src/app/(dashboard)/progress/page.tsx:291-580`; `backend/app/routers/weight.py:17-104`; `frontend/src/app/(dashboard)/chat/page.tsx:42-286`; `backend/app/routers/streaks.py:10-120`). 문제는 이것들이 하나의 loop로 작동하지 않는다는 점이다.
- [Evidence] mobile은 현재 business multiplier가 아니라 liability다. Body scan과 paywall은 static UI이고(`mobile/src/screens/BodyScanScreen.tsx:11-24`; `mobile/src/screens/PaywallScreen.tsx:36-58`), app-level navigation만 실제다(`mobile/src/navigation/RootNavigator.tsx:107-143`).
- [Evidence] 실험 속도는 거의 0에 가깝다. `GoogleAnalytics`는 mount되지만 실제 `trackEvent` callsite가 없고(`frontend/src/components/Analytics.tsx:30-38`; repo-wide `rg -n "trackEvent\\(" frontend/src` 결과 `frontend/src/components/Analytics.tsx:30`만 존재), journey/cost telemetry도 프로세스 메모리 안에서만 산다(`backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36`).

[Inference] The biggest lie this product is currently telling itself is: “우리는 이미 weekly retention product다.” 실제로는 weekly scan promise, streak, challenge, notification, history가 서로 연결되지 않은 partial system들이다(`frontend/src/components/landing/WhyReturnSection.tsx:32-79`; `frontend/src/components/features/WeeklyRescanPrompt.tsx:106-220`; `backend/app/services/notification_service.py:96-148`; `frontend/src/components/features/StreakBadge.tsx:12-24`; `backend/app/routers/body.py:649-777`).

[Inference] The fastest path from demo to business is: `AI transformation demo`를 선두 가치가 아니라 acquisition hook로 낮추고, 제품의 주축을 `progress proof/check-in coach`로 재편하는 것이다. 현재 코드에서 가장 연결 가능한 자산이 `weekly scan + gap-to-goal + progress photos + challenge + plan + coach`이기 때문이다(`frontend/src/app/(dashboard)/home/page.tsx:63-176`; `frontend/src/app/(dashboard)/progress/page.tsx:291-580`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`; `frontend/src/app/(dashboard)/goal-planner/page.tsx:698-849`; `frontend/src/app/(dashboard)/chat/page.tsx:42-286`).

## 2. Product Scorecard

| 항목 | 점수 | Score Confidence | 판단 | Repo Evidence | Unknowns |
| --- | --- | --- | --- | --- | --- |
| Activation | 7/10 | 4/5 | [Inference] guest-first hook는 강하다. 하지만 auth continuity와 onboarding 손실이 paid activation을 깎는다. | [Evidence] `/try`는 sign-up 없이 body scan을 열고 결과 직후 `/register` teaser로 전환한다(`frontend/src/app/try/page.tsx:35-114, 345-383`; `backend/app/routers/guest.py:106-145`). OAuth callback은 원래 의도를 복원하지 않고 `/home` 또는 `/onboarding`으로만 보낸다(`frontend/src/app/(auth)/auth/callback/page.tsx:120-136`). `target_weight`는 수집하지만 저장하지 않는다(`frontend/src/app/(auth)/onboarding/page.tsx:63-79, 333-368`). | [Assumption] `/try -> /register -> /purchase` 전환율은 analytics 부재로 검증할 수 없다. |
| Retention | 3/10 | 4/5 | [Inference] 제품은 retention을 말하지만, 연결된 재방문 loop는 아직 없다. | [Evidence] landing/home가 weekly rescan을 핵심 약속으로 둔다(`frontend/src/components/landing/WhyReturnSection.tsx:32-79`; `frontend/src/app/(dashboard)/home/page.tsx:76-99`). 하지만 `gap-to-goal` 핵심 경로는 confirmed key mismatch가 있고(`backend/app/routers/body.py:477-483, 690-777`; `backend/app/middleware/auth_middleware.py:67-91`), `WeeklyRescanPrompt` full variant는 action이 없고(`frontend/src/components/features/WeeklyRescanPrompt.tsx:106-220`), push reminder는 실제 발송이 없으며(`backend/app/services/notification_service.py:134-145`) streak check-in도 UI에서 호출되지 않는다(`frontend/src/components/features/StreakBadge.tsx:12-24`; `frontend/src/lib/api/services.ts:327-330`). | [Assumption] D1/D7/D30 actual retention은 event/warehouse 부재로 모른다. |
| Monetization | 4/10 | 4/5 | [Inference] 결제 surface는 있으나 contract와 copy가 불안정해서 revenue leakage 위험이 높다. | [Evidence] `/upgrade`는 Stripe checkout을 생성한다(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`). 그러나 checkout completion은 missing symbol import를 가진다(`backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220`). FAQ/free plan copy와 runtime credit cost는 충돌한다(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`; `frontend/src/lib/i18n/en.json:101-109, 819-822`). `/upgrade?success=true`나 `?credits=purchased`는 읽히지 않는다(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`). | [Assumption] checkout drop-off, refund rate, paywall conversion은 측정되지 않는다. |
| Differentiation | 6/10 | 3/5 | [Inference] 순수 image generator로만 보면 약하지만, proof loop로 재조합하면 차별화 잠재력은 있다. | [Evidence] repo에는 transformation journey, goal planner, challenge, progress photos, weight projection, AI coach가 모두 존재한다(`backend/app/routers/body.py:355-558`; `frontend/src/app/(dashboard)/goal-planner/page.tsx:698-849`; `backend/app/routers/seven_day_challenge.py:64-223`; `frontend/src/app/(dashboard)/progress/page.tsx:291-580`; `backend/app/routers/weight.py:17-104`; `frontend/src/app/(dashboard)/chat/page.tsx:42-286`). | [Assumption] model output quality와 competitor 대비 wow 우위는 repo만으로는 정량 비교 불가하다. |
| Trust | 3/10 | 4/5 | [Inference] sensitive body-image product인데 copy truthfulness와 user control이 부족하다. | [Evidence] trust/FAQ copy는 third-party non-storage와 instant deletion을 약속한다(`frontend/src/lib/i18n/en.json:95-99, 803-806`). privacy policy는 third-party retention 불가, Supabase storage 가능, deletion by request/email이라고 밝힌다(`frontend/src/app/(legal)/privacy/page.tsx:109-176, 181-187, 206-223`). guest flow는 self-photo checkbox만 있고(`frontend/src/app/try/page.tsx:246-255`), guest age input은 `min={10}`이다(`frontend/src/app/try/page.tsx:233-242`). profile hub에는 notifications 외 delete/export entry가 없다(`frontend/src/app/(dashboard)/profile/page.tsx:108-124`). | [Assumption] 실제 민원/incident volume은 없다. |
| Virality | 2/10 | 4/5 | [Inference] 공유는 버튼이 있지만 loop는 사실상 막혀 있다. | [Evidence] `ShareButtons`와 `ShareableResultCard`는 `window.location.href`를 공유/복사한다(`frontend/src/components/ui/ShareButtons.tsx:11-25`; `frontend/src/components/features/ShareableResultCard.tsx:48-93, 171-184`). 그런데 dashboard routes는 auth-protected다(`frontend/src/middleware.ts:9-24, 39-42`). | [Assumption] 현재 organic share volume은 측정되지 않는다. |
| Technical Health | 4/10 | 4/5 | [Inference] 구조는 큰 monolith라도 읽을 만하지만, confirmed runtime defects와 schema drift가 위험하다. | [Evidence] body router의 `user_profiles.eq("id")` bug가 confirmed다(`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/supabase_schema.sql:8-10`). payment service는 존재하지 않는 credit symbol을 import한다(`backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220`). runtime은 `monthly_credits/bonus_credits/reset_date`를 기대하지만 doc migration은 `balance`만 만든다(`backend/app/services/payment_service.py:264-276`; `backend/app/services/usage_limiter.py:169-211`; `backend/supabase_credit_rpc.sql:1-50`; `docs/sql/FIX_RLS_MISSING_TABLES.sql:15-21`). | [Risk] production DB에 어떤 migration이 실제 적용됐는지는 repo만으로 확정 불가하다. |
| Experiment Velocity | 2/10 | 5/5 | [Inference] 실험 속도를 막는 가장 큰 이유는 analytics blindness다. | [Evidence] `GoogleAnalytics`는 mount되어도 event callsite가 없고(`frontend/src/app/layout.tsx:72-99`; `frontend/src/components/Analytics.tsx:30-38`), journey telemetry/cost tracking은 비지속적이며(`backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36`), CI는 landing/auth/legal/middleware smoke에 치우쳐 있다(`.github/workflows/ci.yml:9-127`; `tests/e2e/smoke.spec.ts:5-154`; `tests/api/health.spec.ts:5-134`). | [Assumption] feature flag framework도 repo에서 확인되지 않았다. |

## 3. Actual User Journey Map

### 3.1 Web-first entry points

1. [Evidence] 기본 entry는 `/` landing이다. unauthenticated user는 landing을 보고, authenticated user는 middleware에서 `/home`으로 보낸다(`frontend/src/middleware.ts:26-31`). Hero CTA와 WhyReturn CTA 둘 다 `/try`로 간다(`frontend/src/components/landing/HeroSection.tsx:82-89`; `frontend/src/components/landing/WhyReturnSection.tsx:72-78`).
2. [Evidence] `/try`는 guest upload -> details -> analyzing -> result의 4단계다(`frontend/src/app/try/page.tsx:14-18, 35-114, 144-405`). upload는 `full_body` validation과 일치시키고(`frontend/src/app/try/page.tsx:50-56, 82-85`), backend guest body-scan은 result를 저장하지 않는다(`backend/app/routers/guest.py:106-145`).
3. [Evidence] 첫 result는 body fat estimate만 보여주고 transformation은 잠근다. CTA는 `/register`다(`frontend/src/app/try/page.tsx:345-383`).
4. [Evidence] `/register`는 사실상 `SocialLoginButtons`만 가진 Google OAuth surface다. provider 목록은 Google 하나뿐이다(`frontend/src/components/features/SocialLoginButtons.tsx:19-34, 123-145`).
5. [Evidence] OAuth callback은 user profile의 `onboarding_completed`만 확인하고 `/home` 또는 `/onboarding`으로 보낸다. 원래 진입한 deep link나 teaser context는 복구하지 않는다(`frontend/src/app/(auth)/auth/callback/page.tsx:120-136`).
6. [Evidence] `/onboarding`은 consent -> profile -> goals -> tour를 수집한다. 하지만 `target_weight`는 UI에서 수집하고도 save payload에 포함되지 않는다(`frontend/src/app/(auth)/onboarding/page.tsx:63-79, 326-368`).
7. [Evidence] `/home`은 greeting, `StreakBadge`, full `WeeklyRescanPrompt`, `Gap to Goal`, `Goal Preview`, `Progress Timeline`, upgrade CTA 순으로 구성된다(`frontend/src/app/(dashboard)/home/page.tsx:55-176`).
8. [Evidence] `Goal Preview` card는 `/body-scan#transformation`으로 보내지만, `BodyScanPage`는 `activeTab`을 `'scan'`으로 고정 초기화하고 hash를 읽지 않는다(`frontend/src/app/(dashboard)/home/page.tsx:120-135`; `frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`).
9. [Evidence] authenticated `/body-scan`은 `Body Scan`과 `Transformation Journey` 두 탭을 갖고, non-Pro scan cost는 10, journey cost는 30이다(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75, 336-364`). 두 흐름 모두 photo validation을 `upper_body`로 보낸다(`frontend/src/app/(dashboard)/body-scan/page.tsx:118-163, 207-288`).
10. [Evidence] transformation result는 before/after, share, `Goal Planner`, `7-day challenge` CTA를 갖는다(`frontend/src/components/features/JourneyResult.tsx:48-239`).
11. [Evidence] `/goal-planner`는 7-step wizard이며 saved plan load/save가 실제로 있다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:40-98, 265-358, 375-387, 698-849`; `backend/app/routers/goal_planner.py:202-264`; `docs/sql/ADD_SAVED_GOAL_PLANS.sql:4-30`). 하지만 summary end state는 `Start Over`와 `Save Plan`만 있고 challenge start/action loop가 없다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:835-849`).
12. [Evidence] `/challenge`는 active challenge가 없으면 fallback만 보여주고, 있으면 30-second daily check-in을 받는다(`frontend/src/app/(dashboard)/challenge/page.tsx:84-176`; `backend/app/routers/seven_day_challenge.py:64-223`).
13. [Evidence] `/progress`는 goals tab과 photos tab을 갖고 upload/view/compare가 가능하다(`frontend/src/app/(dashboard)/progress/page.tsx:193-245, 291-295, 299-580`). 하지만 photo list는 thumbnail을 못 받아 placeholder만 그리고(`frontend/src/app/(dashboard)/progress/page.tsx:421-424`; `backend/app/routers/progress_photos.py:40-54`), compare metrics도 `None`이다(`backend/app/routers/progress_photos.py:117-123`).
14. [Evidence] `/upgrade`는 Stripe checkout과 credit pack checkout을 만들지만 success query를 소비하지 않는다(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`).

### 3.2 Dead ends, trust breaks, friction points, churn points

- [Evidence] Dead end: `Goal Preview` CTA는 user intent를 `journey` tab으로 보내지 못한다. `/body-scan#transformation` deep link가 사실상 죽어 있다(`frontend/src/app/(dashboard)/home/page.tsx:120-135`; `frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`).
- [Evidence] Dead end: `WeeklyRescanPrompt`의 compact variant는 `/body-scan`으로 눌리지만 full variant는 정보 카드일 뿐 action이 없다. home과 body-scan 상단의 가장 중요한 re-entry surface가 클릭되지 않는다(`frontend/src/components/features/WeeklyRescanPrompt.tsx:62-103, 106-220`; `frontend/src/app/(dashboard)/home/page.tsx:76-77`; `frontend/src/app/(dashboard)/body-scan/page.tsx:333-335`).
- [Evidence] Dead end: scan history API는 존재하지만 UI callsite가 없다. `getScanHistory()`는 정의만 있고 frontend에서 쓰이지 않는다(`frontend/src/lib/api/services.ts:158-171`; repo-wide `rg -n "getScanHistory\\(|saveGoal\\(|checkIn\\(" frontend/src` 결과 callsite 없음).
- [Evidence] Trust break: marketing은 full-body upload를 요구하지만 authenticated runtime validation은 `upper_body`다(`frontend/src/app/try/page.tsx:167-170`; `frontend/src/app/(dashboard)/body-scan/page.tsx:118-163, 207-288, 403-405`).
- [Evidence] Trust break: guest path는 “analyzed once and never stored”라고 말하지만 product-level privacy copy는 authenticated originals may be stored, third-party retention not guaranteed라고 말한다(`frontend/src/app/try/page.tsx:196-199`; `frontend/src/app/(legal)/privacy/page.tsx:109-176, 181-187`).
- [Evidence] Friction: guest result에서 auth로 넘어가면 original goal intent가 사라진다. callback은 `/home` 또는 `/onboarding`만 선택한다(`frontend/src/app/try/page.tsx:372-382`; `frontend/src/app/(auth)/auth/callback/page.tsx:120-136`).
- [Evidence] Friction: register/login primary path는 Google-only다. email login은 feature flag 조건부다(`frontend/src/components/features/SocialLoginButtons.tsx:19-34, 123-145`; `frontend/src/app/(auth)/login/page.tsx:41-95`는 이번 문서에서 직접 재인용하지 않았고, therefore Google-primary만 확정적으로 주장한다).
- [Evidence] Churn point: upgrade success state가 invisible이라 결제 후 가치 확신을 즉시 회복시키지 못한다(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`).
- [Evidence] Churn point: progress photos는 저장돼도 list에서 실제 이미지가 안 보여서 visual proof value가 즉시 드러나지 않는다(`frontend/src/app/(dashboard)/progress/page.tsx:408-424`; `backend/app/routers/progress_photos.py:40-54`).
- [Evidence] Churn point: notifications settings는 저장돼도 실제 발송과 scheduler가 없어 “돌아오게 만드는 장치”가 UI에만 존재한다(`frontend/src/app/(dashboard)/profile/notifications/page.tsx:33-214`; `backend/app/services/notification_service.py:96-148`).

### 3A. Connected Loop Matrix

[Inference] 분류 기준은 다음과 같다. `Connected`는 여섯 칼럼이 모두 살아 있는 경우, `Partial`은 값은 있으나 loop-critical missing link가 있는 경우, `Dead`는 사용자가 약속받는 기능이 실제 작동하지 않는 경우, `Stranded Asset`은 UI 또는 API/DB만 남고 재진입/재사용 연결이 없는 경우다.

| Feature | UI exists | API exists | DB persists | scheduler/trigger exists | analytics exists | re-entry surface exists | Classification | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Guest scan -> locked transformation teaser | Yes | Yes | No | No | No | Yes | Partial | [Evidence] UI/CTA는 `/try`에 있고(`frontend/src/app/try/page.tsx:35-114, 345-383`), guest APIs는 존재하지만 result is not stored(`backend/app/routers/guest.py:106-145`). Re-entry는 landing `/try` CTA뿐이다(`frontend/src/components/landing/HeroSection.tsx:82-89`). |
| Weekly body scan / gap-to-goal | Yes | Yes | Partial | No | No | Yes | Partial | [Evidence] home/body-scan에 surface가 있고(`frontend/src/app/(dashboard)/home/page.tsx:76-99`; `frontend/src/app/(dashboard)/body-scan/page.tsx:333-415`), `gap-to-goal` API가 있으나 profile key mismatch가 confirmed다(`backend/app/routers/body.py:477-483, 690-777`; `backend/app/middleware/auth_middleware.py:67-91`). Re-entry surface는 존재하지만 full prompt는 non-clickable이다(`frontend/src/components/features/WeeklyRescanPrompt.tsx:62-220`). |
| Transformation journey -> Goal Planner | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] journey UI와 result CTA가 있고(`frontend/src/app/(dashboard)/body-scan/page.tsx:271-326`; `frontend/src/components/features/JourneyResult.tsx:129-239`), backend는 journey result를 `body_scans`에 저장한다(`backend/app/routers/body.py:458-475`). Goal Planner saved plan도 있다(`backend/app/routers/goal_planner.py:202-264`). 다만 analytics와 scheduler는 없다. |
| Transformation journey -> 7-day challenge | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] result CTA와 challenge page가 있고(`frontend/src/components/features/JourneyResult.tsx:172-239`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`), backend/DB는 challenge와 daily check-ins를 저장한다(`backend/app/routers/seven_day_challenge.py:64-223`; `docs/sql/ADD_SEVEN_DAY_CHALLENGE.sql:4-81`). Reminder/scheduler/analytics는 없다. |
| Goal Planner saved plan | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] wizard summary에서 `Save Plan`과 `Load saved plan`이 있다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:375-387, 835-849`). Backend와 DB persistence도 있다(`backend/app/routers/goal_planner.py:202-264`; `docs/sql/ADD_SAVED_GOAL_PLANS.sql:4-30`). 하지만 next action loop가 없다. |
| 7-day challenge daily check-in | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] `/challenge` UI, `checkinSevenDay`, table persistence가 있다(`frontend/src/app/(dashboard)/challenge/page.tsx:117-159`; `backend/app/routers/seven_day_challenge.py:166-223`; `docs/sql/ADD_SEVEN_DAY_CHALLENGE.sql:20-30`). 재진입은 `/challenge` 자체뿐이며 notification/analytics가 없다. |
| Streak badge / streak system | Yes | Yes | Yes | No | No | No | Stranded Asset | [Evidence] `StreakBadge`는 `getStreak`만 호출한다(`frontend/src/components/features/StreakBadge.tsx:12-24`). API는 `check-in`까지 제공하지만 UI callsite는 없고(`frontend/src/lib/api/services.ts:327-330`; `backend/app/routers/streaks.py:52-120`), home badge 외 명확한 re-entry surface가 없다(`frontend/src/app/(dashboard)/home/page.tsx:65-67`). |
| Progress photos compare | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] progress UI와 compare modal이 있고(`frontend/src/app/(dashboard)/progress/page.tsx:299-580`), CRUD/compare API와 DB가 있다(`backend/app/routers/progress_photos.py:11-123`; `backend/supabase_progress_photos.sql:1-17`). 하지만 list thumbnail이 비어 있고 compare metrics는 `None`이다(`frontend/src/app/(dashboard)/progress/page.tsx:421-424`; `backend/app/routers/progress_photos.py:117-123`). |
| Weight projection / weight logs | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] progress goals tab가 projection chart를 보여주고(`frontend/src/app/(dashboard)/progress/page.tsx:270-295`), frontend API layer는 weight log/projection endpoints를 갖고(`frontend/src/lib/api/services.ts:273-297`), backend service는 `weight_logs`와 `user_profiles`를 읽고 쓴다(`backend/app/routers/weight.py:17-104`; `backend/app/services/weight_tracking_service.py:33-167, 243-319`). |
| Notifications / weekly reminder | Yes | Yes | Yes | No | No | Yes | Dead | [Evidence] settings UI와 subscription persistence는 존재하지만(`frontend/src/app/(dashboard)/profile/notifications/page.tsx:33-214`; `backend/app/services/notification_service.py:55-93`), actual sender는 `[DEV]` log만 남기고(`backend/app/services/notification_service.py:134-145`), repo에 scheduler/cron trigger가 없다. |
| AI coach chat history | Yes | Yes | Yes | No | No | Yes | Partial | [Evidence] chat UI/history/status는 있다(`frontend/src/app/(dashboard)/chat/page.tsx:42-286`; `backend/app/routers/chat.py:53-143`). 하지만 UI는 `sources`를 렌더하지 않고(`frontend/src/app/(dashboard)/chat/page.tsx:80-86, 203-228`), analytics/re-engagement trigger가 없다. |
| Scan history | No | Yes | Yes | No | No | No | Stranded Asset | [Evidence] `getScanHistory()`와 backend history endpoint는 존재한다(`frontend/src/lib/api/services.ts:158-171`; `backend/app/routers/body.py:649-683`). 하지만 repo-wide frontend callsite는 없다(`rg -n "getScanHistory\\(" frontend/src` 결과 definition 외 없음). |

[Inference] 현재 기준으로 여섯 칼럼을 모두 만족하는 `Connected` retention feature는 하나도 없다.

## 4. Multi-Agent Review

### 4.1 Business Strategist / CEO

- [Inference] What this agent believes: 지금 제품은 “business로 가는 raw material”은 충분하지만, 현재 상태는 아직 curiosity tool에 가깝다. 이유는 acquisition hook는 있으나 반복 결제 근거가 weak하고, 반복 사용 핵심 경로가 confirmed defect와 dead surface로 막혀 있기 때문이다(`frontend/src/app/try/page.tsx:35-114, 345-383`; `backend/app/routers/body.py:690-777`; `backend/app/services/payment_service.py:116-144`).
- [Inference] What this agent thinks is broken: recurring value proposition이 불명확하다. landing은 weekly proof를 팔고(`frontend/src/components/landing/WhyReturnSection.tsx:32-79`), monetization은 credits/subscription을 섞어 쓰지만(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`; `frontend/src/app/(dashboard)/upgrade/page.tsx:51-87`), FAQ/free-plan math는 runtime과 다르다(`frontend/src/lib/i18n/en.json:101-109, 819-822`).
- [Inference] What this agent thinks is underrated: planner + progress photos + challenge + coach를 하나의 “proof engine”으로 묶으면 pure generator보다 defensible하다. 이 자산들은 이미 코드에 있다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:698-849`; `frontend/src/app/(dashboard)/progress/page.tsx:299-580`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`; `frontend/src/app/(dashboard)/chat/page.tsx:42-286`).
- [Inference] What this agent would do first: subscription의 기준 가치를 `weekly proof loop`로 재정의하고, credits는 extra generation에만 남기겠다. 즉, “측정-추적-검증”은 Pro subscription의 본체가 되고, one-off wow generation은 add-on이 되어야 한다(`frontend/src/app/(dashboard)/home/page.tsx:155-176`; `frontend/src/lib/i18n/en.json:101-109`).
- [Evidence] Evidence from the codebase: `Goal Planner`, `Challenge`, `Progress`, `Chat`가 별도 섬으로 존재하고(`backend/app/routers/goal_planner.py:202-264`; `backend/app/routers/seven_day_challenge.py:64-223`; `backend/app/routers/progress_photos.py:11-123`; `backend/app/routers/chat.py:53-143`), paywall/credits는 이미 surface가 있다(`frontend/src/app/(dashboard)/upgrade/page.tsx:37-290`; `backend/app/services/usage_limiter.py:169-211`).

### 4.2 Ruthless Target User

- [Inference] What this agent believes: “사진 한 장으로 body fat 보고 future body도 보여준다”는 문구는 흥미롭다. 하지만 나는 내 사진을 주는 순간부터 매우 의심이 많아지고, 두 번째 방문 이유가 약하면 바로 이탈한다.
- [Evidence] What this agent thinks is broken: 나는 landing에서 weekly proof를 기대했는데(`frontend/src/components/landing/WhyReturnSection.tsx:32-79`), home에 들어와도 가장 큰 카드가 눌리지 않고(`frontend/src/components/features/WeeklyRescanPrompt.tsx:106-220`), `Goal Preview`를 눌러도 내가 기대한 tab이 안 열린다(`frontend/src/app/(dashboard)/home/page.tsx:120-135`; `frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`).
- [Evidence] What this agent thinks is broken: 나는 full-body photo를 올리라는 안내를 보고 행동했는데(`frontend/src/app/try/page.tsx:167-170`; `frontend/src/app/(dashboard)/body-scan/page.tsx:403-405`), authenticated runtime은 `upper_body` 검사를 한다(`frontend/src/app/(dashboard)/body-scan/page.tsx:120, 162, 209, 287`). 이건 “내가 뭘 맞춰야 하는지”를 흐린다.
- [Evidence] What this agent thinks is broken: privacy messaging이 믿기지 않는다. 한 화면에서는 never stored/non-shared라고 말하고(`frontend/src/lib/i18n/en.json:95-99, 803-806`), 다른 화면에서는 third-party retention 못 보장한다고 말한다(`frontend/src/app/(legal)/privacy/page.tsx:109-176, 181-187`).
- [Inference] What this agent thinks is underrated: guest try에서 sign-up 없이 바로 몸 상태를 보는 경험은 좋다. 그건 살려야 한다(`frontend/src/app/try/page.tsx:136-170`; `backend/app/routers/guest.py:106-145`).
- [Inference] What this agent would do first: guest result 직후 “무료 account를 만들면 네 preview, 네 target, 네 weekly proof가 이어진다”를 끊김 없이 보여주고, auth 뒤에도 같은 맥락으로 복귀시켜야 한다. 지금처럼 `/home`으로 튕기면 감정이 식는다(`frontend/src/app/try/page.tsx:345-383`; `frontend/src/app/(auth)/auth/callback/page.tsx:120-136`).
- [Evidence] Evidence from the codebase: share 버튼도 실제로는 protected dashboard URL을 복사한다(`frontend/src/components/ui/ShareButtons.tsx:13-25`; `frontend/src/components/features/ShareableResultCard.tsx:89-93`; `frontend/src/middleware.ts:39-42`).

### 4.3 Growth & Performance Marketer

- [Inference] What this agent believes: paid acquisition은 guest-first funnel 덕분에 시도할 수는 있다. 하지만 post-click/post-wow conversion path가 너무 많이 샌다.
- [Evidence] What this agent thinks is broken: landing-to-try hook는 좋지만(`frontend/src/components/landing/HeroSection.tsx:82-89`; `frontend/src/app/try/page.tsx:136-170`), registration은 Google-only고(`frontend/src/components/features/SocialLoginButtons.tsx:19-34`), callback은 original campaign intent를 유지하지 않으며(`frontend/src/app/(auth)/auth/callback/page.tsx:120-136`), paywall success feedback도 없다(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`).
- [Evidence] What this agent thinks is broken: 공유 루프는 사실상 무효다. share/copy link는 `window.location.href`를 써서 protected dashboard URL만 퍼뜨린다(`frontend/src/components/ui/ShareButtons.tsx:13-25`; `frontend/src/components/features/ShareableResultCard.tsx:62-93`; `frontend/src/middleware.ts:39-42`).
- [Inference] What this agent thinks is underrated: user-generated proof asset은 이미 product 안에 있다. transformation result card, progress photos, weekly BF delta, challenge identity copy는 UGC backbone이 될 수 있다(`frontend/src/components/features/ShareableResultCard.tsx:95-184`; `frontend/src/app/(dashboard)/progress/page.tsx:325-380`; `backend/app/routers/seven_day_challenge.py:30-61`).
- [Inference] What this agent would do first: `guest scan -> free account -> first transformation -> saved target -> week-1 challenge`를 단일 paid funnel로 묶고, 모든 step에 event를 심겠다. 지금은 ASO/ads보다 funnel surgery가 먼저다.
- [Evidence] Evidence from the codebase: analytics helper는 존재하지만 callsite가 없고(`frontend/src/components/Analytics.tsx:30-38`), growth가 가장 의존해야 할 `acquisition_source`, `paywall_viewed`, `checkout_started`, `purchase_completed` 이벤트는 구현 흔적이 없다.

### 4.4 Retention-focused Product Lead / Behavioral Designer

- [Inference] What this agent believes: 이 제품의 진짜 retention wedge는 “너의 실제 몸이 target image를 따라잡고 있다는 증거”다. calorie tracker나 challenge app이 아니다.
- [Evidence] What this agent thinks is broken: weekly check-in loop의 핵심 경로가 끊겨 있다. landing과 home는 weekly proof를 말하지만(`frontend/src/components/landing/WhyReturnSection.tsx:32-79`; `frontend/src/app/(dashboard)/home/page.tsx:63-99`), `gap-to-goal`은 broken key path가 있고(`backend/app/routers/body.py:690-777`), prompt는 full variant가 dead이며(`frontend/src/components/features/WeeklyRescanPrompt.tsx:106-220`), notifications는 실제 delivery가 없다(`backend/app/services/notification_service.py:96-148`).
- [Evidence] What this agent thinks is broken: `Goal Planner`와 `7-day challenge`는 실제로는 finish line이 아니라 side room이다. journey result는 둘 다 CTA로 주지만(`frontend/src/components/features/JourneyResult.tsx:172-239`), planner summary는 challenge start를 유도하지 않고(`frontend/src/app/(dashboard)/goal-planner/page.tsx:835-849`), challenge page는 active challenge가 없으면 fallback만 본다(`frontend/src/app/(dashboard)/challenge/page.tsx:84-101`).
- [Evidence] What this agent thinks is underrated: `progress photos`와 `weight projection`은 “내가 변하고 있다”를 증명하는 데이터 backbone이다(`frontend/src/app/(dashboard)/progress/page.tsx:270-580`; `backend/app/routers/weight.py:17-104`; `backend/app/services/weight_tracking_service.py:243-319`).
- [Inference] What this agent would do first: home를 “이번 주 check-in center”로 바꾸고, 다음 행동을 하나만 남기겠다. `scan if due`, `log weight if not due`, `check in challenge`, `compare proof`를 순서대로 제시해야 한다.
- [Evidence] Evidence from the codebase: `StreakBadge`는 home의 상징이지만 실제 행동과 연결되지 않는다(`frontend/src/components/features/StreakBadge.tsx:12-24`; `backend/app/routers/streaks.py:52-120`).

### 4.5 Principal Engineer / Architect

- [Inference] What this agent believes: 저장소는 rewrite가 필요한 상태는 아니다. 하지만 “작동하는 것처럼 보이는 broken contracts”가 몇 군데 있어서, product velocity보다 먼저 contract repair가 필요하다.
- [Evidence] What this agent thinks is broken: body router의 `user_profiles.eq("id")`는 confirmed defect고, payment credit contract는 confirmed runtime risk다(`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220`).
- [Evidence] What this agent thinks is broken: docs/migration contract도 drift가 있다. runtime은 `monthly_credits`, `bonus_credits`, `reset_date`와 RPC deduction을 기대하지만(`backend/app/services/payment_service.py:264-276`; `backend/app/services/usage_limiter.py:169-211`; `backend/supabase_credit_rpc.sql:1-50`), RLS fix migration은 `balance`만 가진 `user_credits`를 만든다(`docs/sql/FIX_RLS_MISSING_TABLES.sql:15-21`).
- [Evidence] What this agent thinks is broken: progress photos는 raw `image_base64 TEXT`를 DB에 넣는다(`backend/app/routers/progress_photos.py:23-32`; `backend/supabase_progress_photos.sql:1-10`). 이건 storage cost, payload size, list performance, deletion handling 모두에 불리하다.
- [Evidence] What this agent thinks is underrated: core architecture는 feature router 분리, RLS, rate limiting, upload limits, security headers가 이미 있다(`backend/app/main.py:47-94, 123-141`; `backend/supabase_schema.sql:133-205`).
- [Inference] What this agent would do first: 1) profile key helper 통합, 2) credit contract 정리, 3) analytics interface 추가, 4) notification delivery/scheduler বাস্ত화, 5) object storage refactor 순으로 가겠다.
- [Evidence] Evidence from the codebase: CI는 lint + Playwright smoke 중심이라 critical business flows를 보호하지 못한다(`.github/workflows/ci.yml:9-127`; `tests/e2e/smoke.spec.ts:5-154`; `tests/api/health.spec.ts:21-97`).

### 4.6 Data, Monetization, and Experimentation Lead

- [Inference] What this agent believes: 지금 팀은 거의 눈을 감고 제품을 움직이고 있다. score, pricing, onboarding, paywall, retention을 논할 데이터가 없다.
- [Evidence] What this agent thinks is broken: `trackEvent` callsite가 없고(`frontend/src/components/Analytics.tsx:30-38`; repo-wide `rg -n "trackEvent\\(" frontend/src` 결과 `frontend/src/components/Analytics.tsx:30`만 존재), durable analytics warehouse event도 없다. `journey_telemetry`와 `cost_tracker`는 process memory만 쓴다(`backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36`).
- [Evidence] What this agent thinks is broken: revenue measurement에 필요한 purchase state도 UI에서 회수되지 않는다. `/upgrade?success=true`와 `?credits=purchased`를 읽지 않으므로 success path event도, UX도 없다(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`).
- [Evidence] What this agent thinks is broken: free vs Pro vs credit pack packaging을 평가할 수 있는 basis가 없다. runtime credit costs와 FAQ/pricing copy가 다르고(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`; `frontend/src/lib/i18n/en.json:101-109, 819-822`), mobile yearly price도 다르다(`mobile/src/screens/PaywallScreen.tsx:46-48`; `frontend/src/app/(dashboard)/upgrade/page.tsx:51-54`).
- [Inference] What this agent thinks is underrated: guest scan, paywall, challenge, history, notification, share, planner save 등은 전부 measurement point가 명확하다. instrumentation만 깔면 실험 속도는 빠르게 회복된다.
- [Inference] What this agent would do first: event taxonomy를 web/client + backend/server 양쪽에 깔고, `anonymous_id`에서 `user_id`로 identity stitching을 붙인 뒤, activation-to-purchase funnel과 D1/D7/D30 cohort부터 보겠다.
- [Evidence] Evidence from the codebase: retention and monetization에 필요한 named events는 현재 구현 흔적이 없다. 따라서 어떤 논리든 대부분 가정 상태다.

## 5. Top 12 Problems Ranked by Impact

| Problem | Why it matters | Evidence | Severity | Confidence | Effort | Suggested fix | File paths / systems affected |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. `gap-to-goal` / goal save path uses wrong key | 핵심 retention state가 비어 버리면 weekly proof loop 전체가 무너진다. | [Evidence] `user_profiles.eq("id", current_user["id"])` is used in auto-save, read, and save-goal, while auth user id belongs in `user_id` (`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/app/middleware/auth_middleware.py:67-91`; `backend/supabase_schema.sql:8-10`) | 5 | 5 | S | profile access helper를 만들어 전부 `user_id` 기준으로 통일하고 regression test 추가 | `backend/app/routers/body.py:477-483, 690-777`; `backend/app/middleware/auth_middleware.py:67-91`; `backend/supabase_schema.sql:8-10` |
| 2. Checkout completion imports missing credit symbols | 결제 완료 후 credit 부여가 깨지면 revenue 신뢰가 무너지고 refund/support가 폭증한다. | [Evidence] backend payment service imports `add_credits`, `PRO_MONTHLY_CREDITS`, `FREE_MONTHLY_CREDITS` from usage limiter, but they do not exist (`backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220`) | 5 | 5 | M | credit contract를 한 파일/서비스로 재정의하고 webhook/purchase tests 추가 | `backend/app/services/payment_service.py:116-144`; `backend/app/services/usage_limiter.py:1-220` |
| 3. Product analytics are effectively absent | activation, retention, monetization 의사결정이 전부 감에 의존한다. | [Evidence] GA wrapper exists but no event callsites exist (`frontend/src/components/Analytics.tsx:30-38`; repo-wide `rg -n "trackEvent\\(" frontend/src` only matches `frontend/src/components/Analytics.tsx:30`). Server telemetry is in-memory only (`backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36`) | 5 | 5 | M | event taxonomy를 client/server에 도입하고 warehouse sink/BI까지 연결 | `frontend/src/components/Analytics.tsx:30-38`; `backend/app/services/journey_telemetry.py:6-8, 71-90`; `backend/app/services/cost_tracker.py:20-36` |
| 4. Weekly reminder system is not operational | retention promise를 UI만으로 팔고 실제 re-engagement를 못 보내면 돌아올 이유가 사라진다. | [Evidence] preferences and subscriptions persist, but sender logs `[DEV]` only and no scheduler exists in repo (`frontend/src/app/(dashboard)/profile/notifications/page.tsx:33-214`; `backend/app/services/notification_service.py:96-148`) | 4 | 5 | M | actual push provider + scheduled job + delivery/open events 추가, 없으면 promise 제거 | `frontend/src/app/(dashboard)/profile/notifications/page.tsx`, `backend/app/services/notification_service.py`, scheduler/infra |
| 5. Privacy/trust copy overpromises relative to implementation | body-image product에서 copy truthfulness 불일치는 conversion, refunds, legal risk를 동시에 만든다. | [Evidence] trust/FAQ say third parties never store and deletion is immediate (`frontend/src/lib/i18n/en.json:95-99, 803-806`), privacy says retention by third parties cannot be guaranteed and deletion is by request/email (`frontend/src/app/(legal)/privacy/page.tsx:109-176, 181-187, 206-223`) | 4 | 5 | M | truth-aligned copy, scoped promises, self-serve delete/export surfaces 추가 | `frontend/src/lib/i18n/en.json`, `frontend/src/app/(legal)/privacy/page.tsx`, profile/data-controls UX |
| 6. OAuth/auth flow drops original intent | guest wow 이후 auth로 넘어갈 때 context loss가 커서 activation이 새어 나간다. | [Evidence] guest flow ends at `/register` teaser (`frontend/src/app/try/page.tsx:345-383`), callback redirects only to `/home` or `/onboarding` (`frontend/src/app/(auth)/auth/callback/page.tsx:120-136`) | 4 | 4 | M | deep-link preserving `next` param + teaser resume state 구현 | auth pages, callback flow, CTA links |
| 7. `Goal Preview` CTA deep link is dead | home의 핵심 action이 wrong destination을 보내면 second-step conversion이 줄어든다. | [Evidence] home links `/body-scan#transformation`, but page ignores hash and defaults to `scan` (`frontend/src/app/(dashboard)/home/page.tsx:120-135`; `frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`) | 4 | 5 | S | hash/query-based tab selection or direct route split | `frontend/src/app/(dashboard)/home/page.tsx`, `frontend/src/app/(dashboard)/body-scan/page.tsx` |
| 8. `target_weight` is collected but not persisted | user가 적은 목표를 product가 버리면 personalization 신뢰가 떨어지고 plan coherence가 깨진다. | [Evidence] onboarding collects `goals.target_weight` and even warns on unsafe BMI, but `saveProfileAndGoals` only sends profile fields + `calorie_goal` (`frontend/src/app/(auth)/onboarding/page.tsx:63-79, 333-368`) | 4 | 5 | S | persist field or remove it until downstream use exists | `frontend/src/app/(auth)/onboarding/page.tsx`, profile schema/update path |
| 9. Full-body promise and runtime validation disagree | capture instructions가 measurement contract와 다르면 false rejection, user confusion, trust loss가 생긴다. | [Evidence] UI says “Upload a full-body photo” (`frontend/src/app/try/page.tsx:167-170`; `frontend/src/app/(dashboard)/body-scan/page.tsx:403-405`), authenticated runtime sends `framing: 'upper_body'` (`frontend/src/app/(dashboard)/body-scan/page.tsx:120, 162, 209, 287`) | 4 | 4 | S | product-wide framing contract를 하나로 통일하고 validation copy 재작성 | `frontend/src/app/try/page.tsx`, `frontend/src/app/(dashboard)/body-scan/page.tsx`, body photo quality rules |
| 10. Share flow points to protected URLs | virality/UGC loop가 거의 작동하지 않는다. | [Evidence] share and copy-link use `window.location.href` (`frontend/src/components/ui/ShareButtons.tsx:13-25`; `frontend/src/components/features/ShareableResultCard.tsx:62-93`), dashboard pages require auth (`frontend/src/middleware.ts:39-42`) | 3 | 5 | S | public-safe share landing page를 만들거나 share CTA를 임시 제거 | share components, routing, trust/legal policy |
| 11. Progress proof system is visually incomplete | progress photos를 저장해도 즉시 보이지 않으면 repeat value가 약해진다. | [Evidence] list endpoint does not return `image_base64`, so grid shows placeholder only (`backend/app/routers/progress_photos.py:40-54`; `frontend/src/app/(dashboard)/progress/page.tsx:421-424`). Compare payload also returns `None` metrics (`backend/app/routers/progress_photos.py:117-123`) | 3 | 5 | M | thumbnail/object storage refactor + compare metrics 계산 추가 | `backend/app/routers/progress_photos.py`, `backend/supabase_progress_photos.sql`, `frontend/src/app/(dashboard)/progress/page.tsx` |
| 12. Retention assets remain stranded (`streak`, `scan history`) | 이미 만든 자산이 재방문 유도에 전혀 기여하지 못하고 있다. | [Evidence] `streakApi.checkIn()` exists but no UI callsite (`frontend/src/lib/api/services.ts:327-330`; `backend/app/routers/streaks.py:52-120`; repo-wide `rg -n "checkIn\\(" frontend/src` 결과 없음). `getScanHistory()` exists with no frontend callsite (`frontend/src/lib/api/services.ts:158-171`; `backend/app/routers/body.py:649-683`) | 3 | 5 | S | core loop action에 연결하거나 surface를 숨겨 혼란을 줄일 것 | `frontend/src/components/features/StreakBadge.tsx`, `frontend/src/lib/api/services.ts`, `backend/app/routers/streaks.py`, `backend/app/routers/body.py` |

### 5A. Top 5 Reproducible Defects

#### Defect 1. Saved goal / `gap-to-goal` can silently miss the current user

- [Evidence] Reproduction steps:
  1. 로그인한 상태에서 transformation journey를 생성한다.
  2. 완료 후 home 또는 `gap-to-goal` surface를 다시 본다.
  3. `goal_image_url` 또는 `target_body_fat_percentage`가 비어 있거나 `gap`이 기대와 다르게 비어 있을 수 있다.
- [Evidence] Likely cause: body router가 `user_profiles`를 `id == current_user["id"]`로 읽고 쓴다. 하지만 middleware가 넣는 `current_user["id"]`는 `auth.users.id`다(`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/app/middleware/auth_middleware.py:67-91`; `backend/supabase_schema.sql:8-10`).
- [Inference] User-facing impact: 목표 이미지 저장, target BF, weekly gap narrative가 흔들리면서 제품의 중심 약속이 무너진다.
- [Inference] Release risk: High. retention, monetization, trust 전부 동시에 손상한다.

#### Defect 2. `Goal Preview` CTA opens the wrong state

- [Evidence] Reproduction steps:
  1. 로그인 후 `/home`으로 간다.
  2. `Goal Preview` card를 클릭한다.
  3. URL은 `/body-scan#transformation`이 되지만 page는 `Body Scan` tab으로 열린다.
- [Evidence] Likely cause: `HomePage`는 hash를 붙여 보내지만 `BodyScanPage`는 `activeTab` 초기값을 `'scan'`으로 두고 hash를 읽지 않는다(`frontend/src/app/(dashboard)/home/page.tsx:120-135`; `frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`).
- [Inference] User-facing impact: 가장 중요한 upsell action이 one click 늦어지고, 사용자는 product가 엉성하다고 느낀다.
- [Inference] Release risk: Medium. activation-to-preview conversion을 깎는다.

#### Defect 3. Onboarding `target_weight` is never saved

- [Evidence] Reproduction steps:
  1. 신규 사용자로 onboarding을 시작한다.
  2. `Target Weight (kg)`를 입력한다.
  3. onboarding을 완료한 뒤 profile/plan side에서 target weight를 확인하면 저장된 경로가 없다.
- [Evidence] Likely cause: `saveProfileAndGoals` payload에 `target_weight`가 빠져 있다(`frontend/src/app/(auth)/onboarding/page.tsx:63-79, 333-368`).
- [Inference] User-facing impact: personalization 신뢰가 내려가고, 사용자는 “내가 준 정보가 반영되지 않는다”고 느낀다.
- [Inference] Release risk: Medium. activation quality와 trust를 손상한다.

#### Defect 4. `/upgrade` does not acknowledge success

- [Evidence] Reproduction steps:
  1. `/upgrade`에서 subscription 또는 credit pack checkout을 시작한다.
  2. success URL로 `/upgrade?success=true` 또는 `/upgrade?credits=purchased`로 돌아온다.
  3. page는 이 query를 읽지 않아 success toast/banner/state refresh가 없다.
- [Evidence] Likely cause: success query를 생성만 하고 소비하지 않는다(`frontend/src/app/(dashboard)/upgrade/page.tsx:60-80`).
- [Inference] User-facing impact: 결제 직후 “돈은 나갔는데 뭐가 바뀌었는지 모르겠다”는 불신이 생긴다.
- [Inference] Release risk: High. support/refund risk를 키운다.

#### Defect 5. Share / copy-link sends outsiders to a protected page

- [Evidence] Reproduction steps:
  1. dashboard 안에서 result share 또는 copy-link를 누른다.
  2. 공유된 링크를 로그아웃된 브라우저에서 연다.
  3. middleware가 `/login`으로 보낸다.
- [Evidence] Likely cause: share logic가 `window.location.href`를 사용하고, dashboard route는 auth-protected다(`frontend/src/components/ui/ShareButtons.tsx:13-25`; `frontend/src/components/features/ShareableResultCard.tsx:89-93`; `frontend/src/middleware.ts:39-42`).
- [Inference] User-facing impact: virality가 끊기고 공유 의도가 즉시 좌절된다.
- [Inference] Release risk: Medium. growth loop가 작동하지 않는다.

## 6. What to Kill / What to Keep / What to Delay

### Kill

- [Inference] `AI extra modes first` 사고방식은 당장 접어야 한다. `enhancement` 같은 추가 generator surface는 존재하지만(`backend/app/routers/body.py:580-638`), core weekly proof loop가 연결되기 전에는 novelty만 늘린다.
- [Inference] unfinished mobile parity를 주력 전략처럼 다루는 것은 중단해야 한다. mobile paywall/body scan은 static shell이다(`mobile/src/screens/BodyScanScreen.tsx:11-24`; `mobile/src/screens/PaywallScreen.tsx:36-58`).
- [Inference] decorative retention 신호는 없애거나 숨겨야 한다. `streak`는 행동과 연결되지 않은 vanity badge다(`frontend/src/components/features/StreakBadge.tsx:12-24`; `backend/app/routers/streaks.py:52-120`).
- [Inference] “10 credits로 scan + preview 둘 다 된다” 같은 copy는 즉시 폐기해야 한다. runtime과 모순되는 messaging은 short-term conversion보다 long-term trust damage가 크다(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`; `frontend/src/lib/i18n/en.json:819-822`).

### Keep

- [Evidence] guest `/try` funnel은 유지해야 한다. activation hook로 가장 강하다(`frontend/src/app/try/page.tsx:35-114, 345-383`; `backend/app/routers/guest.py:106-145`).
- [Evidence] `Goal Planner`는 keep 대상이다. 이미 wizard, persistence, reload가 있어 conversion/depth layer로 훌륭하다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:40-98, 375-387, 698-849`; `backend/app/routers/goal_planner.py:202-264`).
- [Evidence] `Progress photos`와 `weight projection`은 keep 대상이다. proof backbone이기 때문이다(`frontend/src/app/(dashboard)/progress/page.tsx:270-580`; `backend/app/services/weight_tracking_service.py:243-319`).
- [Evidence] `7-day challenge`는 keep하되 secondary mechanic으로 써야 한다. 이미 daily check-in과 identity copy가 있다(`frontend/src/app/(dashboard)/challenge/page.tsx:103-176`; `backend/app/routers/seven_day_challenge.py:30-61, 166-223`).
- [Evidence] `AI coach chat`는 keep 대상이다. daily cap, history, coaching prompt, retrieval가 있다(`frontend/src/app/(dashboard)/chat/page.tsx:42-286`; `backend/app/services/rag_chat_service.py:17-179`은 이번 문서에서 직접 재인용하지 않았으므로 chat product surface 중심으로 keep 판단을 명시한다).

### Delay

- [Inference] public social sharing of body images는 trust/legal 정리 전까지 미뤄야 한다. 현재는 protected URL만 공유되고, body-image consent 문제도 정리되지 않았다(`frontend/src/components/ui/ShareButtons.tsx:13-25`; `frontend/src/components/features/ShareableResultCard.tsx:89-93`; `frontend/src/app/(legal)/privacy/page.tsx:109-176`).
- [Inference] advanced price experiments는 analytics 없이 미뤄야 한다. 지금은 packaging을 바꾸더라도 무엇이 나아졌는지 측정할 수 없다(`frontend/src/components/Analytics.tsx:30-38`; `backend/app/services/journey_telemetry.py:6-8`).
- [Inference] 더 많은 generator category (`beauty`, `fashion`) 확장은 늦춰야 한다. core thesis와 연결이 약하다(`backend/app/main.py:133-141`).

## 7. Next-Level Upgrade Strategy

### 7A. Forced Strategic Choice

- [Inference] Primary product thesis로 내가 고르는 것은 `progress proof/check-in coach`다.
- [Inference] Why this should lead: 현재 코드에서 실제로 묶을 수 있는 strongest asset set이 `guest scan hook -> weekly scan/gap-to-goal -> progress photos -> weight projection -> goal planner -> 7-day challenge -> coach chat`이기 때문이다(`frontend/src/app/try/page.tsx:35-114`; `frontend/src/app/(dashboard)/home/page.tsx:63-176`; `frontend/src/app/(dashboard)/progress/page.tsx:270-580`; `frontend/src/app/(dashboard)/goal-planner/page.tsx:698-849`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`; `frontend/src/app/(dashboard)/chat/page.tsx:42-286`).
- [Inference] Why `AI transformation demo` should be secondary: acquisition hook로는 강하지만 반복 사용 이유를 직접 만들지 못한다. 현재 guest funnel과 locked teaser가 이미 hook 역할을 하고 있다(`frontend/src/app/try/page.tsx:345-383`).
- [Inference] Why `goal-driven body planner` should be secondary: planner는 깊은 가치를 만들지만 7-step wizard라 entry product로는 무겁다(`frontend/src/app/(dashboard)/goal-planner/page.tsx:13-21, 417-849`).
- [Inference] Why `challenge/streak habit product` should be secondary or cut as lead: generic habit product로는 차별화가 약하고, 현재도 streak/challenge가 core measurement loop 없이 떠 있다(`frontend/src/components/features/StreakBadge.tsx:12-24`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`).

### 7.1 Hard Recommendation

- [Inference] Core user: 외모 중심 deadline이 있는 18+ 성인이다. 예를 들면 summer cut, wedding/photo shoot prep, reunion/wedding guest season, breakup/body recomp처럼 “내 몸이 실제로 바뀌는 증거”에 민감한 사람이다. guest/landing copy도 이미 이 방향으로 쓰여 있다(`frontend/src/lib/i18n/en.json:131-132, 800-800`; `frontend/src/components/landing/HeroSection.tsx:92-120`).
- [Inference] Core promise: “너의 goal body를 believable하게 먼저 보여주고, 그다음 네 실제 몸이 그 이미지를 따라잡고 있는지 매주 증명해 준다.”
- [Inference] Core loop: `guest scan or transformation hook -> account creation -> set target -> weekly scan/check-in -> gap-to-goal update -> progress photo or weight log -> coach or plan adjustment -> next weekly proof`. 이 loop는 현재 코드 자산을 최소 수정으로 연결할 수 있다(`frontend/src/app/try/page.tsx:35-114, 345-383`; `frontend/src/app/(dashboard)/home/page.tsx:76-176`; `frontend/src/app/(dashboard)/progress/page.tsx:270-580`; `frontend/src/app/(dashboard)/challenge/page.tsx:103-176`).
- [Inference] Why a user should come back tomorrow: 아직 weekly rescan day가 아니면 challenge check-in, weight log, coach follow-up, meal/workout adherence check가 있어야 한다. 지금 코드엔 challenge, weight logs, chat, planner가 이미 있다(`frontend/src/app/(dashboard)/challenge/page.tsx:117-159`; `backend/app/routers/weight.py:17-104`; `frontend/src/app/(dashboard)/chat/page.tsx:122-286`; `frontend/src/app/(dashboard)/goal-planner/page.tsx:698-849`).
- [Inference] Why they should still be here in 30 days: 월 단위 누적 proof asset이 생겨야 한다. `scan_history`, `progress photos`, `weight projection`, saved plan, challenge history가 “내 몸이 바뀌고 있다”는 자기증거를 만들어야 한다(`backend/app/routers/body.py:649-683`; `backend/app/routers/progress_photos.py:11-123`; `backend/app/services/weight_tracking_service.py:243-319`; `backend/app/routers/goal_planner.py:202-264`).
- [Inference] The most defensible wedge: 단순 AI rendering이 아니라 `my photo -> my target -> my weekly proof -> my plan correction`의 closed loop다. generic calorie app도, generic image generator도 이 조합을 쉽게 못 한다.
- [Inference] Monetization model that fits: `Free guest scan + free account + first preview`로 activation을 만든 뒤, `Pro subscription`이 weekly proof loop, progress compare, coach, reminders, unlimited/reasonable scans를 책임져야 한다. credits는 high-cost extra generations에만 남겨야 한다. 지금처럼 core loop와 credits를 섞으면 retention이 깨진다(`frontend/src/app/(dashboard)/home/page.tsx:155-176`; `frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`; `frontend/src/lib/i18n/en.json:101-109`).
- [Inference] Trust/privacy posture needed: body-image software로서 “scoped promise + explicit consent + self-serve delete/export + vendor transparency + no public sharing by default + guest 18+ gate + non-consensual upload friction”가 필요하다. 현재는 consent pieces는 일부 있지만 truthfulness와 self-serve control이 부족하다(`backend/app/routers/auth.py:25-36, 64-85`; `frontend/src/app/try/page.tsx:246-255`; `frontend/src/app/(legal)/privacy/page.tsx:109-176, 206-223`; `frontend/src/app/(dashboard)/profile/page.tsx:108-124`).

### 7B. Unit Economics & Operations

- [Evidence] Inference cost: transformation journey는 body-fat estimate 뒤에 4-stage image generation을 호출한다(`backend/app/routers/body.py:389-457`). 그런데 cost tracking은 `COST_PER_CALL` map + in-memory counter뿐이라 실제 margin을 durable하게 모른다(`backend/app/services/cost_tracker.py:7-36`). [Inference] 지금 pricing은 true cost observability 없이 굴러가고 있다.
- [Evidence] Storage cost: progress photos는 raw `image_base64 TEXT`를 DB에 저장한다(`backend/app/routers/progress_photos.py:23-32`; `backend/supabase_progress_photos.sql:1-10`). [Inference] object storage ref 없이 base64를 계속 쌓으면 DB size, query latency, backup burden이 불필요하게 커진다.
- [Evidence] Retry/failure cost: 첫 guest `/validate-photo`는 cold start가 1-3+분 걸릴 수 있다고 backend가 직접 경고한다(`backend/app/main.py:24-30`). journey telemetry도 external analytics가 아니라 in-process observation이다(`backend/app/services/journey_telemetry.py:1-8, 71-90`). [Inference] failure/retry rate를 제대로 볼 수 없어 infra tuning과 vendor failover가 어렵다.
- [Evidence] Paywall leakage: free/FAQ copy는 “10 credits로 scan + transformation preview 충분”이라 하고(`frontend/src/lib/i18n/en.json:819-822`), runtime은 scan 10 / journey 30이라 다르다(`frontend/src/app/(dashboard)/body-scan/page.tsx:73-75`). checkout success UI도 없고(`frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`), auth callback은 original intent를 버린다(`frontend/src/app/(auth)/auth/callback/page.tsx:120-136`). [Inference] leakage는 측정되지 않지만 구조적으로 강하다.
- [Evidence] Refund risk: web yearly는 `$89.99`인데(`frontend/src/app/(dashboard)/upgrade/page.tsx:51-54`), mobile yearly는 `$79.99`다(`mobile/src/screens/PaywallScreen.tsx:46-48`). [Inference] channel inconsistency는 CS와 refund pressure를 높인다.
- [Evidence] Abuse risk: guest endpoints는 IP rate limit이 있고(`backend/app/routers/guest.py:50-52, 106-108`), self-photo checkbox도 있다(`frontend/src/app/try/page.tsx:246-255`). [Risk] 하지만 durable abuse analytics, content moderation pipeline, identity verification는 보이지 않는다. 특히 guest age input은 `10-100` 범위라 under-18 upload를 code level에서 막지 못한다(`frontend/src/app/try/page.tsx:233-242`).
- [Evidence] Support burden: in-app browser OAuth workaround, email-based privacy requests, invisible upgrade success, non-operational push settings가 모두 support 티켓을 만들 구조다(`frontend/src/components/features/SocialLoginButtons.tsx:52-120`; `frontend/src/app/(legal)/privacy/page.tsx:220-223`; `frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`; `backend/app/services/notification_service.py:134-145`).
- [Assumption] 실제 vendor invoice, refund rate, gross margin, support ticket volume은 repo만으로는 측정할 수 없다. 그러므로 여기서의 economics 평가는 구조적 리스크 진단이지 실측 수치가 아니다.

### 7C. Trust & Safety Red-Team

- [Evidence] Minors: registered path는 18+ gating이 있다(`backend/app/routers/auth.py:32-36`). [Risk] 하지만 guest path는 age input이 `min={10}`이고 account 없이 body photo upload를 허용한다(`frontend/src/app/try/page.tsx:233-242`; `backend/app/routers/guest.py:106-145`). 이건 “18+ product”라는 선언과 실제 guest funnel이 어긋난다.
- [Evidence] Non-consensual uploads / partner-ex uploads: current guardrail은 self-photo checkbox뿐이다(`frontend/src/app/try/page.tsx:246-255`; `frontend/src/app/(dashboard)/body-scan/page.tsx:449-455`). [Risk] 타인 업로드를 차단하는 identity or liveness or escalation path가 없다.
- [Evidence] Body dysmorphia risk: onboarding은 low BMI/low calories warning을 일부 준다(`frontend/src/app/(auth)/onboarding/page.tsx:333-358`), 하지만 product message의 중심은 “future body”와 target visual이다(`frontend/src/components/landing/HeroSection.tsx:92-120`). [Risk] extreme goal-seeking user에게 cooling friction, support redirect, crisis copy가 부족하다.
- [Evidence] Sexualized output risk: local diffusion backends explicitly disable `safety_checker` and set `requires_safety_checker=False` (`backend/app/services/diffusion/sd15_cpu.py:56-61`; `backend/app/services/diffusion/sd2_cpu.py:56-61`). [Risk] 별도 image moderation pipeline이 저장소에서 확인되지 않아 sensitive-body generation에서 정책 drift 위험이 있다.
- [Evidence] Deletion truthfulness: trust copy는 “When you delete, it's gone — no hidden copies, no backups retained”라고 말하지만(`frontend/src/lib/i18n/en.json:97-99`), privacy policy는 backup 90일 유지와 third-party deletion non-guarantee를 명시한다(`frontend/src/app/(legal)/privacy/page.tsx:181-187`). [Risk] 이 mismatch는 legal/compliance 리스크다.
- [Evidence] Vendor data handling: privacy policy는 OpenAI, Gemini, Claude, Replicate, Supabase, Stripe, RevenueCat에 어떤 데이터가 가는지 적고 있다(`frontend/src/app/(legal)/privacy/page.tsx:109-163`). [Inference] vendor transparency는 존재하지만, user-facing consent scope와 storage claim이 이 목록과 정렬돼 있지 않다.
- [Evidence] Consent/storage mismatch: guest surface는 “analyzed once and never stored”라고 말한다(`frontend/src/app/try/page.tsx:196-199`), authenticated product/privacy는 originals may be stored라고 말한다(`frontend/src/app/(legal)/privacy/page.tsx:173-176`). [Inference] 이 문구는 guest-only promise인지 전체 product promise인지 스코프를 분리해서 써야 한다.
- [Evidence] No self-serve data controls: privacy rights는 email contact를 요구한다(`frontend/src/app/(legal)/privacy/page.tsx:206-223`), profile hub는 notifications와 logout만 상단 action으로 제공한다(`frontend/src/app/(dashboard)/profile/page.tsx:108-124`). [Risk] body-image product로서는 self-serve delete/export absence가 약하다.

## 8. 30-Day Execution Plan

### Week 1: highest-leverage fixes

| Exact tasks | Why now | Owner type | Likely files/modules to touch | Expected impact |
| --- | --- | --- | --- | --- |
| [Evidence] `user_profiles` key mismatch를 전부 `user_id` 기준으로 수정하고 test 추가 | [Inference] core retention state defect라서 가장 먼저 막아야 한다 | engineering | `backend/app/routers/body.py:477-483, 690-777`, shared profile access helper, regression tests | goal image, target BF, gap-to-goal 복구 |
| [Evidence] payment credit contract 정리: missing import 제거, `user_credits` schema contract 단일화, webhook test 추가 | [Inference] 돈이 걸린 broken path는 즉시 막아야 한다 | engineering | `backend/app/services/payment_service.py:116-144, 264-276`, `backend/app/services/usage_limiter.py:1-220`, `backend/supabase_credit_rpc.sql:1-50`, migration docs/tests | purchase failure/support risk 감소 |
| [Evidence] `Goal Preview` hash routing, `/upgrade` success state, onboarding `target_weight` persistence를 한번에 수정 | [Inference] low-effort, high-signal funnel leaks다 | engineering + product | `frontend/src/app/(dashboard)/home/page.tsx`, `frontend/src/app/(dashboard)/body-scan/page.tsx`, `frontend/src/app/(dashboard)/upgrade/page.tsx`, `frontend/src/app/(auth)/onboarding/page.tsx` | activation friction 감소 |
| [Evidence] pricing/credit copy를 runtime truth에 맞춰 정렬 | [Inference] trust leak와 refund risk를 바로 줄인다 | product + growth | `frontend/src/lib/i18n/en.json`, paywall/FAQ/profile copy | promise-reality mismatch 감소 |
| [Evidence] analytics skeleton 도입: common event payload, `anonymous_id`, server-side success/fail events | [Inference] Week 2 이후 실험 전제조건이다 | data + engineering | `frontend/src/components/Analytics.tsx`, auth/try/home/body-scan/upgrade pages, backend routers | funnel blindness 해소 시작 |

### Week 2: activation and retention improvements

| Exact tasks | Why now | Owner type | Likely files/modules to touch | Expected impact |
| --- | --- | --- | --- | --- |
| [Evidence] OAuth return continuity 구현: guest teaser or intended destination 복구 | [Inference] wow-to-account conversion 회복 | engineering | auth callback flow, CTA links, auth context | auth 이탈 감소 |
| [Evidence] `WeeklyRescanPrompt` full variant를 actionable card로 바꾸고 next-best action logic 추가 | [Inference] home을 real check-in center로 만들기 위한 첫 단계 | product + engineering | `frontend/src/components/features/WeeklyRescanPrompt.tsx`, `frontend/src/app/(dashboard)/home/page.tsx` | repeat use 증가 |
| [Evidence] journey result -> challenge start, planner summary -> challenge start를 연결 | [Inference] planner/challenge를 side room에서 loop step으로 승격 | product + engineering | `frontend/src/components/features/JourneyResult.tsx`, `frontend/src/app/(dashboard)/goal-planner/page.tsx`, challenge API wiring | week-1 retention loop 형성 |
| [Evidence] scan history UI와 progress thumbnails/compare metrics를 연결 | [Inference] proof value가 보여야 반복 동기가 생긴다 | engineering + design | `frontend/src/app/(dashboard)/progress/page.tsx`, `backend/app/routers/progress_photos.py`, `frontend/src/lib/api/services.ts`, scan history surface | visual proof 강화 |
| [Evidence] streak를 real actions에 연결하거나 잠시 숨김 | [Inference] fake gamification은 독이다 | product + engineering | `frontend/src/components/features/StreakBadge.tsx`, `backend/app/routers/streaks.py`, core action flows | retention signal 신뢰도 개선 |

### Week 3: monetization and growth systems

| Exact tasks | Why now | Owner type | Likely files/modules to touch | Expected impact |
| --- | --- | --- | --- | --- |
| [Inference] pricing/packaging를 `subscription = proof loop`, `credits = extra gen`로 재정의 | [Inference] product thesis와 billing을 일치시켜야 한다 | product + growth | paywall copy, FAQ, credit cost display, subscription hooks | conversion clarity 상승 |
| [Evidence] paywall events, checkout events, purchase events, cancellation events를 end-to-end로 심기 | [Inference] monetization experiments 전 필수 | data + engineering | upgrade page, payment backend, analytics sink | monetization visibility 확보 |
| [Evidence] external share flow를 고치거나 임시 비활성화 | [Inference] broken virality는 오히려 신뢰 손상 | product + engineering + trust/legal | share components, routing, public-safe landing design | growth surface 정리 |
| [Evidence] mobile strategy 결정: unfinished paywall/body scan 숨김 또는 explicit beta banner | [Inference] channel confusion 축소 | product + engineering | `mobile/src/navigation/RootNavigator.tsx`, `mobile/src/screens/BodyScanScreen.tsx`, `mobile/src/screens/PaywallScreen.tsx` | support burden 감소 |
| [Inference] landing/ASA/UGC messaging를 “preview + prove it weekly”로 통일 | [Inference] acquisition promise와 retention value alignment | growth + design | landing copy, ad hooks, app store copy if applicable | paid traffic 효율 개선 |

### Week 4: instrumentation, experiments, and hardening

| Exact tasks | Why now | Owner type | Likely files/modules to touch | Expected impact |
| --- | --- | --- | --- | --- |
| [Evidence] scheduled weekly reminder job + actual push sender 구현 | [Inference] re-engagement loop 완성 | engineering + infra | `backend/app/services/notification_service.py`, scheduler infra, notification routes | D7/D30 lift potential |
| [Evidence] trust/legal controls 추가: guest 18+ gate, self-serve delete/export entry, consent scope copy refresh | [Inference] sensitive-image product로서 minimum bar 충족 | trust/legal + product + engineering | `frontend/src/app/try/page.tsx`, profile/legal pages, backend auth/data controls | trust/compliance risk 감소 |
| [Evidence] durable ops instrumentation: cost, failure, retry, success dashboards | [Inference] inference-heavy product의 gross margin/quality 관리 시작 | data + infra | `backend/app/services/cost_tracker.py`, `backend/app/services/journey_telemetry.py`, analytics warehouse | operations visibility 확보 |
| [Evidence] business-critical tests를 CI에 추가: payments, goal save, upgrade success, deep links, reminder trigger | [Inference] fix를 계속 유지하려면 test shield가 필요 | engineering | `.github/workflows/ci.yml`, Playwright/API tests, backend unit/integration tests | release confidence 상승 |

## 9. Engineering Action Plan

1. [Refactor] `user_profiles` 접근을 helper/service로 통합하고 `id` vs `user_id` 혼용을 제거해야 한다. [Evidence] 현재 body router와 weight tracking service가 서로 다른 key 습관을 갖고 있다(`backend/app/routers/body.py:477-483, 700-710, 772-775`; `backend/app/services/weight_tracking_service.py:155-158, 256-259`).
2. [Infra] billing/credits contract를 단일 source of truth로 정리해야 한다. [Evidence] payment service, usage limiter, credit RPC, RLS fix migration이 서로 다른 world model을 갖는다(`backend/app/services/payment_service.py:116-144, 264-276`; `backend/app/services/usage_limiter.py:169-211`; `backend/supabase_credit_rpc.sql:1-50`; `docs/sql/FIX_RLS_MISSING_TABLES.sql:15-21`).
3. [Analytics] client/server 공통 event SDK를 추가하고 funnel-critical paths에 일관된 property set을 붙여야 한다. [Evidence] 현재 analytics helper는 empty shell이다(`frontend/src/components/Analytics.tsx:30-38`).
4. [New feature] `BodyScanPage`는 hash/query로 tab을 받아야 하고, `/upgrade`는 success query를 해석해야 한다. [Evidence] current state is dead link + silent success (`frontend/src/app/(dashboard)/body-scan/page.tsx:29-40`; `frontend/src/app/(dashboard)/upgrade/page.tsx:56-87`).
5. [Refactor] onboarding goal fields와 profile goal fields를 하나의 typed contract로 묶어야 한다. [Evidence] `target_weight`는 UI에만 있고 persistence가 없다(`frontend/src/app/(auth)/onboarding/page.tsx:63-79, 333-368`).
6. [Infra] notification system에 real sender와 scheduler를 넣고 delivery/open instrumentation을 붙여야 한다. [Evidence] current implementation is storage-only + dev log only (`backend/app/services/notification_service.py:55-148`).
7. [New feature] `scan history`, `saved plan`, `challenge start`, `streak check-in`을 하나의 “next action” orchestration layer로 연결해야 한다. [Evidence] assets exist but are disconnected (`backend/app/routers/body.py:649-683`; `backend/app/routers/goal_planner.py:202-264`; `backend/app/routers/streaks.py:52-120`).
8. [Refactor / risky] progress photos를 `image_base64 TEXT`에서 object storage reference + thumbnail model로 옮겨야 한다. [Risk] data migration과 deletion semantics가 따라오므로 migration plan과 backfill test가 먼저 필요하다(`backend/app/routers/progress_photos.py:23-32`; `backend/supabase_progress_photos.sql:1-10`).
9. [Trust / risky] generated image safety pipeline를 분리해야 한다. [Evidence] local diffusion backends disable `safety_checker` (`backend/app/services/diffusion/sd15_cpu.py:56-61`; `backend/app/services/diffusion/sd2_cpu.py:56-61`). [Risk] moderation policy 설계 없이 public growth/share를 밀면 위험하다.
10. [Testing] payments, goal save, OAuth return continuity, guest age gate, share routing, reminder trigger는 shipping 전에 test shield가 필요하다. [Evidence] current CI is mostly smoke/legal/auth coverage (`.github/workflows/ci.yml:9-127`; `tests/e2e/smoke.spec.ts:5-154`; `tests/api/health.spec.ts:21-97`).

[Risk] Feature flags로 보호해야 할 영역:

- [Risk] 새 home orchestration / weekly prompt logic
- [Risk] paywall packaging/copy experiments
- [Risk] notification delivery rollout
- [Risk] public share landing
- [Risk] progress photo storage migration

[Risk] Tests before shipping:

- [Risk] `gap-to-goal` / `save-goal` regression tests
- [Risk] webhook purchase completion and credit grant tests
- [Risk] `/body-scan#transformation` deep-link test
- [Risk] `/upgrade?success=true` success-state test
- [Risk] onboarding goal persistence test
- [Risk] notification schedule + delivery dry-run test

## 10. Metrics and Instrumentation Spec

[Inference] 공통 규칙:

- [Inference] `acquisition_source`, `utm_*`, `anonymous_id`, `user_id`, `session_id`, `app_platform`, `app_version`, `locale`, `plan_tier`, `credits_balance`, `experiment_assignments`는 가능한 모든 event에 공통 property로 붙여야 한다.
- [Inference] UI start/view events는 client에서, success/failure/purchase events는 server에서 emit하는 hybrid 모델이 맞다.
- [Inference] `d1_retained`, `d7_retained`, `d30_retained`는 raw click event가 아니라 identity-stitched derived event 또는 warehouse metric으로 계산해야 한다.

| event name | trigger | properties | why it matters |
| --- | --- | --- | --- |
| `acquisition_source` | first web session or first authenticated session when attribution is known | `anonymous_id`, `utm_source`, `utm_medium`, `utm_campaign`, `referrer`, `landing_path`, `device_type` | first-touch attribution 없이는 paid/growth ROI를 판단할 수 없다 |
| `onboarding_started` | user enters `/onboarding` or starts post-auth profile completion | `user_id`, `entry_path`, `auth_method`, `has_guest_scan_context`, `acquisition_source` | guest wow가 actual setup로 이어지는지 본다 |
| `onboarding_completed` | onboarding final save succeeds | `user_id`, `steps_completed`, `target_weight_present`, `calorie_goal_present`, `time_to_complete_sec` | onboarding completion rate와 data quality를 본다 |
| `photo_upload_started` | user opens picker/camera and selects or captures a photo | `surface`, `flow` (`guest_scan`, `body_scan`, `journey`, `progress_photo`), `capture_method`, `auth_state` | upload friction과 surface별 abandonment를 본다 |
| `photo_upload_succeeded` | photo passes local/client preprocessing and reaches ready state | `surface`, `flow`, `file_size_kb`, `image_width`, `image_height`, `auth_state` | upload bottleneck과 device quality를 본다 |
| `photo_upload_failed` | upload/compression/read fails before generation | `surface`, `flow`, `error_code`, `error_message`, `file_size_kb`, `auth_state` | acquisition/retention loss 원인을 본다 |
| `transformation_generation_started` | journey or preview generation request is sent | `user_id`, `surface`, `flow`, `target_bf`, `current_bf_known`, `credit_cost`, `plan_tier` | generation demand와 paywall pressure를 본다 |
| `transformation_generated` | backend returns successful result | `user_id`, `flow`, `latency_ms`, `stage_count`, `credits_charged`, `current_bf`, `target_bf`, `provider_stack` | wow output quality와 cost/latency를 본다 |
| `transformation_failed` | backend returns failure for journey/preview | `user_id`, `flow`, `error_code`, `error_message`, `latency_ms`, `provider_stack` | failure cost와 refund risk를 본다 |
| `transformation_viewed` | result UI is actually rendered and stays visible | `user_id`, `flow`, `time_from_generate_ms`, `cta_shown` (`planner`, `challenge`, `share`, `upgrade`) | 생성 성공과 실제 소비를 구분한다 |
| `save_tapped` | user taps save on plan/result/card | `user_id`, `surface`, `artifact_type` (`goal_plan`, `share_card`, `goal_image`) | 무엇이 sticky asset인지 본다 |
| `share_tapped` | user taps any share or copy-link action | `user_id`, `surface`, `share_target`, `artifact_type`, `public_safe` | virality surface가 실제로 쓰이는지 본다 |
| `paywall_viewed` | upgrade/paywall modal or page appears | `user_id`, `surface`, `entry_trigger`, `credits_balance`, `plan_tier`, `acquisition_source` | paywall timing과 trigger 품질을 본다 |
| `checkout_started` | checkout session creation succeeds and user is redirected | `user_id`, `surface`, `product_type` (`subscription`, `credit_pack`), `price_id`, `displayed_price`, `credits_balance` | offer별 intent와 purchase rate를 본다 |
| `purchase_completed` | webhook or verified purchase marks success | `user_id`, `product_type`, `price_id`, `revenue`, `currency`, `payment_provider`, `plan_tier_after` | actual revenue event의 source of truth다 |
| `subscription_canceled` | subscription status moves to canceled | `user_id`, `cancel_surface`, `plan_tier_before`, `tenure_days`, `credits_remaining` | churn reason analysis의 출발점이다 |
| `d1_retained` | derived: user has a qualifying session on day 1 after first value event | `user_id`, `cohort_date`, `first_value_event`, `acquisition_source` | activation quality를 본다 |
| `d7_retained` | derived day-7 retention | `user_id`, `cohort_date`, `first_value_event`, `acquisition_source` | weekly loop가 살아 있는지 본다 |
| `d30_retained` | derived day-30 retention | `user_id`, `cohort_date`, `first_value_event`, `plan_tier` | subscription-fit을 본다 |
| `repeat_generation` | user performs second or later journey/preview generation | `user_id`, `generation_count_lifetime`, `days_since_last_generation`, `surface` | novelty tool인지 habit tool인지 판단한다 |
| `progress_checkin` | user submits challenge check-in, weight log, or weekly scan check-in | `user_id`, `checkin_type`, `challenge_active`, `weight_present`, `body_fat_present`, `days_since_last_checkin` | daily/weekly compliance loop를 측정한다 |
| `history_viewed` | user opens history/progress timeline/scan history | `user_id`, `history_type`, `item_count`, `has_comparison_data` | proof assets의 소비를 본다 |
| `notification_received` | push/email is delivered successfully | `user_id`, `channel`, `campaign_type`, `scheduled_at`, `days_since_last_scan` | reminder system quality를 본다 |
| `notification_opened` | user opens app/site from a notification | `user_id`, `channel`, `campaign_type`, `deep_link`, `days_since_last_session` | re-engagement effectiveness를 본다 |
| `reengagement_session` | session starts within attribution window of reminder/reactivation campaign | `user_id`, `source_event` (`notification_opened`, `email_clicked`, `retargeting_click`), `campaign_type` | dormant user recovery를 본다 |

[Inference] 추가 권장 event:

- [Inference] `guest_scan_started`
- [Inference] `guest_scan_completed`
- [Inference] `oauth_login_started`
- [Inference] `oauth_login_completed`
- [Inference] `goal_plan_saved`
- [Inference] `challenge_started`
- [Inference] `streak_checked_in`

## 11. First 3 Moves

### If I only do 3 things this month, do these:

- [Inference] `gap-to-goal` / goal save / checkout credit contract를 먼저 고쳐라. 이 두 군데는 제품의 반복 가치와 돈의 신뢰를 동시에 잡아먹는다(`backend/app/routers/body.py:477-483, 690-777`; `backend/app/services/payment_service.py:116-144`).
- [Inference] `progress proof/check-in coach` thesis에 맞게 home, prompt, challenge, planner, progress를 하나의 loop로 연결하라. 새 기능이 아니라 existing asset 연결이 우선이다(`frontend/src/app/(dashboard)/home/page.tsx:76-176`; `frontend/src/app/(dashboard)/goal-planner/page.tsx:698-849`; `frontend/src/app/(dashboard)/challenge/page.tsx:84-176`; `frontend/src/app/(dashboard)/progress/page.tsx:299-580`).
- [Inference] analytics taxonomy를 이번 달 안에 깔아라. 지금은 무엇이 activation, churn, purchase를 만드는지 볼 수 없다(`frontend/src/components/Analytics.tsx:30-38`; `backend/app/services/journey_telemetry.py:6-8`).

### What I would stop building immediately:

- [Inference] 더 많은 novelty generators
- [Inference] unfinished mobile parity
- [Inference] decorative streak/gamification without connected actions
- [Inference] public body-image sharing before trust/legal controls
- [Inference] pricing experiments before analytics and copy truth alignment

### What I would personally implement first in this codebase:

- [Inference] `backend/app/routers/body.py:477-483, 690-777`의 `user_profiles` key path bug fix와 regression test
- [Inference] `backend/app/services/payment_service.py:116-144, 264-276` / `backend/app/services/usage_limiter.py:1-220` / `user_credits` contract 통합
- [Inference] `BodyScanPage` hash routing + `/upgrade` success handling + onboarding `target_weight` persistence
- [Inference] core event taxonomy plumbing in `/try`, `/home`, `/body-scan`, `/upgrade`, purchase webhook
- [Inference] `WeeklyRescanPrompt` actionable rewrite와 challenge/plan/progress next-step orchestration

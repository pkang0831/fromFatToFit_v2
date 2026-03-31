-- =============================================================================
-- Supabase → SQL Editor 에 붙여 넣어 실행하는 QA 보조 스크립트
-- =============================================================================
--
-- [중요] 비밀번호가 있는 Auth 사용자(이메일 로그인)는
--        이 SQL만으로는 만들 수 없습니다. 비밀번호 해시는 auth 스키마에서
--        GoTrue가 관리하므로, 반드시 아래 ①을 먼저 하세요.
--
-- ① Auth 사용자 만들기 (둘 중 하나)
--    A) Dashboard → Authentication → Users → Add user → Email / Password 입력
--    B) 로컬에서: scripts/supabase_create_qa_email_user.py (SERVICE_ROLE + QA_EMAIL/QA_PASSWORD)
--
-- ② 이 파일의 이메일만 본인 QA 계정으로 바꾼 뒤, 아래 블록을 순서대로 실행
--
-- =============================================================================

-- ── 0) 대상 이메일이 auth에 있는지 확인 (없으면 ①부터) ─────────────────────
SELECT id, email, email_confirmed_at, created_at
FROM auth.users
WHERE email = 'you@example.com';  -- ← 수정

-- ── 1) public.user_profiles 에 행이 없으면 생성 (Auth에는 있는데 앱 프로필만 없을 때) ──
INSERT INTO public.user_profiles (
  user_id,
  email,
  premium_status,
  onboarding_completed,
  created_at
)
SELECT
  u.id,
  u.email,
  FALSE,
  FALSE,
  NOW()
FROM auth.users AS u
LEFT JOIN public.user_profiles AS p ON p.user_id = u.id
WHERE u.email = 'you@example.com'  -- ← 수정
  AND p.id IS NULL;

-- ── 2) (선택) QA에서 온보딩 스킵하고 바로 홈 쓰려면 true 로 ─────────────────
-- UPDATE public.user_profiles
-- SET onboarding_completed = TRUE
-- WHERE email = 'you@example.com';

-- ── 3) 결과 확인 ────────────────────────────────────────────────────────────
SELECT user_id, email, onboarding_completed, premium_status, created_at
FROM public.user_profiles
WHERE email = 'you@example.com';  -- ← 수정

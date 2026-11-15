-- Run in Supabase → SQL Editor
-- Use when: auth.users 에는 있는데 public.user_profiles 행이 없어서 앱이 비는 경우
-- (이메일/비밀번호 계정은 대시보드 Authentication → Users 로 만들거나
--  scripts/supabase_create_qa_email_user.py 로 만드는 것을 권장)

-- 1) 특정 이메일에 대해 프로필이 없으면 한 줄 삽입
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
WHERE u.email = 'you@example.com'  -- ← 여기만 본인 이메일로 바꿈
  AND p.id IS NULL;

-- 2) 삽입/스키마 확인
SELECT user_id, email, onboarding_completed, created_at
FROM public.user_profiles
WHERE email = 'you@example.com';

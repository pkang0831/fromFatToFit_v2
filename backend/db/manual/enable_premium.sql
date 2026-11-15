-- Temporarily enable premium for testing
-- Run this in Supabase SQL Editor

-- Update user profile to premium status
UPDATE user_profiles 
SET premium_status = true
WHERE email = 'pkang0831@gmail.com';

-- Reset all usage limits
DELETE FROM usage_limits 
WHERE user_id IN (
  SELECT user_id FROM user_profiles WHERE email = 'pkang0831@gmail.com'
);

-- Verify the update
SELECT 
  email, 
  premium_status,
  full_name
FROM user_profiles 
WHERE email = 'pkang0831@gmail.com';

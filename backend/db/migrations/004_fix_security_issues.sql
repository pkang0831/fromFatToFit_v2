-- ===================================================================
-- 🔒 SECURITY FIX: Function Search Path & Leaked Password Protection
-- ===================================================================
-- Run this in Supabase SQL Editor to fix security vulnerabilities
-- ===================================================================

-- Fix 1: Re-create update_updated_at_column function with secure search_path
-- Drop the existing function first
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Create secure version with explicit search_path
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp  -- Explicitly set search_path for security
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Recreate all triggers that use this function
-- User Profiles
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- User Subscriptions
DROP TRIGGER IF EXISTS update_user_subscriptions_updated_at ON user_subscriptions;
CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Usage Limits
DROP TRIGGER IF EXISTS update_usage_limits_updated_at ON usage_limits;
CREATE TRIGGER update_usage_limits_updated_at
    BEFORE UPDATE ON usage_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Daily Summaries
DROP TRIGGER IF EXISTS update_daily_summaries_updated_at ON daily_summaries;
CREATE TRIGGER update_daily_summaries_updated_at
    BEFORE UPDATE ON daily_summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- ✅ Security Issue 1 FIXED
-- ===================================================================

-- Note for Issue 2 (Leaked Password Protection):
-- This must be enabled in the Supabase Dashboard:
-- 1. Go to Authentication → Policies
-- 2. Enable "Leaked Password Protection"
-- 3. This will check passwords against HaveIBeenPwned database
-- ===================================================================

-- Migration: Add consent tracking and onboarding columns to user_profiles
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- Date: 2026-02-26

-- Add consent tracking columns
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS consent_terms_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS consent_privacy_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS consent_sensitive_data_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS consent_age_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS consent_version TEXT;

-- Add onboarding tracking
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;

-- Add target weight and body fat goals
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS target_weight_kg DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS target_body_fat_percentage DECIMAL(4,1);

-- Verify columns were added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user_profiles'
  AND column_name LIKE 'consent%' OR column_name IN ('onboarding_completed', 'target_weight_kg', 'target_body_fat_percentage')
ORDER BY ordinal_position;

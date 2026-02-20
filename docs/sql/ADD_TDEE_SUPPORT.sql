-- ===================================================================
-- Add TDEE Support to User Profiles
-- ===================================================================
-- This migration adds activity_level, height_cm, age, and gender fields
-- to support TDEE (Total Daily Energy Expenditure) calculation
-- ===================================================================

-- Step 1: Add new fields to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS activity_level TEXT DEFAULT 'moderate' CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
ADD COLUMN IF NOT EXISTS height_cm DECIMAL(5,1),
ADD COLUMN IF NOT EXISTS age INTEGER,
ADD COLUMN IF NOT EXISTS gender TEXT CHECK (gender IN ('male', 'female', 'other'));

-- Step 2: Add comments for documentation
COMMENT ON COLUMN user_profiles.activity_level IS 'User activity level: sedentary (1.2), light (1.375), moderate (1.55), active (1.725), very_active (1.9)';
COMMENT ON COLUMN user_profiles.height_cm IS 'User height in centimeters';
COMMENT ON COLUMN user_profiles.age IS 'User age in years';
COMMENT ON COLUMN user_profiles.gender IS 'User gender for BMR calculation';

-- Step 3: Set default values for existing users (optional, adjust as needed)
UPDATE user_profiles 
SET 
    activity_level = 'moderate',
    height_cm = 170.0,
    age = 30,
    gender = 'male'
WHERE activity_level IS NULL 
   OR height_cm IS NULL 
   OR age IS NULL 
   OR gender IS NULL;

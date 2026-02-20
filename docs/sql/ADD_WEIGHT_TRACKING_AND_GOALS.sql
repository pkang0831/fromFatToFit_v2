-- Weight Tracking and Goal Projection System
-- Run this in your Supabase SQL Editor

-- Step 1: Add target fields to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS target_weight_kg DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS target_body_fat_percentage DECIMAL(4,1);

-- Step 2: Create weight_logs table for tracking weight and body fat over time
CREATE TABLE IF NOT EXISTS weight_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    body_fat_percentage DECIMAL(4,1),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Create index for efficient queries
CREATE INDEX IF NOT EXISTS idx_weight_logs_user_date ON weight_logs(user_id, date DESC);

-- Enable RLS
ALTER TABLE weight_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own weight logs" ON weight_logs;
DROP POLICY IF EXISTS "Users can insert own weight logs" ON weight_logs;
DROP POLICY IF EXISTS "Users can update own weight logs" ON weight_logs;
DROP POLICY IF EXISTS "Users can delete own weight logs" ON weight_logs;

-- Weight Logs Policies
CREATE POLICY "Users can view own weight logs" ON weight_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own weight logs" ON weight_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own weight logs" ON weight_logs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own weight logs" ON weight_logs
    FOR DELETE USING (auth.uid() = user_id);

-- Step 3: Drop existing function if exists, then create
DROP FUNCTION IF EXISTS get_weight_moving_average(UUID, DATE, INTEGER);

CREATE OR REPLACE FUNCTION get_weight_moving_average(
    p_user_id UUID,
    p_date DATE,
    p_days INTEGER DEFAULT 3
)
RETURNS TABLE (
    avg_weight_kg DECIMAL(5,2),
    avg_body_fat_percentage DECIMAL(4,1)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ROUND(AVG(weight_kg)::numeric, 2) as avg_weight_kg,
        ROUND(AVG(body_fat_percentage)::numeric, 1) as avg_body_fat_percentage
    FROM weight_logs
    WHERE user_id = p_user_id
      AND date <= p_date
      AND date > p_date - p_days
    HAVING COUNT(*) > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

COMMENT ON FUNCTION get_weight_moving_average IS 'Calculate moving average of weight and body fat percentage over specified days';

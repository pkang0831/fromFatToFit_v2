-- Saved interactive goal planner output (one row per user, upsert on save)
-- Run in Supabase SQL Editor after uuid extension exists.

CREATE TABLE IF NOT EXISTS saved_goal_plans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    plan_data JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_saved_goal_plans_user_id ON saved_goal_plans(user_id);

ALTER TABLE saved_goal_plans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own saved goal plan" ON saved_goal_plans;
DROP POLICY IF EXISTS "Users can insert own saved goal plan" ON saved_goal_plans;
DROP POLICY IF EXISTS "Users can update own saved goal plan" ON saved_goal_plans;
DROP POLICY IF EXISTS "Users can delete own saved goal plan" ON saved_goal_plans;

CREATE POLICY "Users can view own saved goal plan" ON saved_goal_plans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own saved goal plan" ON saved_goal_plans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own saved goal plan" ON saved_goal_plans
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own saved goal plan" ON saved_goal_plans
    FOR DELETE USING (auth.uid() = user_id);

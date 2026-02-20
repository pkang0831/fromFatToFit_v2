-- Health & Wellness App Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Profiles (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    email TEXT NOT NULL,
    full_name TEXT,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    age INTEGER,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    ethnicity TEXT,
    activity_level TEXT CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    calorie_goal DECIMAL(6,1),
    premium_status BOOLEAN DEFAULT FALSE,
    stripe_customer_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    subscription_id TEXT NOT NULL,
    subscription_type TEXT NOT NULL,
    status TEXT NOT NULL,
    payment_provider TEXT CHECK (payment_provider IN ('stripe', 'revenuecat_ios', 'revenuecat_android')),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Usage Limits (for freemium features)
CREATE TABLE IF NOT EXISTS usage_limits (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    feature_type TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    reset_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, feature_type)
);

-- Food Logs
CREATE TABLE IF NOT EXISTS food_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    "date" DATE NOT NULL,
    meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    food_name TEXT NOT NULL,
    calories DECIMAL(7,2) NOT NULL,
    protein DECIMAL(6,2) DEFAULT 0,
    carbs DECIMAL(6,2) DEFAULT 0,
    fat DECIMAL(6,2) DEFAULT 0,
    serving_size TEXT,
    source TEXT DEFAULT 'manual' CHECK (source IN ('manual', 'ai')),
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily Summaries
CREATE TABLE IF NOT EXISTS daily_summaries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    "date" DATE NOT NULL,
    total_calories DECIMAL(7,2) DEFAULT 0,
    total_protein DECIMAL(6,2) DEFAULT 0,
    total_carbs DECIMAL(6,2) DEFAULT 0,
    total_fat DECIMAL(6,2) DEFAULT 0,
    workout_count INTEGER DEFAULT 0,
    calorie_goal DECIMAL(6,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, "date")
);

-- Exercise Library
CREATE TABLE IF NOT EXISTS exercise_library (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    muscle_groups TEXT[] NOT NULL,
    form_instructions TEXT NOT NULL,
    demo_image_url TEXT,
    difficulty TEXT DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout Logs
CREATE TABLE IF NOT EXISTS workout_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    "date" DATE NOT NULL,
    exercise_id UUID REFERENCES exercise_library(id),
    exercise_name TEXT NOT NULL,
    sets JSONB NOT NULL, -- Array of {set_number, reps, weight}
    duration_minutes INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Body Scans
CREATE TABLE IF NOT EXISTS body_scans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    scan_type TEXT NOT NULL CHECK (scan_type IN ('bodyfat', 'percentile', 'transformation')),
    image_url TEXT,
    result_data JSONB NOT NULL,
    ai_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON food_logs(user_id, "date");
CREATE INDEX IF NOT EXISTS idx_workout_logs_user_date ON workout_logs(user_id, "date");
CREATE INDEX IF NOT EXISTS idx_daily_summaries_user_date ON daily_summaries(user_id, "date");
CREATE INDEX IF NOT EXISTS idx_body_scans_user ON body_scans(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_limits_user ON usage_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON user_subscriptions(user_id);

-- Row Level Security (RLS) Policies

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE body_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_library ENABLE ROW LEVEL SECURITY;

-- User Profiles Policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Food Logs Policies
CREATE POLICY "Users can view own food logs" ON food_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own food logs" ON food_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own food logs" ON food_logs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own food logs" ON food_logs
    FOR DELETE USING (auth.uid() = user_id);

-- Workout Logs Policies
CREATE POLICY "Users can view own workout logs" ON workout_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own workout logs" ON workout_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own workout logs" ON workout_logs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own workout logs" ON workout_logs
    FOR DELETE USING (auth.uid() = user_id);

-- Daily Summaries Policies
CREATE POLICY "Users can view own summaries" ON daily_summaries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own summaries" ON daily_summaries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own summaries" ON daily_summaries
    FOR UPDATE USING (auth.uid() = user_id);

-- Body Scans Policies
CREATE POLICY "Users can view own body scans" ON body_scans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own body scans" ON body_scans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Usage Limits Policies
CREATE POLICY "Users can view own usage limits" ON usage_limits
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own usage limits" ON usage_limits
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own usage limits" ON usage_limits
    FOR UPDATE USING (auth.uid() = user_id);

-- Subscriptions Policies
CREATE POLICY "Users can view own subscriptions" ON user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Exercise Library - Public read access
CREATE POLICY "Anyone can view exercise library" ON exercise_library
    FOR SELECT USING (true);

-- Seed Exercise Library with common exercises
INSERT INTO exercise_library (name, category, muscle_groups, form_instructions, difficulty) VALUES
('Barbell Back Squat', 'Legs', ARRAY['Quadriceps', 'Glutes', 'Hamstrings'], 'Stand with feet shoulder-width apart. Bar across upper back. Descend by pushing hips back, keeping chest up. Go until thighs are parallel. Drive through heels to stand.', 'intermediate'),
('Bench Press', 'Chest', ARRAY['Chest', 'Triceps', 'Shoulders'], 'Lie on bench, feet flat on floor. Grip bar slightly wider than shoulders. Lower bar to mid-chest with control. Press up explosively, keeping shoulders back.', 'intermediate'),
('Deadlift', 'Back', ARRAY['Back', 'Glutes', 'Hamstrings'], 'Stand with feet hip-width, bar over mid-foot. Hinge at hips, grip bar. Keep back flat, drive through heels. Stand tall, squeeze glutes at top.', 'advanced'),
('Pull-ups', 'Back', ARRAY['Lats', 'Biceps', 'Back'], 'Hang from bar with hands shoulder-width. Pull yourself up until chin clears bar. Lower with control. Keep core tight throughout.', 'intermediate'),
('Overhead Press', 'Shoulders', ARRAY['Shoulders', 'Triceps'], 'Stand with feet shoulder-width. Bar at shoulder height. Press bar overhead until arms fully extended. Lower with control. Keep core braced.', 'intermediate'),
('Dumbbell Row', 'Back', ARRAY['Lats', 'Rhomboids', 'Biceps'], 'Place one hand and knee on bench. Hold dumbbell in other hand. Pull dumbbell to hip, squeezing shoulder blade. Lower with control.', 'beginner'),
('Push-ups', 'Chest', ARRAY['Chest', 'Triceps', 'Core'], 'Start in plank position, hands shoulder-width. Lower body until chest nearly touches ground. Keep elbows at 45 degrees. Push back up.', 'beginner'),
('Lunges', 'Legs', ARRAY['Quadriceps', 'Glutes', 'Hamstrings'], 'Step forward with one leg. Lower hips until both knees at 90 degrees. Front knee over ankle. Push back to start. Alternate legs.', 'beginner'),
('Plank', 'Core', ARRAY['Abs', 'Core'], 'Forearms on ground, elbows under shoulders. Body in straight line from head to heels. Hold position, keeping core tight. Breathe normally.', 'beginner'),
('Romanian Deadlift', 'Legs', ARRAY['Hamstrings', 'Glutes', 'Lower Back'], 'Hold bar at hip level. Hinge at hips, keeping knees slightly bent. Lower bar along legs until hamstrings stretch. Return to start.', 'intermediate')
ON CONFLICT DO NOTHING;

-- Functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_limits_updated_at BEFORE UPDATE ON usage_limits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_summaries_updated_at BEFORE UPDATE ON daily_summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User Food Preferences (for AI food decision & recommendations)
CREATE TABLE IF NOT EXISTS user_food_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Preferences
    favorite_foods JSONB DEFAULT '[]'::jsonb,
    disliked_foods JSONB DEFAULT '[]'::jsonb,
    allergies JSONB DEFAULT '[]'::jsonb,
    dietary_restrictions JSONB DEFAULT '[]'::jsonb,
    
    -- Settings
    avoid_high_sodium BOOLEAN DEFAULT false,
    avoid_high_sugar BOOLEAN DEFAULT false,
    prefer_high_protein BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_food_preferences_user_id ON user_food_preferences(user_id);

-- User Food Preferences Policies
ALTER TABLE user_food_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own food preferences" ON user_food_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own food preferences" ON user_food_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own food preferences" ON user_food_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- Trigger for updated_at
CREATE TRIGGER update_user_food_preferences_updated_at BEFORE UPDATE ON user_food_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

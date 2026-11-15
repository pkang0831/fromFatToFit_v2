CREATE TABLE IF NOT EXISTS user_streaks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_active_date DATE,
    total_active_days INTEGER DEFAULT 0,
    streak_freezes INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id)
);

ALTER TABLE user_streaks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own streaks" ON user_streaks
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Users can insert own streaks" ON user_streaks
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Users can update own streaks" ON user_streaks
    FOR UPDATE USING (auth.uid() = user_id);

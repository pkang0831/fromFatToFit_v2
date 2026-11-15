-- 7-day commitment loop: one active challenge per user, daily check-ins
-- Run in Supabase SQL Editor after uuid-ossp exists.

CREATE TABLE IF NOT EXISTS seven_day_challenges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'ended')),
    ai_weeks_snapshot INT,
    ai_current_bf NUMERIC(5,2),
    ai_target_bf NUMERIC(5,2)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_seven_day_one_active_per_user
    ON seven_day_challenges (user_id)
    WHERE (status = 'active');

CREATE INDEX IF NOT EXISTS idx_seven_day_challenges_user ON seven_day_challenges(user_id);

CREATE TABLE IF NOT EXISTS seven_day_checkins (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    challenge_id UUID NOT NULL REFERENCES seven_day_challenges(id) ON DELETE CASCADE,
    calendar_date DATE NOT NULL,
    weight_kg NUMERIC(5,2),
    body_fat_pct NUMERIC(4,1),
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(challenge_id, calendar_date)
);

CREATE INDEX IF NOT EXISTS idx_seven_day_checkins_challenge ON seven_day_checkins(challenge_id);

ALTER TABLE seven_day_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE seven_day_checkins ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own seven_day_challenges" ON seven_day_challenges;
DROP POLICY IF EXISTS "Users can insert own seven_day_challenges" ON seven_day_challenges;
DROP POLICY IF EXISTS "Users can update own seven_day_challenges" ON seven_day_challenges;
DROP POLICY IF EXISTS "Users can delete own seven_day_challenges" ON seven_day_challenges;

CREATE POLICY "Users can view own seven_day_challenges" ON seven_day_challenges
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own seven_day_challenges" ON seven_day_challenges
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own seven_day_challenges" ON seven_day_challenges
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own seven_day_challenges" ON seven_day_challenges
    FOR DELETE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view own seven_day_checkins" ON seven_day_checkins;
DROP POLICY IF EXISTS "Users can insert own seven_day_checkins" ON seven_day_checkins;
DROP POLICY IF EXISTS "Users can update own seven_day_checkins" ON seven_day_checkins;
DROP POLICY IF EXISTS "Users can delete own seven_day_checkins" ON seven_day_checkins;

CREATE POLICY "Users can view own seven_day_checkins" ON seven_day_checkins
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM seven_day_challenges c
            WHERE c.id = seven_day_checkins.challenge_id AND c.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can insert own seven_day_checkins" ON seven_day_checkins
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM seven_day_challenges c
            WHERE c.id = seven_day_checkins.challenge_id AND c.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can update own seven_day_checkins" ON seven_day_checkins
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM seven_day_challenges c
            WHERE c.id = seven_day_checkins.challenge_id AND c.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can delete own seven_day_checkins" ON seven_day_checkins
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM seven_day_challenges c
            WHERE c.id = seven_day_checkins.challenge_id AND c.user_id = auth.uid()
        )
    );

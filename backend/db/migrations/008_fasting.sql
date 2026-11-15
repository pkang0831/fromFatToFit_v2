CREATE TABLE IF NOT EXISTS fasting_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    protocol VARCHAR(20) NOT NULL DEFAULT '16:8',
    target_hours FLOAT NOT NULL DEFAULT 16,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    actual_hours FLOAT,
    completed BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_fasting_user_active ON fasting_sessions(user_id, ended_at) WHERE ended_at IS NULL;

ALTER TABLE fasting_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own fasting sessions" ON fasting_sessions
    FOR ALL USING (auth.uid() = user_id);

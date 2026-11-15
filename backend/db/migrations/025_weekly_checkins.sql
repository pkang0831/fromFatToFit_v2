CREATE TABLE IF NOT EXISTS weekly_checkins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    progress_photo_id UUID NOT NULL REFERENCES progress_photos(id) ON DELETE CASCADE,
    previous_checkin_id UUID REFERENCES weekly_checkins(id) ON DELETE SET NULL,
    analysis_version TEXT NOT NULL DEFAULT 'v1',
    taken_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    image_quality JSONB NOT NULL,
    observations JSONB NOT NULL,
    estimated_ranges JSONB NOT NULL,
    qualitative_summary JSONB NOT NULL,
    region_notes JSONB NOT NULL,
    derived_scores JSONB NOT NULL,
    delta_from_previous JSONB,
    comparison_confidence NUMERIC NOT NULL,
    weekly_status TEXT NOT NULL CHECK (weekly_status IN ('improved', 'stable', 'regressed', 'low_confidence')),
    is_first_checkin BOOLEAN NOT NULL DEFAULT FALSE,
    regional_visualization JSONB NOT NULL DEFAULT '[]'::jsonb,
    hologram_visualization JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(progress_photo_id)
);

CREATE INDEX IF NOT EXISTS idx_weekly_checkins_user_taken_at
    ON weekly_checkins(user_id, taken_at DESC);

CREATE INDEX IF NOT EXISTS idx_weekly_checkins_previous
    ON weekly_checkins(previous_checkin_id);

ALTER TABLE weekly_checkins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own weekly checkins" ON weekly_checkins
    FOR ALL USING (auth.uid() = user_id);

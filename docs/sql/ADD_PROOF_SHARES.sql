CREATE TABLE IF NOT EXISTS proof_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    progress_photo_id UUID NOT NULL REFERENCES progress_photos(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    week_marker INTEGER,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked')),
    current_bf_snapshot NUMERIC,
    target_bf_snapshot NUMERIC,
    goal_gap_snapshot NUMERIC,
    shared_photo_taken_at TIMESTAMP WITH TIME ZONE,
    shared_photo_weight_kg NUMERIC,
    shared_photo_body_fat_pct NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_proof_shares_user_created
    ON proof_shares(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_proof_shares_photo_status
    ON proof_shares(progress_photo_id, status, created_at DESC);

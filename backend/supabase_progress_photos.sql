CREATE TABLE IF NOT EXISTS progress_photos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    image_base64 TEXT NOT NULL,
    notes TEXT DEFAULT '',
    weight_kg FLOAT,
    body_fat_pct FLOAT,
    taken_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_progress_photos_user ON progress_photos(user_id, taken_at DESC);

ALTER TABLE progress_photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own progress photos" ON progress_photos
    FOR ALL USING (auth.uid() = user_id);

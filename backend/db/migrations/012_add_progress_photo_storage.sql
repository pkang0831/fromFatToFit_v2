ALTER TABLE progress_photos
    ALTER COLUMN image_base64 DROP NOT NULL;

ALTER TABLE progress_photos
    ADD COLUMN IF NOT EXISTS storage_bucket TEXT,
    ADD COLUMN IF NOT EXISTS storage_key TEXT;

ALTER TABLE progress_photos
    DROP CONSTRAINT IF EXISTS progress_photos_image_or_storage_chk;

ALTER TABLE progress_photos
    ADD CONSTRAINT progress_photos_image_or_storage_chk
    CHECK (image_base64 IS NOT NULL OR storage_key IS NOT NULL);

CREATE INDEX IF NOT EXISTS idx_progress_photos_storage_key
    ON progress_photos(storage_key);

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'progress-photos-private',
    'progress-photos-private',
    false,
    10485760,
    ARRAY['image/jpeg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET
    public = EXCLUDED.public,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

DROP POLICY IF EXISTS "Users can read own progress photos storage" ON storage.objects;
CREATE POLICY "Users can read own progress photos storage"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'progress-photos-private'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

DROP POLICY IF EXISTS "Users can upload own progress photos storage" ON storage.objects;
CREATE POLICY "Users can upload own progress photos storage"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'progress-photos-private'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

DROP POLICY IF EXISTS "Users can delete own progress photos storage" ON storage.objects;
CREATE POLICY "Users can delete own progress photos storage"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'progress-photos-private'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

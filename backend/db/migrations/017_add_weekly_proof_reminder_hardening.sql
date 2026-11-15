ALTER TABLE reminder_events
    ADD COLUMN IF NOT EXISTS recipient_email TEXT,
    ADD COLUMN IF NOT EXISTS provider_email_id TEXT,
    ADD COLUMN IF NOT EXISTS job_key TEXT,
    ADD COLUMN IF NOT EXISTS last_provider_event_type TEXT,
    ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS clicked_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS bounced_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS unsubscribed_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS complained_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS failed_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS suppressed_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_reminder_events_recipient_email
    ON reminder_events(recipient_email, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reminder_events_provider_email_id
    ON reminder_events(provider_email_id);

CREATE INDEX IF NOT EXISTS idx_reminder_events_job_key
    ON reminder_events(job_key);

CREATE TABLE IF NOT EXISTS reminder_job_runs (
    job_key TEXT PRIMARY KEY,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    lease_owner TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reminder_job_runs_job_name
    ON reminder_job_runs(job_name, created_at DESC);

CREATE TABLE IF NOT EXISTS reminder_webhook_events (
    svix_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    recipient_email TEXT,
    provider_email_id TEXT,
    reminder_event_id UUID REFERENCES reminder_events(id) ON DELETE SET NULL,
    processing_status TEXT NOT NULL DEFAULT 'processing',
    payload JSONB NOT NULL,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_reminder_webhook_events_recipient
    ON reminder_webhook_events(recipient_email, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reminder_webhook_events_provider_email
    ON reminder_webhook_events(provider_email_id);

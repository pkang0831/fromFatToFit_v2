CREATE TABLE IF NOT EXISTS reminder_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    channel TEXT NOT NULL,
    reminder_type TEXT NOT NULL,
    entry_state TEXT NOT NULL,
    deep_link TEXT NOT NULL,
    status TEXT NOT NULL,
    provider_message_id TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reminder_events_user_type
    ON reminder_events(user_id, reminder_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reminder_events_status
    ON reminder_events(status, created_at DESC);

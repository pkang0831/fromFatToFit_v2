-- ============================================================================
-- Fix RLS for tables missing Row Level Security
-- Run in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
--
-- These 5 tables are referenced in backend code but have no RLS defined:
--   1. user_credits       (payment_service, usage_limiter)
--   2. notification_preferences (notification_service)
--   3. push_subscriptions (notification_service)
--   4. chat_messages      (chat router, rag_chat_service)
--   5. transcript_chunks  (ingest_transcripts, rag_chat_service)
-- ============================================================================

-- ── 1. user_credits ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS user_credits (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    monthly_credits INTEGER DEFAULT 10,
    bonus_credits INTEGER DEFAULT 0,
    reset_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own credits"
    ON user_credits FOR SELECT
    USING (auth.uid() = user_id);

-- Insert/update handled by service_role (backend); no anon write needed.

-- ── 2. notification_preferences ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    email_weekly_summary BOOLEAN DEFAULT TRUE,
    email_inactivity_reminder BOOLEAN DEFAULT TRUE,
    email_credit_low BOOLEAN DEFAULT TRUE,
    push_meal_reminder BOOLEAN DEFAULT TRUE,
    push_workout_reminder BOOLEAN DEFAULT TRUE,
    push_weekly_body_scan BOOLEAN DEFAULT TRUE,
    push_daily_summary BOOLEAN DEFAULT FALSE,
    meal_reminder_time TEXT DEFAULT '12:00',
    workout_reminder_days TEXT[] DEFAULT ARRAY['monday', 'wednesday', 'friday'],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notification prefs"
    ON notification_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own notification prefs"
    ON notification_preferences FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own notification prefs"
    ON notification_preferences FOR UPDATE
    USING (auth.uid() = user_id);

-- ── 3. push_subscriptions ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS push_subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    endpoint TEXT NOT NULL,
    keys JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own push subs"
    ON push_subscriptions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own push subs"
    ON push_subscriptions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own push subs"
    ON push_subscriptions FOR UPDATE
    USING (auth.uid() = user_id);

-- ── 4. chat_messages ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat messages"
    ON chat_messages FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages"
    ON chat_messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat messages"
    ON chat_messages FOR DELETE
    USING (auth.uid() = user_id);

-- ── 5. transcript_chunks (RAG knowledge base — read-only for users) ──────────

CREATE TABLE IF NOT EXISTS transcript_chunks (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE transcript_chunks ENABLE ROW LEVEL SECURITY;

-- Public read: all authenticated users can search the knowledge base.
-- Write is service_role only (ingestion script).
CREATE POLICY "Authenticated users can read transcript chunks"
    ON transcript_chunks FOR SELECT
    USING (auth.role() = 'authenticated');

-- ============================================================================
-- VERIFY: After running, check in Supabase Dashboard → Table Editor.
-- Each table should show a shield icon indicating RLS is enabled.
--
-- If tables already exist with different columns, the CREATE TABLE IF NOT
-- EXISTS will be skipped — only the ALTER TABLE + CREATE POLICY lines matter.
-- If policies already exist, Supabase will raise a notice (not an error).
-- ============================================================================

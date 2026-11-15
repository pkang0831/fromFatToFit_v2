ALTER TABLE user_subscriptions
    ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT,
    ADD COLUMN IF NOT EXISTS current_period_start TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS canceled_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS last_stripe_event_id TEXT,
    ADD COLUMN IF NOT EXISTS last_stripe_event_type TEXT,
    ADD COLUMN IF NOT EXISTS last_webhook_processed_at TIMESTAMP WITH TIME ZONE;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_subscriptions_subscription_id
    ON user_subscriptions(subscription_id);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_customer_id
    ON user_subscriptions(stripe_customer_id);

CREATE TABLE IF NOT EXISTS stripe_webhook_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    processing_status TEXT NOT NULL DEFAULT 'processing',
    error_message TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_customer
    ON stripe_webhook_events(stripe_customer_id);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_subscription
    ON stripe_webhook_events(stripe_subscription_id);

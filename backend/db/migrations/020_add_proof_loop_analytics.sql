CREATE TABLE IF NOT EXISTS funnel_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    event_name TEXT NOT NULL,
    surface TEXT NOT NULL,
    source TEXT,
    entry_state TEXT,
    session_id TEXT,
    reminder_event_id UUID REFERENCES reminder_events(id) ON DELETE SET NULL,
    share_id UUID REFERENCES proof_shares(id) ON DELETE SET NULL,
    share_token TEXT,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    event_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_funnel_events_event_at
    ON funnel_events(event_at DESC);

CREATE INDEX IF NOT EXISTS idx_funnel_events_event_name
    ON funnel_events(event_name, event_at DESC);

CREATE INDEX IF NOT EXISTS idx_funnel_events_user_id
    ON funnel_events(user_id, event_at DESC);

CREATE INDEX IF NOT EXISTS idx_funnel_events_source
    ON funnel_events(source, event_at DESC);

CREATE INDEX IF NOT EXISTS idx_funnel_events_share_token
    ON funnel_events(share_token, event_at DESC);

CREATE INDEX IF NOT EXISTS idx_funnel_events_reminder_event
    ON funnel_events(reminder_event_id, event_at DESC);

CREATE OR REPLACE VIEW analytics_daily_funnel_snapshot AS
SELECT
    date_trunc('day', event_at)::date AS snapshot_date,
    COUNT(*) FILTER (WHERE event_name = 'scan_success') AS scan_success_count,
    COUNT(*) FILTER (WHERE event_name = 'progress_proof_started') AS proof_started_count,
    COUNT(*) FILTER (WHERE event_name = 'progress_proof_completed') AS proof_completed_count,
    COUNT(*) FILTER (WHERE event_name = 'progress_compare_viewed') AS compare_viewed_count,
    COUNT(*) FILTER (WHERE event_name = 'notification_sent') AS notification_sent_count,
    COUNT(*) FILTER (WHERE event_name = 'notification_opened') AS notification_opened_count,
    COUNT(*) FILTER (WHERE event_name = 'reengagement_session') AS reengagement_session_count,
    COUNT(*) FILTER (WHERE event_name = 'share_created') AS share_created_count,
    COUNT(*) FILTER (WHERE event_name = 'share_viewed') AS share_viewed_count,
    COUNT(*) FILTER (WHERE event_name = 'referred_try_started') AS referred_try_started_count,
    COUNT(*) FILTER (WHERE event_name = 'register_completed') AS register_completed_count,
    COUNT(*) FILTER (WHERE event_name = 'purchase_completed') AS purchase_completed_count
FROM funnel_events
GROUP BY 1
ORDER BY 1 DESC;

CREATE OR REPLACE VIEW analytics_weekly_cohort_by_source AS
SELECT
    date_trunc('week', event_at)::date AS cohort_week,
    COALESCE(source, 'direct') AS source,
    COUNT(DISTINCT user_id) FILTER (WHERE user_id IS NOT NULL) AS distinct_users,
    COUNT(*) FILTER (WHERE event_name = 'reengagement_session') AS reengagement_sessions,
    COUNT(*) FILTER (WHERE event_name = 'scan_success') AS scan_successes,
    COUNT(*) FILTER (WHERE event_name = 'progress_proof_completed') AS proof_completions,
    COUNT(*) FILTER (WHERE event_name = 'register_completed') AS register_completions,
    COUNT(*) FILTER (WHERE event_name = 'purchase_completed') AS purchase_completions
FROM funnel_events
GROUP BY 1, 2
ORDER BY 1 DESC, 2;

CREATE OR REPLACE VIEW analytics_entry_state_performance AS
SELECT
    COALESCE(entry_state, 'unknown') AS entry_state,
    COALESCE(source, 'direct') AS source,
    COUNT(*) FILTER (WHERE event_name = 'reengagement_session') AS reengagement_sessions,
    COUNT(*) FILTER (WHERE event_name = 'scan_success') AS scan_successes,
    COUNT(*) FILTER (WHERE event_name = 'progress_proof_completed') AS proof_completions,
    COUNT(*) FILTER (WHERE event_name = 'progress_compare_viewed') AS compare_views,
    COUNT(*) FILTER (WHERE event_name = 'purchase_completed') AS purchases
FROM funnel_events
GROUP BY 1, 2
ORDER BY 3 DESC, 1;

CREATE OR REPLACE VIEW analytics_reminder_open_to_proof AS
WITH opened AS (
    SELECT
        reminder_event_id,
        user_id,
        event_at AS opened_at,
        date_trunc('day', event_at)::date AS opened_date
    FROM funnel_events
    WHERE event_name = 'notification_opened'
      AND source = 'weekly_reminder'
      AND user_id IS NOT NULL
),
proof_completed AS (
    SELECT
        user_id,
        event_at AS proof_completed_at
    FROM funnel_events
    WHERE event_name = 'progress_proof_completed'
      AND user_id IS NOT NULL
)
SELECT
    opened.opened_date,
    COUNT(DISTINCT opened.reminder_event_id) AS reminder_opens,
    COUNT(DISTINCT CASE
        WHEN proof_completed.user_id IS NOT NULL THEN opened.reminder_event_id
        ELSE NULL
    END) AS proof_uploads_after_open,
    CASE
        WHEN COUNT(DISTINCT opened.reminder_event_id) = 0 THEN 0
        ELSE ROUND(
            100.0 * COUNT(DISTINCT CASE
                WHEN proof_completed.user_id IS NOT NULL THEN opened.reminder_event_id
                ELSE NULL
            END)::numeric
            / COUNT(DISTINCT opened.reminder_event_id)::numeric,
            2
        )
    END AS open_to_proof_rate_pct
FROM opened
LEFT JOIN proof_completed
  ON proof_completed.user_id = opened.user_id
 AND proof_completed.proof_completed_at >= opened.opened_at
 AND proof_completed.proof_completed_at <= opened.opened_at + INTERVAL '7 days'
GROUP BY 1
ORDER BY 1 DESC;

CREATE OR REPLACE VIEW analytics_share_view_to_try_to_register AS
WITH share_views AS (
    SELECT
        share_token,
        COUNT(*) AS share_views
    FROM funnel_events
    WHERE event_name = 'share_viewed'
      AND share_token IS NOT NULL
    GROUP BY 1
),
try_starts AS (
    SELECT
        share_token,
        COUNT(*) AS try_starts
    FROM funnel_events
    WHERE event_name = 'referred_try_started'
      AND share_token IS NOT NULL
    GROUP BY 1
),
registers AS (
    SELECT
        share_token,
        COUNT(DISTINCT user_id) AS register_completions
    FROM funnel_events
    WHERE event_name = 'register_completed'
      AND source = 'proof_share'
      AND share_token IS NOT NULL
      AND user_id IS NOT NULL
    GROUP BY 1
)
SELECT
    COALESCE(share_views.share_token, try_starts.share_token, registers.share_token) AS share_token,
    COALESCE(share_views.share_views, 0) AS share_views,
    COALESCE(try_starts.try_starts, 0) AS try_starts,
    COALESCE(registers.register_completions, 0) AS register_completions,
    CASE
        WHEN COALESCE(share_views.share_views, 0) = 0 THEN 0
        ELSE ROUND(
            100.0 * COALESCE(registers.register_completions, 0)::numeric
            / share_views.share_views::numeric,
            2
        )
    END AS view_to_register_rate_pct
FROM share_views
FULL OUTER JOIN try_starts
    ON try_starts.share_token = share_views.share_token
FULL OUTER JOIN registers
    ON registers.share_token = COALESCE(share_views.share_token, try_starts.share_token)
ORDER BY 2 DESC, 1;

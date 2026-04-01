ALTER TABLE funnel_events
    ADD COLUMN IF NOT EXISTS reentry_state TEXT,
    ADD COLUMN IF NOT EXISTS surface_state TEXT,
    ADD COLUMN IF NOT EXISTS event_origin TEXT;

CREATE INDEX IF NOT EXISTS idx_funnel_events_reentry_surface
    ON funnel_events(source, reentry_state, surface_state, event_at DESC);

UPDATE funnel_events
SET reentry_state = COALESCE(reentry_state, entry_state)
WHERE reentry_state IS NULL;

UPDATE funnel_events
SET surface_state = COALESCE(surface_state, reentry_state, entry_state)
WHERE surface_state IS NULL;

UPDATE funnel_events
SET event_origin = COALESCE(event_origin, properties->>'event_origin')
WHERE event_origin IS NULL
  AND properties ? 'event_origin';

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
    COUNT(*) FILTER (WHERE event_name = 'purchase_completed') AS purchase_completed_count,
    COUNT(*) FILTER (WHERE event_name = 'proof_upload_failed') AS proof_upload_failed_count
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
    COUNT(*) FILTER (WHERE event_name = 'purchase_completed') AS purchase_completions,
    COUNT(*) FILTER (WHERE event_name = 'notification_sent' AND COALESCE(event_origin, 'live') = 'live') AS live_notification_sends,
    COUNT(*) FILTER (WHERE event_name = 'notification_sent' AND event_origin = 'backfill') AS backfill_notification_sends
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
    COUNT(*) FILTER (WHERE event_name = 'purchase_completed') AS purchases,
    COALESCE(reentry_state, entry_state, 'unknown') AS reentry_state,
    COALESCE(surface_state, reentry_state, entry_state, 'unknown') AS surface_state,
    COUNT(*) FILTER (WHERE event_name = 'proof_upload_failed') AS proof_upload_failures,
    COUNT(*) FILTER (WHERE event_name = 'share_created') AS share_creations
FROM funnel_events
GROUP BY 1, 2, 8, 9
ORDER BY reengagement_sessions DESC, reentry_state, surface_state;

CREATE OR REPLACE VIEW analytics_reminder_open_to_proof AS
WITH opened AS (
    SELECT
        reminder_event_id,
        user_id,
        COALESCE(reentry_state, entry_state, 'unknown') AS reentry_state,
        COALESCE(surface_state, reentry_state, entry_state, 'unknown') AS surface_state,
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
        COALESCE(reentry_state, entry_state, 'unknown') AS reentry_state,
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
    END AS open_to_proof_rate_pct,
    opened.reentry_state,
    opened.surface_state
FROM opened
LEFT JOIN proof_completed
  ON proof_completed.user_id = opened.user_id
 AND proof_completed.proof_completed_at >= opened.opened_at
 AND proof_completed.proof_completed_at <= opened.opened_at + INTERVAL '7 days'
GROUP BY 1, 5, 6
ORDER BY 1 DESC, 5, 6;

# Proof Loop Readout

Date: 2026-03-31  
Scope: P1-5b Proof Loop Readout & Decision Gate

## Data Sources

- `analytics_daily_funnel_snapshot`
- `analytics_weekly_cohort_by_source`
- `analytics_entry_state_performance`
- `analytics_reminder_open_to_proof`
- `analytics_share_view_to_try_to_register`
- raw `funnel_events`
- raw `reminder_events`

## Verified Continuity

One real continuity path was verified on `2026-03-31` using:

- `user_id`: `70ca5cb6-6c10-4e37-b23a-b331875cc470`
- `reminder_event_id`: `e81ae37f-da35-409e-a38d-15248c9734c0`
- `session_id`: `readout-20260331T222121Z`
- `share_token`: `7jtEKq2sOyrqa-kUYhpixB1J`

Observed event chain:

1. `notification_sent`
2. `reengagement_session`
3. `progress_proof_started`
4. `progress_proof_completed`
5. `progress_compare_viewed`
6. `share_created`
7. `share_viewed`
8. `referred_try_started`

This confirms server-side continuity for:

- `weekly_reminder -> proof upload`
- `proof upload -> compare`
- `compare -> share`
- `share -> try`

It does not yet confirm a real `proof_share -> register_completed -> purchase_completed` path. Those events remain `0`.

## Readout

### 1. weekly_reminder -> proof_completed

Source: `analytics_reminder_open_to_proof`

- `reminder_opens = 1`
- `proof_uploads_after_open = 1`
- `open_to_proof_rate_pct = 100.0`

Interpretation:

- The instrumentation path works.
- The sample is only `n=1`, so this is continuity proof, not product proof.

### 2. Entry-state leak points

Source: `analytics_entry_state_performance`

- `weekly_scan / weekly_reminder`
  - `reengagement_sessions = 1`
  - `scan_successes = 0`
  - `proof_completions = 0`
  - `compare_views = 0`
  - `purchases = 0`
- `progress_proof / weekly_reminder`
  - `proof_completions = 1`
- `review_progress / weekly_reminder`
  - `compare_views = 1`

Leak conclusion:

- The clearest leak is between `weekly_scan` re-entry and the first proof action.
- We have evidence of re-entry, but no evidence yet that `weekly_scan` itself converts directly to `scan_success` or `purchase_completed`.
- Progress happens only after the user moves into the `progress_proof` surface.

### 3. proof_share -> try -> register

Source: `analytics_share_view_to_try_to_register`

- `share_views = 1`
- `try_starts = 1`
- `register_completions = 0`
- `view_to_register_rate_pct = 0.0`

Interpretation:

- Public-safe share routing works.
- The current sample shows share-driven curiosity, but not yet signup conversion.

### 4. Source-level cohort quality through purchase_completed

Source: `analytics_weekly_cohort_by_source`

Week of `2026-03-30`:

- `weekly_reminder`
  - `distinct_users = 1`
  - `reengagement_sessions = 1`
  - `scan_successes = 0`
  - `proof_completions = 1`
  - `register_completions = 0`
  - `purchase_completions = 0`
- `proof_share`
  - `distinct_users = 1`
  - `reengagement_sessions = 0`
  - `scan_successes = 0`
  - `proof_completions = 0`
  - `register_completions = 0`
  - `purchase_completions = 0`

Decision:

- No source has purchase evidence yet.
- There is not enough signal to justify any pricing or paywall change.

### 5. Daily proof-loop health trend

Source: `analytics_daily_funnel_snapshot`

For `2026-03-31`:

- `scan_success_count = 0`
- `proof_started_count = 1`
- `proof_completed_count = 1`
- `compare_viewed_count = 1`
- `notification_sent_count = 1`
- `notification_opened_count = 1`
- `reengagement_session_count = 1`
- `share_created_count = 1`
- `share_viewed_count = 1`
- `referred_try_started_count = 1`
- `register_completed_count = 0`
- `purchase_completed_count = 0`

Trend conclusion:

- We only have one populated day in the truth layer.
- The instrumentation is live, but the time series is not mature enough yet for trend-based optimization.

## Product Decision

Do not change pricing, paywall behavior, or add more top-of-funnel growth mechanics yet.

The only evidence-backed decision right now is:

- keep the current proof loop instrumentation live
- focus the next experiment on the `weekly_scan -> progress_proof` handoff
- wait for multi-day cohort data before making monetization decisions

## One Recommended Next Experiment

Run exactly one experiment:

- For `weekly_reminder` users in `weekly_scan`, change the first destination from journey review to an upload-first proof handoff when the user has fewer than 2 proof photos.

Why this one:

- The only real leak we can see is at `weekly_scan`.
- We already have proof that upload, compare, share, and try logging works after the user reaches the proof surface.
- We do not yet have evidence that share or pricing changes would move purchase.

Success metric:

- Increase `analytics_reminder_open_to_proof.open_to_proof_rate_pct`
- Secondary: increase `progress_compare_viewed`

## Exactly Three Things Not To Build Next

1. Do not run paywall or pricing experiments yet.
   There is `0` purchase signal in the new truth layer.

2. Do not add broader referral or generic invite systems yet.
   `proof_share -> register` is still `0/1`.

3. Do not add more reminder types yet.
   The current gap is conversion after `weekly_scan`, not reminder volume.

## Queries Used

```sql
SELECT * FROM analytics_daily_funnel_snapshot ORDER BY snapshot_date DESC;
```

```sql
SELECT * FROM analytics_weekly_cohort_by_source ORDER BY cohort_week DESC, source;
```

```sql
SELECT * FROM analytics_entry_state_performance ORDER BY reengagement_sessions DESC, entry_state;
```

```sql
SELECT * FROM analytics_reminder_open_to_proof ORDER BY opened_date DESC;
```

```sql
SELECT * FROM analytics_share_view_to_try_to_register ORDER BY share_views DESC, share_token;
```

```sql
SELECT
  event_name,
  source,
  entry_state,
  session_id,
  share_token,
  reminder_event_id,
  event_at
FROM funnel_events
WHERE session_id = 'readout-20260331T222121Z'
ORDER BY event_at ASC;
```

## Data Quality Risks

1. Sample size is still extremely small.
   Current readout is continuity-valid, but not statistically decision-safe.

2. `entry_state` is mixed between re-entry state and in-surface state.
   `weekly_scan`, `progress_proof`, and `review_progress` do not all represent the same moment in the funnel.

3. `notification_sent` for the verified reminder path was backfilled from a real `reminder_event`.
   The event is real, but it was inserted after the fact because `funnel_events` started empty.

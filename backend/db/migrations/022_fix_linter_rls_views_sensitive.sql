-- ============================================================================
-- Fix Supabase Linter: RLS, Security Definer Views, Sensitive Columns
-- Run in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
--
-- Addresses three categories of linter warnings:
--   A. Security Definer Views  (5 analytics views)
--   B. RLS Disabled in Public  (6 server-only tables)
--   C. Sensitive Columns Exposed (funnel_events, proof_shares)
--
-- All six tables are accessed exclusively through the backend service_role
-- client, so enabling RLS with no user policies is the correct approach —
-- service_role bypasses RLS, while anon/authenticated PostgREST access is
-- blocked.
-- ============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- A. SECURITY DEFINER VIEWS → switch to security_invoker = true
--
-- PostgreSQL views default to SECURITY DEFINER semantics (run as view owner).
-- With security_invoker = true the view runs as the calling user, which
-- Supabase recommends for views exposed via PostgREST.
-- Requires PostgreSQL 15+ (Supabase default).
-- ═══════════════════════════════════════════════════════════════════════════

ALTER VIEW analytics_reminder_open_to_proof      SET (security_invoker = true);
ALTER VIEW analytics_daily_funnel_snapshot        SET (security_invoker = true);
ALTER VIEW analytics_weekly_cohort_by_source      SET (security_invoker = true);
ALTER VIEW analytics_share_view_to_try_to_register SET (security_invoker = true);
ALTER VIEW analytics_entry_state_performance      SET (security_invoker = true);

-- ═══════════════════════════════════════════════════════════════════════════
-- B. RLS DISABLED IN PUBLIC → enable RLS on server-only tables
--
-- These tables are never queried directly by end-user clients; all access
-- goes through the FastAPI backend using the service_role key, which
-- bypasses RLS. Enabling RLS with no permissive policies blocks any
-- anon/authenticated PostgREST access.
-- ═══════════════════════════════════════════════════════════════════════════

-- ── 1. stripe_webhook_events ────────────────────────────────────────────────
ALTER TABLE stripe_webhook_events ENABLE ROW LEVEL SECURITY;

-- ── 2. reminder_events ──────────────────────────────────────────────────────
ALTER TABLE reminder_events ENABLE ROW LEVEL SECURITY;

-- ── 3. reminder_job_runs ────────────────────────────────────────────────────
ALTER TABLE reminder_job_runs ENABLE ROW LEVEL SECURITY;

-- ── 4. reminder_webhook_events ──────────────────────────────────────────────
ALTER TABLE reminder_webhook_events ENABLE ROW LEVEL SECURITY;

-- ── 5. proof_shares ─────────────────────────────────────────────────────────
ALTER TABLE proof_shares ENABLE ROW LEVEL SECURITY;

-- ── 6. funnel_events ────────────────────────────────────────────────────────
ALTER TABLE funnel_events ENABLE ROW LEVEL SECURITY;

-- ═══════════════════════════════════════════════════════════════════════════
-- C. SENSITIVE COLUMNS EXPOSED (funnel_events, proof_shares)
--
-- The "Sensitive Columns Exposed" warning fires when PostgREST can return
-- columns that look like PII/credentials (user_id, token, session_id, etc.).
-- Enabling RLS above with no permissive policies already blocks all direct
-- client reads, which fully resolves this warning.
--
-- If you later add SELECT policies for authenticated users on these tables,
-- consider creating a restricted view that omits sensitive columns instead.
-- ═══════════════════════════════════════════════════════════════════════════

COMMIT;

-- ============================================================================
-- VERIFY after running:
--   1. Supabase Dashboard → Table Editor: each table shows a shield icon
--   2. Supabase Dashboard → Database → Views: each analytics view shows
--      security_invoker = true in its properties
--   3. Re-run the Supabase Linter — all 12 warnings should be resolved
--
-- ROLLBACK: If something breaks, run:
--   ALTER VIEW analytics_reminder_open_to_proof SET (security_invoker = false);
--   ALTER VIEW analytics_daily_funnel_snapshot SET (security_invoker = false);
--   ... (repeat for other views)
--   ALTER TABLE stripe_webhook_events DISABLE ROW LEVEL SECURITY;
--   ... (repeat for other tables)
-- ============================================================================

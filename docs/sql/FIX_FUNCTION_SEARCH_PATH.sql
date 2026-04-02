-- ============================================================================
-- Fix: Function Search Path Mutable
-- Run in Supabase SQL Editor
--
-- Supabase linter flags functions whose search_path is not pinned.
-- Adding SET search_path prevents schema injection attacks.
-- ============================================================================

-- ── 1. deduct_user_credits ──────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION deduct_user_credits(
  p_user_id UUID,
  p_amount INTEGER
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_monthly INTEGER;
  v_bonus INTEGER;
  v_remaining INTEGER;
  v_deduct_monthly INTEGER;
  v_deduct_bonus INTEGER;
BEGIN
  SELECT monthly_credits, bonus_credits
  INTO v_monthly, v_bonus
  FROM user_credits
  WHERE user_id = p_user_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RETURN json_build_object('success', false, 'error', 'No credit record found');
  END IF;

  IF (v_monthly + v_bonus) < p_amount THEN
    RETURN json_build_object('success', false, 'error', 'Insufficient credits', 'total', v_monthly + v_bonus);
  END IF;

  v_remaining := p_amount;
  v_deduct_monthly := LEAST(v_monthly, v_remaining);
  v_remaining := v_remaining - v_deduct_monthly;
  v_deduct_bonus := v_remaining;

  UPDATE user_credits
  SET monthly_credits = monthly_credits - v_deduct_monthly,
      bonus_credits = bonus_credits - v_deduct_bonus
  WHERE user_id = p_user_id;

  RETURN json_build_object(
    'success', true,
    'monthly_credits', v_monthly - v_deduct_monthly,
    'bonus_credits', v_bonus - v_deduct_bonus,
    'total', (v_monthly - v_deduct_monthly) + (v_bonus - v_deduct_bonus)
  );
END;
$$;

-- ── 2. match_transcript_chunks ──────────────────────────────────────────────
-- Re-create with search_path pinned. Adjust parameter types if your
-- existing function signature differs.

CREATE OR REPLACE FUNCTION match_transcript_chunks(
  query_embedding VECTOR(1536),
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id BIGINT,
  source TEXT,
  chunk_index INT,
  content TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
BEGIN
  RETURN QUERY
  SELECT
    tc.id,
    tc.source,
    tc.chunk_index,
    tc.content,
    1 - (tc.embedding <=> query_embedding) AS similarity
  FROM transcript_chunks tc
  ORDER BY tc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================================================
-- Extensions in Public schema (Warning only — moving is optional)
--
-- The linter also flags public.vector and public.pg_trgm extensions.
-- Supabase recommends moving extensions to the 'extensions' schema:
--
--   CREATE SCHEMA IF NOT EXISTS extensions;
--   ALTER EXTENSION vector SET SCHEMA extensions;
--   ALTER EXTENSION pg_trgm SET SCHEMA extensions;
--
-- However, this WILL BREAK any queries that reference vector types
-- without schema qualification. Only do this if you add 'extensions'
-- to your default search_path, or qualify all vector references.
-- These warnings are safe to ignore if you prefer stability.
-- ============================================================================

-- ============================================================================
-- Leaked Password Protection (Dashboard setting)
--
-- Go to Supabase Dashboard → Authentication → Settings → Security
-- → Enable "Leaked Password Protection"
-- This checks passwords against the HaveIBeenPwned database.
-- ============================================================================

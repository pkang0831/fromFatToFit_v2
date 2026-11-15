-- ============================================================================
-- Guest scan usage tracking (anti-cannibalization)
-- Run in Supabase SQL Editor
--
-- Tracks guest body scans by IP + browser fingerprint hash to enforce
-- a lifetime cap (default 2 scans) per unique visitor, preventing
-- unlimited free scans that bypass the credit system.
-- ============================================================================

CREATE TABLE IF NOT EXISTS guest_scan_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_hash TEXT NOT NULL,
    fingerprint_hash TEXT NOT NULL,
    scan_count INTEGER NOT NULL DEFAULT 1,
    first_scan_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scan_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_guest_scan_fp
    ON guest_scan_usage(fingerprint_hash);

CREATE INDEX IF NOT EXISTS idx_guest_scan_ip
    ON guest_scan_usage(ip_hash, last_scan_at DESC);

ALTER TABLE guest_scan_usage ENABLE ROW LEVEL SECURITY;
-- No user policies: accessed exclusively via service_role

'use client';

import { analyticsApi } from '@/lib/api/services';

type AnalyticsValue = string | number | boolean | null | undefined;
type SanitizedAnalyticsValue = Exclude<AnalyticsValue, undefined>;

type RetentionEventName =
  | 'scan_success'
  | 'reengagement_session'
  | 'history_viewed'
  | 'notification_sent'
  | 'notification_opened'
  | 'progress_proof_started'
  | 'progress_proof_completed'
  | 'progress_compare_viewed'
  | 'progress_checkin_started'
  | 'progress_checkin_completed'
  | 'progress_checkin_failed'
  | 'share_created'
  | 'share_viewed'
  | 'share_revoked'
  | 'referred_try_started'
  | 'register_completed'
  | 'purchase_completed';

export function trackEvent(
  eventName: string,
  properties: Record<string, AnalyticsValue> = {},
) {
  if (typeof window === 'undefined') return;

  const gtag = (window as Window & {
    gtag?: (command: string, eventName: string, params?: Record<string, AnalyticsValue>) => void;
  }).gtag;

  if (typeof gtag !== 'function') return;

  const params = Object.fromEntries(
    Object.entries(properties).filter(([, value]) => value !== undefined)
  );

  gtag('event', eventName, params);
}

function sanitizeProperties(
  properties: Record<string, AnalyticsValue>
): Record<string, SanitizedAnalyticsValue> {
  return Object.fromEntries(
    Object.entries(properties).filter(([, value]) => value !== undefined)
  ) as Record<string, SanitizedAnalyticsValue>;
}

const RETENTION_SESSION_KEY = 'denevira_retention_session_id';

export function getRetentionSessionId(): string | null {
  if (typeof window === 'undefined') return null;

  try {
    const existing = window.sessionStorage.getItem(RETENTION_SESSION_KEY);
    if (existing) return existing;

    const nextId =
      typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
        ? crypto.randomUUID()
        : `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

    window.sessionStorage.setItem(RETENTION_SESSION_KEY, nextId);
    return nextId;
  } catch {
    return null;
  }
}

export function trackRetentionEvent(
  eventName: RetentionEventName,
  properties: Record<string, AnalyticsValue> = {},
) {
  const params = sanitizeProperties({
    session_id: properties.session_id ?? getRetentionSessionId(),
    ...properties,
  });
  trackEvent(eventName, params);

  if (typeof window === 'undefined') return;

  void analyticsApi.captureRetentionEvent({
    event_name: eventName,
    surface: typeof params.surface === 'string' ? params.surface : 'unknown',
    properties: params,
  }).catch(() => {
    // Ignore sink failures so the product flow never breaks on analytics.
  });
}

const REENGAGEMENT_LAST_SEEN_KEY = 'denevira_reengagement_last_seen_at';
const REENGAGEMENT_MIN_GAP_MS = 6 * 60 * 60 * 1000;

export function trackReengagementSession(
  properties: Record<string, AnalyticsValue> = {},
) {
  if (typeof window === 'undefined') return;

  let sessionGapHours: number | null = null;

  try {
    const lastSeenRaw = window.localStorage.getItem(REENGAGEMENT_LAST_SEEN_KEY);
    const lastSeen = lastSeenRaw ? Number(lastSeenRaw) : 0;
    const now = Date.now();

    if (lastSeen > 0) {
      sessionGapHours = Math.round(((now - lastSeen) / (60 * 60 * 1000)) * 10) / 10;
      if (now - lastSeen < REENGAGEMENT_MIN_GAP_MS) {
        window.localStorage.setItem(REENGAGEMENT_LAST_SEEN_KEY, String(now));
        return;
      }
    }

    trackRetentionEvent('reengagement_session', {
      ...properties,
      session_gap_hours: sessionGapHours,
    });
    window.localStorage.setItem(REENGAGEMENT_LAST_SEEN_KEY, String(now));
  } catch {
    trackRetentionEvent('reengagement_session', properties);
  }
}

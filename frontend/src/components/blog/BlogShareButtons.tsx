'use client';

import { useState } from 'react';

interface BlogShareButtonsProps {
  /** Canonical URL of the post (Medium URL when present, site URL otherwise). */
  url: string;
  /** Display title used in share platforms. */
  title: string;
  /** Optional one-line summary; falls back to title when omitted. */
  summary?: string;
  /** Pre-baked UTM tags appended to the URL per platform. */
  utmCampaign?: string;
}

const LINKED_IN = 'https://www.linkedin.com/sharing/share-offsite/?url=';
const X = 'https://twitter.com/intent/tweet?text=';
const FACEBOOK = 'https://www.facebook.com/sharer/sharer.php?u=';

/**
 * Native share buttons for blog posts.
 *
 * Why this matters:
 * - Reduces friction to share — every click is a free distribution event.
 * - UTM-tagged URLs preserve attribution in analytics.
 * - Each platform gets the optimal share-text shape (X gets a quote +
 *   hashtags; LinkedIn just the URL since it auto-pulls OG; Facebook same).
 * - Copy-link button captures non-platform sharers (SMS, email, Slack).
 *
 * Accessibility: each button has a label and proper aria-label. Copy-link
 * uses the Clipboard API with a visible 'copied' confirmation.
 */
export function BlogShareButtons({
  url,
  title,
  summary,
  utmCampaign,
}: BlogShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  const tagged = (source: string) => {
    if (!utmCampaign) return url;
    const sep = url.includes('?') ? '&' : '?';
    return `${url}${sep}utm_source=${source}&utm_medium=social&utm_campaign=${encodeURIComponent(utmCampaign)}`;
  };

  const xText = encodeURIComponent(`${summary ?? title}\n\n`);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(tagged('copy'));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // ignore — most modern browsers support this
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-2 text-sm">
      <span className="text-xs font-semibold uppercase tracking-[0.18em] text-white/50">
        Share
      </span>

      <a
        href={`${X}${xText}${encodeURIComponent(tagged('x'))}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Share on X"
        className="rounded-full border border-white/[0.12] bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-white/80 transition-colors hover:border-primary/40 hover:text-primary"
      >
        X
      </a>

      <a
        href={`${LINKED_IN}${encodeURIComponent(tagged('linkedin'))}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Share on LinkedIn"
        className="rounded-full border border-white/[0.12] bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-white/80 transition-colors hover:border-primary/40 hover:text-primary"
      >
        LinkedIn
      </a>

      <a
        href={`${FACEBOOK}${encodeURIComponent(tagged('facebook'))}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Share on Facebook"
        className="rounded-full border border-white/[0.12] bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-white/80 transition-colors hover:border-primary/40 hover:text-primary"
      >
        Facebook
      </a>

      <button
        type="button"
        onClick={copyToClipboard}
        aria-label="Copy link"
        className="rounded-full border border-white/[0.12] bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-white/80 transition-colors hover:border-primary/40 hover:text-primary"
      >
        {copied ? 'Copied' : 'Copy link'}
      </button>
    </div>
  );
}

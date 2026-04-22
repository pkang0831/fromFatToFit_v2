import Link from 'next/link';
import type { ReactNode } from 'react';

import type { BlogPost } from '@/content/blog/posts';

/**
 * Represents a link candidate: a human-written anchor phrase that, when
 * found in prose, should be linked to a target blog post.
 */
export interface LinkTarget {
  slug: string;
  /** Lower-cased phrase to match against paragraph text. */
  phrase: string;
}

/**
 * Build the per-render link targets for a post. Candidates are drawn
 * from every OTHER post's title and keywords[0], lower-cased. We rank
 * longer phrases first so "weight loss plateau" beats "plateau" when
 * both could match, reducing ambiguous anchor choices.
 */
export function buildLinkTargets(posts: BlogPost[], currentSlug: string): LinkTarget[] {
  const targets: LinkTarget[] = [];
  for (const p of posts) {
    if (p.slug === currentSlug) continue;
    const candidates: string[] = [];
    // Primary keyword is the strongest anchor signal.
    if (p.keywords && p.keywords[0]) candidates.push(p.keywords[0]);
    // Title second — tends to be a clean natural phrase.
    if (p.title) candidates.push(p.title);
    for (const raw of candidates) {
      const phrase = raw.toLowerCase().trim();
      // Skip very short anchors and anchors that are sub-phrases of the
      // current post's keyword (would self-link visually).
      if (phrase.length < 12) continue;
      targets.push({ slug: p.slug, phrase });
    }
  }
  // Longest-first ordering so overlapping matches prefer the specific one.
  targets.sort((a, b) => b.phrase.length - a.phrase.length);
  return targets;
}

/**
 * Replace up to `budget` occurrences of any target.phrase in the given
 * text with a Next.js <Link> to that target.slug. Matches are
 * case-insensitive, word-boundary-aware, and leftmost-preferred.
 *
 * linkedSlugs is mutated: a slug is only ever linked once across the
 * whole article (tracked externally by the caller).
 */
export function linkifyText(
  text: string,
  targets: LinkTarget[],
  linkedSlugs: Set<string>,
  budget: { remaining: number },
): ReactNode[] {
  if (budget.remaining <= 0) return [text];

  const result: ReactNode[] = [];
  const lower = text.toLowerCase();
  let cursor = 0;
  let key = 0;

  while (cursor < text.length && budget.remaining > 0) {
    // Find the leftmost matching phrase that hasn't been linked yet.
    let bestStart = -1;
    let bestPhrase = '';
    let bestSlug = '';
    for (const t of targets) {
      if (linkedSlugs.has(t.slug)) continue;
      // word-boundary check: ensure match starts at a word boundary and
      // ends at a word boundary in the original-cased text.
      const idx = lower.indexOf(t.phrase, cursor);
      if (idx < 0) continue;
      const charBefore = idx === 0 ? ' ' : text[idx - 1];
      const endIdx = idx + t.phrase.length;
      const charAfter = endIdx >= text.length ? ' ' : text[endIdx];
      if (!/\W|^$/.test(charBefore) || !/\W|^$/.test(charAfter)) continue;
      if (bestStart === -1 || idx < bestStart) {
        bestStart = idx;
        bestPhrase = t.phrase;
        bestSlug = t.slug;
      }
    }
    if (bestStart === -1) break;

    // Emit the leading unlinked text, then the <Link>, then advance.
    if (bestStart > cursor) {
      result.push(text.slice(cursor, bestStart));
    }
    const visible = text.slice(bestStart, bestStart + bestPhrase.length);
    result.push(
      <Link
        key={`il-${key++}`}
        href={`/blog/${bestSlug}`}
        className="text-primary underline-offset-4 hover:underline"
      >
        {visible}
      </Link>,
    );
    linkedSlugs.add(bestSlug);
    budget.remaining -= 1;
    cursor = bestStart + bestPhrase.length;
  }

  if (cursor < text.length) {
    result.push(text.slice(cursor));
  }
  return result.length > 0 ? result : [text];
}

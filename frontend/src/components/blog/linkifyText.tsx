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
 * Curated short anchor phrases that appear organically in prose and
 * are specific enough not to false-match common English. Each phrase
 * maps to the best single destination slug. Additive on top of the
 * automatic title/keyword-based candidates.
 */
const CURATED_ANCHORS: ReadonlyArray<{ phrase: string; slug: string }> = [
  { phrase: 'sleep debt', slug: 'does-bad-sleep-ruin-weight-loss' },
  { phrase: 'water weight', slug: 'is-losing-5kg-in-a-week-water-weight' },
  { phrase: 'water retention', slug: 'does-cutting-sodium-cause-water-retention' },
  { phrase: 'body recomposition', slug: 'my-scale-wont-move-but-my-jeans-fit-looser' },
  { phrase: 'non-scale victories', slug: 'non-scale-victories-weight-loss' },
  { phrase: 'weekly average', slug: 'daily-weighing-eating-disorder-risk' },
  { phrase: 'set point', slug: 'how-do-you-know-youve-reached-set-point' },
  { phrase: 'meal prep', slug: 'do-i-have-to-meal-prep-to-lose-weight' },
  { phrase: 'social events', slug: 'how-to-eat-at-social-events-on-a-diet' },
  { phrase: 'skinny fat', slug: 'skinny-fat-normal-weight-high-body-fat' },
  { phrase: 'neural adaptation', slug: 'why-does-strength-increase-before-muscle-size' },
  { phrase: 'weight loss plateau', slug: 'how-to-break-a-weight-loss-plateau' },
  { phrase: 'progress photos', slug: 'why-progress-photos-dont-show-progress' },
  { phrase: 'cheat day', slug: 'are-cheat-days-bad-for-weight-loss' },
  { phrase: 'leptin', slug: 'why-is-my-appetite-stronger-on-a-diet' },
  { phrase: 'ghrelin', slug: 'why-is-my-appetite-stronger-on-a-diet' },
  { phrase: 'maintenance phase', slug: 'first-month-of-maintenance-after-weight-loss' },
  { phrase: 'fat loss plateau', slug: 'how-to-break-a-weight-loss-plateau' },
  { phrase: 'one bad day', slug: 'does-one-bad-day-ruin-a-diet' },
  { phrase: 'one bad meal', slug: 'does-one-bad-meal-ruin-a-diet' },
  { phrase: 'mirror checking', slug: 'how-to-stop-mirror-checking-on-a-diet' },
  { phrase: 'binge week', slug: 'how-to-stop-a-binge-from-becoming-a-binge-week' },
  { phrase: 'middle of the diet', slug: 'why-is-the-middle-of-weight-loss-the-hardest' },
  { phrase: 'unglamorous middle', slug: 'past-the-messy-middle-of-weight-loss' },
  { phrase: 'body fat percentage', slug: 'why-lower-body-fat-feels-so-stubborn' },
  { phrase: 'calorie deficit', slug: 'why-cant-i-sleep-on-a-calorie-deficit' },
  { phrase: 'protein', slug: 'how-much-protein-do-i-need-to-lose-fat' },
];

/**
 * Build the per-render link targets for a post. Candidates are drawn
 * from every OTHER post's title and keywords[0], lower-cased. Short
 * curated anchors (CURATED_ANCHORS) are added on top so common
 * domain phrases ("plateau", "leptin") can actually be linked. We
 * rank longer phrases first so "weight loss plateau" beats "plateau"
 * when both could match.
 */
export function buildLinkTargets(posts: BlogPost[], currentSlug: string): LinkTarget[] {
  const targets: LinkTarget[] = [];
  for (const p of posts) {
    if (p.slug === currentSlug) continue;
    const candidates: string[] = [];
    if (p.keywords && p.keywords[0]) candidates.push(p.keywords[0]);
    if (p.title) candidates.push(p.title);
    for (const raw of candidates) {
      const phrase = raw.toLowerCase().trim();
      if (phrase.length < 10) continue;
      targets.push({ slug: p.slug, phrase });
    }
  }
  for (const a of CURATED_ANCHORS) {
    if (a.slug === currentSlug) continue;
    if (a.phrase.length < 6) continue;
    targets.push({ slug: a.slug, phrase: a.phrase.toLowerCase() });
  }
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

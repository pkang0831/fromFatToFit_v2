import Image from 'next/image';
import Link from 'next/link';

interface AuthorBylineProps {
  /** ISO date (YYYY-MM-DD) when the post was first published. */
  publishedDate: string;
  /** ISO date (YYYY-MM-DD) of last meaningful update. Rendered only when it
   *  differs from publishedDate. */
  updatedDate?: string;
  /** Reading time string, e.g. "8 min read". */
  readingTime: string;
}

/**
 * Compact author byline shown above the article H1.
 *
 * Purpose in the SEO strategy:
 * - Gives readers the visible "who wrote this" answer Google's E-E-A-T
 *   guidance expects on YMYL (health) content. Without this, the author
 *   signal only lived in metadata, which doesn't move trust behaviors
 *   like dwell time or return visits.
 * - Provides a crawlable in-body link to the author page so Google sees
 *   the association without relying only on rel=author and JSON-LD.
 * - Surfaces "Updated" distinctly from "Published" when the post has
 *   been meaningfully revised, which Google treats as a freshness signal.
 */
export function AuthorByline({ publishedDate, updatedDate, readingTime }: AuthorBylineProps) {
  const showUpdated = updatedDate && updatedDate !== publishedDate;

  return (
    <div className="flex flex-wrap items-center gap-3 text-sm text-white/58">
      <Link
        href="/authors/pkang"
        className="inline-flex items-center gap-2 transition-colors hover:text-primary"
      >
        <span className="relative h-8 w-8 shrink-0 overflow-hidden rounded-full border border-white/[0.12]">
          <Image
            src="/founder/founder-story-hanok-20260119.webp"
            alt="pkang, fitness and diet writer who lost 50 kg"
            fill
            className="object-cover"
            sizes="32px"
          />
        </span>
        <span className="font-medium text-white/80">By pkang</span>
      </Link>
      <span className="h-1 w-1 rounded-full bg-white/20" aria-hidden="true" />
      <time dateTime={publishedDate}>Published {publishedDate}</time>
      {showUpdated ? (
        <>
          <span className="h-1 w-1 rounded-full bg-white/20" aria-hidden="true" />
          <time dateTime={updatedDate}>Updated {updatedDate}</time>
        </>
      ) : null}
      <span className="h-1 w-1 rounded-full bg-white/20" aria-hidden="true" />
      <span>{readingTime}</span>
    </div>
  );
}

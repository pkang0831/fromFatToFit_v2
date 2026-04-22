import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

/**
 * "About the author" box rendered after the article body.
 *
 * Purpose in the SEO strategy (E-E-A-T):
 * - Google's health/YMYL ranking guidance asks for visible author
 *   expertise, experience, and trustworthiness. A rendered bio with
 *   photo, credential, and a link to the author page is the cheapest
 *   single signal that moves this needle.
 * - Keeps the credential ("lost 50 kg over five years") adjacent to
 *   the article content so dwelling readers connect the byline to
 *   the experience that backs every diet/appetite claim the article
 *   makes.
 * - Contributes an extra in-body internal link to /authors/pkang,
 *   reinforcing the author page as a topical pillar.
 */
export function AuthorBox() {
  return (
    <aside
      className="rounded-[32px] border border-white/[0.08] bg-white/[0.03] px-6 py-6 md:px-8 md:py-7"
      aria-label="About the author"
    >
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start">
        <Link
          href="/authors/pkang"
          className="relative h-20 w-20 shrink-0 overflow-hidden rounded-full border border-white/[0.12] transition-opacity hover:opacity-90"
          aria-label="pkang author page"
        >
          <Image
            src="/founder/founder-story-hanok-20260119.webp"
            alt="pkang portrait, the author of this article"
            fill
            className="object-cover"
            sizes="80px"
          />
        </Link>
        <div className="flex-1 space-y-3">
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary/80">
              About the author
            </p>
            <h2 className="text-xl font-bold text-white md:text-2xl">
              <Link
                href="/authors/pkang"
                className="transition-colors hover:text-primary"
              >
                pkang
              </Link>
            </h2>
          </div>
          <p className="text-base leading-7 text-white/68">
            I lost 50 kg over five years and later turned that transformation
            into a professional modelling career. I write about appetite,
            body image, and the slow work of learning how to read the body
            without panic. Every post on Devenira is written from my own
            five-year record of doing the work.
          </p>
          <Link
            href="/authors/pkang"
            className="inline-flex items-center gap-2 text-sm font-semibold text-primary underline-offset-4 hover:underline"
          >
            Read more from pkang
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </div>
    </aside>
  );
}

import type { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';

import { BlogPostCard } from '@/components/blog/BlogPostCard';
import { getAllBlogPosts } from '@/content/blog/posts';
import { SITE_ORIGIN, absoluteUrl } from '@/lib/site';

/**
 * Author page for pkang.
 *
 * Purpose in the SEO strategy:
 * 1. E-E-A-T signal — Google's health/YMYL ranking guidance explicitly
 *    requires a visible author with experience, expertise and
 *    trustworthiness. A 50 kg weight-loss transformation + professional
 *    modelling career is the credential that backs every diet post.
 * 2. JSON-LD Person schema anchor — every blog post's Article schema
 *    references this URL as the author's @id. Having a real page at
 *    that URL makes the reference resolvable.
 * 3. Internal link hub — aggregates all 64 posts behind a single URL
 *    that can accumulate backlinks (guest posts can point here instead
 *    of scattering across slugs).
 */
export const metadata: Metadata = {
  title: 'pkang — Fitness and Diet Writer (Lost 50 kg)',
  description:
    'I am pkang — a fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. I write about appetite, body image, and the slow work of learning how to read the body without panic.',
  keywords: [
    'pkang',
    '50 kg weight loss',
    'weight loss writer',
    'body image writer',
    'founder devenira',
  ],
  alternates: {
    canonical: absoluteUrl('/authors/pkang'),
  },
  openGraph: {
    title: 'pkang — Fitness and Diet Writer',
    description:
      'Lost 50 kg over five years. Wrote about every hard part of it. Now writing about body image, appetite, and honest progress without panic.',
    type: 'profile',
    url: absoluteUrl('/authors/pkang'),
    images: [{ url: absoluteUrl('/founder/founder-story-hanok-20260119.webp') }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'pkang — Fitness and Diet Writer',
    description:
      'Lost 50 kg over five years. Now writing about body image, appetite, and honest progress without panic.',
    images: [absoluteUrl('/founder/founder-story-hanok-20260119.webp')],
  },
};

const AUTHOR_JSON_LD = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  '@id': absoluteUrl('/authors/pkang'),
  name: 'pkang',
  alternateName: ['P. Kang'],
  url: absoluteUrl('/authors/pkang'),
  image: absoluteUrl('/founder/founder-story-hanok-20260119.webp'),
  jobTitle: 'Fitness and Diet Writer',
  description:
    'Fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. Writes about appetite, body image, and the slow work of learning how to read the body without panic.',
  worksFor: {
    '@type': 'Organization',
    '@id': `${SITE_ORIGIN}/#organization`,
    name: 'Devenira',
    url: SITE_ORIGIN,
  },
  knowsAbout: [
    'Weight loss',
    'Body image',
    'Appetite regulation',
    'Dieting psychology',
    'Body recomposition',
    'Maintenance after weight loss',
    'Scale anxiety',
    'Transformation photography',
  ],
  sameAs: ['https://medium.com/@pkang'],
};

export default function AuthorPkangPage() {
  const posts = getAllBlogPosts();

  return (
    <div className="bg-[#0a0a0f] text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(AUTHOR_JSON_LD) }}
      />

      <section className="px-6 py-16 md:py-24">
        <div className="mx-auto max-w-4xl">
          <div className="grid gap-10 md:grid-cols-[220px_1fr] md:items-start">
            <div className="overflow-hidden rounded-[32px] border border-white/[0.08] bg-white/[0.03]">
              <div className="relative aspect-[3/4]">
                <Image
                  src="/founder/founder-story-hanok-20260119.webp"
                  alt="pkang, fitness and diet writer, after a 50 kg transformation"
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 220px"
                  priority
                />
              </div>
            </div>

            <div className="space-y-5">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Author
              </p>
              <h1 className="text-4xl font-bold leading-[0.95] tracking-tight md:text-5xl">
                pkang
              </h1>
              <p className="text-xl leading-8 text-white/80">
                Fitness and diet writer. Lost 50 kg over five years and later turned that
                transformation into a professional modelling career.
              </p>
              <p className="text-base leading-7 text-white/62">
                I write about appetite, body image, and the slow work of learning how to read
                the body without panic. Most of my writing lives on Medium as{' '}
                <a
                  href="https://medium.com/@pkang"
                  className="text-primary underline-offset-4 hover:underline"
                  rel="me noopener"
                >
                  @pkang
                </a>
                . The fuller archive — including research notes and the founder story behind
                Devenira — lives here.
              </p>
            </div>
          </div>

          <div className="mt-16 grid gap-4 rounded-[32px] border border-white/[0.08] bg-white/[0.03] p-8 md:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Experience
              </p>
              <p className="mt-2 text-base leading-7 text-white/75">
                5 years of documented weight-loss work from 128 kg to 78 kg, plus 2 years of
                maintenance. Every piece here is first-person from that arc.
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Expertise
              </p>
              <p className="mt-2 text-base leading-7 text-white/75">
                Body composition, appetite regulation, binge-recovery patterns, maintenance
                psychology, scale-reading literacy, training-volume and hunger interaction.
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Not a doctor
              </p>
              <p className="mt-2 text-base leading-7 text-white/75">
                This is lived experience and observational writing, not medical advice. For
                clinical questions — thyroid, metabolic disease, ED history — see a
                physician, not a blog.
              </p>
            </div>
          </div>

          <div className="mt-16 space-y-8">
            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Recent articles
              </p>
              <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                All posts by pkang
              </h2>
              <p className="text-base text-white/62">
                {posts.length} articles to date. The full body lives on{' '}
                <a
                  href="https://medium.com/@pkang"
                  className="text-primary underline-offset-4 hover:underline"
                  rel="me noopener"
                >
                  Medium
                </a>
                .
              </p>
            </div>
            <div className="grid gap-8 md:grid-cols-2">
              {posts.map((post) => (
                <BlogPostCard key={post.slug} post={post} />
              ))}
            </div>
          </div>

          <div className="mt-16 rounded-[32px] border border-primary/20 bg-primary/[0.08] px-6 py-8 md:px-8">
            <div className="mx-auto max-w-3xl space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Try the product
              </p>
              <h2 className="text-3xl font-bold tracking-tight text-white">
                Start a free body-fat estimate from a photo.
              </h2>
              <p className="max-w-2xl text-lg leading-8 text-white/62">
                Devenira grew out of the same slow middle that this writing is about. If the
                mirror is louder than the evidence right now, start with one scan.
              </p>
              <Link
                href="/try"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-primary px-6 py-3 text-sm font-semibold text-white shadow-glow-cyan transition-transform duration-200 hover:scale-[1.02]"
              >
                Try the free body scan
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

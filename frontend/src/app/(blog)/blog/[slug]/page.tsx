import type { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowRight } from 'lucide-react';

import { AuthorBox } from '@/components/blog/AuthorBox';
import { AuthorByline } from '@/components/blog/AuthorByline';
import { BlogArticleContent } from '@/components/blog/BlogArticleContent';
import { BlogPostCard } from '@/components/blog/BlogPostCard';
import { BlogShareButtons } from '@/components/blog/BlogShareButtons';
import { BlogStructuredData } from '@/components/blog/BlogStructuredData';
import { ReadingProgressBar } from '@/components/blog/ReadingProgressBar';
import {
  CLUSTERS,
  getAllBlogPosts,
  getBlogPostBySlug,
  getRelatedBlogPosts,
} from '@/content/blog/posts';
import { SITE_ORIGIN, absoluteUrl } from '@/lib/site';

interface BlogPostPageProps {
  params: {
    slug: string;
  };
}

export async function generateStaticParams() {
  return getAllBlogPosts().map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({ params }: BlogPostPageProps): Promise<Metadata> {
  const post = getBlogPostBySlug(params.slug);

  if (!post) {
    return {
      title: 'Not Found',
    };
  }

  // SEO title and meta description are distinct from editorial title/description.
  // Editorial title/description is kept for OG + Twitter (social feed voice),
  // while search-facing surfaces use seoTitle / metaDescription when present.
  // See marketing/fitness_blogging/blog_strategy/seo_optimization_rules.md.
  //
  const canonicalUrl = absoluteUrl(`/blog/${post.slug}`);
  return {
    title: post.seoTitle ?? post.title,
    description: post.metaDescription ?? post.description,
    keywords: post.keywords,
    authors: [{ name: 'pkang', url: absoluteUrl('/authors/pkang') }],
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title: post.title,
      description: post.socialDescription,
      type: 'article',
      url: canonicalUrl,
      publishedTime: post.date,
      modifiedTime: post.lastModified ?? post.date,
      images: [
        {
          // MUST use www hostname — apex (devenira.com) 307-redirects to
          // www which breaks non-redirect-following crawlers like
          // Medium's Import-from-URL. Keep canonical/authors URLs on
          // apex though (those are logical identifiers, not fetched).
          url: `${SITE_ORIGIN}${post.heroImage}`,
          width: 1600,
          height: 1000,
          alt: post.heroAlt,
        },
      ],
      authors: ['pkang'],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.socialDescription,
      images: [`${SITE_ORIGIN}${post.heroImage}`],
      creator: '@pkang',
    },
  };
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const post = getBlogPostBySlug(params.slug);

  if (!post) {
    notFound();
  }

  const relatedPosts = getRelatedBlogPosts(post.slug, 2);
  const clusterMeta = post.cluster ? CLUSTERS[post.cluster] : undefined;

  const shareUrl = absoluteUrl(`/blog/${post.slug}`);

  return (
    <div className="bg-[#0a0a0f] text-white">
      <ReadingProgressBar />
      <BlogStructuredData post={post} />
      <section className="px-6 py-16 md:py-20">
        <article className="mx-auto max-w-4xl">
          <div className="space-y-8">
            <div className="flex flex-wrap items-center gap-3 text-xs text-white/42">
              <Link href="/blog" className="transition-colors hover:text-primary">
                Blog
              </Link>
              {clusterMeta ? (
                <>
                  <span className="h-1 w-1 rounded-full bg-white/20" />
                  <Link
                    href={`/blog/topic/${clusterMeta.slug}`}
                    className="transition-colors hover:text-primary"
                  >
                    {clusterMeta.title}
                  </Link>
                </>
              ) : null}
            </div>

            <div className="space-y-5">
              <div className="flex flex-wrap gap-2">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full border border-white/[0.1] bg-white/[0.03] px-3 py-1 text-[11px] font-medium uppercase tracking-[0.16em] text-white/70"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <h1 className="max-w-3xl text-4xl font-bold leading-[0.95] tracking-tight text-white md:text-6xl">
                {post.title}
              </h1>
              <p className="max-w-3xl text-lg leading-8 text-white/62 md:text-xl">{post.deck}</p>
              <AuthorByline
                publishedDate={post.date}
                updatedDate={post.lastModified}
                readingTime={post.readingTime}
              />
            </div>

            {/*
              Hero rendered as <figure><img> with an ABSOLUTE URL +
              `unoptimized` (bypass Next.js image proxy). Rationale:
              Medium's Import-from-URL feature fetches the page, finds
              the first content <img>, and uses it as the story cover
              ONLY if the `src` is an absolute URL that resolves
              directly to an image payload without a proxy hop.

              Previous attempts:
                1. <Image fill> → rendered as <img position:absolute>
                   inside a wrapper. Medium treated as page chrome and
                   skipped.
                2. <Image width height> with Next.js proxy →
                   <img src="/_next/image?url=..."> relative proxy URL.
                   Medium importer still failed to carry it.

              This version renders a clean
                <img src="https://www.devenira.com/founder/..."
                     width="1600" height="1000">
              that Medium's importer reliably picks up.

              CRITICAL: URL MUST include `www.` subdomain. Apex
              (https://devenira.com) 307-redirects to www, and
              Medium's importer doesn't follow redirects — images
              fetched via apex URLs get silently dropped from the
              imported story, which we spent three iterations
              debugging before discovering the redirect (2026-04-23).

              Performance cost: the hero webp (~100 KB, already
              orientation-corrected) is served at full size instead of
              via Next.js responsive srcSet. Vercel's edge still
              caches it, and on mobile this is at most ~60 KB extra.
              Trade is worth it: reliable Medium import on every post.
            */}
            <figure className="relative overflow-hidden rounded-[32px] border border-white/[0.08] bg-white/[0.03]">
              <Image
                src={`${SITE_ORIGIN}${post.heroImage}`}
                alt={post.heroAlt}
                width={1600}
                height={1000}
                className="h-auto w-full object-cover"
                sizes="(max-width: 1024px) 100vw, 960px"
                priority
                unoptimized
              />
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#060609] via-transparent to-transparent" />
            </figure>

            <div className="rounded-[32px] border border-white/[0.08] bg-[#080810] px-6 py-8 md:px-10 md:py-10">
              <div className="mx-auto max-w-3xl">
                <BlogArticleContent sections={post.sections} currentSlug={post.slug} />
              </div>
            </div>

            <AuthorBox />

            <div className="rounded-[24px] border border-white/[0.08] bg-white/[0.02] px-6 py-5">
              <BlogShareButtons
                url={shareUrl}
                title={post.title}
                summary={post.socialDescription}
                utmCampaign={post.slug}
              />
            </div>

            <div className="rounded-[32px] border border-primary/20 bg-primary/[0.08] px-6 py-8 md:px-8">
              <div className="mx-auto max-w-3xl space-y-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">Next step</p>
                <h2 className="text-3xl font-bold tracking-tight text-white">{post.ctaTitle}</h2>
                <p className="max-w-2xl text-lg leading-8 text-white/62">{post.ctaBody}</p>
                <Link
                  href="/try"
                  className="inline-flex items-center gap-2 rounded-full bg-gradient-primary px-6 py-3 text-sm font-semibold text-white shadow-glow-cyan transition-transform duration-200 hover:scale-[1.02]"
                >
                  Try the free body scan
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </article>
      </section>

      {relatedPosts.length > 0 ? (
        <section className="px-6 pb-16">
          <div className="mx-auto max-w-6xl space-y-8">
            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                {clusterMeta ? `More in ${clusterMeta.title}` : 'Keep reading'}
              </p>
              <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                More articles
              </h2>
            </div>
            <div className="grid gap-8 md:grid-cols-2">
              {relatedPosts.map((relatedPost) => (
                <BlogPostCard key={relatedPost.slug} post={relatedPost} />
              ))}
            </div>
            {clusterMeta ? (
              <div className="pt-4">
                <Link
                  href={`/blog/topic/${clusterMeta.slug}`}
                  className="inline-flex items-center gap-2 text-sm font-semibold text-primary underline-offset-4 hover:underline"
                >
                  See all articles on {clusterMeta.title}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            ) : null}
          </div>
        </section>
      ) : null}
    </div>
  );
}

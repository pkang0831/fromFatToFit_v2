import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowRight } from 'lucide-react';

import { BlogPostCard } from '@/components/blog/BlogPostCard';
import {
  CLUSTERS,
  getAllClusters,
  getBlogPostsByCluster,
} from '@/content/blog/posts';
import { SITE_ORIGIN, absoluteUrl } from '@/lib/site';

interface ClusterPageProps {
  params: { cluster: string };
}

/**
 * Pillar / topic hub pages.
 *
 * Purpose:
 * 1. Topical authority signal — Google rewards sites with
 *    pillar-and-spoke structures. A "Hunger on a Diet" pillar that links
 *    to 9 spoke posts, each linking back, is stronger than 9 orphan posts.
 * 2. Internal-link concentration — every cluster pillar is a high-value
 *    internal anchor that captures long-tail traffic around the pillar
 *    keyword, then routes visitors to the right spoke.
 * 3. Backlink magnet — guest posts / external mentions can point at the
 *    pillar URL and have it be evergreen. Pillar URLs live at
 *    /blog/topic/[cluster] and are stable.
 *
 * This page is rendered statically at build time (generateStaticParams).
 */

export function generateStaticParams() {
  return getAllClusters().map((c) => ({ cluster: c.slug }));
}

export function generateMetadata({ params }: ClusterPageProps): Metadata {
  const meta = CLUSTERS[params.cluster];
  if (!meta) return { title: 'Not found' };
  return {
    title: meta.seoTitle,
    description: meta.metaDescription,
    keywords: [meta.primaryKeyword, ...meta.secondaryKeywords],
    authors: [{ name: 'pkang', url: absoluteUrl('/authors/pkang') }],
    alternates: {
      canonical: absoluteUrl(`/blog/topic/${meta.slug}`),
    },
    openGraph: {
      title: meta.title,
      description: meta.description,
      type: 'website',
      url: absoluteUrl(`/blog/topic/${meta.slug}`),
    },
    twitter: {
      card: 'summary_large_image',
      title: meta.title,
      description: meta.description,
    },
  };
}

export default function ClusterPage({ params }: ClusterPageProps) {
  const meta = CLUSTERS[params.cluster];
  if (!meta) notFound();

  const posts = getBlogPostsByCluster(params.cluster);

  const itemListJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': absoluteUrl(`/blog/topic/${meta.slug}`),
    name: meta.title,
    description: meta.description,
    url: absoluteUrl(`/blog/topic/${meta.slug}`),
    about: meta.primaryKeyword,
    keywords: [meta.primaryKeyword, ...meta.secondaryKeywords].join(', '),
    mainEntity: {
      '@type': 'ItemList',
      itemListElement: posts.map((post, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        url: absoluteUrl(`/blog/${post.slug}`),
        name: post.title,
      })),
    },
  };

  // Pillar-page FAQPage schema. Aggregated from the answerBox sections on
  // 4-5 representative posts in the cluster (see scripts/seo_retrofit/
  // apply_cluster_faq_20260422.py). FAQPage rich result on the pillar URL
  // expands SERP real-estate massively for the pillar keyword.
  const faqJsonLd = meta.faqItems && meta.faqItems.length > 0
    ? {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: meta.faqItems.map((item) => ({
          '@type': 'Question',
          name: item.question,
          acceptedAnswer: {
            '@type': 'Answer',
            text: item.answer,
          },
        })),
      }
    : null;

  const breadcrumbJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: SITE_ORIGIN },
      { '@type': 'ListItem', position: 2, name: 'Blog', item: absoluteUrl('/blog') },
      {
        '@type': 'ListItem',
        position: 3,
        name: meta.title,
        item: absoluteUrl(`/blog/topic/${meta.slug}`),
      },
    ],
  };

  return (
    <div className="bg-[#0a0a0f] text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      {faqJsonLd ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
        />
      ) : null}

      <section className="px-6 py-16 md:py-24">
        <div className="mx-auto max-w-4xl">
          <div className="space-y-5">
            <div className="flex items-center gap-3 text-xs text-white/62">
              <Link href="/blog" className="transition-colors hover:text-primary">
                Blog
              </Link>
              <span>/</span>
              <span>Topic</span>
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
              Pillar
            </p>
            <h1 className="text-4xl font-bold leading-[0.95] tracking-tight md:text-6xl">
              {meta.title}
            </h1>
            <p className="max-w-3xl text-lg leading-8 text-white/80 md:text-xl">
              {meta.description}
            </p>
            <p className="text-sm text-white/62">
              {posts.length} article{posts.length === 1 ? '' : 's'} in this topic.
            </p>
          </div>

          {posts.length > 0 ? (
            <div className="mt-14 grid gap-8 md:grid-cols-2">
              {posts.map((post) => (
                <BlogPostCard key={post.slug} post={post} />
              ))}
            </div>
          ) : (
            <p className="mt-14 text-base text-white/62">
              No articles here yet. New writing lands first on{' '}
              <a
                href="https://medium.com/@pkang"
                className="text-primary underline-offset-4 hover:underline"
                rel="me noopener"
              >
                Medium
              </a>
              .
            </p>
          )}

          {meta.faqItems && meta.faqItems.length > 0 ? (
            <section className="mt-20">
              <div className="space-y-3">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                  FAQ
                </p>
                <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                  Common questions on {meta.title.toLowerCase()}
                </h2>
                <p className="max-w-3xl text-base leading-7 text-white/62">
                  Direct answers pulled from the most-read posts in this topic.
                </p>
              </div>
              <div className="mt-8 space-y-3">
                {meta.faqItems.map((item) => (
                  <details
                    key={item.question}
                    className="group rounded-2xl border border-white/[0.08] bg-white/[0.02] px-5 py-4 transition-colors hover:border-primary/30"
                  >
                    <summary className="cursor-pointer list-none text-base font-semibold text-white">
                      {item.question}
                    </summary>
                    <p className="mt-3 text-base leading-7 text-white/70">
                      {item.answer}
                    </p>
                  </details>
                ))}
              </div>
            </section>
          ) : null}

          <div className="mt-16 rounded-[32px] border border-primary/20 bg-primary/[0.08] px-6 py-8 md:px-8">
            <div className="mx-auto max-w-3xl space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
                Next step
              </p>
              <h2 className="text-3xl font-bold tracking-tight text-white">
                Start a free body-fat estimate from one photo.
              </h2>
              <p className="max-w-2xl text-lg leading-8 text-white/62">
                Reading about weight loss is one thing. Building a weekly record that
                panic cannot rewrite is another.
              </p>
              <Link
                href="/try"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-primary px-6 py-3 text-sm font-semibold text-white shadow-glow-cyan transition-transform duration-200 hover:scale-[1.02]"
              >
                Try the free body scan
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="mt-16 space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
              Other topics
            </p>
            <div className="flex flex-wrap gap-2">
              {getAllClusters()
                .filter((c) => c.slug !== meta.slug)
                .map((c) => (
                  <Link
                    key={c.slug}
                    href={`/blog/topic/${c.slug}`}
                    className="rounded-full border border-white/[0.1] bg-white/[0.03] px-4 py-2 text-sm text-white/80 transition-colors hover:border-primary/40 hover:text-primary"
                  >
                    {c.title}
                  </Link>
                ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

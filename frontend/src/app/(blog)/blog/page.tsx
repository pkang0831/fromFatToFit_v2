import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

import { BlogPostCard } from '@/components/blog/BlogPostCard';
import { getAllBlogPosts, getAllClusters } from '@/content/blog/posts';

export const metadata: Metadata = {
  title: 'Weight Loss Blog by pkang — Honest Writing on Diet, Body, Appetite',
  description:
    'Honest writing on weight loss, body image, scale anxiety, appetite, and maintenance. By pkang, who lost 50 kg over 5 years.',
  keywords: [
    'weight loss blog',
    'body image writing',
    'scale anxiety',
    'appetite during diet',
    'weight loss maintenance',
    'pkang',
  ],
  authors: [{ name: 'pkang', url: 'https://devenira.com/authors/pkang' }],
  alternates: {
    canonical: 'https://devenira.com/blog',
  },
  openGraph: {
    title: 'Weight Loss Blog — Honest Writing by pkang',
    description:
      'Lost 50 kg over 5 years. Now writing about appetite, body image, and the slow work of reading the body without panic.',
    type: 'website',
    url: 'https://devenira.com/blog',
    images: [
      {
        url: 'https://devenira.com/founder/founder-story-hanok-20260119.webp',
        alt: 'pkang, fitness and diet writer behind the blog, after a 50 kg transformation',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Weight Loss Blog — Honest Writing by pkang',
    description:
      'Lost 50 kg over 5 years. Now writing about appetite, body image, and the slow work of reading the body without panic.',
    images: ['https://devenira.com/founder/founder-story-hanok-20260119.webp'],
    creator: '@pkang',
  },
};

// Blog-level JSON-LD: declares this index page as the home of the Blog
// resource, with the publisher and author resolved to existing nodes
// (Organization @id, Person @id). Strengthens the topical hub signal.
const BLOG_JSON_LD = {
  '@context': 'https://schema.org',
  '@type': 'Blog',
  '@id': 'https://devenira.com/blog#blog',
  url: 'https://devenira.com/blog',
  name: 'Devenira Blog',
  description:
    'Honest writing on weight loss, body image, scale anxiety, appetite, and maintenance. By pkang, who lost 50 kg over 5 years.',
  inLanguage: 'en',
  author: { '@id': 'https://devenira.com/authors/pkang' },
  publisher: { '@id': 'https://devenira.com/#organization' },
  about: [
    'Weight loss',
    'Body image',
    'Appetite regulation',
    'Dieting psychology',
    'Body recomposition',
    'Maintenance after weight loss',
  ],
};

export default function BlogIndexPage() {
  const posts = getAllBlogPosts();
  if (posts.length === 0) {
    return (
      <div className="bg-[#0a0a0f] px-6 py-32 text-white">
        <div className="mx-auto max-w-4xl rounded-[32px] border border-white/[0.08] bg-white/[0.03] p-10 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">Blog</p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-white">Articles are on the way.</h1>
          <p className="mt-4 text-lg leading-8 text-white/58">
            We are preparing founder notes, body-change essays, and weekly proof thinking.
          </p>
        </div>
      </div>
    );
  }
  const [featuredPost, ...restPosts] = posts;

  return (
    <div className="bg-[#0a0a0f] text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(BLOG_JSON_LD) }}
      />
      <section className="relative overflow-hidden px-6 py-20 md:py-28">
        <div
          className="absolute inset-0 opacity-30"
          style={{ background: 'radial-gradient(ellipse at 20% 20%, rgba(139,92,246,0.14) 0%, transparent 55%)' }}
        />
        <div
          className="absolute inset-0 opacity-25"
          style={{ background: 'radial-gradient(ellipse at 80% 30%, rgba(59,130,246,0.12) 0%, transparent 55%)' }}
        />

        <div className="relative mx-auto max-w-6xl space-y-8">
          <div className="max-w-3xl space-y-5">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-primary/80">Devenira blog</p>
            <h1 className="text-4xl font-bold leading-[0.95] tracking-tight text-white md:text-6xl">
              Proof over panic,
              <span className="gradient-text"> written down.</span>
            </h1>
            <p className="text-lg leading-8 text-white/58 md:text-xl">
              Founder story, mirror logic, scale noise, and body-change thinking for people
              who need better evidence than one emotional morning.
            </p>
          </div>

          <div className="rounded-[32px] border border-white/[0.08] bg-white/[0.03] p-8">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-3xl space-y-3">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/75">
                  Featured article
                </p>
                <h2 className="text-3xl font-bold text-white md:text-4xl">{featuredPost.title}</h2>
                <p className="text-lg leading-8 text-white/58">{featuredPost.description}</p>
              </div>
              <Link
                href={`/blog/${featuredPost.slug}`}
                className="inline-flex items-center gap-2 rounded-full bg-gradient-primary px-6 py-3 text-sm font-semibold text-white shadow-glow-cyan transition-transform duration-200 hover:scale-[1.02]"
              >
                Read featured article
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 pb-12">
        <div className="mx-auto max-w-6xl space-y-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/80">
            Browse by topic
          </p>
          <div className="flex flex-wrap gap-2">
            {getAllClusters().map((c) => (
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
      </section>

      <section className="px-6 pb-24">
        <div className="mx-auto max-w-6xl space-y-12">
          {restPosts.length > 0 ? (
            <div className="grid gap-8 md:grid-cols-2">
              {restPosts.map((post) => (
                <BlogPostCard key={post.slug} post={post} />
              ))}
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}

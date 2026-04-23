import type { BlogPost } from '@/content/blog/posts';

const SITE_ORIGIN = 'https://devenira.com';
// Image / media URLs must use www — apex 307-redirects and most scrapers
// (Medium Import-from-URL, OG crawlers) silently drop images fetched via
// redirects. Canonical / schema @id values stay on apex.
const MEDIA_ORIGIN = 'https://www.devenira.com';
const AUTHOR = {
  '@type': 'Person',
  '@id': `${SITE_ORIGIN}/authors/pkang`,
  name: 'pkang',
  url: `${SITE_ORIGIN}/authors/pkang`,
  image: `${MEDIA_ORIGIN}/founder/founder-story-hanok-20260119.webp`,
  description:
    'Fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career.',
  knowsAbout: [
    'Weight loss',
    'Body image',
    'Appetite regulation',
    'Dieting psychology',
    'Body recomposition',
    'Maintenance after weight loss',
  ],
  sameAs: ['https://medium.com/@pkang'],
} as const;

const PUBLISHER = {
  '@type': 'Organization',
  '@id': `${SITE_ORIGIN}/#organization`,
  name: 'Devenira',
  url: SITE_ORIGIN,
  logo: {
    '@type': 'ImageObject',
    url: `${SITE_ORIGIN}/favicon.ico`,
  },
} as const;

interface BlogStructuredDataProps {
  post: BlogPost;
}

/**
 * Emits JSON-LD structured data for a blog post page.
 *
 * Always includes:
 * - Article schema (or NewsArticle if date is within 48h — not needed here)
 * - Person schema for author (referenced)
 * - BreadcrumbList for blog hierarchy
 *
 * Conditionally includes:
 * - FAQPage when post.schemaType === 'faq' and post.faqItems is present
 * - HowTo when post.schemaType === 'howto' and post.howToSteps is present
 *
 * Rationale: Google uses these schemas for rich results (FAQ accordion in SERP,
 * HowTo carousel, article byline snippet). See seo_optimization_rules.md.
 */
export function BlogStructuredData({ post }: BlogStructuredDataProps) {
  const url = `${SITE_ORIGIN}/blog/${post.slug}`;
  const mainUrl = post.mediumUrl ?? url;

  const article = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    '@id': `${url}#article`,
    mainEntityOfPage: { '@type': 'WebPage', '@id': mainUrl },
    headline: post.title,
    alternativeHeadline: post.seoTitle,
    description: post.metaDescription ?? post.description,
    image: `${MEDIA_ORIGIN}${post.heroImage}`,
    datePublished: post.date,
    dateModified: post.lastModified ?? post.date,
    author: AUTHOR,
    publisher: PUBLISHER,
    keywords: post.keywords?.join(', '),
    articleSection: post.cluster,
    inLanguage: 'en',
  };

  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: SITE_ORIGIN,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Blog',
        item: `${SITE_ORIGIN}/blog`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: post.title,
        item: url,
      },
    ],
  };

  const nodes: object[] = [article, breadcrumb];

  // FAQ: prefer an explicit post.faqItems list (authoritative), but if the
  // author left that empty, harvest any `type: 'faq'` sections from the
  // post body — writers only have to author the question/answer pairs in
  // one place.
  const faqFromSections = post.sections
    .filter((s): s is Extract<typeof s, { type: 'faq' }> => s.type === 'faq')
    .flatMap((s) => s.items);
  const faqItems = post.faqItems?.length ? post.faqItems : faqFromSections;

  if ((post.schemaType === 'faq' || faqItems.length > 0) && faqItems.length > 0) {
    nodes.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqItems.map((item) => ({
        '@type': 'Question',
        name: item.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: item.answer,
        },
      })),
    });
  }

  if (post.schemaType === 'howto' && post.howToSteps?.length) {
    nodes.push({
      '@context': 'https://schema.org',
      '@type': 'HowTo',
      name: post.title,
      description: post.metaDescription ?? post.description,
      image: `${MEDIA_ORIGIN}${post.heroImage}`,
      step: post.howToSteps.map((step, index) => ({
        '@type': 'HowToStep',
        position: index + 1,
        name: step.name,
        text: step.text,
      })),
    });
  }

  return (
    <>
      {nodes.map((node, index) => (
        <script
          key={index}
          type="application/ld+json"
          // JSON.stringify escapes the needed characters; no user input flows
          // through without being serialized first.
          dangerouslySetInnerHTML={{ __html: JSON.stringify(node) }}
        />
      ))}
    </>
  );
}

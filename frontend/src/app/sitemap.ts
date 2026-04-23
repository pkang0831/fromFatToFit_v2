import { MetadataRoute } from 'next';
import { getAllBlogPosts, getAllClusters } from '@/content/blog/posts';

/**
 * Sitemap priority strategy:
 *
 * - Posts that have an answerBox or faq section (i.e. high featured-snippet
 *   intent) get priority 0.85 because they're the surfaces most likely to win
 *   position-0 results.
 * - Question-style posts (slug starts with `why-`, `how-`, `what-`, `is-`,
 *   `does-`, `do-`, `should-`, `can-`, `am-`) get priority 0.80 — they target
 *   high-volume PAA queries.
 * - All other blog posts: priority 0.70.
 * - Topic pillar pages: priority 0.85 — they're the topical-authority anchors.
 * - changeFrequency = 'monthly' for posts (rarely re-edited);
 *   'weekly' for hub pages (new posts join the cluster regularly).
 */
const QUESTION_PREFIXES = ['why-', 'how-', 'what-', 'is-', 'does-', 'do-', 'should-', 'can-', 'am-'];

function postPriority(post: { slug: string; sections: { type: string }[] }) {
  const hasFeaturedSnippetSection = post.sections.some(
    (s) => s.type === 'answerBox' || s.type === 'faq',
  );
  if (hasFeaturedSnippetSection) return 0.85;
  if (QUESTION_PREFIXES.some((p) => post.slug.startsWith(p))) return 0.8;
  return 0.7;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://devenira.com';
  const blogEntries = getAllBlogPosts().map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.lastModified ?? post.date),
    changeFrequency: 'monthly' as const,
    priority: postPriority(post),
  }));
  const topicEntries = getAllClusters().map((cluster) => ({
    url: `${baseUrl}/blog/topic/${cluster.slug}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.85,
  }));

  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    { url: `${baseUrl}/blog`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${baseUrl}/authors/pkang`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.65 },
    { url: `${baseUrl}/login`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
    { url: `${baseUrl}/register`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
    { url: `${baseUrl}/terms`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.3 },
    { url: `${baseUrl}/privacy`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.3 },
    { url: `${baseUrl}/disclaimer`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.3 },
    ...topicEntries,
    ...blogEntries,
  ];
}

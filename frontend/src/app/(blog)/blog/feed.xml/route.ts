import { getAllBlogPosts } from '@/content/blog/posts';

/**
 * RSS feed for the blog at /blog/feed.xml.
 *
 * Why have an RSS feed when canonical points to Medium:
 * 1. Medium publications and aggregators (Feedly, Inoreader, Substack
 *    importers) discover content via RSS — having a feed enables them
 *    to subscribe to the site as a syndication source.
 * 2. Google uses RSS as a signal to discover new posts faster than
 *    sitemap re-crawl alone.
 * 3. Each <item> link points to the Medium URL when present (canonical
 *    consistency); falls back to the site URL otherwise.
 */
export async function GET() {
  const posts = getAllBlogPosts();
  const siteUrl = 'https://devenira.com';
  const lastBuildDate = new Date().toUTCString();

  const xmlEscape = (s: string) =>
    s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');

  const items = posts
    .slice(0, 50)
    .map((post) => {
      const link = post.mediumUrl ?? `${siteUrl}/blog/${post.slug}`;
      const description = post.metaDescription ?? post.description ?? '';
      const pubDate = new Date(post.date).toUTCString();
      const cluster = post.cluster ? `<category>${xmlEscape(post.cluster)}</category>` : '';
      const tagsXml = post.tags
        .map((tag) => `<category>${xmlEscape(tag)}</category>`)
        .join('');
      return `
    <item>
      <title>${xmlEscape(post.title)}</title>
      <link>${xmlEscape(link)}</link>
      <guid isPermaLink="true">${xmlEscape(link)}</guid>
      <pubDate>${pubDate}</pubDate>
      <author>noreply@devenira.com (pkang)</author>
      <description>${xmlEscape(description)}</description>
      ${cluster}
      ${tagsXml}
    </item>`;
    })
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Devenira Blog by pkang</title>
    <link>${siteUrl}/blog</link>
    <atom:link href="${siteUrl}/blog/feed.xml" rel="self" type="application/rss+xml" />
    <description>Fitness and diet writing by pkang — appetite, body image, and the slow work of reading the body without panic. From a 50 kg transformation.</description>
    <language>en</language>
    <lastBuildDate>${lastBuildDate}</lastBuildDate>
    <managingEditor>noreply@devenira.com (pkang)</managingEditor>
    <webMaster>noreply@devenira.com (pkang)</webMaster>${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  });
}

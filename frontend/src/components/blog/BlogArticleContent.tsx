import { getAllBlogPosts, type BlogSection } from '@/content/blog/posts';
import { buildLinkTargets, linkifyText } from './linkifyText';

interface BlogArticleContentProps {
  sections: BlogSection[];
  /** Slug of the current post; its keyword phrases are excluded from
   *  auto-linking so articles never link to themselves. */
  currentSlug: string;
}

/**
 * Max 3 distinct internal links per article (see SEO_AUDIT_20260422.md A6).
 * Each unique slug is linked at most once per article, so 3 anchors means
 * 3 different destination posts.
 */
const LINK_BUDGET_PER_ARTICLE = 3;

export function BlogArticleContent({ sections, currentSlug }: BlogArticleContentProps) {
  const targets = buildLinkTargets(getAllBlogPosts(), currentSlug);
  const linkedSlugs = new Set<string>();
  const budget = { remaining: LINK_BUDGET_PER_ARTICLE };
  return (
    <div className="space-y-10">
      {sections.map((section, index) => {
        if (section.type === 'quote') {
          return (
            <blockquote
              key={`${section.type}-${index}`}
              className="rounded-[28px] border border-white/[0.08] bg-white/[0.03] px-6 py-8 text-2xl font-semibold leading-relaxed tracking-tight text-white md:px-8 md:text-3xl"
            >
              “{section.quote}”
            </blockquote>
          );
        }

        if (section.type === 'list') {
          return (
            <section key={`${section.type}-${index}`} className="space-y-5">
              {section.title ? (
                <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">{section.title}</h2>
              ) : null}
              {section.intro ? (
                <p className="text-lg leading-8 text-white/68">{section.intro}</p>
              ) : null}
              <ul className="space-y-3 rounded-[28px] border border-white/[0.08] bg-white/[0.03] p-6 text-white/72">
                {section.items.map((item, itemIndex) => (
                  <li key={`${index}-${itemIndex}`} className="flex items-start gap-3 text-base leading-7">
                    <span className="mt-2 h-1.5 w-1.5 rounded-full bg-primary" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              {section.outro ? (
                <p className="text-lg leading-8 text-white/68">{section.outro}</p>
              ) : null}
            </section>
          );
        }

        if (section.type === 'answerBox') {
          // Featured snippet target. The H3 is visible as the question,
          // and the p is the 40-60 word direct answer Google is expected
          // to pluck into position 0. Keep styling minimal and semantic
          // so Google has no parsing ambiguity.
          return (
            <section
              key={`${section.type}-${index}`}
              className="rounded-[28px] border border-primary/30 bg-primary/[0.05] px-6 py-6 md:px-8"
            >
              <h3 className="text-xl font-semibold tracking-tight text-primary/90 md:text-2xl">
                {section.question}
              </h3>
              <p className="mt-3 text-lg leading-8 text-white/85">{section.answer}</p>
            </section>
          );
        }

        if (section.type === 'faq') {
          return (
            <section key={`${section.type}-${index}`} className="space-y-5">
              {section.title ? (
                <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                  {section.title}
                </h2>
              ) : null}
              <div className="divide-y divide-white/[0.06] rounded-[28px] border border-white/[0.08] bg-white/[0.03]">
                {section.items.map((item, itemIndex) => (
                  <details
                    key={`${index}-${itemIndex}`}
                    className="group px-6 py-5 md:px-8"
                  >
                    <summary className="cursor-pointer list-none text-lg font-semibold text-white marker:hidden">
                      <span className="flex items-start justify-between gap-4">
                        <span>{item.question}</span>
                        <span className="mt-1 text-primary/80 transition-transform group-open:rotate-45">
                          +
                        </span>
                      </span>
                    </summary>
                    <p className="mt-3 text-base leading-7 text-white/72">{item.answer}</p>
                  </details>
                ))}
              </div>
            </section>
          );
        }

        return (
          <section key={`${section.type}-${index}`} className="space-y-5">
            {section.title ? (
              <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">{section.title}</h2>
            ) : null}
            <div className="space-y-5">
              {section.paragraphs.map((paragraph, paragraphIndex) => (
                <p key={`${index}-${paragraphIndex}`} className="text-lg leading-8 text-white/68">
                  {linkifyText(paragraph, targets, linkedSlugs, budget)}
                </p>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}

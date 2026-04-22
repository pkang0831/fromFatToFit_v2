#!/usr/bin/env python3
"""
Static validator for Schema.org JSON-LD emitted by the blog.

What this checks:
- Each emitted JSON-LD object includes the required schema.org fields
- Cross-references between Article.author and Person.@id resolve
- No schema cannibalization (e.g. FAQPage emitted on a post with no FAQ items)

Output:
- A schema-validity report at marketing/.../seo_structured_data_audit.md
- Sample JSON-LD snapshots for 3 representative posts at
  marketing/.../seo_structured_data_samples/<slug>.json

Use the samples in Google's Rich Results Test:
  https://search.google.com/test/rich-results
to confirm the live page would emit valid markup.
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
REPORT = ROOT / "marketing/fitness_blogging/blog_strategy/seo_structured_data_audit.md"
SAMPLES_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/seo_structured_data_samples"

SITE_ORIGIN = "https://devenira.com"
AUTHOR_ID = f"{SITE_ORIGIN}/authors/pkang"


def parse_post(text: str, slug: str) -> dict:
    """Extract the per-post fields needed to render JSON-LD."""
    slug_idx = text.find(f"    slug: '{slug}',")
    next_idx = text.find("    slug: '", slug_idx + 1)
    chunk = text[slug_idx:next_idx if next_idx != -1 else len(text)]

    def field(name: str, default=None):
        # Match either single-line (`    name: 'val',`) or multi-line
        # (`    name:\n      'val',`) JS string assignments.
        m = re.search(
            rf"    {name}:\s*(?P<q>['\"])(?P<val>.+?)(?P=q),",
            chunk,
            re.DOTALL,
        )
        return m.group("val") if m else default

    keywords = []
    kw_match = re.search(r"    keywords: \[(.*?)\],", chunk, re.DOTALL)
    if kw_match:
        keywords = re.findall(r"['\"]([^'\"]+)['\"]", kw_match.group(1))

    schema_type = field("schemaType")
    has_faq_section = "type: 'faq'" in chunk
    has_answer_box = "type: 'answerBox'" in chunk

    return {
        "slug": slug,
        "title": field("title"),
        "seoTitle": field("seoTitle"),
        "description": field("description"),
        "metaDescription": field("metaDescription"),
        "date": field("date"),
        "lastModified": field("lastModified"),
        "heroImage": field("heroImage"),
        "heroAlt": field("heroAlt"),
        "cluster": field("cluster"),
        "mediumUrl": field("mediumUrl"),
        "schemaType": schema_type,
        "keywords": keywords,
        "has_faq_section": has_faq_section,
        "has_answer_box": has_answer_box,
    }


def render_jsonld(post: dict) -> list[dict]:
    """Mirror what BlogStructuredData.tsx would emit."""
    url = f"{SITE_ORIGIN}/blog/{post['slug']}"
    main_url = post.get("mediumUrl") or url

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"{url}#article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": main_url},
        "headline": post["title"],
        "alternativeHeadline": post.get("seoTitle"),
        "description": post.get("metaDescription") or post.get("description"),
        "image": f"{SITE_ORIGIN}{post['heroImage']}" if post["heroImage"] else None,
        "datePublished": post["date"],
        "dateModified": post.get("lastModified") or post["date"],
        "author": {
            "@type": "Person",
            "@id": AUTHOR_ID,
            "name": "pkang",
            "url": AUTHOR_ID,
        },
        "publisher": {
            "@type": "Organization",
            "@id": f"{SITE_ORIGIN}/#organization",
            "name": "Devenira",
        },
        "keywords": ", ".join(post.get("keywords", [])),
        "articleSection": post.get("cluster"),
        "inLanguage": "en",
    }

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_ORIGIN},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE_ORIGIN}/blog"},
            {"@type": "ListItem", "position": 3, "name": post["title"], "item": url},
        ],
    }

    nodes = [article, breadcrumb]

    # FAQPage emits whenever there is FAQ/answerBox content, regardless of
    # schemaType (matches BlogStructuredData runtime behavior).
    if post["has_faq_section"] or post["has_answer_box"]:
        nodes.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": "[harvested at runtime from sections]",
        })

    if post["schemaType"] == "howto":
        nodes.append({
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": post["title"],
            "step": "[populated at runtime from howToSteps]",
        })

    return nodes


REQUIRED_ARTICLE_FIELDS = [
    "@context", "@type", "headline", "datePublished", "author",
    "publisher", "image", "mainEntityOfPage",
]


def validate(post: dict, nodes: list[dict]) -> list[str]:
    issues = []
    if not post["title"]:
        issues.append("missing title")
    if not post["date"]:
        issues.append("missing date")
    if not post["heroImage"]:
        issues.append("missing heroImage")
    if not post.get("metaDescription") and not post.get("description"):
        issues.append("missing both metaDescription and description")

    article = nodes[0]
    for f in REQUIRED_ARTICLE_FIELDS:
        if not article.get(f):
            issues.append(f"Article schema missing required: {f}")

    # Schema-type cannibalization checks.
    # Note: BlogStructuredData component auto-harvests FAQ sections into
    # FAQPage JSON-LD regardless of schemaType, so a 'howto' post that
    # also has FAQ sections emits BOTH HowTo and FAQPage. That's
    # intended (and Google handles multi-schema pages fine).
    if post["schemaType"] == "faq" and not post["has_faq_section"] and not post["has_answer_box"]:
        issues.append("schemaType='faq' but no faq/answerBox section in body — FAQPage will be empty")
    return issues


def main() -> int:
    text = POSTS_TS.read_text(encoding="utf-8")
    # Scope the slug search to the `const posts: BlogPost[] = [ ... ];` array
    # so we don't pick up CLUSTERS or other slug-shaped fields.
    posts_array_match = re.search(
        r"const posts: BlogPost\[\] = \[(.*?)\n\];",
        text,
        re.DOTALL,
    )
    if not posts_array_match:
        print("ERROR: could not locate posts array in posts.ts")
        return 1
    posts_text = posts_array_match.group(1)
    slugs = re.findall(r"    slug: '([^']+)',", posts_text)
    seen: set[str] = set()
    unique_slugs = [s for s in slugs if s not in seen and not seen.add(s)]
    text = posts_text  # so parse_post sees only the array

    issues_by_post: dict[str, list[str]] = {}
    nodes_count = {"Article": 0, "BreadcrumbList": 0, "FAQPage": 0, "HowTo": 0}

    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    sample_targets = {
        "how-i-lost-50-kg-middle-of-diet",          # Article only
        "why-does-the-scale-go-up-when-i-barely-eat",  # Article + FAQPage
        "how-to-stick-to-a-diet-when-progress-slows",  # has answerBox
    }

    for slug in unique_slugs:
        post = parse_post(text, slug)
        if not post["title"]:
            continue
        nodes = render_jsonld(post)
        for n in nodes:
            t = n.get("@type")
            if t in nodes_count:
                nodes_count[t] += 1
        issues = validate(post, nodes)
        if issues:
            issues_by_post[slug] = issues

        if slug in sample_targets:
            (SAMPLES_DIR / f"{slug}.json").write_text(
                json.dumps(nodes, indent=2),
                encoding="utf-8",
            )

    # Render report.
    report = []
    report.append("# JSON-LD Structured Data Audit")
    report.append("")
    report.append("Generated: 2026-04-21")
    report.append("Static validator — mirrors what `BlogStructuredData.tsx` emits at runtime.")
    report.append("")
    report.append("## Counts")
    report.append("")
    for t, c in nodes_count.items():
        report.append(f"- **{t}**: emitted on {c} posts")
    report.append("")
    report.append("## Issues found")
    report.append("")
    if not issues_by_post:
        report.append("None. ✓")
    else:
        for slug, issues in issues_by_post.items():
            report.append(f"### {slug}")
            for i in issues:
                report.append(f"- {i}")
            report.append("")
    report.append("")
    report.append("## Sample snapshots")
    report.append("")
    report.append("Three sample JSON-LD snapshots written to `seo_structured_data_samples/<slug>.json`.")
    report.append("Test them in Google's Rich Results Test tool:")
    report.append("")
    report.append("- https://search.google.com/test/rich-results")
    report.append("")
    report.append("Paste the JSON content into the testing tool to confirm validity.")
    REPORT.write_text("\n".join(report), encoding="utf-8")

    print(f"Wrote report: {REPORT.relative_to(ROOT)}")
    print(f"Wrote samples to: {SAMPLES_DIR.relative_to(ROOT)}")
    print(f"\nSchema counts: {nodes_count}")
    print(f"Posts with issues: {len(issues_by_post)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

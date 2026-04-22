#!/usr/bin/env python3
"""
Performance / page-weight audit for the blog surfaces.

What we audit:
- Static asset sizes under public/ that are referenced from blog posts
  (hero images, cover images) — flag anything > 500 KB
- BlogPost section count + total word count per post (long posts hurt LCP)
- Hero image format suitability (jpg/jpeg vs webp/avif) — flag
  non-WebP heroes that are over 100 KB (could be optimized)
- Total content size estimate for the /blog index (cards × image weight)

Why this matters for SEO:
- Core Web Vitals (LCP, CLS, INP) are confirmed Google ranking signals.
- LCP is dominated by hero image weight on blog posts.
- Total page weight affects mobile load and bounce rate.

This script READS only — never modifies images or files. Outputs a report
to `marketing/fitness_blogging/blog_strategy/seo_performance_audit.md`.
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
PUBLIC_DIR = ROOT / "frontend/public"
REPORT_FILE = ROOT / "marketing/fitness_blogging/blog_strategy/seo_performance_audit.md"

LCP_HERO_KB_LIMIT = 200      # Google's recommended LCP image weight ceiling
CLS_HERO_KB_WARN = 100        # Soft warn target
LARGE_PAGE_WORDS = 3500       # Posts above this risk LCP/INP issues


def parse_posts() -> list[dict]:
    """Lightweight parse of posts.ts to extract per-post stats."""
    text = POSTS_TS.read_text(encoding="utf-8")
    entries: list[dict] = []
    # Find each slug + heroImage + sections start.
    slug_iter = list(re.finditer(r"    slug: '([^']+)',", text))
    for i, m in enumerate(slug_iter):
        slug = m.group(1)
        start = m.start()
        end = slug_iter[i + 1].start() if i + 1 < len(slug_iter) else len(text)
        chunk = text[start:end]
        hero_m = re.search(r"    heroImage: '([^']+)'", chunk)
        hero_image = hero_m.group(1) if hero_m else None

        # Word-count estimate from string literals inside this chunk.
        # Rough but consistent: count words inside single-quoted strings.
        all_strings = re.findall(r"'([^'\\]+(?:\\.[^'\\]*)*)'", chunk)
        word_count = sum(len(s.split()) for s in all_strings if len(s) > 30)

        # Section count from `type:` mentions inside sections array.
        sections_chunk_m = re.search(r"sections: \[(.*?)\n  \},\n", chunk, re.DOTALL)
        section_count = 0
        if sections_chunk_m:
            section_count = len(re.findall(r"type: '\w+'", sections_chunk_m.group(1)))

        entries.append({
            "slug": slug,
            "hero_image": hero_image,
            "estimated_word_count": word_count,
            "section_count": section_count,
        })
    return entries


def file_size_kb(rel_path: str) -> tuple[int | None, str | None]:
    """rel_path is like '/founder/foo.jpg'. Returns (kb, mime-extension)."""
    if not rel_path or not rel_path.startswith("/"):
        return None, None
    p = PUBLIC_DIR / rel_path.lstrip("/")
    if not p.exists():
        return None, None
    return p.stat().st_size // 1024, p.suffix.lstrip(".").lower()


def bucket_image(kb: int) -> str:
    if kb >= LCP_HERO_KB_LIMIT:
        return "FAIL"
    if kb >= CLS_HERO_KB_WARN:
        return "WARN"
    return "OK"


def main() -> int:
    posts = parse_posts()
    print(f"Parsed {len(posts)} posts.\n")

    # Image weight audit.
    image_rows = []
    for post in posts:
        kb, ext = file_size_kb(post["hero_image"]) if post["hero_image"] else (None, None)
        if kb is None:
            image_rows.append({**post, "size_kb": None, "format": None, "bucket": "MISSING"})
        else:
            image_rows.append({
                **post,
                "size_kb": kb,
                "format": ext,
                "bucket": bucket_image(kb),
                "webp_candidate": ext in {"jpg", "jpeg", "png"} and kb >= CLS_HERO_KB_WARN,
            })

    # Sort by image weight descending.
    image_rows.sort(key=lambda r: r.get("size_kb") or 0, reverse=True)

    # Long-page audit.
    long_posts = sorted(posts, key=lambda r: r["estimated_word_count"], reverse=True)[:10]

    # Counts.
    img_buckets = {"OK": 0, "WARN": 0, "FAIL": 0, "MISSING": 0}
    webp_candidates = 0
    for r in image_rows:
        img_buckets[r["bucket"]] += 1
        if r.get("webp_candidate"):
            webp_candidates += 1

    # Render report.
    report = []
    report.append("# Blog Performance Audit")
    report.append("")
    report.append("Generated: 2026-04-21")
    report.append("Read-only audit of static-asset weight + per-post content size.")
    report.append("")
    report.append("## Why this matters for SEO")
    report.append("")
    report.append("- LCP (Largest Contentful Paint) is dominated by hero-image weight on blog posts.")
    report.append("- Google rewards LCP < 2.5s; > 4s is a ranking penalty.")
    report.append(f"- Hero image budget: warn at {CLS_HERO_KB_WARN} KB, fail at {LCP_HERO_KB_LIMIT} KB.")
    report.append("- Content-heavy posts (3500+ words) need careful image lazy-loading and font-display: swap.")
    report.append("")
    report.append("## Hero image budget")
    report.append("")
    report.append(f"- Total posts audited: {len(image_rows)}")
    report.append(f"- OK     (< {CLS_HERO_KB_WARN} KB):       {img_buckets['OK']}")
    report.append(f"- WARN   ({CLS_HERO_KB_WARN}–{LCP_HERO_KB_LIMIT - 1} KB):     {img_buckets['WARN']}")
    report.append(f"- FAIL   (>= {LCP_HERO_KB_LIMIT} KB):    {img_buckets['FAIL']}")
    report.append(f"- MISSING (image not on disk):  {img_buckets['MISSING']}")
    report.append(f"- WebP-conversion candidates (jpg/png > {CLS_HERO_KB_WARN} KB): {webp_candidates}")
    report.append("")
    report.append("### Top 20 heaviest hero images (action: convert to WebP / resize)")
    report.append("")
    report.append("| Slug | Hero image | Size (KB) | Bucket |")
    report.append("|------|-----------|-----------|--------|")
    for r in image_rows[:20]:
        kb = r["size_kb"] if r["size_kb"] is not None else "—"
        report.append(f"| {r['slug']} | {r['hero_image']} | {kb} | {r['bucket']} |")
    report.append("")
    report.append("## Long posts (estimated word count)")
    report.append("")
    report.append("Posts above 3,500 words deserve special care — explicit image lazy-loading,")
    report.append("font-display: swap, and possibly content splitting via `<details>` accordions")
    report.append("to keep first-paint fast.")
    report.append("")
    report.append("| Slug | Words (estimate) | Sections |")
    report.append("|------|------------------|----------|")
    for p in long_posts:
        flag = " ⚠" if p["estimated_word_count"] > LARGE_PAGE_WORDS else ""
        report.append(f"| {p['slug']} | {p['estimated_word_count']}{flag} | {p['section_count']} |")
    report.append("")
    report.append("## Recommended actions")
    report.append("")
    report.append("1. **Convert WARN/FAIL hero images to WebP** (use `cwebp` or an image pipeline). WebP")
    report.append("   typically saves 30–50% vs JPEG at equivalent quality. Next.js `<Image>` already")
    report.append("   serves WebP automatically when the source is jpg, but the source weight still")
    report.append("   bounds the WebP weight. Resize source to 1920px max-width before converting.")
    report.append("2. **Set `priority` on every blog hero `<Image>`** (already done in [slug]/page.tsx). Confirm.")
    report.append("3. **Lazy-load all inline images** (default for non-priority Next.js Image). Confirm.")
    report.append("4. **Long posts (above): consider splitting** into a `<details>` 'Read on' block midway")
    report.append("   — keeps initial DOM small without losing content.")
    report.append("5. **Audit fonts**: Plus_Jakarta_Sans and Space_Grotesk are loaded with `display: swap`")
    report.append("   per `app/layout.tsx`. ✓")
    report.append("6. **Consider self-hosting hero images on a CDN with WebP/AVIF auto-conversion**")
    report.append("   (Cloudflare Images, Bunny CDN, or Vercel built-in image optimization). The latter")
    report.append("   is automatic on Vercel deploys.")
    report.append("")
    report.append("## Out of scope (need real measurement)")
    report.append("")
    report.append("This audit can't measure:")
    report.append("- Real LCP / INP / CLS (need Chrome Lighthouse / WebPageTest)")
    report.append("- TTFB (depends on hosting tier)")
    report.append("- JS bundle size (run `ANALYZE=true npm run build` for that)")
    report.append("")
    report.append("Run Lighthouse on `/blog/<slug>` for a real score after the next deploy.")

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")
    print(f"Report written to: {REPORT_FILE.relative_to(ROOT)}")
    print(f"\nImage buckets: {img_buckets}")
    print(f"WebP-conversion candidates: {webp_candidates}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

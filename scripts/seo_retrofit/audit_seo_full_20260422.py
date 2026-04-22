"""
Phase A — comprehensive read-only SEO audit (2026-04-22 session).

Measures 10 dimensions across all 69 posts and writes a per-post
findings JSON + a markdown summary.

Dimensions (A1-A10):

A1. seoTitle pixel width      (Google SERP budget ~580px on desktop)
A2. metaDescription char count (ideal 120-158, Google truncates ~160)
A3. Primary keyword placement (in seoTitle? first 100 words of first
    paragraphs? deck? H2 of first section?)
A4. Content word count         (body text only, ideal 1500-3000)
A5. Heading hierarchy          (counts of paragraph-title sections
    (~H2), section count, keyword-in-H2 presence)
A6. Internal link density      (currently 0 on most posts since the
    blog system doesn't auto-link; flagged as gap)
A7. JSON-LD shapes declared    (read schemaType, presence of
    faqItems/howToSteps, will be validated in A7-prod)
A8. Hero image budget          (webp size in bytes — LCP proxy;
    fetched from frontend/public/founder/)
A9. Canonical policy           (mediumUrl set -> canonical = Medium;
    else self-canonical)
A10. E-E-A-T signal inventory  (tags mention author? ctaBody present?
    mediumUrl earned?). Real E-E-A-T check requires visual rendering,
    so this is a field-level proxy.

Output:
  /tmp/seo_audit_findings.json (per-post dict of all measurements)
  /tmp/seo_audit_findings.md   (markdown summary with distributions,
                                per-dimension histograms, top offenders)
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "frontend/src/content/blog/posts.ts"
FOUNDER = ROOT / "frontend/public/founder"

# --- Title pixel-width model (approximate Arial/Roboto-ish Helvetica) ---
# Google SERP uses Roboto. We approximate char widths in pixels at the
# 18px/20px line height used for desktop titles. Source: pixelwidth
# measurements of Roboto 16px bold.
CHAR_WIDTH = {
    " ": 4, "!": 4, '"': 5, "#": 9, "$": 9, "%": 14, "&": 11, "'": 3,
    "(": 5, ")": 5, "*": 6, "+": 9, ",": 4, "-": 5, ".": 4, "/": 5,
    "0": 9, "1": 9, "2": 9, "3": 9, "4": 9, "5": 9, "6": 9, "7": 9, "8": 9, "9": 9,
    ":": 4, ";": 4, "<": 9, "=": 9, ">": 9, "?": 9, "@": 16,
    "A": 11, "B": 11, "C": 12, "D": 12, "E": 10, "F": 10, "G": 13, "H": 12, "I": 5,
    "J": 8, "K": 11, "L": 9, "M": 14, "N": 12, "O": 13, "P": 11, "Q": 13, "R": 12,
    "S": 11, "T": 10, "U": 12, "V": 11, "W": 15, "X": 11, "Y": 11, "Z": 10,
    "[": 5, "\\": 5, "]": 5, "^": 8, "_": 8, "`": 5,
    "a": 9, "b": 9, "c": 8, "d": 9, "e": 9, "f": 5, "g": 9, "h": 9, "i": 4, "j": 4,
    "k": 9, "l": 4, "m": 14, "n": 9, "o": 9, "p": 9, "q": 9, "r": 6, "s": 8, "t": 5,
    "u": 9, "v": 8, "w": 12, "x": 8, "y": 8, "z": 8,
    "{": 5, "|": 4, "}": 5, "~": 9,
}


def title_pixels(s: str) -> int:
    return sum(CHAR_WIDTH.get(c, 9) for c in s)


# --- Parse posts ---


def parse_posts(src: str) -> list[str]:
    m = re.search(
        r"const posts: BlogPost\[\] = \[\n(.*?)\n\];\s*\n\s*\n?export function getAllBlogPosts",
        src, re.DOTALL,
    )
    body = m.group(1)

    out = []
    depth = 0
    start = None
    in_s = False; sc = None; in_t = False; esc = False
    for i, c in enumerate(body):
        if esc: esc = False; continue
        if c == "\\": esc = True; continue
        if in_s:
            if c == sc: in_s = False
            continue
        if in_t:
            if c == "`": in_t = False
            continue
        if c in ("'", '"'):
            in_s = True; sc = c; continue
        if c == "`":
            in_t = True; continue
        if c == "{":
            if depth == 0: start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                out.append(body[start:i+1])
                start = None
    return out


def extract_field(post: str, name: str) -> str | None:
    # Handle both single-quoted ('...') and double-quoted ("...") string values,
    # and value either on same line as name: or on next line (indented).
    # Single-quoted:
    m = re.search(rf"{name}:\s*\n?\s*'((?:[^'\\]|\\.)*)'", post)
    if m:
        return m.group(1).replace("\\'", "'").replace("\\\\", "\\")
    # Double-quoted:
    m = re.search(rf'{name}:\s*\n?\s*"((?:[^"\\]|\\.)*)"', post)
    if m:
        return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
    return None


def extract_array_of_strings(post: str, name: str) -> list[str]:
    m = re.search(rf"{name}:\s*\[(.*?)\]", post, re.DOTALL)
    if not m:
        return []
    # include both quote types inside the array
    return re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", m.group(1)) and [
        a or b for (a, b) in re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", m.group(1))
    ]


def has_field(post: str, name: str) -> bool:
    return bool(re.search(rf"\n\s+{re.escape(name)}:\s*", post))


# Extract the first paragraphs section's text for first-100-words check
_STRING_LITERAL_RE = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")


def _extract_all_strings(seg: str) -> list[str]:
    return [a or b for (a, b) in _STRING_LITERAL_RE.findall(seg)]


def first_paragraphs_text(post: str) -> str:
    """Return concatenated text of the first paragraphs-type section."""
    idx = post.find("type: 'paragraphs'")
    if idx < 0:
        return ""
    after = post[idx:idx+10000]
    end = after.find("},\n      {")
    if end < 0:
        end = len(after)
    seg = after[:end]
    strings = _extract_all_strings(seg)
    return " ".join(strings[1:])


def all_body_text(post: str) -> str:
    """Return all paragraph/list/quote/answer text from sections, both
    single- and double-quoted string literals."""
    sec_idx = post.find("sections:")
    if sec_idx < 0:
        return ""
    return " ".join(_extract_all_strings(post[sec_idx:]))


def count_sections(post: str, types: tuple[str, ...] = None) -> dict:
    m = re.search(r"sections:\s*\[(.*)", post, re.DOTALL)
    if not m:
        return {}
    body = m.group(1)
    counts = {t: len(re.findall(rf"type:\s*'{t}'", body)) for t in (types or ("paragraphs", "list", "quote", "answerBox", "faq"))}
    titled = len(re.findall(r"title:\s*'", body))  # sections with explicit title (H2-equivalent)
    return {"section_type_counts": counts, "titled_sections": titled}


def main() -> None:
    src = POSTS.read_text()
    posts = parse_posts(src)
    print(f"parsed posts: {len(posts)}")

    findings = []
    for post in posts:
        slug = extract_field(post, "slug") or "(unknown)"
        title = extract_field(post, "title") or ""
        seo_title = extract_field(post, "seoTitle") or ""
        meta_desc = extract_field(post, "metaDescription") or ""
        description = extract_field(post, "description") or ""
        deck = extract_field(post, "deck") or ""
        hero = extract_field(post, "heroImage") or ""
        cluster = extract_field(post, "cluster") or ""
        schema_type = extract_field(post, "schemaType") or ""
        medium_url = extract_field(post, "mediumUrl")
        last_mod = extract_field(post, "lastModified") or ""
        date = extract_field(post, "date") or ""
        keywords = extract_array_of_strings(post, "keywords")
        primary_kw = keywords[0] if keywords else ""

        body = all_body_text(post)
        word_count = len(body.split())
        first_100 = " ".join(body.split()[:100]).lower()
        sections = count_sections(post)

        # A1 — title pixel width
        px = title_pixels(seo_title)

        # A2 — metadescription length
        md_len = len(meta_desc)

        # A3 — primary keyword placement
        kw_lower = primary_kw.lower() if primary_kw else ""
        kw_in_seo_title = kw_lower in seo_title.lower() if kw_lower else False
        kw_in_title = kw_lower in title.lower() if kw_lower else False
        kw_in_deck = kw_lower in deck.lower() if kw_lower else False
        kw_in_first_100 = kw_lower in first_100 if kw_lower else False
        kw_in_meta_desc = kw_lower in meta_desc.lower() if kw_lower else False
        # also check: is ANY keyword in the first 100 words?
        any_kw_in_first_100 = any(k.lower() in first_100 for k in keywords) if keywords else False

        # A5 — heading/section
        ss = sections.get("section_type_counts", {})
        titled = sections.get("titled_sections", 0)

        # A6 — internal links: count anchor-style refs to other blog posts
        # our posts.ts doesn't have explicit <a href=/blog/...> because
        # content is plain strings. Internal links are achieved only via
        # cluster pillar pages and the blog index. Flag it.
        internal_link_count = len(re.findall(r"/blog/[a-z][a-z0-9-]+", post))

        # A8 — hero image size (bytes)
        hero_path = ROOT / "frontend/public" / hero.lstrip("/")
        hero_size = hero_path.stat().st_size if hero_path.is_file() else None

        # A9 — canonical policy  (reported only, validated against prod later)
        canonical_target = "medium" if medium_url else "self"

        # A10 — E-E-A-T proxy
        tags = extract_array_of_strings(post, "tags")
        has_cta_body = bool(extract_field(post, "ctaBody"))

        findings.append({
            "slug": slug,
            "cluster": cluster,
            "date": date,
            "lastModified": last_mod,
            "schemaType": schema_type,
            # A1
            "seoTitle": seo_title,
            "seoTitle_len_chars": len(seo_title),
            "seoTitle_px": px,
            "seoTitle_over_580px": px > 580,
            "seoTitle_under_200px": px < 200,
            # A2
            "metaDescription_len": md_len,
            "metaDescription_too_short_lt_120": md_len < 120,
            "metaDescription_too_long_gt_158": md_len > 158,
            # A3
            "primary_keyword": primary_kw,
            "kw_in_seoTitle": kw_in_seo_title,
            "kw_in_title": kw_in_title,
            "kw_in_deck": kw_in_deck,
            "kw_in_metaDescription": kw_in_meta_desc,
            "kw_in_first_100_words": kw_in_first_100,
            "any_kw_in_first_100_words": any_kw_in_first_100,
            # A4
            "body_word_count": word_count,
            "word_count_under_1500": word_count < 1500,
            "word_count_over_3000": word_count > 3000,
            # A5
            "section_type_counts": ss,
            "titled_sections_h2_count": titled,
            # A6
            "internal_blog_refs_in_posts_ts": internal_link_count,
            # A8
            "hero_path": hero,
            "hero_bytes": hero_size,
            "hero_over_200KB": (hero_size or 0) > 200 * 1024,
            # A9
            "canonical_target": canonical_target,
            # A10
            "has_cta_body": has_cta_body,
            "tag_count": len(tags),
            "keyword_count": len(keywords),
        })

    # -----  Aggregate stats -----
    def pct(frac, total):
        return f"{100 * frac / total:.0f}%" if total else "n/a"

    total = len(findings)
    agg = {
        "A1_title_over_580px":  sum(1 for f in findings if f["seoTitle_over_580px"]),
        "A1_title_under_200px": sum(1 for f in findings if f["seoTitle_under_200px"]),
        "A2_metaDescription_too_short": sum(1 for f in findings if f["metaDescription_too_short_lt_120"]),
        "A2_metaDescription_too_long":  sum(1 for f in findings if f["metaDescription_too_long_gt_158"]),
        "A3_kw_in_seoTitle":           sum(1 for f in findings if f["kw_in_seoTitle"]),
        "A3_kw_in_metaDescription":    sum(1 for f in findings if f["kw_in_metaDescription"]),
        "A3_kw_in_first_100":          sum(1 for f in findings if f["kw_in_first_100_words"]),
        "A3_any_kw_in_first_100":      sum(1 for f in findings if f["any_kw_in_first_100_words"]),
        "A4_under_1500_words":         sum(1 for f in findings if f["word_count_under_1500"]),
        "A4_over_3000_words":          sum(1 for f in findings if f["word_count_over_3000"]),
        "A8_hero_over_200KB":          sum(1 for f in findings if f["hero_over_200KB"]),
        "A9_canonical_medium":         sum(1 for f in findings if f["canonical_target"] == "medium"),
        "A9_canonical_self":           sum(1 for f in findings if f["canonical_target"] == "self"),
    }

    # Word count distribution
    wc = sorted(f["body_word_count"] for f in findings)
    wc_p25 = wc[len(wc)//4] if wc else 0
    wc_p50 = wc[len(wc)//2] if wc else 0
    wc_p75 = wc[3*len(wc)//4] if wc else 0

    # Hero size distribution
    hs = sorted([f["hero_bytes"] for f in findings if f["hero_bytes"]])
    hs_p50 = hs[len(hs)//2] if hs else 0
    hs_p90 = hs[9*len(hs)//10] if hs else 0

    # Cluster distribution
    cluster_ct = Counter(f["cluster"] for f in findings)

    # Dump JSON
    Path("/tmp/seo_audit_findings.json").write_text(json.dumps(findings, indent=2))

    # Markdown report
    md = []
    md.append("# SEO Audit — Phase A findings (2026-04-22)\n")
    md.append(f"Total posts audited: **{total}**\n")

    md.append("## Aggregate counts\n")
    md.append("| Dimension | Count | % |")
    md.append("|---|---|---|")
    for k, v in agg.items():
        md.append(f"| {k} | {v} | {pct(v, total)} |")
    md.append("")

    md.append("## A4 word count distribution (body text)\n")
    md.append(f"- p25 = {wc_p25}, p50 = {wc_p50}, p75 = {wc_p75}")
    md.append(f"- min = {min(wc) if wc else 0}, max = {max(wc) if wc else 0}")
    md.append(f"- posts < 1500 words: **{agg['A4_under_1500_words']}**  /  > 3000 words: **{agg['A4_over_3000_words']}**")
    md.append("")

    md.append("## A8 hero image size distribution\n")
    md.append(f"- p50 = {hs_p50//1024} KB, p90 = {hs_p90//1024} KB")
    md.append(f"- posts > 200 KB hero: **{agg['A8_hero_over_200KB']}**")
    md.append("")

    md.append("## A9 canonical targets\n")
    md.append(f"- canonical -> medium: {agg['A9_canonical_medium']}")
    md.append(f"- canonical -> self:   {agg['A9_canonical_self']}")
    md.append("")

    md.append("## Cluster distribution\n")
    md.append("| Cluster | # |")
    md.append("|---|---|")
    for k, v in sorted(cluster_ct.items(), key=lambda x: -x[1]):
        md.append(f"| {k or '(none)'} | {v} |")
    md.append("")

    # Per-post table of flags  (offenders only)
    md.append("## Flagged posts (at least one issue)\n")
    md.append("| slug | title px | meta len | kw in title | kw in desc | kw in 1st 100 | words | hero KB | flags |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for f in sorted(findings, key=lambda x: (x["slug"])):
        flags = []
        if f["seoTitle_over_580px"]: flags.append("title>580px")
        if f["metaDescription_too_short_lt_120"]: flags.append("desc<120")
        if f["metaDescription_too_long_gt_158"]: flags.append("desc>158")
        if not f["kw_in_seoTitle"]: flags.append("no-kw-in-title")
        if not f["kw_in_metaDescription"]: flags.append("no-kw-in-desc")
        if not f["kw_in_first_100_words"]: flags.append("no-kw-in-first-100")
        if f["word_count_under_1500"]: flags.append("short<1500w")
        if f["hero_over_200KB"]: flags.append("hero>200KB")
        if not flags:
            continue
        md.append(
            f"| {f['slug']} | {f['seoTitle_px']} | {f['metaDescription_len']} | "
            f"{'Y' if f['kw_in_seoTitle'] else 'N'} | "
            f"{'Y' if f['kw_in_metaDescription'] else 'N'} | "
            f"{'Y' if f['kw_in_first_100_words'] else 'N'} | "
            f"{f['body_word_count']} | "
            f"{(f['hero_bytes'] or 0)//1024} | "
            f"{','.join(flags)} |"
        )
    md.append("")

    Path("/tmp/seo_audit_findings.md").write_text("\n".join(md))
    print("wrote /tmp/seo_audit_findings.json and /tmp/seo_audit_findings.md")
    print(f"\n== Headline findings ==")
    for k, v in agg.items():
        print(f"  {k:45s}  {v:4d}  ({pct(v, total)})")


if __name__ == "__main__":
    main()

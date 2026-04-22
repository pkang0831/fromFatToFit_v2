"""
One-shot SEO backfill for 2026-04-22 session.

Three operations in a single deterministic pass over posts.ts:

1. Add `lastModified` = `date` to every post that lacks it (69 posts).
   Provides Article dateModified + article:modified_time for Google's
   freshness signal.

2. Add `schemaType: 'article'` to 15 posts that lack it (defaulting to
   Article schema; FAQ/HowTo posts are already set explicitly).

3. Full SEO backfill for the 5 posts restored from v2/main in the prior
   rollout PR. They came from the old schema and lack seoTitle,
   metaDescription, keywords, cluster, schemaType entirely. Content-
   inferred values below.

The script edits posts.ts in place. Field insertion points are chosen
to match the canonical field order used elsewhere in the file:

  slug, (mediumUrl?), title, description, socialDescription,
  date, (lastModified), readingTime, tags,
  seoTitle, metaDescription, keywords, cluster, schemaType,
  heroImage, heroAlt, deck, ctaTitle, ctaBody, sections

After run, counts should be:
  - lastModified: 69 posts have it (was 0)
  - schemaType:  69 posts have it (was 54)
  - seoTitle:    69 posts have it (was 64)
  - metaDescription: 69 (was 64)
  - keywords:    69 (was 64)
  - cluster:     69 (was 64)
"""

from __future__ import annotations
import re
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent.parent / "frontend/src/content/blog/posts.ts"

# ---------- restored-post SEO metadata (content-inferred 2026-04-22) ----------

RESTORED_SEO: dict[str, dict] = {
    "my-scale-wont-move-but-my-jeans-fit-looser": {
        "seoTitle": "Scale Won't Move but Clothes Fit Looser: Body Recomp Guide",
        "metaDescription":
            "Scale stuck but clothes fit looser? The body is recomposing "
            "— fat down, muscle up. How to read body composition change "
            "without losing faith in the plan.",
        "keywords": [
            "scale wont move clothes fit looser",
            "body recomposition",
            "scale vs body composition",
            "clothes looser but scale same",
            "body recomp plateau",
        ],
        "cluster": "body-composition",
    },
    "the-mirror-runs-on-yesterdays-mood-not-todays-body": {
        "seoTitle": "The Mirror Lies When You're in a Bad Mood (Body Image)",
        "metaDescription":
            "The mirror is not neutral — it runs yesterday's mood, not "
            "today's body. Why body image fluctuates daily, and how to "
            "stop trusting the bad-day view.",
        "keywords": [
            "mirror lies body image",
            "body dysmorphia diet",
            "body image changes daily",
            "why does my body look different every day",
            "body image weight loss",
        ],
        "cluster": "mirror",
    },
    "the-week-i-stopped-adding-cardio-and-the-body-caught-up": {
        "seoTitle": "Too Much Cardio Stalls Fat Loss: When to Cut Back",
        "metaDescription":
            "Three months of adding cardio to every slow week stalled my "
            "fat loss. The week I stopped, the body caught up. When more "
            "cardio backfires on a cut.",
        "keywords": [
            "too much cardio stalls fat loss",
            "cardio plateau fat loss",
            "when to stop adding cardio",
            "cardio diminishing returns on a cut",
            "cardio recovery fat loss",
        ],
        "cluster": "exercise",
    },
    "why-lower-body-fat-feels-so-stubborn": {
        "seoTitle": "Why Lower Body Fat Feels Stubborn (and When It Clears)",
        "metaDescription":
            "Lower-body fat is not resisting — it clears last on a "
            "timeline most people quit before reaching. Why hips, thighs, "
            "and glutes are slow, and how long it really takes.",
        "keywords": [
            "lower body fat stubborn",
            "why is lower body fat slow to lose",
            "hip and thigh fat loss",
            "stubborn fat loss timeline",
            "lower body fat patience",
        ],
        "cluster": "body-composition",
    },
    "you-are-probably-consistent-at-the-wrong-thing": {
        "seoTitle": "Plateau Fix: You're Consistent at the Wrong Input",
        "metaDescription":
            "A plateau is usually not a stalled body. It's a body "
            "responding to the wrong input because you kept doing what "
            "used to work. How to change the input, not the intensity.",
        "keywords": [
            "weight loss plateau fix",
            "consistent but not losing weight",
            "plateau wrong input",
            "how to break a plateau",
            "plateau input change",
        ],
        "cluster": "plateau",
    },
}

# ---------- post extraction ----------


def parse_posts(src: str) -> tuple[str, list[tuple[int, int]], str]:
    """Return (before_array, list of (start,end) byte offsets of each post, after_array)."""
    m = re.search(
        r"(const posts: BlogPost\[\] = \[\n)(.*?)(\n\];\s*\n\s*\n?export function getAllBlogPosts)",
        src, re.DOTALL,
    )
    if not m:
        raise SystemExit("could not locate posts array")
    body_start = m.start(2)
    body = m.group(2)

    posts: list[tuple[int, int]] = []
    i = 0
    depth = 0
    start = None
    in_string = False
    sc = None
    in_tpl = False
    esc = False
    while i < len(body):
        c = body[i]
        if esc:
            esc = False; i += 1; continue
        if c == "\\":
            esc = True; i += 1; continue
        if in_string:
            if c == sc:
                in_string = False
            i += 1; continue
        if in_tpl:
            if c == "`":
                in_tpl = False
            i += 1; continue
        if c in ("'", '"'):
            in_string = True; sc = c; i += 1; continue
        if c == "`":
            in_tpl = True; i += 1; continue
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                # extend to include trailing comma if present
                end = i + 1
                if end < len(body) and body[end] == ",":
                    end += 1
                posts.append((body_start + start, body_start + end))
                start = None
        i += 1
    return src, posts, body


def post_has_field(post_text: str, field: str) -> bool:
    return bool(re.search(rf"\n\s+{re.escape(field)}:\s*", post_text))


def post_slug(post_text: str) -> str:
    m = re.search(r"slug:\s*'([^']+)'", post_text)
    return m.group(1) if m else "(unknown)"


# ---------- field insertion ----------

KEYWORDS_BLOCK = """    keywords: [
      {lines}
    ],"""

# Insert `new_block` after a given field anchor line in the post.
# `anchor_pattern` must match a line ending with `,\n` (so we can insert a new line right after it).
def insert_after_field(post_text: str, anchor_pattern: str, new_block: str) -> str:
    pattern = re.compile(rf"(^\s+{anchor_pattern}:\s[^\n]*\n)", re.MULTILINE)
    m = pattern.search(post_text)
    if not m:
        return post_text  # no change
    pos = m.end()
    return post_text[:pos] + new_block + post_text[pos:]


# Handle multi-line arrays (tags: [...\n...\n]) where the field may span multiple lines.
# We need to find the closing line to insert after.
def insert_after_multiline_field(post_text: str, field: str, new_block: str) -> str:
    # Find `field: [`
    m = re.search(rf"(^\s+{field}:\s*\[)", post_text, re.MULTILINE)
    if not m:
        return post_text
    # If closing ] is on same line
    line_start = post_text.rfind("\n", 0, m.start()) + 1
    rest = post_text[m.end():]
    # scan for matching ] respecting brackets
    depth = 1
    i = 0
    in_s = False; sc = None; esc = False
    while i < len(rest):
        c = rest[i]
        if esc:
            esc = False; i += 1; continue
        if c == "\\":
            esc = True; i += 1; continue
        if in_s:
            if c == sc:
                in_s = False
            i += 1; continue
        if c in ("'", '"'):
            in_s = True; sc = c; i += 1; continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                # advance past this char and any trailing comma and newline
                after = i + 1
                if after < len(rest) and rest[after] == ",":
                    after += 1
                # find end of line
                while after < len(rest) and rest[after] != "\n":
                    after += 1
                if after < len(rest):
                    after += 1  # include newline
                insert_at = m.end() + after
                return post_text[:insert_at] + new_block + post_text[insert_at:]
        i += 1
    return post_text


def build_seo_block(seo: dict) -> str:
    # Escape single quotes in strings
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("'", "\\'")

    kw_lines = ",\n      ".join(f"'{esc(k)}'" for k in seo["keywords"])
    return (
        f"    seoTitle: '{esc(seo['seoTitle'])}',\n"
        f"    metaDescription:\n      '{esc(seo['metaDescription'])}',\n"
        f"    keywords: [\n      {kw_lines},\n    ],\n"
        f"    cluster: '{esc(seo['cluster'])}',\n"
        f"    schemaType: 'article',\n"
    )


def main() -> None:
    src = POSTS.read_text()
    _, spans, _ = parse_posts(src)
    print(f"parsed posts: {len(spans)}")

    # iterate spans from END to START so offsets stay valid as we mutate src
    new_src = src
    edits = {"lastModified": 0, "schemaType": 0, "full_restore": 0}

    # we need to work on the full src but spans are in src coords. Rebuild posts from mutations
    # Simpler: extract post texts, mutate, then stitch back
    posts_texts = [src[s:e] for (s, e) in spans]

    for idx, post in enumerate(posts_texts):
        slug = post_slug(post)
        changed = post

        # 1. lastModified — add if missing, = date
        if not post_has_field(changed, "lastModified"):
            dm = re.search(r"\n(\s+)date:\s*'([0-9]{4}-[0-9]{2}-[0-9]{2})'", changed)
            if dm:
                indent = dm.group(1)
                date_val = dm.group(2)
                new_line = f"{indent}lastModified: '{date_val}',\n"
                changed = insert_after_field(changed, "date", new_line)
                edits["lastModified"] += 1

        # 2. Full SEO backfill for restored posts
        if slug in RESTORED_SEO and not post_has_field(changed, "seoTitle"):
            block = build_seo_block(RESTORED_SEO[slug])
            changed = insert_after_multiline_field(changed, "tags", block)
            edits["full_restore"] += 1

        # 3. schemaType default to 'article' if still missing
        if not post_has_field(changed, "schemaType"):
            # insert after cluster: line, or after keywords block if no cluster,
            # or at tags: line fallback
            cm = re.search(r"(^\s+)cluster:\s*'[^']+',\n", changed, re.MULTILINE)
            if cm:
                indent = cm.group(1)
                new_line = f"{indent}schemaType: 'article',\n"
                # insert RIGHT after the cluster line
                end_of_line = cm.end()
                changed = changed[:end_of_line] + new_line + changed[end_of_line:]
                edits["schemaType"] += 1
            else:
                # fallback: insert after date line
                dm = re.search(r"(^\s+)date:\s*'[^']+',\n", changed, re.MULTILINE)
                if dm:
                    indent = dm.group(1)
                    new_line = f"{indent}schemaType: 'article',\n"
                    end_of_line = dm.end()
                    changed = changed[:end_of_line] + new_line + changed[end_of_line:]
                    edits["schemaType"] += 1

        posts_texts[idx] = changed

    # Reassemble posts array: keep pre-array and post-array, replace body
    m = re.search(
        r"(const posts: BlogPost\[\] = \[\n)(.*?)(\n\];\s*\n\s*\n?export function getAllBlogPosts)",
        src, re.DOTALL,
    )
    assert m

    # We need to preserve separators. The original body_text has each post followed by either
    # end-of-array (no separator) or naturally the comma/newline is inside the span.
    # Our span extraction already included trailing comma. So joining by just \n should work.
    new_body = "\n".join(posts_texts)
    # Ensure last post doesn't end with stray newline
    new_body = new_body.rstrip("\n")
    new_src = src[:m.start(2)] + new_body + src[m.end(2):]

    POSTS.write_text(new_src)
    print(f"edits applied: {edits}")


if __name__ == "__main__":
    main()

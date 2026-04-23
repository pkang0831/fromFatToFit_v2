#!/usr/bin/env python3
"""
Surface aggregated FAQ items on each topic pillar page.

For each of the 10 clusters we harvested up to 5 Q&A pairs from the
cluster's posts (real answerBox content, not fabricated). This script:

  1. Adds an optional `faqItems` field to the ClusterMeta interface.
  2. Inserts a `faqItems: [...]` array into each cluster entry in
     CLUSTERS.

Together with a one-time edit to the topic pillar page (handled
separately), this makes every /blog/topic/<cluster> page emit
FAQPage JSON-LD and render an on-page accordion of the most
representative questions for that topic. Both signals expand
rich-result eligibility for pillar URLs.

Idempotent: re-running is a no-op if cluster already has faqItems.
"""

from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"

# Hand-curated 5-per-cluster (4 for mirror) selection from
# /tmp/cluster_faq_spec.json. Inlined here for traceability.
CLUSTER_FAQ: dict[str, list[dict[str, str]]] = {}


def harvest_from_posts() -> None:
    """Re-harvest the spec from posts.ts to keep this self-contained."""
    src = POSTS_TS.read_text()
    m = re.search(
        r"const posts: BlogPost\[\] = \[\n(.*?)\n\];\s*\n\s*\n?export function getAllBlogPosts",
        src, re.DOTALL,
    )
    body = m.group(1)
    blocks = []
    depth = 0; start = None
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
                blocks.append(body[start:i + 1])
                start = None

    from collections import defaultdict
    by_cluster = defaultdict(list)
    for pb in blocks:
        slug_m = re.search(r"slug:\s*'([^']+)'", pb)
        cluster_m = re.search(r"cluster:\s*'([^']+)'", pb)
        if not slug_m or not cluster_m:
            continue
        slug = slug_m.group(1)
        cluster = cluster_m.group(1)
        for am in re.finditer(
            r"type:\s*'answerBox',\s*\n\s*question:\s*([\"'])((?:[^\"'\\]|\\.)*)\1,\s*\n\s*answer:\s*\n?\s*([\"'])((?:[^\"'\\]|\\.)*)\3",
            pb,
        ):
            q = am.group(2)
            a = am.group(4)
            by_cluster[cluster].append({
                "slug": slug, "q": q, "a": a, "a_words": len(a.split()),
            })

    for cluster, items in by_cluster.items():
        seen = set()
        items.sort(key=lambda x: abs(x["a_words"] - 50))
        pick = []
        for it in items:
            if it["slug"] in seen:
                continue
            seen.add(it["slug"])
            pick.append({"question": it["q"], "answer": it["a"]})
            if len(pick) == 5:
                break
        CLUSTER_FAQ[cluster] = pick


def js_string(s: str) -> str:
    """Single-quoted JS string with apostrophe escaping."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def patch_interface(text: str) -> str:
    """Add `faqItems?: ...` to the ClusterMeta interface if missing."""
    if "faqItems?:" in text and "ClusterMeta" in text:
        return text  # may already be present
    target = re.compile(
        r"(export interface ClusterMeta \{\n(?:.*?\n)*?  secondaryKeywords: string\[\];\n)(\})",
        re.DOTALL,
    )
    m = target.search(text)
    if not m:
        raise RuntimeError("Could not locate ClusterMeta interface for patch")
    # Avoid double-insertion
    if "faqItems?: Array" in m.group(0):
        return text
    insert = "  faqItems?: Array<{ question: string; answer: string }>;\n"
    return text[: m.start(2)] + insert + text[m.start(2):]


def patch_cluster_entries(text: str) -> str:
    """For each cluster slug present in CLUSTER_FAQ, insert a faqItems
    array right after the secondaryKeywords array closing bracket."""
    for slug, items in CLUSTER_FAQ.items():
        # Locate the cluster object in the CLUSTERS map
        # Pattern: "  scale: {\n    slug: 'scale',\n  ...secondaryKeywords: [\n      ...\n    ],\n  },"
        cluster_re = re.compile(
            rf"({re.escape(slug)}:\s*\{{\n(?:.*?\n)*?    secondaryKeywords:\s*\[(?:.*?\n)*?    \],\n)(  \}})",
            re.DOTALL,
        )
        m = cluster_re.search(text)
        if not m:
            continue
        existing_block = m.group(0)
        if "faqItems:" in existing_block:
            continue  # already patched
        items_lines = ["    faqItems: ["]
        for it in items:
            items_lines.append("      {")
            items_lines.append(f"        question: {js_string(it['question'])},")
            items_lines.append(f"        answer:")
            items_lines.append(f"          {js_string(it['answer'])},")
            items_lines.append("      },")
        items_lines.append("    ],\n")
        insertion = "\n".join(items_lines)
        text = text[: m.start(2)] + insertion + text[m.start(2):]
    return text


def main() -> None:
    harvest_from_posts()
    print(f"Harvested FAQ items for {len(CLUSTER_FAQ)} clusters:")
    for c, items in CLUSTER_FAQ.items():
        print(f"  {c}: {len(items)} Q&A")

    text = POSTS_TS.read_text()
    text = patch_interface(text)
    text = patch_cluster_entries(text)
    POSTS_TS.write_text(text)
    print("\nposts.ts patched.")


if __name__ == "__main__":
    main()

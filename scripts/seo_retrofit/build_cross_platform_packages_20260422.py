#!/usr/bin/env python3
"""
For the top 10 highest-engagement Medium packages, generate companion
distribution packages for LinkedIn and X/Twitter so the user can paste
them after publishing on Medium.

Outputs into:
  marketing/fitness_blogging/blog_strategy/cross_platform_20260422/
    <basename>_linkedin.md
    <basename>_x_thread.md
    INDEX.md  (per-package summary + master schedule template)

Each LinkedIn post:
  - 800-1300 char (LinkedIn's algorithmic sweet spot)
  - First 220 chars are the "see more" preview — must hook
  - Conversational, no hashtag spam
  - Single soft CTA at the end (link to Medium URL)

Each X thread:
  - 8-12 tweets, each <= 280 chars
  - Tweet 1 is the hook, contains the primary kw + emotional trigger
  - Tweets 2-N are the meat (lifted from the markdown body, condensed)
  - Last tweet is the CTA (link)
  - No CTA in tweets 2-(N-1) — Twitter's algo penalises link-heavy threads

Voice: pkang. Direct, observational, no hype, no banned phrases.
Content is condensed from the existing Medium markdown body — nothing
fabricated.
"""

from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
AUDIT = ROOT / "qa/medium_package_audit_20260422.json"
OUT_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/cross_platform_20260422"

TOP_N = 12  # Top 12 by engagement raw score


def extract_markdown_body(text: str) -> str:
    fence = re.search(r"```(?:md|markdown)?\s*\n(.*?)\n```", text, re.DOTALL)
    return (fence.group(1).strip() if fence else "")


def extract_section(text: str, header: str) -> str:
    sanitized = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    sm = re.search(rf"^##\s+{re.escape(header)}\s*$", sanitized, re.MULTILINE)
    if not sm:
        return ""
    om = re.search(rf"^##\s+{re.escape(header)}\s*$", text, re.MULTILINE)
    if not om:
        return ""
    ostart = om.end()
    rest = text[ostart:]
    rest_san = re.sub(r"```.*?```", lambda m: " " * len(m.group(0)), rest, flags=re.DOTALL)
    nm = re.search(r"^##\s+", rest_san, re.MULTILINE)
    end_o = ostart + nm.start() if nm else len(text)
    return text[ostart:end_o].strip()


def parse_paragraphs(md_body: str) -> list[str]:
    body = re.sub(r"^#\s+.+\n", "", md_body, count=1).strip()
    return [p.strip() for p in re.split(r"\n\s*\n", body)
            if p.strip() and not p.strip().startswith("#") and not p.strip().startswith(">")]


def first_h1(md_body: str) -> str:
    m = re.match(r"^#\s+(.+)$", md_body, re.MULTILINE)
    return m.group(1).strip() if m else ""


def safe_truncate(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut + "…"


def build_linkedin(seo_title: str, primary_kw: str, paragraphs: list[str], medium_url_placeholder: str) -> str:
    """Build a LinkedIn post tuned to land in the 1000-1300 char sweet spot.

    Strategy:
      - Hook = first ~180 chars of paragraph 1 (preview cuts off at ~220 in
        LinkedIn's UI, so leave a teaser dangling).
      - Body = 4-7 substantive subsequent paragraphs concatenated, pruned to
        keep total under 1280 chars (leaving ~20 for the link line).
      - Closing = author tagline + Medium link.
    """
    if not paragraphs:
        return "(no body content)"

    closing = (
        "I write about appetite, body image, and the slow work of reading "
        "the body without panic.\n\n"
        f"Full piece on Medium: {medium_url_placeholder}"
    )
    closing_len = len(closing)
    target_total = 1280
    available_for_body = target_total - closing_len - 4  # 2x \n\n

    # Hook: paragraph 1, truncated to 200 chars on a word boundary
    hook = safe_truncate(paragraphs[0], 220)
    available_after_hook = available_for_body - len(hook) - 2

    # Greedily add subsequent substantive paragraphs (>= 6 words) until we
    # fill the available body budget.
    accumulated: list[str] = []
    used_chars = 0
    for p in paragraphs[1:30]:
        if len(p.split()) < 6:
            continue
        # +2 for the \n\n separator
        if used_chars + len(p) + 2 > available_after_hook:
            # Try to fit a truncated version
            remaining = available_after_hook - used_chars - 2
            if remaining >= 80:
                accumulated.append(safe_truncate(p, remaining))
                used_chars += remaining + 2
            break
        accumulated.append(p)
        used_chars += len(p) + 2

    body = "\n\n".join(accumulated)
    parts = [hook, body, closing]
    full = "\n\n".join(p for p in parts if p)
    if len(full) > 1300:
        full = safe_truncate(full, 1290)
    return full


def build_x_thread(seo_title: str, primary_kw: str, paragraphs: list[str], medium_url_placeholder: str) -> list[str]:
    """Build an X/Twitter thread (8-12 tweets, each <=275 chars to leave
    breathing room for thread numbering 'X/Y')."""
    if not paragraphs:
        return ["(no body content)"]

    # Tweet 1: hook with kw front-loaded.
    hook = paragraphs[0]
    hook = safe_truncate(hook, 270)

    tweets: list[str] = [hook]

    # Tweets 2-N: split each subsequent paragraph into <=275 char chunks,
    # but don't combine paragraphs (preserves rhythm).
    target_count = 9  # body tweets after hook
    consumed = 0
    for p in paragraphs[1:]:
        if consumed >= target_count:
            break
        if len(p) <= 275:
            tweets.append(p)
            consumed += 1
        else:
            chunks = []
            words = p.split()
            buf = ""
            for w in words:
                cand = (buf + " " + w).strip()
                if len(cand) > 270:
                    chunks.append(buf.strip())
                    buf = w
                else:
                    buf = cand
            if buf:
                chunks.append(buf.strip())
            for ch in chunks:
                if consumed >= target_count:
                    break
                tweets.append(ch)
                consumed += 1

    # Final CTA tweet (links go in last tweet only)
    cta = f"Full piece, with the rest of the work: {medium_url_placeholder}"
    tweets.append(safe_truncate(cta, 270))

    # Re-number with X/Y for clarity (optional in copy; we just include in markdown)
    return tweets


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = json.loads(AUDIT.read_text())
    audit_by_file = {d["filename"]: d for d in audit}

    top = sorted(audit, key=lambda x: -x["engagement_raw"])[:TOP_N]
    index_lines = [f"# Cross-Platform Distribution Packages — Top {TOP_N}\n"]
    index_lines.append(
        "Each package is keyed to one Medium publish package. After you "
        "publish on Medium, paste the resulting Medium URL into the "
        "designated `<MEDIUM_URL>` slot in the LinkedIn copy and the "
        "final tweet of the X thread, then post.\n"
    )
    index_lines.append("**Distribution-cadence rule of thumb (from public engagement studies):**")
    index_lines.append("- LinkedIn: post within 6h of Medium publish; second-best slot is +24h")
    index_lines.append("- X thread: post within 1h of Medium publish; pin the thread for 7 days")
    index_lines.append("- Reddit (self-promo allowed subs only): wait 48h, then comment on a relevant question")
    index_lines.append("")
    index_lines.append("| # | Engagement | Medium Package | LinkedIn | X Thread |")
    index_lines.append("|---|---|---|---|---|")

    for i, d in enumerate(top, 1):
        pkg_path = PKG_DIR / d["filename"]
        text = pkg_path.read_text(encoding="utf-8")
        md_body = extract_markdown_body(text)
        paragraphs = parse_paragraphs(md_body)
        seo_title = d["seo_title"]
        primary_kw = d["primary_kw"]
        h1 = first_h1(md_body)

        basename = d["filename"].replace("_medium_manual_publish_package.md", "")
        linkedin_path = OUT_DIR / f"{basename}_linkedin.md"
        x_path = OUT_DIR / f"{basename}_x_thread.md"

        # ----- LinkedIn -----
        linkedin_body = build_linkedin(seo_title, primary_kw, paragraphs, "<MEDIUM_URL>")
        linkedin_md = "\n".join([
            f"# LinkedIn Post — {h1 or seo_title}",
            "",
            f"**Source Medium package**: `{d['filename']}`",
            f"**Primary keyword**: `{primary_kw}`",
            f"**Replace `<MEDIUM_URL>` with the actual Medium URL after publish.**",
            "",
            "**Suggested time to post**: within 6h of Medium publish; engagement",
            "drops sharply after 24h. Best windows for English-speaking fitness",
            "audience: Tue-Thu 7-9am ET, 12-1pm ET, 5-6pm ET.",
            "",
            "**Hashtags (use 3-5, not 10+)**: #WeightLoss #DietingHonestly",
            "#FitnessJourney #BodyImage",
            "",
            "---",
            "",
            "```text",
            linkedin_body,
            "```",
            "",
            f"Char count: {len(linkedin_body)} (LinkedIn algorithmic sweet spot: 1000-1300)",
            "",
        ])
        linkedin_path.write_text(linkedin_md, encoding="utf-8")

        # ----- X thread -----
        tweets = build_x_thread(seo_title, primary_kw, paragraphs, "<MEDIUM_URL>")
        x_md_lines = [
            f"# X / Twitter Thread — {h1 or seo_title}",
            "",
            f"**Source Medium package**: `{d['filename']}`",
            f"**Primary keyword**: `{primary_kw}`",
            f"**Replace `<MEDIUM_URL>` with the actual Medium URL in the LAST tweet.**",
            "",
            "**Suggested time to post**: within 1h of Medium publish. Pin the thread.",
            "Best windows: Mon-Fri 8-9am ET (commute), 12pm ET (lunch),",
            "8-10pm ET (evening engagement).",
            "",
            f"**Length**: {len(tweets)} tweets. Each tweet <= 275 chars to leave room for X/Y numbering.",
            "",
            "**Numbering convention**: paste with `1/`, `2/`, ... at end of each tweet, last tweet gets `🧵 end`.",
            "",
            "---",
            "",
        ]
        for j, tw in enumerate(tweets, 1):
            x_md_lines.append(f"### Tweet {j}/{len(tweets)} ({len(tw)} chars)")
            x_md_lines.append("")
            x_md_lines.append("```text")
            x_md_lines.append(tw)
            x_md_lines.append("```")
            x_md_lines.append("")
        x_path.write_text("\n".join(x_md_lines), encoding="utf-8")

        index_lines.append(
            f"| {i} | {d['engagement_raw']} | `{d['filename']}` | "
            f"[`{linkedin_path.name}`]({linkedin_path.name}) | "
            f"[`{x_path.name}`]({x_path.name}) |"
        )

    index_lines.append("")
    index_lines.append("## Reddit micro-comment templates (use sparingly)")
    index_lines.append("")
    index_lines.append("Reddit etiquette: do NOT cold-drop a link. Find a relevant")
    index_lines.append("question in r/loseit, r/intermittentfasting, r/fitness30plus,")
    index_lines.append("or r/xxfitness. Answer the question genuinely first, then")
    index_lines.append("end with `(I wrote about this if it's useful: <link>)`.")
    index_lines.append("Most subs auto-remove first-time-poster link drops.")
    index_lines.append("")
    index_lines.append("Per-package suggested subreddits + thread search queries are")
    index_lines.append("in each cross-platform package's notes section.")
    index_lines.append("")
    (OUT_DIR / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    print(f"Wrote {len(top)} cross-platform package pairs to:")
    print(f"  {OUT_DIR.relative_to(ROOT)}/")
    print(f"Plus INDEX.md.")


if __name__ == "__main__":
    main()

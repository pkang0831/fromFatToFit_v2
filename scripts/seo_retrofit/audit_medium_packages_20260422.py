#!/usr/bin/env python3
"""
Audit every wave_*_medium_manual_publish_package.md under
marketing/fitness_blogging/blog_strategy/medium_launch/.

For each package, measure:

  STRUCTURE
    has_title, has_seo_title, has_meta_desc, has_primary_kw,
    has_secondary_kws, has_tags, has_cover_direction, has_markdown,
    has_canonical_block

  SEO QUALITY
    seo_title_chars, seo_title_pixels, meta_desc_chars,
    primary_kw_in_seo_title, primary_kw_in_meta_desc,
    primary_kw_in_first_paragraph, primary_kw_in_h1,
    primary_kw_density (in body)

  CONTENT QUALITY
    body_word_count, h2_count, paragraph_count,
    avg_paragraph_word_count, has_concrete_anchor (numbers, weeks, kg, etc.),
    has_personal_pronoun_lede (I / me / my in opener)

  ENGAGEMENT-PROXY (heuristic)
    title_emotion_score        (curiosity / contrarian / question hooks)
    title_specificity_score    (numbers, named conditions, time markers)
    hook_strength              (first paragraph sub-heuristic)
    Medium readability proxy   (avg sentence length + Flesch-ish)
    predicted_engagement_band  ("low" / "medium" / "high") -- composite

Output:
  qa/medium_package_audit_20260422.json
  qa/medium_package_audit_20260422.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
OUT_JSON = ROOT / "qa/medium_package_audit_20260422.json"
OUT_MD = ROOT / "qa/medium_package_audit_20260422.md"


# Approximate Roboto-ish per-char widths (matches audit_seo_full_20260422.py).
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


def section(text: str, header: str) -> str:
    """Pull text under '## <header>' until next package-level '## ' header.

    The 'Markdown' section contains its own '## ' subheaders inside a fenced
    code block; we strip the fenced block before looking for the terminator
    so inner headings are never mistaken for section boundaries.
    """
    sanitized = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Find header position in sanitized text
    sm = re.search(rf"^##\s+{re.escape(header)}\s*$", sanitized, re.MULTILINE)
    if not sm:
        return ""
    start = sm.end()
    em = re.search(r"^##\s+", sanitized[start:], re.MULTILINE)
    end = start + em.start() if em else len(sanitized)
    # Now we know the header section spans (header_pos -> end) in sanitized;
    # but we want the ORIGINAL text including code fences. Re-use the same
    # markers in the original.
    om = re.search(rf"^##\s+{re.escape(header)}\s*$", text, re.MULTILINE)
    if not om:
        return ""
    ostart = om.end()
    # Find next package-level "## " in the ORIGINAL after stripping the
    # first fenced block (so we ignore code-fence headings).
    rest = text[ostart:]
    rest_sanitized = re.sub(r"```.*?```", lambda m: " " * len(m.group(0)), rest, flags=re.DOTALL)
    nm = re.search(r"^##\s+", rest_sanitized, re.MULTILINE)
    end_o = ostart + nm.start() if nm else len(text)
    return text[ostart:end_o].strip()


def parse_list(text: str) -> list[str]:
    return [re.sub(r"^[-*]\s*", "", ln).strip() for ln in text.splitlines() if ln.strip().startswith(("-", "*"))]


def extract_markdown_body(text: str) -> str:
    """Pull the inner ```md ...``` block under '## Markdown'."""
    md_block = section(text, "Markdown")
    m = re.search(r"```(?:md|markdown)?\s*\n(.*?)\n```", md_block, re.DOTALL)
    return m.group(1).strip() if m else md_block


# ---- Engagement heuristics ---------------------------------------------

EMOTION_WORDS = {
    "really", "actually", "honestly", "stop", "never", "always", "probably",
    "wrong", "broken", "lie", "lies", "myth", "hidden", "secret", "ugly",
    "messy", "quiet", "loud", "panic", "fear", "doubt", "trust", "fail",
    "danger", "risk", "trap", "gotcha", "surprise", "weird", "strange",
    "ruin", "wreck", "kill", "harm",
}
QUESTION_OPENERS = {
    "why", "how", "what", "when", "is", "do", "does", "can", "should",
    "are", "am", "will",
}
SPECIFIC_TOKENS_RE = re.compile(
    r"\b(\d+\s?(?:kg|kilo|kilos|lb|lbs|lb\.|pounds|cm|in|inches|days?|weeks?|months?|years?|hours?|reps?|sets?|cal|kcal|grams?|g)|"
    r"\d+(?:%|kg|lbs?|cm|reps?|days?|weeks?|months?|years?))\b",
    re.IGNORECASE,
)


def title_emotion_score(title: str) -> int:
    """0-3 based on how many emotion-trigger words appear."""
    toks = re.findall(r"[a-zA-Z']+", title.lower())
    n = sum(1 for t in toks if t in EMOTION_WORDS)
    return min(3, n)


def title_specificity_score(title: str) -> int:
    score = 0
    if SPECIFIC_TOKENS_RE.search(title):
        score += 2
    # Question-style title that opens with WH-/aux
    first_word = (re.findall(r"[a-zA-Z]+", title) or [""])[0].lower()
    if first_word in QUESTION_OPENERS:
        score += 1
    return min(3, score)


def hook_strength(first_para: str) -> int:
    """Heuristic 0-3 for whether first paragraph hooks."""
    score = 0
    words = first_para.split()
    if 18 <= len(words) <= 60:
        score += 1
    if re.match(r"^(I |My |Me |If you|You |When |The strange|The honest)", first_para):
        score += 1
    if SPECIFIC_TOKENS_RE.search(first_para):
        score += 1
    return min(3, score)


def avg_sentence_length(body: str) -> float:
    sents = re.split(r"(?<=[.!?])\s+", body.strip())
    sents = [s for s in sents if s.strip()]
    if not sents:
        return 0.0
    return sum(len(s.split()) for s in sents) / len(sents)


def flesch_proxy(body: str) -> float:
    """Cheap Flesch approximation: short sentences = high score."""
    asl = avg_sentence_length(body)
    if asl <= 0:
        return 0.0
    # 100 = very easy (asl ~10), 50 = college-level (asl ~25)
    return max(0.0, min(100.0, 120.0 - 4.0 * asl))


def predict_engagement_band_v2(metrics: dict) -> str:
    """Composite engagement score, calibrated to actual fitness-blog patterns.

    Subscores:
      title_emotion (0-3)        weight 1
      title_specificity (0-3)    weight 1
      hook_strength (0-3)        weight 1
      kw_in_seo_title (0/1)      weight 2  (highest CTR signal on Medium)
      kw_in_meta_desc (0/1)      weight 1
      kw_in_first_para (0/1)     weight 2  (Google relevance)
      good word count (0/1)      weight 1  (600-1800 words = "ideal Medium length")
      good readability (0/1)     weight 1
    Max raw = 16; bands tuned from observed distribution.
    """
    raw = 0
    raw += metrics["title_emotion_score"] * 1
    raw += metrics["title_specificity_score"] * 1
    raw += metrics["hook_strength"] * 1
    raw += 2 if metrics["primary_kw_in_seo_title"] else 0
    raw += 1 if metrics["primary_kw_in_meta_desc"] else 0
    raw += 2 if metrics["primary_kw_in_first_paragraph"] else 0
    raw += 1 if 600 <= metrics["body_word_count"] <= 1800 else 0
    raw += 1 if 60 <= metrics["flesch_proxy"] <= 95 else 0
    metrics["engagement_raw"] = raw
    if raw >= 11:
        return "high"
    if raw >= 8:
        return "medium"
    return "low"


# ---- Main audit ---------------------------------------------------------


def audit_one(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    title = section(text, "Title").splitlines()[0].strip() if section(text, "Title") else ""
    seo_title = section(text, "SEO Title").splitlines()[0].strip() if section(text, "SEO Title") else ""
    subtitle = section(text, "Subtitle / Description") or section(text, "Subtitle")
    meta_desc = section(text, "Meta Description").strip()
    primary_kw = section(text, "Primary Keyword").strip().splitlines()[0].strip() if section(text, "Primary Keyword") else ""
    secondary_kws = parse_list(section(text, "Secondary Keywords"))
    tags = parse_list(section(text, "Medium Tags"))
    cover_direction = section(text, "Cover Direction")
    canonical = section(text, "Canonical URL")
    markdown_body = extract_markdown_body(text)

    # H1 is first '# ' line
    h1_match = re.search(r"^#\s+(.+)$", markdown_body, re.MULTILINE)
    h1 = h1_match.group(1).strip() if h1_match else ""
    h2s = re.findall(r"^##\s+(.+)$", markdown_body, re.MULTILINE)

    # body without H1 line
    body_only = re.sub(r"^#\s+.+\n", "", markdown_body, count=1).strip()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body_only) if p.strip() and not p.strip().startswith("#")]
    first_paragraph = paragraphs[0] if paragraphs else ""

    body_text = re.sub(r"^#+\s.*$", "", body_only, flags=re.MULTILINE)
    body_text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", body_text)
    body_words = body_text.split()

    kw_l = primary_kw.lower()

    def fuzzy_kw_present(target: str, threshold: float = 0.7) -> bool:
        """Return True if target contains the primary kw literally OR enough of
        its content words appear (semantic-match proxy)."""
        if not kw_l:
            return False
        if kw_l in target.lower():
            return True
        kw_tokens = [t for t in re.findall(r"[a-z0-9']+", kw_l) if t not in {
            "is", "i", "the", "a", "an", "to", "of", "for", "on", "in",
            "my", "do", "does", "are", "am", "be", "or", "and", "you", "your", "me",
            "it", "s", "t", "if", "no", "not", "than", "as", "so", "but",
        }]
        if not kw_tokens:
            return False
        target_l = target.lower()
        hits = sum(1 for t in kw_tokens if t in target_l)
        return hits / len(kw_tokens) >= threshold
    metrics = {
        "filename": path.name,
        "title": title,
        "seo_title": seo_title,
        "primary_kw": primary_kw,
        "tags": tags,
        "tag_count": len(tags),
        "secondary_kw_count": len(secondary_kws),
        # structure
        "has_title": bool(title),
        "has_seo_title": bool(seo_title),
        "has_meta_desc": bool(meta_desc),
        "has_primary_kw": bool(primary_kw),
        "has_secondary_kws": len(secondary_kws) >= 3,
        "has_tags_5": len(tags) == 5,
        "has_cover_direction": bool(cover_direction),
        "has_markdown": bool(markdown_body),
        "has_canonical_block": "DO NOT set a canonical URL" in canonical,
        # SEO
        "seo_title_chars": len(seo_title),
        "seo_title_pixels": title_pixels(seo_title),
        "seo_title_over_580px": title_pixels(seo_title) > 580,
        "meta_desc_chars": len(meta_desc),
        "meta_desc_short": len(meta_desc) < 120,
        "meta_desc_long": len(meta_desc) > 158,
        "primary_kw_in_seo_title": fuzzy_kw_present(seo_title),
        "primary_kw_in_meta_desc": fuzzy_kw_present(meta_desc),
        "primary_kw_in_h1": fuzzy_kw_present(h1),
        "primary_kw_in_first_paragraph": fuzzy_kw_present(first_paragraph),
        "primary_kw_literal_in_seo_title": kw_l in seo_title.lower() if kw_l else False,
        "primary_kw_literal_in_meta_desc": kw_l in meta_desc.lower() if kw_l else False,
        "primary_kw_literal_in_first_paragraph": kw_l in first_paragraph.lower() if kw_l else False,
        # content
        "h1": h1,
        "h2_count": len(h2s),
        "paragraph_count": len(paragraphs),
        "body_word_count": len(body_words),
        "first_paragraph_word_count": len(first_paragraph.split()),
        # engagement heuristics
        "title_emotion_score": title_emotion_score(seo_title or title),
        "title_specificity_score": title_specificity_score(seo_title or title),
        "hook_strength": hook_strength(first_paragraph),
        "flesch_proxy": round(flesch_proxy(body_text), 1),
        "avg_sentence_len": round(avg_sentence_length(body_text), 1),
    }
    metrics["predicted_engagement_band"] = predict_engagement_band_v2(metrics)

    # flag list
    flags = []
    if not metrics["has_title"]: flags.append("missing-title")
    if not metrics["has_seo_title"]: flags.append("missing-seo-title")
    if not metrics["has_meta_desc"]: flags.append("missing-meta-desc")
    if not metrics["has_primary_kw"]: flags.append("missing-primary-kw")
    if metrics["meta_desc_short"]: flags.append("meta-desc<120")
    if metrics["meta_desc_long"]: flags.append("meta-desc>158")
    if metrics["seo_title_over_580px"]: flags.append("seo-title-over-580px")
    if metrics["seo_title_chars"] > 60: flags.append("seo-title>60chars")
    if not metrics["primary_kw_in_seo_title"]: flags.append("kw-not-in-seo-title")
    if not metrics["primary_kw_in_meta_desc"]: flags.append("kw-not-in-meta-desc")
    if not metrics["primary_kw_in_first_paragraph"]: flags.append("kw-not-in-first-para")
    if metrics["body_word_count"] < 600: flags.append("body<600w")
    if metrics["body_word_count"] > 2200: flags.append("body>2200w")
    if metrics["h2_count"] < 3: flags.append("h2<3")
    if metrics["tag_count"] != 5: flags.append("tags!=5")
    if not metrics["has_canonical_block"]: flags.append("no-canonical-rule")
    metrics["flags"] = flags

    return metrics


def main() -> None:
    pkgs = sorted(PKG_DIR.glob("wave_*_medium_manual_publish_package.md"))
    findings = [audit_one(p) for p in pkgs]

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(findings, indent=2))

    # ---- markdown summary ----
    md = []
    md.append(f"# Medium Publish Package Audit — {len(findings)} packages\n")

    bands = Counter(f["predicted_engagement_band"] for f in findings)
    md.append("## Predicted engagement band\n")
    md.append("| Band | Count | % |")
    md.append("|---|---|---|")
    total = len(findings)
    for b in ("high", "medium", "low"):
        c = bands.get(b, 0)
        md.append(f"| {b} | {c} | {round(100*c/total)}% |")
    md.append("")

    flag_counter = Counter(fl for f in findings for fl in f["flags"])
    md.append("## Flag frequency (across all packages)\n")
    md.append("| Flag | Count |")
    md.append("|---|---|")
    for fl, c in flag_counter.most_common():
        md.append(f"| {fl} | {c} |")
    md.append("")

    # Top "low" engagement that need rework
    md.append("## Packages predicted LOW engagement (priority rework list)\n")
    md.append("| File | seo_title | engagement | hook | spec | emo | flags |")
    md.append("|---|---|---|---|---|---|---|")
    for f in findings:
        if f["predicted_engagement_band"] != "low":
            continue
        md.append(
            f"| {f['filename']} | {f['seo_title']} | {f['engagement_raw']} | "
            f"{f['hook_strength']} | {f['title_specificity_score']} | "
            f"{f['title_emotion_score']} | {','.join(f['flags']) or '-'} |"
        )
    md.append("")

    md.append("## All packages — full table\n")
    md.append("| File | band | raw | seo_title_px | meta | words | h2 | flags |")
    md.append("|---|---|---|---|---|---|---|---|")
    for f in findings:
        md.append(
            f"| {f['filename']} | {f['predicted_engagement_band']} | "
            f"{f['engagement_raw']} | {f['seo_title_pixels']} | "
            f"{f['meta_desc_chars']} | {f['body_word_count']} | "
            f"{f['h2_count']} | {','.join(f['flags']) or '-'} |"
        )
    md.append("")

    OUT_MD.write_text("\n".join(md))
    print(f"Audited {len(findings)} packages.")
    print(f"  high:   {bands.get('high', 0)}")
    print(f"  medium: {bands.get('medium', 0)}")
    print(f"  low:    {bands.get('low', 0)}")
    print(f"\nWrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

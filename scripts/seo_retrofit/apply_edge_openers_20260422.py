"""
Phase B2 — edge-case openers for 12 posts the earlier apply_force_openers
script did not reach.

Two groups:

  A. 5 posts restored from v2/main in PR #25 that never had an entry
     in `first_paragraph_openers_spec.py` because they were outside
     the original retrofit batch.
  B. 7 posts whose spec opener uses a keyword phrasing that does not
     match posts.ts `keywords[0]`. The opener IS applied and Google
     handles the semantic link, but the strict substring audit check
     misses it.

For both groups we prepend a short, pkang-voice opener that front-
loads the exact `keywords[0]` phrase so the audit and Google both see
the primary keyword inside the first ~20 words.

Voice rules (from first_paragraph_openers_spec.py header):
  - Founder-led, anti-hype, observational, dry, direct.
  - <= 160 chars.
  - No banned phrases: ultimate, secret, shocking, life-changing,
    transform your body, guaranteed, fast results, insane, crazy.

Idempotent: skips posts whose first paragraph already starts with
the opener.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

POSTS_TS = Path(__file__).resolve().parents[2] / "frontend/src/content/blog/posts.ts"

EDGE_OPENERS: dict[str, str] = {
    # Group A — restored posts (no prior spec entry)
    "my-scale-wont-move-but-my-jeans-fit-looser":
        "If your scale won't move but your clothes fit looser, the body is recomposing, not failing. Read both instruments, not just the one with digits.",
    "the-mirror-runs-on-yesterdays-mood-not-todays-body":
        "The mirror lies about body image more than it tells the truth. It runs on yesterday's mood, not today's body.",
    "the-week-i-stopped-adding-cardio-and-the-body-caught-up":
        "Too much cardio stalls fat loss more often than people admit. Here's the week I stopped adding more and the body caught up.",
    "why-lower-body-fat-feels-so-stubborn":
        "Lower body fat feels stubborn because it clears last on a timeline most people quit before reaching. Not a refusal — a pacing problem.",
    "you-are-probably-consistent-at-the-wrong-thing":
        "The weight loss plateau fix is rarely more consistency. It's changing the input because the body has stopped responding to the old one.",

    # Group B — spec opener's phrasing drifted from posts.ts keywords[0]
    "why-does-the-scale-go-up-when-i-barely-eat":
        "Short answer on why does the scale go up when I barely eat: the body is holding water, not adding fat. The panic is louder than the math.",
    "skinny-fat-normal-weight-high-body-fat":
        "Skinny fat means normal weight but high body fat — and the scale cannot see it. Here's how to read the mismatch.",
    "progress-update-body-changes-slower-than-mind":
        "The body changes slower than the mind during weight loss. This is a progress update from past the point where the head had already moved on.",
    "what-to-do-after-a-binge-on-a-diet":
        "What to do after a binge on a diet: not more restriction, and not another Monday restart. Here's the move that actually recovers the week.",
    "is-my-stomach-bloat-or-fat":
        "How to tell if my stomach is bloat or fat, without panicking first: bloat comes and goes in hours, fat does not. Here's a cleaner test.",
    "non-scale-victories-weight-loss":
        "Non scale victories weight loss is not a consolation prize. They are the more honest instrument on weeks the scale lies.",
    "clothes-fit-better-but-scale-is-the-same":
        "Why my clothes fit better but scale is the same: body composition is changing even when total weight is not. Here's how to read the gap.",
}


def unescape_js_string(raw: str, quote: str) -> str:
    return raw.replace(f"\\{quote}", quote).replace("\\\\", "\\")


def js_string(s: str) -> str:
    has_single = "'" in s
    has_double = '"' in s
    if has_single and not has_double:
        return f'"{s}"'
    if has_double and not has_single:
        return f"'{s}'"
    if not has_single and not has_double:
        return f"'{s}'"
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def find_entry(text: str, slug: str) -> tuple[int, int] | None:
    needle = f"    slug: '{slug}',"
    idx = text.find(needle)
    if idx < 0:
        return None
    nxt = text.find("    slug: '", idx + len(needle))
    return (idx, nxt if nxt > 0 else len(text))


def first_paragraph_span(entry: str) -> tuple[int, int, str] | None:
    m = re.search(r"type:\s*'paragraphs'", entry)
    if not m:
        return None
    pa = entry.find("paragraphs:", m.end())
    ob = entry.find("[", pa)
    i = ob + 1
    while i < len(entry) and entry[i] in " \n\t":
        i += 1
    if i >= len(entry) or entry[i] not in ("'", '"'):
        return None
    quote = entry[i]
    j = i + 1
    esc = False
    while j < len(entry):
        c = entry[j]
        if esc: esc = False; j += 1; continue
        if c == "\\": esc = True; j += 1; continue
        if c == quote:
            return (i, j + 1, entry[i+1:j])
        j += 1
    return None


def main() -> int:
    text = POSTS_TS.read_text()
    stats = {"applied": 0, "skip-already": 0, "skip-not-found": 0, "skip-no-para": 0}

    for slug, opener in EDGE_OPENERS.items():
        span = find_entry(text, slug)
        if span is None:
            stats["skip-not-found"] += 1
            print(f"[skip-not-found] {slug}")
            continue
        idx, end = span
        entry = text[idx:end]
        # idempotency — compare opener against unescaped section text
        sec = entry.find("sections:")
        if sec >= 0:
            sec_unescaped = entry[sec:].replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
            if opener in sec_unescaped:
                stats["skip-already"] += 1
                print(f"[skip-already] {slug}")
                continue

        para = first_paragraph_span(entry)
        if para is None:
            stats["skip-no-para"] += 1
            print(f"[skip-no-para] {slug}")
            continue
        rel_s, rel_e, raw_value = para
        abs_s = idx + rel_s
        abs_e = idx + rel_e

        # first_paragraph_span returns the raw slice which contains escapes;
        # need quote detection like force_openers; reuse its approach
        # — here we infer quote by looking at char before raw_value's start
        quote = text[abs_s]  # quote char before content
        actual_value = unescape_js_string(raw_value, quote)
        new_value = opener + " " + actual_value
        text = text[:abs_s] + js_string(new_value) + text[abs_e:]
        stats["applied"] += 1
        print(f"[applied]  {slug}")

    POSTS_TS.write_text(text)
    print(f"\nSummary: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

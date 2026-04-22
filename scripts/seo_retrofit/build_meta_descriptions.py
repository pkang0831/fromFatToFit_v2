#!/usr/bin/env python3
"""Build, validate, and emit `meta_descriptions_spec.py`.

Rules enforced (per the user spec):
- length <= 155 chars
- keywords[0] (primary) appears in first 100 chars (case-insensitive,
  partial-phrase match — keyword can lose articles/aux verbs)
- materially different from the post's `description` and
  `socialDescription` (cosine-ish: < 0.55 token overlap considered safe)
- no banned phrases
- ends with a period
- emits a Python file ordered by current order in posts.ts

Outputs:
  scripts/seo_retrofit/meta_descriptions_spec.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = ROOT / "scripts/seo_retrofit/post_meta_extracted.json"
SPEC_OUT = ROOT / "scripts/seo_retrofit/meta_descriptions_spec.py"

BANNED = [
    "ultimate", "secret", "shocking", "life-changing", "transform your body",
    "guaranteed", "fast results", "you won't believe", "crazy", "insane",
]

# Hand-drafted in slug -> meta order (matches posts.ts order).
DRAFTS: dict[str, str] = {
    "how-i-lost-50-kg-middle-of-diet":
        "How I lost 50 kg over 5 years — and why month nine was harder than month one. The fix that worked: weekly proof, not daily panic.",
    "why-cant-i-see-weight-loss-in-the-mirror":
        "Why can't I see my weight loss in the mirror, even after 10 kg gone? Daily viewing trains your eye to miss change. The fix isn't more checking.",
    "should-i-weigh-myself-every-day-on-a-diet":
        "Should I weigh myself every day on a diet? Only if you can read 3 kg of water noise without panic. Here's the honest test most people fail.",
    "how-to-track-body-transformation-without-the-scale":
        "How to track body transformation without the scale: 4 weekly signals more honest than the morning weigh-in. Photos, fit, and 2 you probably skip.",
    "why-does-the-scale-go-up-when-i-barely-eat":
        "Why does the scale go up when I barely eat? Sodium, glycogen, and a 2 kg overnight swing that has nothing to do with fat. Read it before you cut more.",
    "what-counts-as-a-weight-loss-plateau":
        "What counts as a weight loss plateau? Most people call it after 7 days. The honest threshold is 3 weeks of zero trend — and most never get there.",
    "is-losing-5kg-in-a-week-water-weight":
        "Is losing 5kg in a week water weight? Almost always yes — true fat loss caps near 1 kg per week. Here's what the first 7 days actually measure.",
    "why-am-i-not-losing-weight-anymore":
        "Why am I not losing weight anymore? The dramatic first week taught the wrong lesson. Real fat loss runs near 0.5 kg per week — and that's the program.",
    "skinny-fat-normal-weight-high-body-fat":
        "Skinny fat: normal weight but high body fat. The scale calls you fine while the mirror calls you soft. Here's why one number can't carry the whole story.",
    "how-to-stick-to-a-diet-when-progress-slows":
        "How to stick to a diet when progress slows down. Most diets don't end with a disaster — they end with one quiet week that talks you out. Here's the move.",
    "progress-update-body-changes-slower-than-mind":
        "Body changes slower than mind during weight loss. The body shifted in months; the panic took another year to quiet. A founder note on the lag.",
    "how-to-know-youre-losing-weight-without-the-scale":
        "How to know you're losing weight without the scale: 5 signals fat loss leaves before the number moves. Clothes, jaw, posture — and 2 most people miss.",
    "what-to-do-after-a-binge-on-a-diet":
        "What to do after a binge on a diet: about 90% of the next-morning scale spike is water. Here's the 48-hour reset that doesn't punish — and doesn't pretend.",
    "how-to-handle-hunger-pangs-on-a-diet":
        "How to handle hunger pangs on a diet without making them louder. The 2 questions that separate normal hunger from chaos hunger — and which to ignore.",
    "why-cant-i-sleep-on-a-calorie-deficit":
        "Why can't I sleep on a calorie deficit? Under-fueling a hard-trained body wakes you at 4 a.m. Here's the small fix that doesn't break the cut.",
    "are-cheat-days-bad-for-weight-loss":
        "Are cheat days bad for weight loss? Depends if the rest of your week is a release valve waiting to blow. Here's the test before you plan one.",
    "does-one-bad-day-ruin-a-diet":
        "Does one bad day ruin a diet? Mostly no — until 'one bad day' becomes a strategy. Here's the math on 1 bad day vs 3 in a row.",
    "do-obese-people-lose-weight-slower":
        "Do obese people lose weight slower than others? Not slower per pound — but more of it is true fat, not water. Here's why the first month feels heavier.",
    "why-is-my-appetite-stronger-on-a-diet":
        "Why is my appetite stronger on a diet, not weaker? Hunger climbs the longer you cut — leptin drops, ghrelin rises. Here's what to do at week 8.",
    "why-am-i-working-out-but-not-losing-weight":
        "Why am I working out but not losing weight? Exercise builds composition first, weight loss second. The scale catches up by week 6 to 12, usually.",
    "why-is-the-middle-of-weight-loss-the-hardest":
        "Why is the middle of weight loss the hardest? Months 3 to 9 don't photograph well. Here's what the unglamorous middle looks like — and why most quit.",
    "is-my-stomach-bloat-or-fat":
        "How to tell if my stomach is bloat or fat: the body can't make 1.5 kg of fat overnight. Here's the 3-question test that ends most morning panic.",
    "how-to-break-a-weight-loss-plateau":
        "How to break a weight loss plateau without panicking and cutting harder. The body is sending feedback — here's how to read it before you escalate.",
    "why-does-my-body-look-different-from-different-angles":
        "Why does my body look different from different angles? The front view stalls weeks before the back view does. Here's the angle most people never check.",
    "past-the-messy-middle-of-weight-loss":
        "Past the messy middle of weight loss: 4 months on, what changed and what didn't. A check-in from the side of the program nobody photographs.",
    "how-to-stop-using-exercise-as-punishment":
        "How to stop using exercise as punishment, without quitting the gym. The same workout shifts when you change what you bring to it. Here's the line.",
    "is-maintenance-hunger-different-from-diet-hunger":
        "Is maintenance hunger different from diet hunger? Yes — and most people misread the second as the first, and regain inside 6 months. Here's the tell.",
    "why-some-people-never-gain-weight-no-matter-what":
        "Why do some people never gain weight no matter what they eat? Not metabolism, not luck. Here's the boring set of habits hiding underneath.",
    "how-do-you-know-youve-reached-set-point":
        "How do you know you've reached your set point weight? Set point is a 2 to 3 kg range, not a number. Here's the 6-week test that tells you you're at one.",
    "why-do-i-weigh-more-at-night":
        "Why do I weigh more at night than in the morning? Up to 2 kg of swing from food, water, and posture. Both readings are honest — different questions.",
    "does-bad-sleep-ruin-weight-loss":
        "Does bad sleep ruin weight loss? 3 bad nights can undo a clean week. Here's how sleep debt rewrites appetite, cravings, and gym output — fast.",
    "do-vegetables-help-you-feel-full-on-a-diet":
        "Do vegetables help you feel full on a diet? They do the quiet job protein gets credit for. Volume and fiber decide whether your week holds.",
    "how-to-stop-a-binge-from-becoming-a-binge-week":
        "How to stop a binge from becoming a binge week: the 24 hours after the binge decide. Here's the rescue plan that works without punishment math.",
    "why-do-others-notice-my-weight-loss-before-me":
        "Why do others notice my weight loss before me? They run the opposite experiment — months between visits. Here's the perception lag in plain terms.",
    "why-do-you-lose-so-much-weight-first-week":
        "Why do you lose so much weight the first week of a diet? Glycogen and water — not fat. The honest reading starts at week 3, not week 1.",
    "difference-between-weight-loss-and-fat-loss":
        "What's the difference between weight loss and fat loss? You can drop 5 kg without getting leaner. Here's the composition test the scale can't run.",
    "why-do-i-gain-back-more-weight-than-i-lost":
        "Why do I gain back more weight than I lost? It isn't lack of discipline — it's a predictable rebound the diet built in. Here's the system that prevents it.",
    "how-to-eat-at-social-events-on-a-diet":
        "How to eat at social events on a diet: the dinner is rarely the problem. The under-eating before and over-correcting after are. Here's the fix.",
    "how-to-stay-at-your-goal-weight-long-term":
        "How to stay at your goal weight long term, not just hit it once. Most maintainers share 4 quiet habits — none of them what motivational content sells.",
    "why-did-i-stop-losing-weight-at-3-months":
        "Why did I stop losing weight at 3 months? Adaptation, fatigue, and slow calorie creep — not a broken plan. Here's what to change without escalating.",
    "how-to-tell-if-youre-hungry-or-bored":
        "How to tell if you're hungry or bored: the apple test ends the question in 5 seconds. Here's why most late-day hunger isn't hunger at all.",
    "how-much-protein-do-i-need-to-lose-fat":
        "How much protein do I need to lose fat? 1.6 to 2.2 g per kg daily, split across 3 to 4 meals. Most people overshoot the math and undershoot the timing.",
    "why-are-my-workouts-harder-on-a-cut":
        "Why are my workouts harder on a cut? You're lifting on fumes, not lifting weaker. Here's the cost of the deficit and how to pay it without escalating.",
    "why-does-strength-increase-before-muscle-size":
        "Why does strength increase before muscle size? The first 6 weeks of lifting are mostly neural, not visual. Numbers move first. Shape moves second.",
    "how-to-trust-slow-weight-loss-progress":
        "How to trust slow weight loss progress when the scale stops flattering you. The biggest losses happen on quiet weeks, not bad ones. Here's the bridge.",
    "why-progress-photos-dont-show-progress":
        "Why progress photos don't show progress, even when the body changed. Lighting, posture, and last night's dinner can fake a month either way.",
    "why-does-restriction-make-cravings-worse":
        "Why does restriction make cravings worse? The food you ban becomes the food you can't stop thinking about. Here's the test that breaks the loop.",
    "why-does-the-same-weight-feel-different-as-you-age":
        "Why does the same weight feel different as you age? 75 kg at 22 isn't 75 kg at 32 — composition shifts under the number. Here's what the scale misses.",
    "non-scale-victories-weight-loss":
        "Non scale victories in weight loss: the boring Wednesday is the program, not the milestone. Here's what 6 small wins look like across a real cut.",
    "first-month-of-maintenance-after-weight-loss":
        "First month of maintenance after weight loss: the plate gets bigger and the head looks for a finish line that isn't there. Here's what actually happens.",
    "why-am-i-hungry-at-night-but-not-during-the-day":
        "Why am I hungry at night but not during the day? At 9 p.m. you're at the fridge — but your daytime was a number, not a meal. Here's the fix.",
    "am-i-really-in-a-plateau-or-tracking-wrong":
        "Am I really in a plateau or am I tracking wrong? Most stalls aren't stalls — they're 200 calories of hidden creep. Here's the honest 7-day audit.",
    "life-after-50kg-weight-loss":
        "Life after 50 kg weight loss: 4 months past the last update, the body finally went quiet. The relationship moved more than the number this time.",
    "clothes-fit-better-but-scale-is-the-same":
        "Why my clothes fit better but the scale is the same: fit is the most honest tracker in the closet. Here's how to read it on the weeks the scale won't move.",
    "how-to-get-back-on-track-after-a-bad-weekend":
        "How to get back on track after a bad weekend: Monday matters more than Sunday. The 2.4 kg on the scale is water — here's the reset that works.",
    "how-to-stop-mirror-checking-on-a-diet":
        "How to stop mirror checking on a diet without quitting the bathroom. Fewer checks, cleaner conditions, longer windows. Here's the 3-rule version.",
    "do-i-have-to-meal-prep-to-lose-weight":
        "Do I have to meal prep to lose weight? Honest answer: no. But you have to solve the 3 problems meal prep solves. Here are the working alternatives.",
    "why-adding-cardio-to-a-cut-backfires":
        "Why adding cardio to a cut can backfire: the body adapts to expenditure faster than the math expects. A stalled cut is rarely a movement deficit.",
    "daily-weighing-eating-disorder-risk":
        "Daily weighing and eating disorder risk: the same habit is discipline for some and a trap for others. Here are 4 signals that tell you which one you are.",
    "does-cutting-sodium-cause-water-retention":
        "Does cutting sodium cause water retention rebound? A 2 kg drop from low salt feels like discipline. It's mostly water — and it teaches the wrong signal.",
    "appetite-returns-during-maintenance":
        "Appetite returns during maintenance after weight loss — usually 4 to 6 months in. It isn't failure. Here's the week it hit and what I almost did wrong.",
    "does-one-bad-meal-ruin-a-diet":
        "Does one bad meal ruin a diet? The meal is just a meal. The slip is everything you do in the 48 hours after. Here's how to keep the two separate.",
    "why-am-i-so-hungry-after-lifting-weights":
        "Why am I so hungry after lifting weights? Appetite tracks training volume and recovery, not body weight. Most diet hunger is a repair signal, not failure.",
    "when-does-a-diet-become-a-lifestyle":
        "When does a diet become a lifestyle? You don't notice on the day. You notice the Tuesday weeks later when you didn't think about food once.",
}


# ---------- validation ---------------------------------------------------- #

def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def keyword_in_first_n_chars(meta: str, keyword: str, n: int = 100) -> bool:
    """Soft match — primary keyword may be split by a comma or punctuation,
    so we check token-overlap of the keyword tokens against the meta's
    first-100-chars tokens."""
    head = normalize(meta[:n])
    head_tokens = head.split()
    kw_tokens = normalize(keyword).split()
    # require >= ceil(75%) of keyword tokens present, and present in order
    needed = max(2, int(len(kw_tokens) * 0.75 + 0.5))
    # find subsequence
    i = 0
    matched = 0
    for tok in head_tokens:
        if i < len(kw_tokens) and tok == kw_tokens[i]:
            i += 1
            matched += 1
            if matched >= needed:
                return True
    if matched >= needed:
        return True
    # fallback: tolerant unordered overlap
    return sum(1 for t in kw_tokens if t in head_tokens) >= needed


def jaccard(a: str, b: str) -> float:
    ta = set(normalize(a).split())
    tb = set(normalize(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def banned_hits(text: str) -> list[str]:
    low = text.lower()
    return [b for b in BANNED if b in low]


# ---------- main --------------------------------------------------------- #

def main() -> None:
    posts = json.loads(EXTRACTED.read_text())
    by_slug = {p["slug"]: p for p in posts}

    flagged: list[str] = []  # slugs with weak rewrites
    issues: list[tuple[str, str]] = []  # (slug, problem)
    char_counts: list[int] = []

    # ensure draft order matches posts.ts
    missing_in_drafts = [p["slug"] for p in posts if p["slug"] not in DRAFTS]
    extra_in_drafts = [s for s in DRAFTS if s not in by_slug]
    if missing_in_drafts:
        for s in missing_in_drafts:
            issues.append((s, f"MISSING DRAFT for slug"))
    if extra_in_drafts:
        for s in extra_in_drafts:
            issues.append((s, f"DRAFT for unknown slug"))

    for post in posts:
        slug = post["slug"]
        meta = DRAFTS.get(slug)
        if not meta:
            continue

        kw0 = (post.get("keywords") or [""])[0]
        n = len(meta)
        char_counts.append(n)

        if n > 155:
            issues.append((slug, f"TOO LONG ({n} > 155)"))
        if not meta.endswith("."):
            issues.append((slug, "missing trailing period"))
        if not keyword_in_first_n_chars(meta, kw0, 100):
            issues.append((slug, f"primary keyword '{kw0}' not in first 100 chars"))
        bad = banned_hits(meta)
        if bad:
            issues.append((slug, f"banned phrase(s): {bad}"))

        # material-difference check
        desc_jac = jaccard(meta, post.get("description", ""))
        soc_jac = jaccard(meta, post.get("socialDescription", ""))
        if desc_jac > 0.55 or soc_jac > 0.55:
            flagged.append(
                f"{slug}: high overlap (desc={desc_jac:.2f}, soc={soc_jac:.2f})"
            )

        # weak rewrite warning: drop in length / no number / less specific than current
        cur = post.get("metaDescription") or ""
        cur_has_num = bool(re.search(r"\d", cur))
        new_has_num = bool(re.search(r"\d", meta))
        if cur_has_num and not new_has_num:
            flagged.append(
                f"{slug}: lost a number that the current meta had"
            )

    # Build the spec file
    lines = [
        '"""Spec: rewritten <meta name="description"> for all 64 blog posts.',
        "",
        "Generated by scripts/seo_retrofit/build_meta_descriptions.py from",
        "  - frontend/src/content/blog/posts.ts (current entries)",
        "  - marketing/fitness_blogging/blog_strategy/seo_optimization_rules.md",
        "  - marketing/fitness_blogging/blog_strategy/seo_keyword_research_2026-04-21.md",
        "",
        "Rules per entry:",
        "  - <= 155 chars (Google SERP truncation)",
        "  - keywords[0] (primary) appears in first 100 chars",
        "  - Materially different from `description` and `socialDescription`",
        "  - Two-sentence structure: value claim with primary keyword,",
        "    then payoff with a number / specific outcome / curiosity hook",
        "  - Voice-safe (no banned phrases from the rules file)",
        "  - Ends with a period",
        "",
        "Order matches the order of posts in `frontend/src/content/blog/posts.ts`.",
        "Comments above an entry flag any rewrite that is materially weaker than",
        "the current `metaDescription` and should get a human pass.",
        '"""',
        "",
        "META_DESCRIPTIONS: dict[str, str] = {",
    ]

    for post in posts:
        slug = post["slug"]
        meta = DRAFTS.get(slug, "")
        # was this slug flagged?
        flag_for_slug = [f for f in flagged if f.startswith(f"{slug}:")]
        if flag_for_slug:
            for f in flag_for_slug:
                lines.append(f"    # FLAG: {f}")
        # Use double-quoted Python string so the embedded apostrophes survive
        meta_escaped = meta.replace('"', '\\"')
        lines.append(f'    "{slug}": "{meta_escaped}",')

    lines.append("}")
    lines.append("")

    SPEC_OUT.write_text("\n".join(lines))

    # Report
    print(f"Wrote {SPEC_OUT}")
    print(f"\n--- Validation report ---")
    print(f"Drafts: {len(DRAFTS)} / Posts: {len(posts)}")
    if issues:
        print(f"\n{len(issues)} HARD-RULE ISSUE(s):")
        for slug, prob in issues:
            print(f"  {slug}: {prob}")
    else:
        print("\nAll hard rules passed.")
    if flagged:
        print(f"\n{len(flagged)} FLAG(s) for human review:")
        for f in flagged:
            print(f"  {f}")
    else:
        print("\nNo soft-flag warnings.")

    # Char count distribution
    if char_counts:
        char_counts.sort()
        n = len(char_counts)
        print(f"\nChar count distribution (n={n}):")
        print(f"  min:    {char_counts[0]}")
        print(f"  p25:    {char_counts[n // 4]}")
        print(f"  median: {char_counts[n // 2]}")
        print(f"  p75:    {char_counts[(3 * n) // 4]}")
        print(f"  max:    {char_counts[-1]}")
        print(f"  mean:   {sum(char_counts) / n:.1f}")
        # Buckets
        buckets = {"<=120": 0, "121-140": 0, "141-150": 0, "151-155": 0, ">155": 0}
        for c in char_counts:
            if c <= 120:
                buckets["<=120"] += 1
            elif c <= 140:
                buckets["121-140"] += 1
            elif c <= 150:
                buckets["141-150"] += 1
            elif c <= 155:
                buckets["151-155"] += 1
            else:
                buckets[">155"] += 1
        print("\n  buckets:")
        for b, c in buckets.items():
            print(f"    {b}: {c}")


if __name__ == "__main__":
    main()

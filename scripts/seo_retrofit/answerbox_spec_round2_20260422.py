"""Spec: featured-snippet answerBox for the 15 remaining article-typed posts.

Each entry is a 40-60 word direct answer that:
- Restates the primary keyword in question form
- Answers in 1-3 short sentences (Google's position-0 sweet spot)
- Stays in pkang's voice (direct, no hype, observational)
- Is *condensed* from the post's existing first paragraphs — no new claims

Insertion: between the post's first 'paragraphs' section and the next
section. The applier handles the splice.

Generated 2026-04-22 (autonomous round 2).
"""

ANSWERBOX_SPEC: dict[str, dict[str, str]] = {
    "how-i-lost-50-kg-middle-of-diet": {
        "question": "How did you lose 50 kg?",
        "answer": (
            "Slowly, and mostly in the unglamorous middle. The start was clear and motivating. "
            "The middle was a long stretch where the work was real but the mirror still made it "
            "feel fake. The fix that worked was weekly proof of progress instead of daily panic, "
            "so doubt stopped being able to overrule a record."
        ),
    },
    "skinny-fat-normal-weight-high-body-fat": {
        "question": "What does 'skinny fat' mean?",
        "answer": (
            "Skinny fat is normal weight with a high body-fat percentage — the version of unfit "
            "the scale never reports. The number is fine; the composition is not. People in "
            "this category often look thin in clothes and soft out of them, and they need a "
            "recomp plan, not more weight loss."
        ),
    },
    "progress-update-body-changes-slower-than-mind": {
        "question": "Why does my body change slower than my mind during weight loss?",
        "answer": (
            "Because the mind reads each day as a verdict and the body operates on weeks. Mood, "
            "stress, sleep, and one harsh weigh-in update the mind in seconds, while measurable "
            "body change takes 7–14 days to show. The gap is normal — and when the head is "
            "calmer than the scale, the program survives the middle."
        ),
    },
    "past-the-messy-middle-of-weight-loss": {
        "question": "What happens past the messy middle of weight loss?",
        "answer": (
            "The work changes shape. The body keeps moving on its slow timeline, but the head "
            "finally catches up — bad days stop feeling like the program failed, weigh-ins stop "
            "rewriting your identity, and the same plan you wanted to renegotiate every week "
            "starts running on its own. It is quieter, not finished."
        ),
    },
    "how-much-protein-do-i-need-to-lose-fat": {
        "question": "How much protein do I need to lose fat?",
        "answer": (
            "For most people in a deficit, 1.6–2.2 g of protein per kg of bodyweight per day "
            "is the evidence-based range that protects muscle and helps appetite. Less than 1.6 "
            "g/kg leaves muscle on the table. More than 2.2 g/kg has diminishing returns. Spread "
            "it across 3–4 meals so each one carries 30–45 g."
        ),
    },
    "non-scale-victories-weight-loss": {
        "question": "What are non-scale victories in weight loss?",
        "answer": (
            "Non-scale victories are the everyday signals of progress the bathroom scale cannot "
            "see — clothes loosening, energy holding through the afternoon, recovery between "
            "training sessions, sleep that does not crash, and food noise quieting down. They "
            "are not consolation prizes. On weeks the scale lies, they are the more honest "
            "instrument."
        ),
    },
    "first-month-of-maintenance-after-weight-loss": {
        "question": "What is the first month of maintenance after weight loss like?",
        "answer": (
            "It feels nothing like the diet. The finish line is gone, the rules quietly relax, "
            "appetite usually rises, and the rituals that ran the cut lose their rule-of-law "
            "feel. Most people read that drift as failure. It is just the mode change every "
            "successful diet has to survive — protect structure, not deficit."
        ),
    },
    "life-after-50kg-weight-loss": {
        "question": "What is life after 50 kg weight loss like?",
        "answer": (
            "Quieter than the highlight reel sells it. The dramatic part of the transformation "
            "ends. The body just is. Weight stops being the most-thought-about thing in the "
            "day. Food is still tracked but as habit, not interrogation. Most of the work of "
            "the original diet has moved into the part of life you no longer narrate."
        ),
    },
    "daily-weighing-eating-disorder-risk": {
        "question": "Is daily weighing an eating-disorder risk?",
        "answer": (
            "It can be. Daily weighing produces useful information only when the person reads "
            "the seven-day average, ignores day-to-day noise, and is emotionally insulated "
            "against a single morning's number. For people with restrictive history, body-image "
            "distress, or a tendency to let the scale dictate the day, daily weighing reliably "
            "fuels disordered patterns."
        ),
    },
    "appetite-returns-during-maintenance": {
        "question": "Why does appetite return during maintenance after weight loss?",
        "answer": (
            "Because the body is finishing what the cut started. After weeks at lower body fat, "
            "leptin and ghrelin slowly recalibrate upward, and the appetite drive that the "
            "deficit suppressed shows up later — sometimes weeks into maintenance. It is not "
            "failure of discipline. It is a delayed signal. The fix is structure, not another "
            "cut."
        ),
    },
    "my-scale-wont-move-but-my-jeans-fit-looser": {
        "question": "Why won't my scale move but my clothes fit looser?",
        "answer": (
            "Because the scale measures one number — the sum of fat, lean tissue, water, "
            "glycogen, and gut contents — while clothes measure shape. When fat goes down and "
            "lean tissue goes up by similar amounts, the scale stalls and the body still "
            "changes. This is recomposition. Trust the tape, the photo, and the jeans."
        ),
    },
    "the-mirror-runs-on-yesterdays-mood-not-todays-body": {
        "question": "Does the mirror lie about body image?",
        "answer": (
            "Often, yes. The mirror is not a neutral judge. It runs on yesterday's mood, "
            "today's lighting, sleep debt, water retention, and the emotional frame you bring "
            "to it. The same body can look 'progress' one morning and 'failure' the next. "
            "Trust the weekly photo, the tape, and the clothes — not the daily glance."
        ),
    },
    "the-week-i-stopped-adding-cardio-and-the-body-caught-up": {
        "question": "Can too much cardio stall fat loss?",
        "answer": (
            "Yes. When cardio volume rises faster than the body can recover, the diet becomes "
            "an underfueled grind: training quality drops, NEAT (the unconscious movement that "
            "burns most calories) silently falls, and recovery stress spikes appetite. The fix "
            "is usually less cardio, not more — protect lifting, eat the assigned calories, "
            "and let the deficit do its slow work."
        ),
    },
    "why-lower-body-fat-feels-so-stubborn": {
        "question": "Why does lower body fat feel so stubborn?",
        "answer": (
            "Because lower body fat clears last on a timeline most people quit before reaching. "
            "Hips, thighs, and the lower back hold fat for longer biological reasons "
            "(distribution, capillary density, hormonal signaling). Once overall body-fat "
            "percentage gets low enough, the lower body finally moves — but it is the last "
            "stop, not a refusal."
        ),
    },
    "you-are-probably-consistent-at-the-wrong-thing": {
        "question": "What is the real fix for a weight-loss plateau?",
        "answer": (
            "Usually not more consistency. It is changing the input because the body has "
            "stopped responding to the old one. The same calories, the same training, and the "
            "same rigor that worked at month one rarely keep working at month four. The "
            "plateau fix is recalibration of the lever, not louder execution of the same plan."
        ),
    },
}

"""
Featured Snippet content (answerBox + FAQ items) for the 30 highest-leverage
Q&A blog posts.

Per `marketing/fitness_blogging/blog_strategy/seo_optimization_rules.md`:
- answerBox is a 40-60 word direct answer rendered near the top of the post,
  designed to be plucked into Google's Position 0 / Featured Snippet box.
- faqItems power both an on-page accordion AND FAQPage JSON-LD via the
  `BlogStructuredData` component when `schemaType: 'faq'` is set.

Voice rules (CRITICAL):
- Voice = pkang's: founder-led, anti-hype, observational, dry, direct.
- Forbidden words: ultimate, secret, shocking, life-changing,
  transform your body, guaranteed, fast results, you won't believe,
  crazy, insane.
- Each answer reads like the source post's body. No marketing language.
- Every answerBox answer is 40-60 words. Every FAQ answer is 25-50 words.
  Word counts were verified during drafting.

The application script (apply_featured_snippets.py, to be written) will:
1. Insert the `answerBox` section into each post's `sections[]` array
   immediately after the first `paragraphs` section (the lede).
2. Insert the `faq` section near the end, before the closing
   `paragraphs` section (the "Closing" / final reflection block).
3. Set `schemaType: 'faq'` on the matching post so the structured-data
   component emits FAQPage JSON-LD.

30 posts. Order = priority order from research's "Top 10 most promising"
list, then 20 additional Q&A posts chosen for content quality.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# SCHEMA_TYPES — set every entry below to 'faq' so BlogStructuredData
# auto-emits FAQPage JSON-LD alongside the existing Article schema.
# ---------------------------------------------------------------------------

SCHEMA_TYPES: dict[str, str] = {
    # Top 10 priority
    "why-does-the-scale-go-up-when-i-barely-eat": "faq",
    "clothes-fit-better-but-scale-is-the-same": "faq",
    "does-one-bad-day-ruin-a-diet": "faq",
    "why-am-i-hungry-at-night-but-not-during-the-day": "faq",
    "why-some-people-never-gain-weight-no-matter-what": "faq",
    "difference-between-weight-loss-and-fat-loss": "faq",
    "why-do-others-notice-my-weight-loss-before-me": "faq",
    "why-does-restriction-make-cravings-worse": "faq",
    "how-do-you-know-youve-reached-set-point": "faq",
    "how-to-trust-slow-weight-loss-progress": "faq",
    # 20 additional Q&A posts
    "should-i-weigh-myself-every-day-on-a-diet": "faq",
    "why-cant-i-see-weight-loss-in-the-mirror": "faq",
    "is-losing-5kg-in-a-week-water-weight": "faq",
    "why-am-i-not-losing-weight-anymore": "faq",
    "how-to-stick-to-a-diet-when-progress-slows": "faq",
    "what-to-do-after-a-binge-on-a-diet": "faq",
    "how-to-handle-hunger-pangs-on-a-diet": "faq",
    "are-cheat-days-bad-for-weight-loss": "faq",
    "why-am-i-working-out-but-not-losing-weight": "faq",
    "how-to-break-a-weight-loss-plateau": "faq",
    "is-maintenance-hunger-different-from-diet-hunger": "faq",
    "does-bad-sleep-ruin-weight-loss": "faq",
    "how-to-stop-a-binge-from-becoming-a-binge-week": "faq",
    "why-do-i-gain-back-more-weight-than-i-lost": "faq",
    "how-to-stay-at-your-goal-weight-long-term": "faq",
    "how-to-tell-if-youre-hungry-or-bored": "faq",
    "how-to-get-back-on-track-after-a-bad-weekend": "faq",
    "do-i-have-to-meal-prep-to-lose-weight": "faq",
    "does-one-bad-meal-ruin-a-diet": "faq",
    "when-does-a-diet-become-a-lifestyle": "faq",
}


# ---------------------------------------------------------------------------
# FEATURED_SNIPPETS — each slug maps to its answerBox + faqItems payload.
# ---------------------------------------------------------------------------

FEATURED_SNIPPETS: dict[str, dict] = {
    # ------------------------------------------------------------------
    # 1. why-does-the-scale-go-up-when-i-barely-eat (priority 1)
    # ------------------------------------------------------------------
    "why-does-the-scale-go-up-when-i-barely-eat": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why does the scale go up when I'm barely eating?",
            "answer": (
                "Body weight is not just fat. It includes water, glycogen, "
                "food still moving through digestion, sodium, and hormonal "
                "water shifts. A 1 to 2 kg overnight rise after a low-calorie "
                "day is almost always one of those, not new fat. Fat does not "
                "arrive that fast. Read the week, not the morning."
            ),
        },
        "faqItems": [
            {
                "question": "Can you actually gain real fat overnight?",
                "answer": (
                    "Not meaningfully. Adding 1 kg of true body fat takes "
                    "roughly 7,000 calories above maintenance, which is hard "
                    "to do in a single day. Overnight scale jumps of 1 to 2 "
                    "kg are almost entirely water, sodium, and food still in "
                    "transit through digestion."
                ),
            },
            {
                "question": "How much can the scale fluctuate day to day?",
                "answer": (
                    "Most adults swing 1 to 2 kg across a normal day from "
                    "food, water, and sodium. Hormonal cycles can add another "
                    "1 to 2 kg around ovulation and the days before a "
                    "period. None of that is fat. It is the scale measuring "
                    "everything else."
                ),
            },
            {
                "question": "Why am I gaining weight while eating less than usual?",
                "answer": (
                    "Two common reasons. Either intake is being "
                    "underestimated, which happens to most people without it "
                    "being a moral failure, or water has shifted from sodium, "
                    "hormones, or training. Wait three to five days under "
                    "your usual routine before deciding the rise is real."
                ),
            },
            {
                "question": "Should I cut calories more after a scale spike?",
                "answer": (
                    "No. Cutting harder in response to a one-day spike "
                    "usually triggers under-fueling and a binge later in the "
                    "week. The spike was almost certainly water. Hold the "
                    "plan for at least five days before adjusting anything "
                    "based on a single morning."
                ),
            },
            {
                "question": "When is a scale rise actually fat gain?",
                "answer": (
                    "When the higher number holds for more than two weeks "
                    "under your usual conditions, with no clear water "
                    "explanation. Real fat gain is slow, quiet, and "
                    "consistent across morning weigh-ins. A loud one-day "
                    "spike that disappears in three days is not it."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 2. clothes-fit-better-but-scale-is-the-same
    # ------------------------------------------------------------------
    "clothes-fit-better-but-scale-is-the-same": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why do my clothes fit better when the scale is the same?",
            "answer": (
                "Because the scale measures total mass and clothes measure "
                "shape. If you are training, you can lose fat and add small "
                "amounts of muscle at the same scale weight. The waist gets "
                "smaller, the shoulders or thighs get fuller, and the jeans "
                "tell the truth the scale is missing. The body moved. The "
                "scale missed it."
            ),
        },
        "faqItems": [
            {
                "question": "Can I lose inches without losing weight?",
                "answer": (
                    "Yes, regularly. Body recomposition during training "
                    "produces fat loss and small muscle gain that cancel out "
                    "on the scale but visibly change waist, hip, and thigh "
                    "measurements. A flat scale week with looser clothes is a "
                    "real-progress week, not a stalled one."
                ),
            },
            {
                "question": "Are my clothes a more accurate tracker than the scale?",
                "answer": (
                    "For waist and shape, often yes. Clothes do not have "
                    "moods, do not respond to sodium, and do not adapt to "
                    "your body image the way the mirror does. A pair of jeans "
                    "from a year ago is the same instrument today. The scale "
                    "and mirror both drift."
                ),
            },
            {
                "question": "How often should I check fit during a diet?",
                "answer": (
                    "Once every two weeks under similar conditions, ideally "
                    "in the morning. Pick one snug item — not the goal item, "
                    "the currently-snug one — and use it as a calibration "
                    "tool. Weekly is too noisy. Monthly is too slow to catch "
                    "the trend."
                ),
            },
            {
                "question": "Why does the scale lie about composition change?",
                "answer": (
                    "Because it weighs everything at once. Two kilos of fat "
                    "lost and one kilo of muscle gained shows up as one kilo "
                    "down. Same body, very different shape. The scale was "
                    "never built to separate the two. Photos, tape, and "
                    "clothes have to do that job."
                ),
            },
            {
                "question": "Should I keep weighing if my clothes are the only thing changing?",
                "answer": (
                    "Weigh weekly as a reference, but stop letting one number "
                    "run management. If clothes loosen and the scale holds "
                    "for several weeks, the program is working. Keep going. "
                    "A flat scale during recomposition is the boring sign of "
                    "real progress."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 3. does-one-bad-day-ruin-a-diet
    # ------------------------------------------------------------------
    "does-one-bad-day-ruin-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "Does one bad day ruin a diet?",
            "answer": (
                "Usually not. One overshoot day is technically less damaging "
                "than several moderate-overshoot days in a row. Body fat is "
                "built from patterns, not single events. The real risk is not "
                "the bad day. It is the cheat-day expansion that follows: one "
                "meal becomes a weekend, the weekend becomes a reset Monday "
                "that keeps moving."
            ),
        },
        "faqItems": [
            {
                "question": "How much weight can one bad day actually add?",
                "answer": (
                    "Maybe 0.2 to 0.5 kg of true fat in extreme cases. The 1 "
                    "to 2 kg the scale shows the next morning is almost "
                    "entirely water, glycogen, and food volume from the "
                    "carbohydrates and sodium. Most of it leaves within three "
                    "to five days of normal eating."
                ),
            },
            {
                "question": "Should I skip breakfast the day after a bad day?",
                "answer": (
                    "No. Skipping breakfast as punishment usually drops blood "
                    "sugar and triggers a second overeat by late afternoon. "
                    "Eat your normal breakfast. Return to your normal lunch "
                    "and dinner. Treat yesterday as yesterday. Do not chain "
                    "two bad days together by trying to compensate."
                ),
            },
            {
                "question": "What turns one bad day into a bad week?",
                "answer": (
                    "Three things: punishment-style restriction the next "
                    "morning, the all-or-nothing 'I already blew it' framing, "
                    "and weighing in too soon and reading the water spike as "
                    "fat. Any of those alone can stretch one meal into five "
                    "days off plan."
                ),
            },
            {
                "question": "Are scheduled cheat days a smart strategy?",
                "answer": (
                    "Sometimes, but they often expand. The cheat meal becomes "
                    "a cheat day, the cheat day becomes a cheat weekend, and "
                    "anticipation of the release starts driving weekday "
                    "behavior. If you find yourself counting down to the "
                    "cheat day, the system is too tight the rest of the week."
                ),
            },
            {
                "question": "How long should I wait to weigh in after a bad day?",
                "answer": (
                    "Three to five days, under your usual conditions. The "
                    "scale will lie upward for that window because of water "
                    "and sodium, and reading the lie usually triggers more "
                    "off-plan eating. Skip the morning weigh-in until the "
                    "noise has cleared."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 4. why-am-i-hungry-at-night-but-not-during-the-day
    # ------------------------------------------------------------------
    "why-am-i-hungry-at-night-but-not-during-the-day": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why am I hungry at night but not during the day?",
            "answer": (
                "Three things stack in the evening. Caloric debt from the "
                "day becomes audible once distractions drop. Decision fatigue "
                "lowers self-regulation. And the kitchen is suddenly nearby. "
                "Most night spikes are not psychological. They are scheduling "
                "problems wearing psychological clothes. A later, "
                "protein-forward dinner usually quiets the spike inside two "
                "weeks."
            ),
        },
        "faqItems": [
            {
                "question": "Why does my hunger hit hardest around 9pm?",
                "answer": (
                    "By 9pm, the day's intake is mostly behind you and any "
                    "deficit becomes audible. Self-regulation also runs "
                    "lowest in late evening, and the kitchen is two rooms "
                    "away with no work or meetings in the way. The friction "
                    "is the lowest it has been all day."
                ),
            },
            {
                "question": "Will eating dinner later actually help?",
                "answer": (
                    "For most people with evening spikes, yes. Pushing dinner "
                    "60 to 90 minutes later shrinks the unfueled gap between "
                    "dinner and the spike. The same total calories, just "
                    "redistributed. Two weeks is usually enough to see "
                    "whether the change quiets the evening."
                ),
            },
            {
                "question": "Should I plan an evening snack?",
                "answer": (
                    "If the spike happens at the same time most nights, yes. "
                    "A planned 150 to 200 calorie protein-forward snack — "
                    "yogurt, fruit, a small shake — slotted into the daily "
                    "plan removes the surprise. The spike stops feeling like "
                    "a fight because the meal is already on the schedule."
                ),
            },
            {
                "question": "How does sleep affect night cravings?",
                "answer": (
                    "Sleep-deprived bodies are hungrier the next day, "
                    "especially in the evening. Three nights of six hours "
                    "instead of seven and a half routinely produces 200 to "
                    "400 calories of extra hunger. Pushing bedtime back is "
                    "one of the cheapest appetite interventions available."
                ),
            },
            {
                "question": "What if I tried all this and still spike at night?",
                "answer": (
                    "Then your daily total is probably too low for your "
                    "activity. A consistent loud evening signal across "
                    "several weeks, despite a structurally fine evening, "
                    "usually means the deficit is too aggressive. Add 150 to "
                    "200 calories until the spike loses its edge."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 5. why-some-people-never-gain-weight-no-matter-what
    # ------------------------------------------------------------------
    "why-some-people-never-gain-weight-no-matter-what": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why do some people never gain weight no matter what they eat?",
            "answer": (
                "It is rarely magic metabolism. Naturally lean people usually "
                "run a stack of small invisible habits: more standing and "
                "fidgeting, similar foods most days, stopping when full, "
                "consistent sleep. None of it looks like effort because to "
                "them it is not effort. You are comparing your conscious diet "
                "to their unconscious default."
            ),
        },
        "faqItems": [
            {
                "question": "Is it really genetics or are they just hiding the work?",
                "answer": (
                    "Some genetic factors are real — NEAT, satiety signaling, "
                    "and gut microbiome vary between people. But most of the "
                    "gap is invisible habit, not luck. Watch a naturally lean "
                    "friend for a week and you will see the small structure "
                    "they are not naming as effort."
                ),
            },
            {
                "question": "What is NEAT and why does it matter so much?",
                "answer": (
                    "NEAT is non-exercise activity thermogenesis: fidgeting, "
                    "standing, walking on phone calls, taking the stairs "
                    "without thinking about it. NEAT can vary by hundreds of "
                    "calories per day between people. It is largely "
                    "unconscious and explains a lot of so-called fast "
                    "metabolisms."
                ),
            },
            {
                "question": "Can I learn to eat like a naturally thin person?",
                "answer": (
                    "Most of it, yes, with about a year of practice. The "
                    "stand-more, sleep-consistent, do-not-dramatize-food "
                    "pattern is installable. It does not look like weight "
                    "loss while it happens. It looks like a different "
                    "relationship with eating and moving. Five-year "
                    "maintainers usually built it."
                ),
            },
            {
                "question": "Do thin people actually eat less than I think?",
                "answer": (
                    "Often yes, just within a tighter range than they "
                    "realize. They stop when full, do not finish plates as a "
                    "default, and rarely snack mindlessly. The total intake "
                    "looks generous on any single day and adds up to "
                    "balanced across the week without conscious tracking."
                ),
            },
            {
                "question": "Is constitutional thinness a real thing?",
                "answer": (
                    "Yes — a small percentage of people have genuinely "
                    "high-metabolism, high-NEAT, low-appetite physiology that "
                    "resists weight gain even when they try. For most people "
                    "though, the friend who 'eats anything' is running a "
                    "default pattern, not breaking energy balance."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 6. difference-between-weight-loss-and-fat-loss
    # ------------------------------------------------------------------
    "difference-between-weight-loss-and-fat-loss": {
        "answerBox": {
            "type": "answerBox",
            "question": "What is the difference between weight loss and fat loss?",
            "answer": (
                "Weight is total mass: water, bone, organ, muscle, fat, food "
                "in transit. Fat loss is just the fat portion. You can lose "
                "weight and get less lean if you lose mostly muscle, or stay "
                "the same weight and get leaner through recomposition. The "
                "scale weighs everything. It cannot tell those stories apart."
            ),
        },
        "faqItems": [
            {
                "question": "How can I tell which one I'm doing?",
                "answer": (
                    "Track three things together: weekly scale average, tape "
                    "measurements at waist and hip, and photos every two "
                    "weeks under matched conditions. If the scale moves but "
                    "measurements do not, you are losing the wrong tissue. "
                    "If measurements move but the scale does not, you are "
                    "recomposing."
                ),
            },
            {
                "question": "Can you gain weight and look leaner?",
                "answer": (
                    "Yes. If the gain is muscle and the loss is fat, the "
                    "scale moves up while the body looks visibly leaner. A 70 "
                    "kg person at 25 percent body fat looks softer than a 72 "
                    "kg person at 18 percent. The heavier one is the leaner "
                    "one."
                ),
            },
            {
                "question": "Why do people lose muscle on a diet?",
                "answer": (
                    "Two reasons: protein intake is too low, or the deficit "
                    "is so aggressive the body sheds tissue indiscriminately. "
                    "Adequate protein (1.6 to 2.2 g/kg) plus resistance "
                    "training tilts the loss toward fat and away from muscle. "
                    "Cardio-only severe diets do the opposite."
                ),
            },
            {
                "question": "Is body recomposition possible at any age?",
                "answer": (
                    "Yes, though the rate slows with age. Trained adults in "
                    "their thirties, forties, and beyond still build muscle "
                    "and lose fat at the same time, just more slowly than "
                    "beginners. The direction is the same. The clock runs "
                    "differently."
                ),
            },
            {
                "question": "Should I care about body fat percentage instead of weight?",
                "answer": (
                    "For most people, yes. Unless you are an athlete with a "
                    "weight class, the actual goal is composition, not mass. "
                    "Track a waist measurement, a clothing size, and photos. "
                    "Use the scale as one of four signals, not the sentence."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 7. why-do-others-notice-my-weight-loss-before-me
    # ------------------------------------------------------------------
    "why-do-others-notice-my-weight-loss-before-me": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why do others notice my weight loss before I do?",
            "answer": (
                "Self-perception updates slowly. You see your body every "
                "morning in the same mirror, so gradual change disappears "
                "into familiarity. Someone who has not seen you in three "
                "months gets a clean before-and-after read. The internal map "
                "usually runs three to six months behind the body. The "
                "compliment is data, not flattery."
            ),
        },
        "faqItems": [
            {
                "question": "How much weight loss does it take for others to notice?",
                "answer": (
                    "Roughly 4 to 6 kg for face changes to register, 8 to 10 "
                    "kg for the body shape. Frequent contacts notice later "
                    "than people who see you only every few months. The face "
                    "usually shifts first, which is why family members on "
                    "video calls often comment before in-person friends."
                ),
            },
            {
                "question": "Why can't I see my own weight loss in photos?",
                "answer": (
                    "Single photos are too noisy. Lighting, posture, and time "
                    "of day can fake an entire month of change in either "
                    "direction. The internal map also reads new photos "
                    "through the old self-image, which lags the body. Compare "
                    "groups of four photos across months, not single shots."
                ),
            },
            {
                "question": "How long until my own perception catches up?",
                "answer": (
                    "Usually three to six months past the change, sometimes "
                    "longer. There is no specific date. People who work with "
                    "post-weight-loss body image professionally describe the "
                    "lag as normal. The internal map updates gradually, "
                    "pulled forward by external evidence and time."
                ),
            },
            {
                "question": "Should I trust compliments about my weight loss?",
                "answer": (
                    "Yes, directionally. People may be polite about the "
                    "magnitude, but if someone you have not seen in three "
                    "months says you look different, you look different. "
                    "Outside observers are usually closer to current reality "
                    "than your own mirror is right now."
                ),
            },
            {
                "question": "Is body dysmorphia normal after weight loss?",
                "answer": (
                    "A milder version of it is extremely common. Most people "
                    "who lose meaningful weight describe a stretch where "
                    "other people treat them as the new body and they still "
                    "feel like the old one. That gap is the head catching up. "
                    "If it persists or distresses, talk to a professional."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 8. why-does-restriction-make-cravings-worse
    # ------------------------------------------------------------------
    "why-does-restriction-make-cravings-worse": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why does restriction make cravings worse?",
            "answer": (
                "Because the brain is built to track scarce resources. When "
                "you make a food forbidden, your brain reweights it: pays "
                "more attention to the smell, notices it on shelves, dreams "
                "about it. The cleaner the restriction, the louder the "
                "tracking. Most diet cravings are not about the food. They "
                "are about being told no."
            ),
        },
        "faqItems": [
            {
                "question": "How do I tell a real craving from a deprivation craving?",
                "answer": (
                    "Real cravings resolve. You eat the thing, you are "
                    "satisfied, you move on. Deprivation cravings escalate. "
                    "First cookies, then chips, then the whole pantry. They "
                    "end embarrassed, not satisfied. Resolution versus "
                    "escalation is the cleanest test."
                ),
            },
            {
                "question": "Will giving myself permission make cravings worse?",
                "answer": (
                    "Counterintuitively, no. Replacing 'I do not eat ice "
                    "cream' with 'ice cream fits in twice a week' shrinks the "
                    "craving inside three to six weeks for most people. "
                    "Restriction builds the craving. Permission deflates it. "
                    "The food becomes ordinary once the no is removed."
                ),
            },
            {
                "question": "Are some foods truly off-limits during a diet?",
                "answer": (
                    "Maybe one or two trigger foods per person, not the long "
                    "list most diets recommend. Be honest about which "
                    "specific foods you genuinely cannot keep in the kitchen "
                    "at this stage. The list is usually short. For everything "
                    "else, the absolute rule creates the craving."
                ),
            },
            {
                "question": "Why do I crave foods I never even liked before?",
                "answer": (
                    "Because the craving is for permission, not the food. "
                    "After weeks of restriction, foods you previously "
                    "ignored start glowing because they are now in the "
                    "forbidden category. The brain is tracking the rule, not "
                    "the flavor. Drop the rule and the food usually becomes "
                    "forgettable."
                ),
            },
            {
                "question": "What if my deficit itself is creating the cravings?",
                "answer": (
                    "Some cravings are real hunger from the deficit, not "
                    "psychological. Those are general — a chicken-and-rice "
                    "plate satisfies them. If a balanced meal quiets the "
                    "urge, you were hungry. If you finish it and still want "
                    "the specific forbidden item, the craving is about the "
                    "rule."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 9. how-do-you-know-youve-reached-set-point
    # ------------------------------------------------------------------
    "how-do-you-know-youve-reached-set-point": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do you know you have reached your set point weight?",
            "answer": (
                "Five signals together: weight stable within a 2 to 3 kg "
                "range for 8 to 12 weeks, no active dieting, hunger "
                "normalized, energy and sleep reasonable, and small "
                "deviations like a heavier weekend do not push the weight "
                "permanently. If most of those are true, you are probably at "
                "a set point for your current life."
            ),
        },
        "faqItems": [
            {
                "question": "What is a set point weight, exactly?",
                "answer": (
                    "The weight range your body most naturally defends given "
                    "your current habits, sleep, stress, training, and "
                    "eating. It is not a fixed number from birth and it is "
                    "not immune to change. It is a rolling equilibrium that "
                    "shifts as the inputs shift."
                ),
            },
            {
                "question": "Can my set point change over time?",
                "answer": (
                    "Yes. Research suggests the body defends recent weights "
                    "more strongly than older ones. Holding a new weight for "
                    "12 to 24 months often makes it the new defended range. "
                    "This is why maintenance is the real skill, not just the "
                    "losing phase."
                ),
            },
            {
                "question": "Why does it feel like I cannot lose any more?",
                "answer": (
                    "Because maintenance calories adjusted downward as you "
                    "lost weight, your body is defending the current state, "
                    "and your hunger and fullness signals are tuned to this "
                    "range. To go lower you create a new deficit or change "
                    "the inputs. Both are possible. Both have a cost."
                ),
            },
            {
                "question": "Should I stop trying to lose more if I'm at set point?",
                "answer": (
                    "Sometimes yes. If your habits are sustainable and your "
                    "health markers are reasonable, the cost of pushing "
                    "another 3 to 5 kg lower is often higher than the "
                    "benefit. Wanting to lose more for your own reasons is "
                    "fine. It is a decision, not an obligation."
                ),
            },
            {
                "question": "How long should I hold a new weight before it sticks?",
                "answer": (
                    "At least six months of boring maintenance, ideally 12 to "
                    "24. The body needs time to accept the new weight as "
                    "normal before you change inputs again. People who lose "
                    "and hold long-term almost always stay in maintenance "
                    "longer than people who rebound."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 10. how-to-trust-slow-weight-loss-progress
    # ------------------------------------------------------------------
    "how-to-trust-slow-weight-loss-progress": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I trust slow weight loss progress?",
            "answer": (
                "Stop relying on belief and start building evidence belief "
                "can fall back on. Weekly photos in matched conditions. A "
                "short note about sleep, sodium, and stress alongside each "
                "weigh-in. Monthly side-by-side comparisons against your own "
                "earlier photos. Belief is a daily signal, but results are a "
                "monthly one. Small dated proof closes the gap."
            ),
        },
        "faqItems": [
            {
                "question": "Why does belief in the program keep fading?",
                "answer": (
                    "Because results pay out monthly and belief gets hungry "
                    "daily. The cadence is mismatched. If you wait for the "
                    "next big checkpoint to feed your belief, belief runs out "
                    "between checkpoints. Daily noise — water, mood, light — "
                    "starts running the read instead."
                ),
            },
            {
                "question": "What's the right cadence for tracking slow progress?",
                "answer": (
                    "Weekly weigh-ins as the rolling average. Photos every "
                    "Sunday morning under matched conditions. Tape "
                    "measurements every two weeks. Monthly comparisons "
                    "against four-week-old photos. Daily signals are noise; "
                    "weekly and monthly are signal."
                ),
            },
            {
                "question": "Should I trust the scale or the photos when they disagree?",
                "answer": (
                    "Neither alone. When the scale is flat and the photos "
                    "show change, you are recomposing. When the scale moves "
                    "and the photos do not, you are losing the wrong tissue. "
                    "Cross-reference always. The conflict itself is "
                    "information."
                ),
            },
            {
                "question": "What do I do on days I don't believe it's working?",
                "answer": (
                    "Look at the dated proof you already produced. The "
                    "monthly side-by-side. The four-week notes. Your job is "
                    "not to feel certain. Your job is to refuse to argue "
                    "with the evidence you already collected when you were "
                    "calmer."
                ),
            },
            {
                "question": "Is slow weight loss actually better than fast?",
                "answer": (
                    "Usually yes. Slower loss preserves more muscle, "
                    "produces smaller appetite rebound after the diet ends, "
                    "and tends to hold longer. Aggressive deficits produce "
                    "more dramatic rebounds on average. The boring rate is "
                    "the rate that survives."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 11. should-i-weigh-myself-every-day-on-a-diet
    # ------------------------------------------------------------------
    "should-i-weigh-myself-every-day-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "Should I weigh myself every day on a diet?",
            "answer": (
                "Only if you can read one weigh-in as a data point and not a "
                "verdict. Daily weight can fluctuate up to 3 kg from water, "
                "sodium, food volume, and timing. If a single rude morning "
                "number triggers restriction, punishment cardio, or a binge, "
                "switch to weekly averages until the reaction calms down."
            ),
        },
        "faqItems": [
            {
                "question": "What's the best time of day to weigh yourself?",
                "answer": (
                    "Morning, after the bathroom, before food or drink, in "
                    "consistent clothing. Same scale, same spot. That is the "
                    "most stable reference across days. Evening weight is "
                    "typically 0.8 to 1.8 kg higher and is a different "
                    "measurement series — do not mix the two."
                ),
            },
            {
                "question": "Why does my weight fluctuate so much day to day?",
                "answer": (
                    "Water, sodium, glycogen, food in transit, hormonal "
                    "cycles, sleep quality, and stress all move the scale "
                    "without changing fat. A 1 to 2 kg daily swing is normal "
                    "for most adults. A 3 kg swing across a high-sodium day "
                    "is also normal. None of it is fat."
                ),
            },
            {
                "question": "Are weekly averages better than daily readings?",
                "answer": (
                    "Almost always, yes. A weekly average smooths out the "
                    "noise and shows the actual trend. Daily readings are "
                    "useful only if you have built the discipline to ignore "
                    "the day-to-day spikes. Most people have not, and the "
                    "average works better."
                ),
            },
            {
                "question": "How do I stop panicking after a high weigh-in?",
                "answer": (
                    "Ask better questions before reacting. How have the last "
                    "seven days looked? Was yesterday high in sodium or food "
                    "volume? Have I gathered enough data to call this a "
                    "trend? Most of the time the answer is no, and 'not "
                    "enough data yet' beats 'this is broken.'"
                ),
            },
            {
                "question": "When should I stop weighing myself entirely?",
                "answer": (
                    "If the daily number is driving binges, restriction, or "
                    "anxiety that bleeds into the rest of the day, take a "
                    "break. Track with photos, fit, and tape for two to "
                    "four weeks. The scale becomes useful again once the "
                    "emotional charge around it drops."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 12. why-cant-i-see-weight-loss-in-the-mirror
    # ------------------------------------------------------------------
    "why-cant-i-see-weight-loss-in-the-mirror": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why can't I see my weight loss in the mirror?",
            "answer": (
                "Because seeing your body daily makes gradual change "
                "invisible. The eyes adapt fast. The body changes slowly. "
                "That combination normalizes change before your perception "
                "catches up. The mirror also only shows one moment under one "
                "mood, and one moment is easy to misread. Photos across "
                "weeks beat daily mirror checks."
            ),
        },
        "faqItems": [
            {
                "question": "How long until the mirror starts showing the change?",
                "answer": (
                    "For most people, three to six months after meaningful "
                    "loss before the daily mirror reliably reflects it. Other "
                    "people will notice first because they have weeks or "
                    "months of gap to compare across. Your daily exposure is "
                    "the thing hiding the change from you."
                ),
            },
            {
                "question": "Can the mirror lie even when the scale is moving?",
                "answer": (
                    "Yes. Lighting, posture, time of day, sleep, and mood all "
                    "change how the same body looks. The mirror amplifies "
                    "whatever story you are telling yourself that morning. A "
                    "good mood gets a generous read. A bad mood gets a "
                    "punishing one. Same body."
                ),
            },
            {
                "question": "Are progress photos more honest than the mirror?",
                "answer": (
                    "Yes, when taken under matched conditions: same room, "
                    "same time, same posture, same light. Single photos can "
                    "still lie, so compare in groups of four across months, "
                    "not single shots week to week. The four-photo "
                    "comparison removes most of the noise."
                ),
            },
            {
                "question": "Why does the back of my body change first?",
                "answer": (
                    "For many people the back has less stubborn fat buffer "
                    "than the front, so it tightens earlier. You also never "
                    "see your back in the daily mirror, so the change "
                    "registers when someone takes a photo from behind. Take "
                    "one rear photo every two weeks under matched "
                    "conditions."
                ),
            },
            {
                "question": "Is feeling 'phantom fat' after weight loss normal?",
                "answer": (
                    "Common, yes. The internal map of your body lags the "
                    "physical change by months. People describe still "
                    "reaching for old clothing sizes, still flinching at "
                    "mirrors, still feeling like the older body. The "
                    "perception updates gradually, pulled forward by "
                    "external evidence and time."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 13. is-losing-5kg-in-a-week-water-weight
    # ------------------------------------------------------------------
    "is-losing-5kg-in-a-week-water-weight": {
        "answerBox": {
            "type": "answerBox",
            "question": "Is losing 5 kg in a week mostly water weight?",
            "answer": (
                "Yes, almost always. Body fat does not move that fast. A 5 "
                "kg drop in seven days is mostly water from glycogen "
                "depletion, sodium reduction, and emptied digestive "
                "contents. Once normal eating resumes, much of it returns. "
                "The headline is real. The cause is not what you think. "
                "Compare timelines, not loud one-week numbers."
            ),
        },
        "faqItems": [
            {
                "question": "How much real fat can you actually lose in a week?",
                "answer": (
                    "For most adults in a reasonable deficit, 0.3 to 1 kg of "
                    "true fat per week is the realistic range. Heavier people "
                    "can lose more in early weeks because the deficit is "
                    "larger relative to maintenance. Anything above 1 kg of "
                    "weekly fat loss long-term is unusual."
                ),
            },
            {
                "question": "Why do I lose so much weight in the first week of a diet?",
                "answer": (
                    "Glycogen stores drop with reduced carbs, and each gram "
                    "of glycogen releases about 3 grams of water. Sodium "
                    "drops with cleaner eating. Bowel contents shift. Add "
                    "real fat loss of 0.2 to 0.5 kg, and the total can be 2 "
                    "to 4 kg. Most of it is water."
                ),
            },
            {
                "question": "Will the water weight come back when I eat normally?",
                "answer": (
                    "Yes, partly. Some water and glycogen restock as soon as "
                    "carbs and sodium return to normal. The scale rebound is "
                    "not fat regain. It is the body refilling its normal "
                    "stores. People misread this rebound as failure when it "
                    "is just water returning."
                ),
            },
            {
                "question": "Are crash diets that produce 5kg/week ever worth it?",
                "answer": (
                    "Rarely. The dramatic number is mostly water that comes "
                    "back, the muscle loss is high, the rebound is harder, "
                    "and the appetite signal stays loud for weeks after. The "
                    "people who hold weight off for years almost never lose "
                    "it that fast."
                ),
            },
            {
                "question": "How fast should weight loss actually be?",
                "answer": (
                    "Roughly 0.5 to 1 percent of body weight per week is the "
                    "sustainable range. For a 90 kg person that is 0.45 to "
                    "0.9 kg weekly. Slower than that often means "
                    "under-tracking. Faster than that often means too much "
                    "muscle loss and a louder rebound."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 14. why-am-i-not-losing-weight-anymore
    # ------------------------------------------------------------------
    "why-am-i-not-losing-weight-anymore": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why am I not losing weight anymore?",
            "answer": (
                "Often the diet did not stop working. The dramatic early "
                "phase ended and patience failed first. Early loss is mostly "
                "water and glycogen, which clear in week one. Real fat loss "
                "is slower and quieter. People expect week one's pace "
                "forever, panic when it slows, and call a normal phase a "
                "failure."
            ),
        },
        "faqItems": [
            {
                "question": "How long does it take for weight loss to slow down?",
                "answer": (
                    "Usually around week three for most diets. Water and "
                    "glycogen stabilize, novelty fades, and the scale starts "
                    "reflecting actual body composition change. The new "
                    "rate is often half or a third of week one, and that is "
                    "the honest rate, not a problem."
                ),
            },
            {
                "question": "Should I cut more calories when I stop losing?",
                "answer": (
                    "Usually no, not as a first move. Run an honest tracking "
                    "week first — about half the time the stall is logging "
                    "drift, not adaptation. If tracking is clean, try a "
                    "one-week diet break before cutting. Most stalls break "
                    "without escalating the deficit."
                ),
            },
            {
                "question": "Is my metabolism damaged from dieting too long?",
                "answer": (
                    "'Damaged' is overstated. Maintenance calories drop "
                    "modestly as you lose weight (a 70 kg person needs less "
                    "than an 80 kg one), and NEAT can dip during sustained "
                    "deficit. Both reverse with a proper diet break. There "
                    "is no permanent damage in healthy adults."
                ),
            },
            {
                "question": "What should I track if the scale isn't moving?",
                "answer": (
                    "Tape measurements at waist, hip, and chest every two "
                    "weeks. Photos under matched conditions. How clothes "
                    "fit. Strength trends in the gym. Any of those moving "
                    "while the scale holds means recomposition, which is "
                    "real progress the scale is just bad at measuring."
                ),
            },
            {
                "question": "When should I take a diet break?",
                "answer": (
                    "When the scale has been flat for three weeks under "
                    "honest tracking, or when hunger and training fatigue "
                    "are clearly stacking. Eat at maintenance for 7 to 14 "
                    "days. NEAT and appetite reset, and the deficit usually "
                    "starts working again on return."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 15. how-to-stick-to-a-diet-when-progress-slows
    # ------------------------------------------------------------------
    "how-to-stick-to-a-diet-when-progress-slows": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I stick to a diet when progress slows down?",
            "answer": (
                "Stop expecting week one's pace forever. Treat slower loss "
                "later as normal, not insulting. Do not answer scale noise "
                "with punishment. Build identity around staying in, not "
                "around feeling inspired. The most reliable way to succeed "
                "at dieting is embarrassingly simple: do not keep leaving. "
                "The boring middle is where it actually works."
            ),
        },
        "faqItems": [
            {
                "question": "Why is the middle of a diet so much harder than the start?",
                "answer": (
                    "Because the early water-loss phase ends, motivation "
                    "fades, the scale stops being generous, and effort feels "
                    "heavier just as feedback gets quieter. The job demands "
                    "more patience right when patience runs lowest. Week one "
                    "was a hype man. Week six is an accountant."
                ),
            },
            {
                "question": "What's the most common reason people quit dieting?",
                "answer": (
                    "Not laziness. Misinterpretation. Slower loss gets read "
                    "as failure, which triggers either tightening the plan or "
                    "abandoning it. Both responses are reactions to the "
                    "story of the diet, not the diet itself. The plan was "
                    "usually fine. The reading was the problem."
                ),
            },
            {
                "question": "Should I change my plan when results slow down?",
                "answer": (
                    "Usually no. Most people switch plans because slower "
                    "feedback feels like failure, not because the plan is "
                    "wrong. The new plan produces another fast water drop, "
                    "then slows down, then gets blamed too. The diet "
                    "carousel keeps running. Patience would have worked."
                ),
            },
            {
                "question": "How do I stay motivated when the scale won't budge?",
                "answer": (
                    "Stop relying on motivation. Build a default — same "
                    "breakfast, same training cadence, same weighing rhythm "
                    "— that runs without conscious effort. Defaults survive "
                    "bad weeks. Motivation does not. The people who finish "
                    "are not more inspired. They are more boring."
                ),
            },
            {
                "question": "Is it okay to take a break from dieting?",
                "answer": (
                    "Yes, planned. A one-to-two-week diet break at "
                    "maintenance calories every 4 to 8 weeks on a long cut "
                    "tends to retain more muscle, reduce hunger, and improve "
                    "12-month outcomes versus continuous dieting. The break "
                    "is part of the program, not quitting it."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 16. what-to-do-after-a-binge-on-a-diet
    # ------------------------------------------------------------------
    "what-to-do-after-a-binge-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "What should I do after a binge on a diet?",
            "answer": (
                "Eat your normal breakfast. Drink water. Do not weigh "
                "yourself for three to five days. Return to your regular "
                "meal plan at the next meal, not next Monday. Most of the "
                "scale spike is water, not fat. The damage is not the binge. "
                "The damage is the punishment response that turns one meal "
                "into a week."
            ),
        },
        "faqItems": [
            {
                "question": "How much weight do you actually gain from a binge?",
                "answer": (
                    "About 0.2 to 0.5 kg of true fat for most people, even "
                    "after a 1,500 to 3,500 calorie overshoot. The 1 to 2 kg "
                    "the scale shows the next morning is almost entirely "
                    "water, sodium, glycogen, and food still moving through "
                    "digestion. It clears in three to five days."
                ),
            },
            {
                "question": "Should I skip meals the day after a binge?",
                "answer": (
                    "No. Skipping breakfast or lunch as punishment usually "
                    "drops blood sugar, raises appetite, and makes a second "
                    "binge likely by late afternoon. Eat your normal meals. "
                    "Your usual deficit absorbs the binge over 7 to 14 days "
                    "without any extra effort."
                ),
            },
            {
                "question": "Why did the binge happen in the first place?",
                "answer": (
                    "Most binges follow restriction, repetitive meals, "
                    "ignored cravings, or stress with food as the fast exit. "
                    "Binges rarely happen randomly. The honest question is "
                    "not 'why am I weak' but 'what set this up?' Pattern "
                    "detection beats damage control."
                ),
            },
            {
                "question": "Should I add cardio to compensate for a binge?",
                "answer": (
                    "No. Compensation cardio reinforces the punishment loop "
                    "and does not meaningfully change the math. The "
                    "additional 300 to 500 calories burned does not undo a "
                    "binge and trains you to keep using exercise as repayment "
                    "for food."
                ),
            },
            {
                "question": "When should I take a maintenance week instead?",
                "answer": (
                    "If you have binged twice in seven days, or if the plan "
                    "feels brittle for more than ten days, eat at "
                    "maintenance for a week. This is not quitting — it is "
                    "the most common professional intervention for broken "
                    "diet weeks. Hunger settles, head resets, deficit "
                    "becomes possible again."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 17. how-to-handle-hunger-pangs-on-a-diet
    # ------------------------------------------------------------------
    "how-to-handle-hunger-pangs-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I handle hunger pangs on a diet?",
            "answer": (
                "Stop treating all hunger as one signal. Normal hunger "
                "between meals is fine. Aggressive food noise that ambushes "
                "the day usually means the meals are too small, too "
                "repetitive, or too restrictive. Aim for quieter hunger, not "
                "heroic suffering. Inspect the food pattern before "
                "inspecting your character."
            ),
        },
        "faqItems": [
            {
                "question": "What's the difference between hunger and food noise?",
                "answer": (
                    "Real hunger is general, patient, and stomach-based. Any "
                    "reasonable meal satisfies it. Food noise is specific, "
                    "urgent, and head-based. You eat and the thought of food "
                    "does not quiet down. Food noise usually points to a "
                    "system problem, not a willpower problem."
                ),
            },
            {
                "question": "What foods actually keep you full longest?",
                "answer": (
                    "High-protein meals, plus high-volume vegetables, plus "
                    "some fiber. A 30 to 45 gram protein meal with a real "
                    "vegetable component holds appetite for hours. Low-volume "
                    "meals heavy in refined carbs leave most people hungry "
                    "two hours later regardless of calorie count."
                ),
            },
            {
                "question": "Does intermittent fasting help with hunger?",
                "answer": (
                    "For some people, yes. For others, the long unfed window "
                    "amplifies the evening spike. Fasting works when the "
                    "underlying food pattern is stable. It does not rescue a "
                    "fragile pattern. Try it for two to three weeks and read "
                    "your own response, not someone else's."
                ),
            },
            {
                "question": "Why is my hunger getting worse the longer I diet?",
                "answer": (
                    "Hormonal signals shift during sustained dieting in ways "
                    "that raise appetite. Restriction also makes ordinary "
                    "food feel more important than it is. The longer the "
                    "deficit and the tighter the rules, the louder the "
                    "appetite. A planned diet break often quiets it."
                ),
            },
            {
                "question": "Should I drink water when I'm hungry?",
                "answer": (
                    "It sometimes helps, but it is overrated as a fix. Water "
                    "can blunt mild hunger for 20 to 40 minutes. It cannot "
                    "replace a missing meal. If the hunger keeps returning "
                    "after water, the body is asking for actual fuel and the "
                    "meal structure needs adjusting."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 18. are-cheat-days-bad-for-weight-loss
    # ------------------------------------------------------------------
    "are-cheat-days-bad-for-weight-loss": {
        "answerBox": {
            "type": "answerBox",
            "question": "Are cheat days bad for weight loss?",
            "answer": (
                "It depends on how restrictive the rest of the week is. For "
                "people with steady food patterns, a planned cheat meal is "
                "fine. For people running tight all-or-nothing weeks, the "
                "cheat day usually turns into a payback event. The food is "
                "rarely the real story. The system that needed the release "
                "valve is."
            ),
        },
        "faqItems": [
            {
                "question": "Why do cheat days turn into binges for some people?",
                "answer": (
                    "Because the body and brain were primed for it. Sustained "
                    "restriction, loud appetite, and forbidden-food framing "
                    "make cheat day function as compensation, not relaxation. "
                    "The same pizza eaten by someone with a calmer pattern "
                    "is just a meal. Same food. Different aftermath."
                ),
            },
            {
                "question": "Is one cheat meal less damaging than a cheat day?",
                "answer": (
                    "Usually yes. A single meal is easier to absorb into the "
                    "week's total than a full day. Cheat-day expansion — "
                    "meal becomes day, day becomes weekend — is the actual "
                    "risk, not the original meal. Smaller, less ritualized "
                    "indulgences cause less rebound for most people."
                ),
            },
            {
                "question": "Should I plan cheat meals or eat intuitively?",
                "answer": (
                    "Either works depending on your relationship with food. "
                    "If forbidden foods still carry an emotional charge, "
                    "planned cheat meals reduce surprise binges. If the "
                    "weekly pattern is calm and food noise is low, intuitive "
                    "indulgences work. Read your own pattern, not someone "
                    "else's rule."
                ),
            },
            {
                "question": "How do I stop cheat days from turning into cheat weeks?",
                "answer": (
                    "Watch for cheat-day expansion early. Track when the meal "
                    "becomes a day. Return to normal at the next meal, not "
                    "next Monday. Build a week that does not need a "
                    "scheduled explosion in the first place. Restriction "
                    "creates the pressure that the cheat day releases."
                ),
            },
            {
                "question": "Will cheat days slow my weight loss?",
                "answer": (
                    "One planned cheat meal a week, absorbed into the week's "
                    "total, has minimal effect on a fat-loss phase. A cheat "
                    "weekend that adds 3,000 calories, repeated weekly, is "
                    "effectively a maintenance phase. Whether it slows you "
                    "depends entirely on whether the days around it return "
                    "to plan."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 19. why-am-i-working-out-but-not-losing-weight
    # ------------------------------------------------------------------
    "why-am-i-working-out-but-not-losing-weight": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why am I working out but not losing weight?",
            "answer": (
                "Because exercise is not a shrinking machine. A full hour of "
                "cardio burns 300 to 500 calories, which most people eat "
                "back without noticing. Training also raises appetite and "
                "retains water in recovering tissue. The workout builds the "
                "engine. The plate decides what the engine runs on. The "
                "scale catches up last."
            ),
        },
        "faqItems": [
            {
                "question": "How many calories does a workout actually burn?",
                "answer": (
                    "Less than people think. A vigorous one-hour gym session "
                    "burns roughly 300 to 500 calories depending on body "
                    "mass and intensity. Most fitness trackers overestimate "
                    "by 20 to 50 percent. A single post-workout snack often "
                    "covers the entire session's burn."
                ),
            },
            {
                "question": "Why does the scale go up after I start exercising?",
                "answer": (
                    "Recovering muscle holds extra water for a few days, "
                    "which adds 0.5 to 1.5 kg of scale weight that has "
                    "nothing to do with fat. Appetite also nudges up, so "
                    "intake often rises slightly. Both effects pass. The "
                    "scale rarely lies long-term, just short-term."
                ),
            },
            {
                "question": "Should I do more cardio if the scale isn't moving?",
                "answer": (
                    "Usually no. Adding cardio to a stalled cut often "
                    "triggers compensatory eating and lower NEAT later in the "
                    "day. The session burned 300 calories. The compensation "
                    "ate them back. Run an honest tracking week, take a diet "
                    "break, or adjust intake before adding cardio."
                ),
            },
            {
                "question": "Does lifting weights actually help with fat loss?",
                "answer": (
                    "Indirectly, yes. Lifting preserves muscle during a "
                    "deficit so more of the scale loss is fat. It does not "
                    "burn many calories during the session itself. The "
                    "long-term composition payoff is real even when the "
                    "weekly scale change is small."
                ),
            },
            {
                "question": "How long until exercise shows in the mirror?",
                "answer": (
                    "Strength changes show up in 6 to 8 weeks. Visible shape "
                    "change for most recreational lifters is 12 to 16 weeks, "
                    "sometimes longer. The numbers in the gym move first. "
                    "The body moves second. Most people quit at week 5 to 9, "
                    "right before the visual change starts."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 20. how-to-break-a-weight-loss-plateau
    # ------------------------------------------------------------------
    "how-to-break-a-weight-loss-plateau": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I break a weight loss plateau?",
            "answer": (
                "First, confirm it is a real plateau: three weeks of stable "
                "weight under same conditions, not three days. Then check "
                "actual eating, sleep, stress, and NEAT before cutting "
                "calories. Most plateaus break by fixing the thing that "
                "drifted, not by adding more deficit. A plateau is a report, "
                "not a verdict."
            ),
        },
        "faqItems": [
            {
                "question": "How long does it take to break a real plateau?",
                "answer": (
                    "Two to four weeks once the right intervention is "
                    "applied. Honest re-tracking, a one-week diet break, "
                    "fixing sleep, or adding daily walks all tend to resolve "
                    "stalls within that window. Cutting more calories often "
                    "extends the plateau by raising stress and dropping NEAT "
                    "further."
                ),
            },
            {
                "question": "Should I add cardio to break a plateau?",
                "answer": (
                    "Usually as a later move, not the first. Cardio added to "
                    "an already-aggressive deficit tends to be compensated "
                    "for behaviorally — lower NEAT and higher appetite later "
                    "in the day. A 30-minute walk on rest days often works "
                    "better than adding a structured cardio session."
                ),
            },
            {
                "question": "Is a diet break necessary or just helpful?",
                "answer": (
                    "On a long cut, diet breaks tend to be necessary. People "
                    "who take planned 7-to-14-day breaks at maintenance "
                    "every 4 to 8 weeks retain more muscle, report lower "
                    "hunger, and have better outcomes at six and twelve "
                    "months than people who diet straight through."
                ),
            },
            {
                "question": "Why does my weight stall right at month three?",
                "answer": (
                    "Maintenance calories drop as you lose weight, NEAT "
                    "decreases unconsciously, and appetite rises. All four "
                    "things stack around month three for most diets. The fix "
                    "is a 7 to 14 day maintenance break, not deeper cuts. "
                    "Cutting harder usually backfires here."
                ),
            },
            {
                "question": "What's the difference between slow progress and a real plateau?",
                "answer": (
                    "Slow progress is still movement — even 0.2 kg per week "
                    "is direction. A plateau is no scale movement and no "
                    "shape change for three weeks under your usual "
                    "conditions. Most 'plateaus' people complain about are "
                    "actually slow weeks called the wrong name."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 21. is-maintenance-hunger-different-from-diet-hunger
    # ------------------------------------------------------------------
    "is-maintenance-hunger-different-from-diet-hunger": {
        "answerBox": {
            "type": "answerBox",
            "question": "Is maintenance hunger different from diet hunger?",
            "answer": (
                "Yes, physiologically and behaviorally. Diet hunger is loud, "
                "urgent, food-specific, and emotional. Maintenance hunger is "
                "quieter, mechanical, and rhythmic. The transition takes "
                "weeks to months as leptin and ghrelin recalibrate. Reading "
                "early-maintenance hunger as cut-era hunger is the main "
                "reason people regain within six months."
            ),
        },
        "faqItems": [
            {
                "question": "How long does the maintenance hunger transition take?",
                "answer": (
                    "Usually three to four months for most people, sometimes "
                    "longer after aggressive cuts. Hunger and satiety "
                    "hormones recalibrate gradually to the new weight. "
                    "Waiting out that window is the actual skill of early "
                    "maintenance, not eating less or eating more."
                ),
            },
            {
                "question": "Why am I still hungry on maintenance calories?",
                "answer": (
                    "Because hormonal signals from the diet phase have not "
                    "fully recalibrated yet. The body may still be defending "
                    "the old weight for weeks after the deficit ends. The "
                    "hunger is real, but it is in transit, not a signal that "
                    "maintenance is broken."
                ),
            },
            {
                "question": "Should I keep eating more if hunger persists in maintenance?",
                "answer": (
                    "Not automatically. If the hunger is loud but the "
                    "weight is holding within a 1 to 2 kg range, the signal "
                    "is recalibrating. Wait it out. If the weight is "
                    "drifting up steadily for three weeks despite stable "
                    "intake, then bump down slightly. Read the trend, not "
                    "the day."
                ),
            },
            {
                "question": "What helps the most during early maintenance?",
                "answer": (
                    "Consistent meal timing. Protein and fiber at most "
                    "meals. Adequate sleep — poor sleep amplifies every "
                    "hunger signal. And time. The signal settles for most "
                    "people who hold the weight three to four months in. "
                    "None of these are dramatic. All are necessary."
                ),
            },
            {
                "question": "Why do most people regain weight after dieting?",
                "answer": (
                    "Three things stack: maintenance calories drop after "
                    "weight loss, appetite signals run louder than the new "
                    "caloric need for weeks, and NEAT decreases "
                    "unconsciously. Reading those signals through cut-era "
                    "logic — restrict more, or give up — produces the "
                    "rebound. Maintenance is the program, not the finish "
                    "line."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 22. does-bad-sleep-ruin-weight-loss
    # ------------------------------------------------------------------
    "does-bad-sleep-ruin-weight-loss": {
        "answerBox": {
            "type": "answerBox",
            "question": "Does bad sleep ruin weight loss?",
            "answer": (
                "Yes, faster than people realize. Three nights of "
                "under-sleeping push hunger signals up, cravings up, and "
                "decision-making around food down. The crack often shows up "
                "two to three days later as a binge people misread as "
                "willpower failure. Look at sleep before willpower. No "
                "amount of meal prep fixes three bad nights."
            ),
        },
        "faqItems": [
            {
                "question": "How many hours of sleep do I need to lose weight?",
                "answer": (
                    "Most adults need 7 to 9 hours. Below 6 consistently, "
                    "appetite-regulating hormones shift in ways that make "
                    "food feel louder. Sleep is the input that silently "
                    "decides whether the diet works. It is the cheapest and "
                    "least-used appetite intervention."
                ),
            },
            {
                "question": "Why do I crave sugar when I'm sleep-deprived?",
                "answer": (
                    "Under-sleeping pushes leptin down and ghrelin up, "
                    "raises cravings for high-calorie carb and fat foods, "
                    "and drops the brain's ability to delay gratification. "
                    "The craving is physiological, not character-based. "
                    "Fixing sleep usually quiets it within a few nights."
                ),
            },
            {
                "question": "Can one bad night of sleep affect a whole week?",
                "answer": (
                    "Often, yes. Three bad nights in a row tend to produce "
                    "elevated appetite for the next two to four days. The "
                    "delay is what fools people — they binge Thursday and "
                    "blame Thursday, not the Monday-Tuesday-Wednesday "
                    "shortfall that built the appetite up."
                ),
            },
            {
                "question": "Should I eat less if I sleep badly?",
                "answer": (
                    "No. Under-eating on top of sleep debt usually triggers "
                    "a worse binge later in the week. Eat normally, "
                    "prioritize protein and water, and prioritize fixing "
                    "sleep. The diet recovers when sleep recovers, not when "
                    "you punish the day."
                ),
            },
            {
                "question": "Does sleep affect weight more than calories?",
                "answer": (
                    "Calories still drive the math, but sleep decides "
                    "whether you can hit the calorie target consistently. A "
                    "perfect plan plus poor sleep usually fails. A decent "
                    "plan plus good sleep usually works. Sleep is the "
                    "input that lets the rest of the plan run honestly."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 23. how-to-stop-a-binge-from-becoming-a-binge-week
    # ------------------------------------------------------------------
    "how-to-stop-a-binge-from-becoming-a-binge-week": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I stop a binge from becoming a binge week?",
            "answer": (
                "Eat your normal breakfast the morning after. Drink water. "
                "Do not weigh yourself for three to five days. Return to "
                "your regular meal plan at lunch, not next Monday. The "
                "damage is not the binge. It is the response. Act as if "
                "yesterday was yesterday and today is today, because that "
                "is literally what they are."
            ),
        },
        "faqItems": [
            {
                "question": "Why does one binge often turn into several days off plan?",
                "answer": (
                    "Three patterns: hard restriction the morning after "
                    "drops blood sugar and triggers a second binge; "
                    "all-or-nothing framing turns one meal into 'the day is "
                    "ruined'; and obsessive scale-checking reads water "
                    "weight as fat and confirms failure. Any of those alone "
                    "stretches the binge."
                ),
            },
            {
                "question": "Should I cut calories the week after a binge?",
                "answer": (
                    "No. Your normal deficit absorbs the binge into the "
                    "weekly total over 7 to 14 days without any extra "
                    "effort. Trying to compensate with a deeper deficit "
                    "usually triggers another binge or stress water "
                    "retention that makes the scale worse, not better."
                ),
            },
            {
                "question": "How can I tell if another binge is coming?",
                "answer": (
                    "Common signals: under-eating the day before in "
                    "compensation, under-sleeping, high-stress day, more "
                    "than four hours past a regular meal. Eat a real meal "
                    "with protein and volume. The craving usually drops by "
                    "half within 30 to 60 minutes if the issue was fuel."
                ),
            },
            {
                "question": "When should I take a maintenance week instead?",
                "answer": (
                    "If you have binged twice in seven days, or the plan "
                    "feels brittle for more than ten days. Eat at "
                    "maintenance for 7 to 10 days. Hunger settles, the head "
                    "resets, and a return to deficit becomes possible "
                    "without another binge. This is intervention, not "
                    "quitting."
                ),
            },
            {
                "question": "How long does the scale stay up after a binge?",
                "answer": (
                    "Three to five days under normal eating. The 1 to 2 kg "
                    "scale jump is mostly water, sodium, and food still "
                    "moving through digestion. Real fat addition is usually "
                    "0.2 to 0.5 kg, and the deficit absorbs it across the "
                    "next week without intervention."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 24. why-do-i-gain-back-more-weight-than-i-lost
    # ------------------------------------------------------------------
    "why-do-i-gain-back-more-weight-than-i-lost": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why do I gain back more weight than I lost?",
            "answer": (
                "Three things collide after a diet ends. Maintenance "
                "calories dropped because you weigh less. Appetite signals "
                "stay louder than the new caloric need for weeks. NEAT "
                "drops unconsciously. Eating like the old you, while "
                "hungrier, while moving less, produces overshoot. The "
                "rebound is not character failure. It is three lines "
                "crossing at once."
            ),
        },
        "faqItems": [
            {
                "question": "Is rebound weight gain mostly fat or muscle?",
                "answer": (
                    "Mostly fat for people who dieted aggressively without "
                    "training. Metabolic and fat-storage patterns can shift "
                    "after severe cuts in ways that make regained weight "
                    "more likely to be fat, not the muscle that was lost. "
                    "Slow loss with strength training reduces this effect."
                ),
            },
            {
                "question": "How long does the rebound risk last?",
                "answer": (
                    "The most vulnerable window is the first 6 to 12 months "
                    "of maintenance. Hunger signals stay louder, NEAT stays "
                    "lower, and the body can keep defending the old weight "
                    "for that period. Surviving it without rebounding is "
                    "what separates long-term maintainers from yo-yo "
                    "dieters."
                ),
            },
            {
                "question": "What's the best way to prevent regaining weight?",
                "answer": (
                    "Lose slower. Train through the diet to keep muscle. "
                    "Treat maintenance as the actual program, not a finish "
                    "line. Expect appetite to run louder than your caloric "
                    "need for weeks and plan for it. None of these are "
                    "slogans. They change the outcome."
                ),
            },
            {
                "question": "Does yo-yo dieting permanently change metabolism?",
                "answer": (
                    "Repeated aggressive cycles can compound the "
                    "compensation responses — lower NEAT, louder appetite, "
                    "reduced lean mass. 'Permanent damage' is overstated, "
                    "but each cycle tends to be harder than the last. "
                    "Slower, less-extreme approaches break the pattern."
                ),
            },
            {
                "question": "Why does my body 'overshoot' my old weight?",
                "answer": (
                    "Defended-weight signals do not always shut off at the "
                    "old weight. They may keep pushing past it until the "
                    "body is certain food is plentiful. Combined with "
                    "post-restriction food intensity and lower NEAT, the "
                    "regain often passes the original starting point."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 25. how-to-stay-at-your-goal-weight-long-term
    # ------------------------------------------------------------------
    "how-to-stay-at-your-goal-weight-long-term": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I stay at my goal weight long term?",
            "answer": (
                "Become boring. People who hold weight off for years eat "
                "similar things most days, train three to four times a week "
                "without drama, sleep enough, walk more than average, and "
                "stop chasing a goal weight. They have an emergency "
                "protocol for small drifts. They do not run on willpower or "
                "inspiration. The defaults do the work."
            ),
        },
        "faqItems": [
            {
                "question": "What do successful long-term maintainers actually do?",
                "answer": (
                    "Eat similar meals most days. Train consistently without "
                    "treating it as a punishment project. Sleep enough. Walk "
                    "more than they realize. Weigh less often than during "
                    "the cut. Tighten quickly without drama if weight drifts "
                    "up 2 to 3 kg. They do not look like fitness people."
                ),
            },
            {
                "question": "How is maintenance different from being on a diet?",
                "answer": (
                    "Maintenance has no finish line, no scale milestone, no "
                    "trend to chase. The structure stays the same — same "
                    "meal patterns, same training, same logging — but the "
                    "deficit goes away. The food gets bigger. The discipline "
                    "around it does not."
                ),
            },
            {
                "question": "Should I keep weighing myself in maintenance?",
                "answer": (
                    "Yes, but less often. Once or twice a week, same "
                    "morning conditions, weekly average. Daily weighing in "
                    "maintenance amplifies noise — flat trends do not "
                    "swallow the spikes the way deficit trends do. Less "
                    "frequent, longer comparison windows work better."
                ),
            },
            {
                "question": "What should I do if my weight starts creeping up?",
                "answer": (
                    "Tighten for two weeks without drama and return to "
                    "baseline. Most successful maintainers run an emergency "
                    "protocol when drift hits 2 to 3 kg. The tightening is "
                    "not a diet. It is a correction. It works because it "
                    "starts early, before the drift compounds."
                ),
            },
            {
                "question": "How long until maintenance feels automatic?",
                "answer": (
                    "Usually 6 to 12 months of consistent practice for the "
                    "defaults to run on autopilot. Then the program fades "
                    "from foreground to background. There is no celebration "
                    "moment. You just notice, weeks later, that you have "
                    "stopped thinking about food the way you used to."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 26. how-to-tell-if-youre-hungry-or-bored
    # ------------------------------------------------------------------
    "how-to-tell-if-youre-hungry-or-bored": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I tell if I'm hungry or just bored?",
            "answer": (
                "Run the apple test. Would you eat an apple right now? If "
                "yes, you are probably hungry. If no, but you want ice "
                "cream, you are probably bored or emotionally eating. Real "
                "hunger is general and patient. Boredom eating is specific, "
                "urgent, and mouth-based. The craving is specific. The "
                "hunger is general."
            ),
        },
        "faqItems": [
            {
                "question": "What does real hunger actually feel like?",
                "answer": (
                    "General. Patient. Stomach-based. Your whole body is "
                    "mildly under-fueled. Mood and energy dip. Any reasonable "
                    "meal — a sandwich, leftover rice, a banana — would feel "
                    "fine. Real hunger grows slowly over 15 to 20 minutes. "
                    "It does not spike on contact with the kitchen."
                ),
            },
            {
                "question": "Why does boredom eating usually hit in the afternoon?",
                "answer": (
                    "Three things stack: decision fatigue from the day, "
                    "wobbly blood sugar from a light or distant lunch, and "
                    "looser social structure. You are home, alone, or "
                    "winding down. Food becomes the most available source of "
                    "fast pleasure. None of this is a character failure."
                ),
            },
            {
                "question": "How can I stop boredom eating without restricting?",
                "answer": (
                    "Wait five minutes. Drink water or tea. Change location "
                    "— the trigger is often the room, not the stomach. If "
                    "the pull persists, eat intentionally at the table, not "
                    "standing at the fridge. Intention is what separates a "
                    "snack from 40 minutes of unconscious grazing."
                ),
            },
            {
                "question": "Could my 'boredom eating' actually be under-fueling?",
                "answer": (
                    "Often, yes. If you are in a real deficit and consistently "
                    "hungry mid-afternoon, the lunch was probably too light. "
                    "Move calories there. Protein-forward lunches and larger "
                    "breakfasts usually fix what looked like an emotional "
                    "eating pattern."
                ),
            },
            {
                "question": "Is it ever okay to eat when I'm not hungry?",
                "answer": (
                    "Yes. Sharing popcorn during a movie is not dietary "
                    "dysfunction. It is being a person. The problem is "
                    "unconscious repeated boredom eating that adds 300 to "
                    "700 calories a day without registering. The occasional "
                    "social or comfort eat is fine."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 27. how-to-get-back-on-track-after-a-bad-weekend
    # ------------------------------------------------------------------
    "how-to-get-back-on-track-after-a-bad-weekend": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I get back on track after a bad weekend?",
            "answer": (
                "Eat your normal breakfast Monday. Do not weigh in for "
                "three to five days. Return to your regular plan at the "
                "next meal, not next Monday. Treat the weekend as absorbed "
                "into the week, not as a reason to compensate. Most of the "
                "Monday scale jump is water and gut content, not fat. The "
                "math is fine."
            ),
        },
        "faqItems": [
            {
                "question": "How much damage does one bad weekend actually do?",
                "answer": (
                    "Usually 0.5 to 1 kg of true fat from a 3,000 to 5,000 "
                    "calorie overshoot. The 2 to 3 kg the scale shows "
                    "Monday morning is mostly water from carbs, sodium, "
                    "and alcohol. It clears in three to five days. The "
                    "weekly trend recovers within ten days."
                ),
            },
            {
                "question": "Should I eat less Monday to make up for the weekend?",
                "answer": (
                    "No. Skipping breakfast or cutting Monday hard usually "
                    "triggers another binge by Wednesday. Eat your normal "
                    "Monday meals. The weekend's overshoot absorbs into the "
                    "weekly total over 7 to 14 days without compensation. "
                    "The fix is calm, not cardio."
                ),
            },
            {
                "question": "Why do I always blow my diet on weekends?",
                "answer": (
                    "Usually because the weekday plan is too tight, weekend "
                    "social structure is looser, and the binary "
                    "'on-plan-or-off-plan' framing turns one slip into a "
                    "Friday-through-Sunday spiral. A system with a "
                    "tolerance band — not a hard daily target — survives "
                    "weekends without breaking."
                ),
            },
            {
                "question": "What should I do if I keep having bad weekends?",
                "answer": (
                    "Build a system that bends. Tolerance bands of about "
                    "300 calories per day. Read the week as the unit, not "
                    "the day. A bad Friday under this framing is an "
                    "inconvenience, not a crisis. The perfect-looking plan "
                    "that breaks under one Friday is the actual problem."
                ),
            },
            {
                "question": "Is the Monday scale jump actually fat gain?",
                "answer": (
                    "Almost never. A 1.5 to 2.5 kg Monday spike after a "
                    "high-sodium, high-carb weekend is mostly water, "
                    "glycogen, and food in transit. Reading it as fat is "
                    "what triggers the next bad week. Wait three to five "
                    "days. The number drops back close to baseline."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 28. do-i-have-to-meal-prep-to-lose-weight
    # ------------------------------------------------------------------
    "do-i-have-to-meal-prep-to-lose-weight": {
        "answerBox": {
            "type": "answerBox",
            "question": "Do I have to meal prep to lose weight?",
            "answer": (
                "No, but you have to solve what meal prep solves: decision "
                "fatigue, macro reliability, and friction at 7pm on a "
                "Wednesday. Weeknight defaults, component prep, restaurant "
                "defaults, or repeated breakfasts can do the same job "
                "without a Sunday batch. The Sunday is not the program. "
                "The default is the program."
            ),
        },
        "faqItems": [
            {
                "question": "What problem is meal prep actually solving?",
                "answer": (
                    "Three at once: removing the daily 'what do I eat' "
                    "decision, hitting consistent calorie and protein "
                    "targets, and reducing the friction of cooking when "
                    "you are tired. Solve those three some other way and "
                    "you do not need a Sunday batch. Skip them and no "
                    "system holds."
                ),
            },
            {
                "question": "What are alternatives to Sunday meal prep?",
                "answer": (
                    "Default weeknight meals you can cook on autopilot in "
                    "25 minutes. Component prep — just protein and "
                    "vegetables, combined fresh. Two or three reliable "
                    "restaurant orders. The same breakfast every day. Most "
                    "people use a combination of two or three of these."
                ),
            },
            {
                "question": "When does meal prep actually help most?",
                "answer": (
                    "Three cases: when weeknight cooking is genuinely "
                    "impossible (long shifts, small kids, long commutes), "
                    "when you happily eat the same lunch five days a week, "
                    "or when you are early in the program and still "
                    "building eyeball portion skills."
                ),
            },
            {
                "question": "When does meal prep actively backfire?",
                "answer": (
                    "When the four-hour Sunday leaves you resentful before "
                    "the week starts, when you throw out food in week three "
                    "from boredom, or when the system depends so much on "
                    "perfect Sundays that one missed Sunday wrecks the "
                    "week. A program that brittle was always going to fail."
                ),
            },
            {
                "question": "What should I cook on weeknights instead?",
                "answer": (
                    "A short list of three or four default meals you can "
                    "make in 25 to 30 minutes — usually a one-pan combo of "
                    "protein, frozen vegetables, a starch, and a sauce. "
                    "Rotate the protein and sauce. Nine combinations from "
                    "three of each. None of them require pre-cooking."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 29. does-one-bad-meal-ruin-a-diet
    # ------------------------------------------------------------------
    "does-one-bad-meal-ruin-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "Does one bad meal ruin a diet?",
            "answer": (
                "No. The meal is the meal. The slip is what you do the "
                "morning after. Most 'slips' people remember were normal "
                "over-target meals that the system absorbed without "
                "consequence. The only way one meal becomes a slip is if "
                "the next morning gets shaped like punishment instead of "
                "structure. The work is at the morning."
            ),
        },
        "faqItems": [
            {
                "question": "What's the difference between a bad meal and a slip?",
                "answer": (
                    "A bad meal is a single over-target meal. A slip is the "
                    "behavior pattern that follows: skipped breakfast as "
                    "punishment, larger lunch from blood-sugar drop, snacks "
                    "from irregular eating, bigger dinner from fatigue. The "
                    "meal was the trigger. The slip is the next 48 hours."
                ),
            },
            {
                "question": "How do I tell if my meal is becoming a slip?",
                "answer": (
                    "Ask one question the morning after: is my first meal "
                    "today the planned breakfast, or a punishment version "
                    "of it? Planned breakfast means the system is intact. "
                    "Skipped or shrunk breakfast means the slip is being "
                    "set up. Eat the planned breakfast and stop the cycle."
                ),
            },
            {
                "question": "What about the scale jump after one bad meal?",
                "answer": (
                    "It is water and gut content, not fat. A 0.6 to 1.2 kg "
                    "morning-after jump after a high-sodium dinner is "
                    "almost entirely temporary. Reading it as fat is what "
                    "triggers the slip. Wait three days under normal eating "
                    "and the number comes back."
                ),
            },
            {
                "question": "Should I restart 'tomorrow' or 'Monday' after a slip?",
                "answer": (
                    "Neither. Restart at the next meal. Days do not "
                    "restart, meals do. If lunch on day 2 is the meal that "
                    "started getting punishment-shaped, dinner on day 2 is "
                    "the meal where you go back to the plan. 'Tomorrow' "
                    "framing keeps the slip alive through tomorrow."
                ),
            },
            {
                "question": "Are some meals automatically slips by themselves?",
                "answer": (
                    "A few cases: a meal eaten in clearly out-of-control "
                    "binge mode, a meal that triggers same-evening "
                    "continuation, or a meal that follows weeks of tight "
                    "restriction. Outside those, most 'bad meals' are "
                    "ordinary over-target meals that the morning-after "
                    "handling decides the fate of."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 30. when-does-a-diet-become-a-lifestyle
    # ------------------------------------------------------------------
    "when-does-a-diet-become-a-lifestyle": {
        "answerBox": {
            "type": "answerBox",
            "question": "When does a diet become a lifestyle?",
            "answer": (
                "Usually between month 6 and month 12 of consistent "
                "practice, sometimes longer. There is no announcement. The "
                "moment is noticed weeks later, by accident — a Tuesday "
                "where you have not consciously thought about food, "
                "training, or weight all day. The transition is a fade, "
                "not a celebration. The defaults stop feeling like effort."
            ),
        },
        "faqItems": [
            {
                "question": "How long before diet habits feel automatic?",
                "answer": (
                    "Three habit layers each take their own time: cooking "
                    "defaults usually 6 to 9 months, training cadence 4 to "
                    "6 months, calm weighing rhythm 6 to 12 months. When "
                    "all three run unconsciously, conscious effort drops to "
                    "near-zero. That is when the diet becomes a lifestyle."
                ),
            },
            {
                "question": "Why doesn't the transition feel like a milestone?",
                "answer": (
                    "Because it is the absence of an event. The program "
                    "fades from foreground to background slowly, across "
                    "many ordinary days. The point you notice the fade is "
                    "just one of those days. People waiting for a "
                    "finish-line moment usually miss the transition "
                    "entirely."
                ),
            },
            {
                "question": "Can a diet become unsustainable if it never becomes a lifestyle?",
                "answer": (
                    "Yes. Effortful systems do not hold for years. They "
                    "hold for months and break. If maintenance still feels "
                    "like a project at month twelve, the system has not "
                    "finished converting. The body change does not last "
                    "without the lifestyle change underneath it."
                ),
            },
            {
                "question": "What does the lifestyle phase actually look like?",
                "answer": (
                    "Boring. Same breakfast most mornings. Same training "
                    "cadence most weeks. Calm weekly weigh-ins. Meals you "
                    "do not frame as 'diet meals.' Sessions you do not "
                    "frame as 'training for the project.' The body is just "
                    "your body now. The work happens in the background."
                ),
            },
            {
                "question": "How do I know I'm not just on a longer diet?",
                "answer": (
                    "If you still consciously frame meals as 'on plan' or "
                    "'off plan,' you are still in diet mode. If meals just "
                    "happen, with the right macros, without you naming "
                    "them as part of a program, the transition has "
                    "started. The naming fades before the behaviors do."
                ),
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Sanity assertions — kept inline so any edit accidentally breaking the
# 30-entry contract or the SCHEMA_TYPES alignment fails loudly at import.
# ---------------------------------------------------------------------------

assert len(FEATURED_SNIPPETS) == 30, (
    f"Expected 30 entries, got {len(FEATURED_SNIPPETS)}"
)
assert set(SCHEMA_TYPES.keys()) == set(FEATURED_SNIPPETS.keys()), (
    "SCHEMA_TYPES and FEATURED_SNIPPETS must cover the same slugs"
)
assert all(v == "faq" for v in SCHEMA_TYPES.values()), (
    "All SCHEMA_TYPES entries must be 'faq' for FAQPage JSON-LD emission"
)


def _word_count(text: str) -> int:
    """Tiny helper used by the validator below. Whitespace tokens, no html."""
    return len([w for w in text.split() if w.strip()])


def validate_word_counts() -> list[str]:
    """
    Returns a list of human-readable warnings for any answer that falls
    outside its expected word range.

    Rules per `seo_optimization_rules.md` and the brief:
    - answerBox.answer: 40-60 words STRICTLY
    - faqItems[].answer: 25-50 words STRICTLY
    """
    warnings: list[str] = []
    for slug, payload in FEATURED_SNIPPETS.items():
        ab = payload["answerBox"]["answer"]
        n = _word_count(ab)
        if not (40 <= n <= 60):
            warnings.append(f"[{slug}] answerBox is {n} words (expected 40-60)")
        for i, item in enumerate(payload["faqItems"]):
            n = _word_count(item["answer"])
            if not (25 <= n <= 50):
                warnings.append(
                    f"[{slug}] faqItems[{i}] is {n} words (expected 25-50): "
                    f"{item['question']!r}"
                )
    return warnings


if __name__ == "__main__":
    issues = validate_word_counts()
    if issues:
        print(f"Found {len(issues)} word-count issues:")
        for w in issues:
            print(f"  - {w}")
    else:
        print(
            f"OK: {len(FEATURED_SNIPPETS)} posts, "
            f"all answerBox 40-60 words, all FAQ items 25-50 words."
        )

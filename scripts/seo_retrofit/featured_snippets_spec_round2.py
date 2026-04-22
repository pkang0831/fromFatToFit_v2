"""
Featured Snippet content (answerBox + FAQ items) — Round 2.

Round 1 covered the 30 highest-leverage Q&A posts (see
`featured_snippets_spec.py`). This round covers the remaining Q&A blog
posts in `frontend/src/content/blog/posts.ts` that:

- Have a slug starting with how-to / what / why / when / is / are / do /
  does / should / am / can
- Do NOT yet carry `schemaType: 'faq'` or have an `answerBox` / `faq`
  section in their `sections[]` array

Per `marketing/fitness_blogging/blog_strategy/seo_optimization_rules.md`:

- answerBox is a 40–60 word direct answer rendered near the top of the
  post, designed to be plucked into Google's Position 0 / Featured
  Snippet box.
- faqItems power both an on-page accordion AND FAQPage JSON-LD via the
  `BlogStructuredData` component when `schemaType: 'faq'` is set.

Voice rules (CRITICAL — same as round 1):

- Voice = pkang's: founder-led, anti-hype, observational, dry, direct.
- Forbidden words: ultimate, secret, shocking, life-changing,
  transform your body, guaranteed, fast results, you won't believe,
  crazy, insane, top [N], best.
- Each answer reads like the source post's body. No marketing language.
- Every answerBox answer is 40–60 words. Every FAQ answer is 25–50
  words. Word counts were verified during drafting and are enforced by
  the validator at the bottom of this file.

The application script (`apply_featured_snippets.py`) inserts the
`answerBox` section after each post's lede `paragraphs` block and the
`faq` section before the closing `paragraphs` (Closing) block, then sets
`schemaType: 'faq'` on the matching post.

24 posts.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# SCHEMA_TYPES — set every entry below to 'faq' so BlogStructuredData
# auto-emits FAQPage JSON-LD alongside the existing Article schema.
# ---------------------------------------------------------------------------

SCHEMA_TYPES: dict[str, str] = {
    "how-to-track-body-transformation-without-the-scale": "faq",
    "what-counts-as-a-weight-loss-plateau": "faq",
    "how-to-know-youre-losing-weight-without-the-scale": "faq",
    "why-cant-i-sleep-on-a-calorie-deficit": "faq",
    "do-obese-people-lose-weight-slower": "faq",
    "why-is-my-appetite-stronger-on-a-diet": "faq",
    "why-is-the-middle-of-weight-loss-the-hardest": "faq",
    "is-my-stomach-bloat-or-fat": "faq",
    "why-does-my-body-look-different-from-different-angles": "faq",
    "how-to-stop-using-exercise-as-punishment": "faq",
    "why-do-i-weigh-more-at-night": "faq",
    "do-vegetables-help-you-feel-full-on-a-diet": "faq",
    "why-do-you-lose-so-much-weight-first-week": "faq",
    "how-to-eat-at-social-events-on-a-diet": "faq",
    "why-did-i-stop-losing-weight-at-3-months": "faq",
    "why-are-my-workouts-harder-on-a-cut": "faq",
    "why-does-strength-increase-before-muscle-size": "faq",
    "why-progress-photos-dont-show-progress": "faq",
    "why-does-the-same-weight-feel-different-as-you-age": "faq",
    "am-i-really-in-a-plateau-or-tracking-wrong": "faq",
    "how-to-stop-mirror-checking-on-a-diet": "faq",
    "why-adding-cardio-to-a-cut-backfires": "faq",
    "does-cutting-sodium-cause-water-retention": "faq",
    "why-am-i-so-hungry-after-lifting-weights": "faq",
}


# ---------------------------------------------------------------------------
# FEATURED_SNIPPETS — each slug maps to its answerBox + faqItems payload.
# ---------------------------------------------------------------------------

FEATURED_SNIPPETS: dict[str, dict] = {
    # ------------------------------------------------------------------
    # 1. how-to-track-body-transformation-without-the-scale
    # ------------------------------------------------------------------
    "how-to-track-body-transformation-without-the-scale": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I track body transformation without obsessing over the scale?",
            "answer": (
                "Build one weekly evidence loop instead of a daily judgment "
                "ritual. Take a baseline photo, add weekly progress photos "
                "under similar conditions, watch how clothes fit, and use "
                "the scale as a supporting metric rather than the main "
                "judge. The body usually changes slower than emotion. "
                "Weekly tracking gives the body room to tell a real story."
            ),
        },
        "faqItems": [
            {
                "question": "How often should I take progress photos?",
                "answer": (
                    "Once a week, same spot, same lighting, same pose. "
                    "Save them without analyzing them on the day. Compare "
                    "in groups of four. Weekly is frequent enough to stay "
                    "relevant; comparing every four weeks is slow enough "
                    "to let your body actually show direction."
                ),
            },
            {
                "question": "Why is daily scale tracking misleading?",
                "answer": (
                    "Daily readings are mostly water, sodium, and digestive "
                    "contents — almost everything except fat. The number "
                    "swings two kilos in a normal day. Reading those swings "
                    "as fat loss or gain creates emotional volatility with "
                    "numbers attached, not tracking."
                ),
            },
            {
                "question": "What should a baseline check-in include?",
                "answer": (
                    "One honest starting photo, taken under conditions you "
                    "can repeat. Not a flattering angle. Not your best "
                    "lighting. Just a clear reference point. Without a "
                    "baseline, every future photo becomes a guess. With "
                    "one, every check-in becomes a real comparison."
                ),
            },
            {
                "question": "What signals are more honest than the scale?",
                "answer": (
                    "Weekly progress photos under matched conditions. "
                    "Visual changes in waist, torso, face, and posture. "
                    "How familiar clothes are fitting. Tape measurements "
                    "at waist and hip every two weeks. Together those four "
                    "catch composition shifts the scale silently misses."
                ),
            },
            {
                "question": "Why do most people quit before they see real progress?",
                "answer": (
                    "Because they track on a daily timescale and grade "
                    "emotionally. Daily noise is louder than weekly signal, "
                    "so the program feels like it is failing while the "
                    "body is quietly moving. Most people quit not from "
                    "lack of discipline, but from lack of believable evidence."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 2. what-counts-as-a-weight-loss-plateau
    # ------------------------------------------------------------------
    "what-counts-as-a-weight-loss-plateau": {
        "answerBox": {
            "type": "answerBox",
            "question": "What actually counts as a weight loss plateau?",
            "answer": (
                "A real plateau is three weeks of stable weight under the "
                "same conditions, with no shape change either. Less than "
                "that is noise. Slower progress than week one is not a "
                "plateau. One or two flat weigh-ins is not a plateau. Most "
                "people use the word way too early and start punishing a "
                "plan that is still working."
            ),
        },
        "faqItems": [
            {
                "question": "How long until I can call it a plateau?",
                "answer": (
                    "Three weeks of stable weight under similar conditions, "
                    "with no shape change either. Anything shorter is "
                    "noise. The early water-loss phase fooled people about "
                    "what real progress looks like, so the second month "
                    "often gets read as a plateau when it is just adulthood."
                ),
            },
            {
                "question": "Can the scale stay flat while I'm still losing fat?",
                "answer": (
                    "Yes. If body fat is going down while a small amount "
                    "of muscle is going up, the scale shows nothing while "
                    "the body is still changing. That is why one number "
                    "should not be treated as a final verdict, especially "
                    "during training."
                ),
            },
            {
                "question": "Why does cutting more usually backfire?",
                "answer": (
                    "Because most plateaus are not actually plateaus, so "
                    "the harsher response is solving a problem that does "
                    "not exist. Even on real plateaus, cutting harder "
                    "tends to drop NEAT, raise appetite, and trigger a "
                    "binge later in the week. Bolt cutters on an unlocked door."
                ),
            },
            {
                "question": "Why does week one feel so dramatic compared to week three?",
                "answer": (
                    "Week one is mostly water, glycogen, and a noisier "
                    "scale. Motivation is fresh. The body is not yet in "
                    "any real fat-loss rhythm. By week three, the noise "
                    "has cleared and the actual rate of loss is what shows. "
                    "Week one was the bad teacher."
                ),
            },
            {
                "question": "How should I respond if it is a real plateau?",
                "answer": (
                    "Run an honest tracking week before changing anything. "
                    "Check sleep, stress, and unconscious activity drift. "
                    "Most plateaus break by fixing the variable that "
                    "drifted, not by cutting calories or adding cardio. A "
                    "plateau is a report, not a verdict. Read it before reacting."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 3. how-to-know-youre-losing-weight-without-the-scale
    # ------------------------------------------------------------------
    "how-to-know-youre-losing-weight-without-the-scale": {
        "answerBox": {
            "type": "answerBox",
            "question": "How can I tell I'm losing weight without the scale?",
            "answer": (
                "Look at shape, fit, firmness, and where the body is "
                "changing. The waistline on familiar clothes loosens "
                "before the scale fully cooperates. The upper abdomen "
                "feels less pushed out. The lower section softens and "
                "shifts. Real fat loss is often visible before it becomes "
                "official on a number."
            ),
        },
        "faqItems": [
            {
                "question": "What signals show up before the scale moves?",
                "answer": (
                    "How clothes fit at the waist. Whether the upper "
                    "abdomen feels less pushed out. How the lower section "
                    "sits. Where shape is loosening or shifting. None of "
                    "these are as neat as a number, but they often arrive "
                    "earlier than the scale agrees to."
                ),
            },
            {
                "question": "Why doesn't fat loss look the same on every body?",
                "answer": (
                    "Because fat does not sit or leave the same way for "
                    "everyone. Some people carry more around the upper "
                    "abdomen, some lower, some at the back or thighs. "
                    "Posture and muscle change how the midsection projects. "
                    "Waiting for one universal pattern keeps people confused for years."
                ),
            },
            {
                "question": "Are progress photos more reliable than the mirror?",
                "answer": (
                    "Usually yes, if the conditions match. The mirror "
                    "reads through the day's mood. A photo taken in the "
                    "same light, same posture, same time of day every "
                    "week strips most of that out. Looked at in groups of "
                    "four, photos catch what the daily mirror misses."
                ),
            },
            {
                "question": "What if my clothes look different but the scale hasn't moved?",
                "answer": (
                    "Your body composition probably shifted. The scale "
                    "weighs everything at once: water, gut content, "
                    "muscle, fat. A flat number can mean fat down and a "
                    "little muscle up. Clothes catch what the scale is "
                    "silent about. Trust the fit before the number."
                ),
            },
            {
                "question": "How long should I wait before deciding nothing changed?",
                "answer": (
                    "Three weeks at minimum. Most weeks contain enough "
                    "water and digestive noise to fake a stall in either "
                    "direction. Comparing weekly photos, weekly waist "
                    "measurements, and a rolling weekly weight average "
                    "over three weeks tells you whether the body actually "
                    "held or moved."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 4. why-cant-i-sleep-on-a-calorie-deficit
    # ------------------------------------------------------------------
    "why-cant-i-sleep-on-a-calorie-deficit": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why can't I sleep on a calorie deficit?",
            "answer": (
                "Usually because the deficit is bigger than the body wants "
                "to admit, especially if training is also high. Hard "
                "sessions plus aggressive food cuts plus poor sleep is not "
                "discipline. It is a low-grade emergency. Severe fatigue "
                "stacked with insomnia means the plan is under-fueling a "
                "body asked to do too much."
            ),
        },
        "faqItems": [
            {
                "question": "Is insomnia a normal part of dieting?",
                "answer": (
                    "Mild restless nights happen for many people in the "
                    "first weeks. Persistent 4 a.m. wake-ups, severe "
                    "fatigue, and a body that feels fragile are not "
                    "normal. They are signs the plan and the training "
                    "load are out of balance. Persistent insomnia deserves "
                    "real attention."
                ),
            },
            {
                "question": "Why does 'not hungry' not equal 'well-fueled'?",
                "answer": (
                    "Appetite gets weird when the system is pushed too "
                    "hard. Feeling less hungry can mean the body has "
                    "stopped expecting fuel, not that it has enough. If "
                    "performance is dropping, sleep is wrecked, and energy "
                    "is low, low appetite is not proof of success."
                ),
            },
            {
                "question": "Should I add more calories or train less?",
                "answer": (
                    "Usually both, but eating slightly more is the cheaper "
                    "move first. A small bump in carbs or total calories "
                    "often restores sleep within a week. If insomnia "
                    "continues despite that, training volume needs to come "
                    "down too. Make the plan more livable before making "
                    "it more extreme."
                ),
            },
            {
                "question": "Why do clean-looking diets still wreck the person doing them?",
                "answer": (
                    "A plan can photograph well and still under-fuel the "
                    "body running it. Disciplined-looking meals and "
                    "admirable workouts mean nothing if the person is "
                    "freezing, waking at 4 a.m., and dragging through the "
                    "day. The plan was never meant to produce a low-grade emergency."
                ),
            },
            {
                "question": "When should I see a doctor?",
                "answer": (
                    "When sleep stays broken for more than two to three "
                    "weeks despite eating more, training less, and "
                    "stabilizing the basics. Persistent insomnia, racing "
                    "heart, severe mood changes, or lasting fatigue are "
                    "not diet badges. They are reasons to get a real medical opinion."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 5. do-obese-people-lose-weight-slower
    # ------------------------------------------------------------------
    "do-obese-people-lose-weight-slower": {
        "answerBox": {
            "type": "answerBox",
            "question": "Do obese people lose weight slower than others?",
            "answer": (
                "Not slower per pound, often faster early. But more of the "
                "loss is true fat instead of water, so it takes longer to "
                "feel and see. Weight gained slowly over years is mostly "
                "fat, and fat moves slower than water. Long-term obesity "
                "is also a long-term habit pattern. Both take time to change."
            ),
        },
        "faqItems": [
            {
                "question": "Why does 'gained quickly, lost quickly' not apply here?",
                "answer": (
                    "That phrase is usually about water. Holiday eating, "
                    "travel, and a few salty days can move 3 to 5 kg of "
                    "water that comes off fast. Fat built up over years "
                    "is a different story. The body did not store it "
                    "overnight, and it does not leave overnight."
                ),
            },
            {
                "question": "Is the metabolism actually broken?",
                "answer": (
                    "Usually no. The fat itself is not stubborn because "
                    "it has been there longer. The pattern around it is. "
                    "Years of certain meals, routines, and stress "
                    "responses became normal, and that is what feels "
                    "hardest to change. The body is not signing secret "
                    "contracts against you."
                ),
            },
            {
                "question": "Will I always crave the foods I crave now?",
                "answer": (
                    "Probably not. Most cravings shift as the body and "
                    "routine change. The thoughts that feel permanent "
                    "today are usually thoughts produced by the body and "
                    "lifestyle you have right now. When the body changes, "
                    "the mind tends to follow, even if it lags by months."
                ),
            },
            {
                "question": "What's a realistic rate of fat loss after long-term obesity?",
                "answer": (
                    "Roughly 0.5 to 1 percent of body weight per week is "
                    "sustainable for most people. The first month often "
                    "shows more because of water. Then the rate steadies "
                    "into a quieter, less photogenic version. The total "
                    "trajectory matters more than any single week's number."
                ),
            },
            {
                "question": "How should I track if the long game is mine?",
                "answer": (
                    "Use weekly check-ins, not daily verdicts. Photos, "
                    "fit, waist measurements, and a rolling weight average "
                    "over three to four weeks. The body is moving slower "
                    "than emotion is. Daily readings make panic more "
                    "persuasive than progress, which is the worst "
                    "combination over years."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 6. why-is-my-appetite-stronger-on-a-diet
    # ------------------------------------------------------------------
    "why-is-my-appetite-stronger-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why is my appetite stronger the longer I diet?",
            "answer": (
                "Because dieting changes hunger signaling over time. "
                "Restriction makes ordinary food feel more important than "
                "it is. The first weeks run on novelty and momentum. "
                "Several weeks in, the system stops cooperating and food "
                "gets louder, both in the stomach and in the head. That "
                "usually means a pattern problem, not a willpower problem."
            ),
        },
        "faqItems": [
            {
                "question": "Why does the early phase feel easier than the middle?",
                "answer": (
                    "Because momentum carries the first stretch. The plan "
                    "is fresh, the rules feel meaningful, and the scale "
                    "is generous. People often mistake that phase for "
                    "being disciplined. The harder phase comes later, "
                    "when the system has had time to argue back."
                ),
            },
            {
                "question": "What's the difference between hunger and food noise?",
                "answer": (
                    "Hunger is general, patient, and stomach-based. Any "
                    "reasonable meal satisfies it. Food noise is loud in "
                    "the head, specific, and does not quiet down even "
                    "after eating. Food noise usually points to a system "
                    "problem — too much restriction, too little variety — "
                    "not a character flaw."
                ),
            },
            {
                "question": "Why do cheat meals start feeling so emotional?",
                "answer": (
                    "Because the rest of the week became joyless. When "
                    "food gets moralized, ordinary meals turn into "
                    "anticipation, fantasy, and resentment. The cheat "
                    "meal stops being a meal and becomes scheduled relief. "
                    "That is why so many of them turn into binges instead of meals."
                ),
            },
            {
                "question": "What usually quiets appetite back down?",
                "answer": (
                    "Meals that are actually satisfying. Less mythology "
                    "around specific foods. Fewer all-or-nothing swings. "
                    "A structure you can stay inside without fantasizing "
                    "about escape all day. Once cravings stop being "
                    "treated as character verdicts, the system has space to settle."
                ),
            },
            {
                "question": "Is louder appetite a sign I should quit the diet?",
                "answer": (
                    "Not automatically. It is a sign the system needs "
                    "adjustment, not abandonment. A planned diet break, a "
                    "small calorie bump, or fewer banned foods often "
                    "fixes it within a couple of weeks. Quitting because "
                    "of louder appetite usually starts the next round at "
                    "the same pattern."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 7. why-is-the-middle-of-weight-loss-the-hardest
    # ------------------------------------------------------------------
    "why-is-the-middle-of-weight-loss-the-hardest": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why is the middle of weight loss the hardest stretch?",
            "answer": (
                "Because the dramatic feedback is gone and the work has "
                "not ended. The first 5 kg often come from water, better "
                "sleep, and accidental protein increases. The middle is "
                "when the body starts negotiating, the novelty fades, and "
                "the diet becomes boring. Most transformation content "
                "skips it because the middle is not a story."
            ),
        },
        "faqItems": [
            {
                "question": "Is the middle the same as a plateau?",
                "answer": (
                    "No. A plateau is the body holding under the same "
                    "conditions for three or more weeks. The middle is "
                    "broader: the easy wins are gone, motivation has "
                    "thinned, and the work has become unphotogenic. The "
                    "graph still moves; it just moves quietly."
                ),
            },
            {
                "question": "Why do most people quit during this phase?",
                "answer": (
                    "Because the dopamine drops at the same time the work "
                    "continues. Visible feedback stops. Compliments slow. "
                    "The plan still demands the same things and gives "
                    "back less. People assume something is wrong with the "
                    "program. Usually the program is fine. The middle is "
                    "the cost of being in one."
                ),
            },
            {
                "question": "Should I change the plan if the middle drags?",
                "answer": (
                    "Usually not. Chasing a new plan in the middle is "
                    "almost always a way to feel busy without making "
                    "progress. The middle keeps asking for novelty "
                    "because novelty feels like motion. It is not. The "
                    "skill in the middle is staying boring while the body adapts."
                ),
            },
            {
                "question": "How long does the middle usually last?",
                "answer": (
                    "Months three through nine for most longer cuts. Some "
                    "people get out earlier; many take longer. The exact "
                    "length matters less than recognizing what phase you "
                    "are in. Treating month four like month one is the "
                    "fastest way to make month five worse than it had to be."
                ),
            },
            {
                "question": "What is actually happening to the body in the middle?",
                "answer": (
                    "Habits are becoming structure. The body is learning "
                    "what the new normal is. Composition shifts are "
                    "quietly continuing. Maintenance calories are dropping "
                    "as the body gets smaller. None of that photographs "
                    "well. All of it is the program doing the thing it is "
                    "supposed to do."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 8. is-my-stomach-bloat-or-fat
    # ------------------------------------------------------------------
    "is-my-stomach-bloat-or-fat": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I tell if my stomach is bloat or fat?",
            "answer": (
                "Time it across days, not minutes. Bloat moves; fat does "
                "not. The body cannot synthesize 1.5 kg of fat overnight — "
                "that would take roughly 11,000 calories above maintenance "
                "in a day. Real fat gain is slow, gradual, and survives a "
                "normal week. If the spike clears in three days, it was "
                "never fat."
            ),
        },
        "faqItems": [
            {
                "question": "Can I really gain 1.5 kg of fat overnight?",
                "answer": (
                    "No. That would require roughly 11,000 calories above "
                    "maintenance in 24 hours, and you would remember "
                    "doing it. Overnight scale jumps of 1 to 2 kg are "
                    "almost entirely water, sodium, glycogen, and food "
                    "still moving through digestion. Fat does not arrive that fast."
                ),
            },
            {
                "question": "What does real fat gain look like on the scale?",
                "answer": (
                    "Slow, quiet, and unglamorous. Usually a gradual drift "
                    "of 0.5 to 1 kg over two to four weeks that does not "
                    "reverse after a normal day. The daily noise is still "
                    "there, but the trendline is moving in one direction "
                    "across multiple weeks."
                ),
            },
            {
                "question": "How can I tell which is which in the moment?",
                "answer": (
                    "Usually you cannot, in the moment. That is the point. "
                    "Wait four days, weigh again under your usual "
                    "conditions. If the spike has cleared, it was bloat. "
                    "If it has held across three consecutive measurements "
                    "under usual conditions, then it is worth looking at."
                ),
            },
            {
                "question": "What about how the mirror looks?",
                "answer": (
                    "The mirror is worse than the scale for this. Bloat "
                    "changes how you look dramatically within hours. Fat "
                    "changes how you look slowly over weeks. If you "
                    "thought you looked smaller yesterday and larger "
                    "today, you are looking at bloat, not at a body change."
                ),
            },
            {
                "question": "Is it ever worth panicking about a one-day spike?",
                "answer": (
                    "No. There is no decision you can make on a one-day "
                    "spike that a calmer decision three days later would "
                    "not also catch. Over-reacting almost always leads to "
                    "a binge or skipped meal that does more damage than "
                    "the original blip. Waiting costs nothing."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 9. why-does-my-body-look-different-from-different-angles
    # ------------------------------------------------------------------
    "why-does-my-body-look-different-from-different-angles": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why does my body look different from different angles?",
            "answer": (
                "Because most people only ever check the front view. The "
                "back can change weeks before the front catches up. "
                "Different bodies carry fat differently, and the front "
                "view often holds the stubborn lower-belly buffer the "
                "longest. The back loses shape first for many people, "
                "and the front mirror cannot answer that question."
            ),
        },
        "faqItems": [
            {
                "question": "Why doesn't the front mirror catch progress?",
                "answer": (
                    "Because it shows the same view every morning, and "
                    "that view is often the slowest one to change. The "
                    "front holds the deepest fat for many people. The "
                    "mirror you see most is also the one with the least "
                    "new information to give you."
                ),
            },
            {
                "question": "What changes show up in the back view first?",
                "answer": (
                    "The dip between the shoulder blades. The slope from "
                    "waist to hip. Whether the lats have any shape. How "
                    "the glute sits relative to the thigh. Where fat loss "
                    "is starting. The bra line loosening. None of that is "
                    "visible in a front mirror."
                ),
            },
            {
                "question": "How often should I take a back-angle photo?",
                "answer": (
                    "Every two weeks. Same spot, same lighting, same "
                    "shirt or no shirt. Save them in a folder and look at "
                    "them in groups of four. Daily back photos are noise. "
                    "Two-week comparisons start to show the actual story "
                    "the front mirror is missing."
                ),
            },
            {
                "question": "Why does lighting and angle change the verdict so much?",
                "answer": (
                    "Because a body in the same condition can be "
                    "photographed thinner or heavier depending on the "
                    "camera height, the light direction, and posture. "
                    "Lifting the camera a few centimeters changes the "
                    "entire silhouette. Holding posture for the photo, "
                    "or not, changes the waist by 1 to 2 cm."
                ),
            },
            {
                "question": "What if the back changed but I still feel the same about my body?",
                "answer": (
                    "That is normal. The head adapts slower than the body. "
                    "Even after weeks of visible change, the internal "
                    "image is calibrated against the older version. The "
                    "fix is not more checking. The fix is letting weeks "
                    "of dated proof slowly outvote the daily mirror."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 10. how-to-stop-using-exercise-as-punishment
    # ------------------------------------------------------------------
    "how-to-stop-using-exercise-as-punishment": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I stop using exercise as punishment?",
            "answer": (
                "Change what the workout is paying for. Punishment-training "
                "closes the loop between effort and food, which makes "
                "rest days feel like unpaid debt. Stop weighing yourself "
                "right after sessions. Train on a fixed cadence, not a "
                "guilt cadence. The same workout shifts when it stops "
                "being a receipt for what you ate."
            ),
        },
        "faqItems": [
            {
                "question": "What does punishment training actually cost you?",
                "answer": (
                    "Three things. Rest days start feeling morally "
                    "dangerous, so you overcompensate later. Hard sessions "
                    "land on bad sleep and underfed mornings, because "
                    "mood drives them, not readiness. And you slowly "
                    "start disliking your body more, because every "
                    "session is evidence of something you did wrong."
                ),
            },
            {
                "question": "Why does weighing post-workout reinforce the loop?",
                "answer": (
                    "Because it ties effort to a number that is mostly "
                    "water retention from the session. The scale rises "
                    "slightly. The mood drops. The next session starts "
                    "angrier. Breaking the post-workout weigh-in habit is "
                    "one of the smallest changes that produces the "
                    "biggest shift in how training lands."
                ),
            },
            {
                "question": "What does therapy training look like instead?",
                "answer": (
                    "Boring, mostly. Same lifts. Same cadence. Same days. "
                    "The sessions stop carrying mood. You walk in without "
                    "something to regulate. You walk out without needing "
                    "the scale to validate the effort. The training "
                    "starts working on the rest of the day instead of "
                    "the other way around."
                ),
            },
            {
                "question": "Doesn't this mean training has to be soft?",
                "answer": (
                    "No. The lifts can still be heavy. The intervals can "
                    "still be hard. The recovery can still be real. What "
                    "changes is the emotional function of the session. "
                    "The body knows the difference between hard work and "
                    "apology. So does the body's response to it."
                ),
            },
            {
                "question": "How long does the shift take?",
                "answer": (
                    "Usually a few weeks of training without the scale "
                    "right after. The change is not announced. You "
                    "notice, weeks later, that you walked into a session "
                    "without a mood to regulate. That noticing is the "
                    "signal that the old loop has finished closing."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 11. why-do-i-weigh-more-at-night
    # ------------------------------------------------------------------
    "why-do-i-weigh-more-at-night": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why do I weigh more at night than in the morning?",
            "answer": (
                "Food, water, and salt have moved through you all day. "
                "Evening weight is typically 0.8 to 1.8 kg higher than "
                "morning weight. None of that is fat. Morning is the "
                "lowest sample because you are mildly dehydrated, your "
                "bladder is empty, and you have not eaten. Both readings "
                "are honest — they answer different questions."
            ),
        },
        "faqItems": [
            {
                "question": "What is morning weight actually showing?",
                "answer": (
                    "The bottom of your daily range. You are lightly "
                    "dehydrated overnight, you have emptied most of your "
                    "bladder, and you have not eaten. That is why morning "
                    "weighing is the most stable reference across days. "
                    "It is one sample, not a complete picture of the body."
                ),
            },
            {
                "question": "Why is the gap between morning and evening so wide?",
                "answer": (
                    "Water retention shifts through the day. Food sits in "
                    "the digestive tract for hours. Sodium intake peaks "
                    "around dinner. Carbs bind about 3 grams of water "
                    "per gram of stored glycogen. A 1.5 kg morning-to-evening "
                    "swing is normal and means nothing about fat."
                ),
            },
            {
                "question": "Should I weigh in the morning or the evening?",
                "answer": (
                    "If you weigh once a day, morning is the cleanest "
                    "baseline. If you weigh at multiple times, do not "
                    "mix them in your head. Compare evenings to evenings, "
                    "mornings to mornings. The scale is not lying at "
                    "either time. It is answering different questions."
                ),
            },
            {
                "question": "Is one reading enough to judge progress?",
                "answer": (
                    "No. One reading tells you almost nothing. Seven "
                    "readings under the same conditions tell you the "
                    "shape of the week. Compare this week's average to "
                    "last week's average, not today's number to "
                    "yesterday's. Daily numbers are noise. Weekly trends "
                    "are signal."
                ),
            },
            {
                "question": "What if my evening weight has been creeping up?",
                "answer": (
                    "If both your evenings and your mornings are drifting "
                    "up across two to three weeks under the same "
                    "conditions, that is real movement. If only your "
                    "evenings shifted while mornings held, you probably "
                    "ate saltier or larger dinners that week. Keep the "
                    "comparison consistent."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 12. do-vegetables-help-you-feel-full-on-a-diet
    # ------------------------------------------------------------------
    "do-vegetables-help-you-feel-full-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "Do vegetables help you feel full on a diet?",
            "answer": (
                "Yes, more than people give them credit for. They add "
                "volume without much energy, slow digestion through fiber, "
                "increase chewing time, and quietly displace denser "
                "calories on the plate. A meal with a real vegetable "
                "component holds appetite for hours. Most diets that fail "
                "in the evening were under-vegged at lunch."
            ),
        },
        "faqItems": [
            {
                "question": "Why does protein-only dieting often stall?",
                "answer": (
                    "Because high-protein, low-volume meals leave the "
                    "stomach feeling unused even when calories are "
                    "technically met. The afternoon starts looking for "
                    "snacks. The evening starts looking for relief. "
                    "Adding a real vegetable component to the same meal "
                    "usually fixes that without changing protein or calories."
                ),
            },
            {
                "question": "How much volume actually helps?",
                "answer": (
                    "Disproportionate volume, not a side salad. A real "
                    "vegetable component on most plates — large bowl, "
                    "full half of the plate, real cooked portion — does "
                    "the work. A tablespoon of spinach does not. Fresh, "
                    "frozen, roasted, or raw all count. Whatever form "
                    "you will actually eat."
                ),
            },
            {
                "question": "Are frozen vegetables as good as fresh?",
                "answer": (
                    "For dieting purposes, yes. Frozen vegetables go from "
                    "freezer to plate in four minutes, do not spoil, and "
                    "count for the same fiber and volume work. Most "
                    "weeknight diet failures are vegetable-skipping "
                    "because fresh produce decayed in the fridge before "
                    "it could be cooked."
                ),
            },
            {
                "question": "Which vegetables work best for satiety?",
                "answer": (
                    "The exact ones matter less than people think. "
                    "Anything green, leafy, or fibrous adds the volume "
                    "and fiber that flatten the appetite curve. Broccoli, "
                    "cabbage, spinach, peppers, mushrooms, and green "
                    "beans all work. The vegetable you will actually cook "
                    "three times this week is the right pick."
                ),
            },
            {
                "question": "What does a good plate composition look like?",
                "answer": (
                    "A protein source, a starch or carb appropriate to "
                    "the calorie target, and a disproportionately large "
                    "vegetable component. Disproportionate is the part "
                    "most people skip. Not a side salad. A real cooked "
                    "portion, present at most meals. Over a week, that "
                    "structure outperforms any single rule."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 13. why-do-you-lose-so-much-weight-first-week
    # ------------------------------------------------------------------
    "why-do-you-lose-so-much-weight-first-week": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why do you lose so much weight the first week of a diet?",
            "answer": (
                "Mostly water, glycogen, salt balance, and a temporary "
                "digestive clearing. A 3 kg drop in week one is often "
                "only 0.3 kg of actual fat and 2.7 kg of fluid and food "
                "volume. Week two looks like nothing happened, but it is "
                "the first honest data point. The real diet starts around "
                "day fifteen."
            ),
        },
        "faqItems": [
            {
                "question": "How much of week one's drop is actually fat?",
                "answer": (
                    "Roughly 0.2 to 0.5 kg for most people in a "
                    "reasonable deficit. The rest is water from glycogen "
                    "depletion, lower sodium retention from less "
                    "processed food, and a one-time empty-out of "
                    "digestive backlog. Real fat loss in week one is the "
                    "smallest part of the number."
                ),
            },
            {
                "question": "Why does week two look like the diet stopped?",
                "answer": (
                    "Because the water and glycogen drop has stabilized. "
                    "What moves now is mostly fat, and fat moves slowly. "
                    "Week two usually shows 0.3 to 0.8 kg loss, sometimes "
                    "nothing, sometimes a small upward blip. None of that "
                    "means failure. It means week one was misleading."
                ),
            },
            {
                "question": "Should I lock in a weekly target based on week one?",
                "answer": (
                    "No. A week-one target builds the wrong expectation "
                    "for every week after. Most diets fail at week two "
                    "because the person was anchored to a 3 kg week and "
                    "read 0.3 kg as broken. Use the third or fourth week "
                    "as the basis for what your real rate is."
                ),
            },
            {
                "question": "Should I weigh daily during week one?",
                "answer": (
                    "Probably not. Week one is mostly fluid noise. Daily "
                    "readings during this phase teach you to interpret "
                    "water shifts as fat changes, which sets up bad "
                    "habits for the rest of the program. A weekly "
                    "weigh-in or a rolling average reads the trend more honestly."
                ),
            },
            {
                "question": "When does the diet start telling the truth?",
                "answer": (
                    "Around week three. By then the water effects have "
                    "stabilized, the new eating pattern has become more "
                    "consistent, and the scale starts reflecting actual "
                    "body composition change. Almost every serious "
                    "transformation across coaching contexts follows this "
                    "pattern: fast week, slow week, honest week."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 14. how-to-eat-at-social-events-on-a-diet
    # ------------------------------------------------------------------
    "how-to-eat-at-social-events-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I eat at social events on a diet?",
            "answer": (
                "Eat normally around the event, not before and after. "
                "Most damage happens in the under-eating before and the "
                "over-correcting after, not at the dinner itself. Skip "
                "the breakfast-skipping. Skip the morning-after "
                "restriction. Arrive not-hungry. Eat what you want at "
                "the event. Return to your plan at the next meal, not "
                "next Monday."
            ),
        },
        "faqItems": [
            {
                "question": "Should I save calories during the day for the event?",
                "answer": (
                    "No. Saving calories almost always backfires. You "
                    "arrive hungry, under-fueled, and with appetite "
                    "cranked up — the worst possible state for making "
                    "food choices around a calorie-dense spread. Eat "
                    "your normal breakfast. Eat your normal lunch. "
                    "Arrive not-hungry, not-full."
                ),
            },
            {
                "question": "What should I actually do at the event?",
                "answer": (
                    "Eat slower than you would at home. Start with "
                    "vegetables, salad, or protein before the dense "
                    "carbs and sweets. Drink water between alcoholic "
                    "drinks. Stop when done, not when the plate is "
                    "empty. There is no secret move. The slowness is "
                    "most of it."
                ),
            },
            {
                "question": "Should I avoid certain foods at the event?",
                "answer": (
                    "Not categorically. The avoidance frame usually "
                    "wrecks the night. If you label bread as forbidden "
                    "and then eat bread, the brain often reads it as "
                    "the diet is over. Decide bread is fine and one "
                    "piece stops there. The avoidance framing is more "
                    "dangerous than any single food."
                ),
            },
            {
                "question": "What should I do the morning after?",
                "answer": (
                    "Eat your normal breakfast. Drink water. Do not "
                    "weigh yourself for three to five days while the "
                    "sodium clears. Return to your plan at lunch, as if "
                    "the event was last week. The drastic morning-after "
                    "restriction is what turns one event into three "
                    "days off plan."
                ),
            },
            {
                "question": "How often can I do social events without losing progress?",
                "answer": (
                    "One a week, handled this way, has almost no effect "
                    "on a fat-loss phase. Two a week starts compressing "
                    "the deficit. Three a week is essentially a "
                    "maintenance phase. The events themselves are not "
                    "the threshold. Whether the days around them return "
                    "to plan is the threshold."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 15. why-did-i-stop-losing-weight-at-3-months
    # ------------------------------------------------------------------
    "why-did-i-stop-losing-weight-at-3-months": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why did I stop losing weight at 3 months?",
            "answer": (
                "Because four things stack quietly around month three. "
                "Maintenance calories drop as the body weighs less. "
                "Unconscious daily movement drops. Digestive efficiency "
                "shifts slightly. Appetite climbs. The diet did not "
                "break. The body adapted to it. Cutting harder usually "
                "backfires here. The fix is almost always a 7 to 14 day "
                "diet break."
            ),
        },
        "faqItems": [
            {
                "question": "Why does cutting more calories backfire here?",
                "answer": (
                    "Because it works for a week or two, then the body "
                    "adapts again. A few cycles in, you are eating 1,200 "
                    "calories a day, losing nothing, and have trained "
                    "your appetite louder, NEAT quieter, and muscle "
                    "protein down. Smaller, weaker, hungrier — and the "
                    "scale still has not moved."
                ),
            },
            {
                "question": "What is a diet break and how long should it be?",
                "answer": (
                    "Seven to fourteen days at maintenance calories. Not "
                    "a binge, not a cheat day. NEAT rises back up, "
                    "appetite settles slightly, and the body stops "
                    "aggressively defending its current weight. When you "
                    "return to deficit, the deficit starts working again "
                    "for another four to six weeks."
                ),
            },
            {
                "question": "Will I gain weight during a diet break?",
                "answer": (
                    "Yes, in the form of water and glycogen. Expect 1 to "
                    "2 kg in the first few days. That is normal and not "
                    "fat. It comes off when you return to deficit. The "
                    "discomfort of seeing the scale rise is the price of "
                    "breaking the plateau cleanly."
                ),
            },
            {
                "question": "How do I know the slowdown is a real plateau and not a slow week?",
                "answer": (
                    "Three consecutive weeks of no scale movement under "
                    "your usual conditions, with no shape change either. "
                    "Less than that is noise. Most month-three slowdowns "
                    "turn into resumed loss within a couple of weeks if "
                    "the response is patient instead of aggressive."
                ),
            },
            {
                "question": "Are diet breaks studied or just a coaching trick?",
                "answer": (
                    "Studied, in several formal trials. People who take "
                    "planned 7 to 14 day breaks every 4 to 8 weeks on "
                    "long diets tend to retain more muscle, report lower "
                    "hunger, and have better outcomes at six and twelve "
                    "months than people who diet straight through."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 16. why-are-my-workouts-harder-on-a-cut
    # ------------------------------------------------------------------
    "why-are-my-workouts-harder-on-a-cut": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why are my workouts harder on a cut?",
            "answer": (
                "Because there is less fuel in the tank. Glycogen is the "
                "primary fuel for intense work, and a deficit, especially "
                "a low-carb one, stores less of it. You run out faster. "
                "Sets feel heavier. Recovery between sets slows. The "
                "session is the same. The fuel is different. You are not "
                "lifting weaker — you are lifting on fumes."
            ),
        },
        "faqItems": [
            {
                "question": "Am I actually losing strength on a cut?",
                "answer": (
                    "Usually not the way you think. Absolute strength may "
                    "dip 5 to 10 percent during aggressive dieting, often "
                    "less. What dips is endurance within the session. "
                    "Come off the deficit for a week and strength tends "
                    "to return to baseline within days. The strength was "
                    "not gone. The fuel was."
                ),
            },
            {
                "question": "Should I change my training during a cut?",
                "answer": (
                    "Slightly. Keep the big lifts at reasonable "
                    "intensities to protect muscle. Reduce total volume "
                    "— fewer sets, fewer sessions if needed. Drop "
                    "circuit finishers and conditioning complexes. Stop "
                    "chasing PRs. The deficit phase is for maintaining "
                    "strength. Save push phases for when you are eating more."
                ),
            },
            {
                "question": "Should I add cardio while my workouts are getting harder?",
                "answer": (
                    "Almost never. Extra cardio on an already aggressive "
                    "deficit eats into recovery, drops NEAT later in the "
                    "day, and raises evening appetite. The session "
                    "burned 200 to 400 calories. The compensation "
                    "usually erased them. The deficit did not grow. You "
                    "just got more tired."
                ),
            },
            {
                "question": "How do I know the diet has gone too far?",
                "answer": (
                    "Four signals. Missing reps you used to hit by three "
                    "or four. Sleep degraded noticeably. Resting heart "
                    "rate up for a week or more. Mood around training "
                    "shifted from neutral to actively reluctant. Two or "
                    "more of those means step up to maintenance for a "
                    "week. Training will snap back."
                ),
            },
            {
                "question": "Why does every session feel slightly worse than the last?",
                "answer": (
                    "Because the compounding is gradual. Week one feels "
                    "normal. Week three caps your usual reps a couple "
                    "early. Week six the warmups feel heavier. Week ten "
                    "you finish thinking something is wrong. Nothing is. "
                    "You are a dieting person lifting weights, and that "
                    "is what it feels like."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 17. why-does-strength-increase-before-muscle-size
    # ------------------------------------------------------------------
    "why-does-strength-increase-before-muscle-size": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why does strength increase before muscle size?",
            "answer": (
                "Because the first six to eight weeks of lifting are "
                "mostly neural, not visual. The nervous system learns to "
                "recruit muscle you already have. Coordination improves. "
                "Stabilizers wake up. The motor pattern cleans up. The "
                "numbers move first because the body upgrades the "
                "existing tissue before deciding to commit resources to "
                "growing new tissue."
            ),
        },
        "faqItems": [
            {
                "question": "When does visible muscle growth actually start?",
                "answer": (
                    "For most recreational lifters, somewhere between "
                    "week 12 and week 16, sometimes longer. Strength "
                    "changes show up in 6 to 8 weeks. Visible shape "
                    "change runs on a slower clock. Most people quit at "
                    "week 5 to 9, right before the visual change starts."
                ),
            },
            {
                "question": "Why doesn't the body just build muscle right away?",
                "answer": (
                    "Because muscle is expensive to build. The body "
                    "tries the existing tissue first. If it can do the "
                    "job through better recruitment, it quietly upgrades "
                    "coordination and stops there. Only when the "
                    "workouts persist and the stimulus accumulates does "
                    "the body start adding new tissue as a second-stage response."
                ),
            },
            {
                "question": "How should I judge the program in the early weeks?",
                "answer": (
                    "Not on the mirror. Judge it on three things. Are "
                    "working weights going up week to week, gradually? "
                    "Are reps feeling more controlled? Is form holding "
                    "on the last set? If yes to those, the program is "
                    "working. The body will follow. The mirror is behind."
                ),
            },
            {
                "question": "Why do beginners gain strength so fast?",
                "answer": (
                    "Because they have a lot of unrecruited muscle to "
                    "wake up. The first six weeks of any program produce "
                    "the steepest neural learning curve a lifter ever "
                    "has. Lifts climb fast not because tissue grew, but "
                    "because the body finally started using what was "
                    "already there."
                ),
            },
            {
                "question": "Does this mean light weights are pointless early on?",
                "answer": (
                    "No, but consistency matters more than intensity in "
                    "the first weeks. Your job is to show up three or "
                    "four times a week and let the nervous system do its "
                    "first pass. The visual program runs on the "
                    "foundation that pass builds. Quit early, never get to it."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 18. why-progress-photos-dont-show-progress
    # ------------------------------------------------------------------
    "why-progress-photos-dont-show-progress": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why don't my progress photos show progress?",
            "answer": (
                "Because the photo changed, not the body. Lighting, "
                "posture, time of day, last night's food, sleep, and "
                "camera angle can each fake an entire month of progress "
                "in either direction. The same body in two photos can "
                "give two verdicts. Treat any single photo as a sample, "
                "not a sentence."
            ),
        },
        "faqItems": [
            {
                "question": "What makes the same body look different in two photos?",
                "answer": (
                    "Lighting direction, posture, time of day, last "
                    "night's food, sleep quality, and camera height. "
                    "Lifting the camera a few centimeters slims the "
                    "torso. Standing braced removes 1 to 2 cm at the "
                    "waist. None of those is fat loss. All of them are "
                    "the photo, not the body."
                ),
            },
            {
                "question": "Why is the photo lie more dangerous than the mirror lie?",
                "answer": (
                    "Because you can stare at a photo for weeks. You can "
                    "save it to a folder. You can compare it to last "
                    "month's photo and conclude, with what feels like "
                    "proof, that nothing is happening. The mirror only "
                    "ruins one morning. The photo can ruin the program."
                ),
            },
            {
                "question": "What does an honest progress-photo setup look like?",
                "answer": (
                    "Same room. Same time of day, ideally morning, "
                    "fasted. Same camera distance and angle, marked on "
                    "the floor. Same light source. Same posture and "
                    "stance. Most people skip this and then blame their "
                    "body when nothing shows. The setup, not the body, "
                    "was the problem."
                ),
            },
            {
                "question": "How often should I compare progress photos?",
                "answer": (
                    "Four weeks minimum. Often eight. Body composition "
                    "does not move fast enough for a one-week comparison "
                    "to mean much. Most of what changes between weekly "
                    "photos is water, glycogen, and posture, not fat or "
                    "muscle. The photo is a quarterly proof, not a "
                    "weekly check."
                ),
            },
            {
                "question": "What do I do on a bad-photo day?",
                "answer": (
                    "Wait three days. Take the photo again under your "
                    "standard conditions. The setback almost always "
                    "disappears. Bad photo days are not bad body days. "
                    "Panic-restricting on a bad photo day teaches your "
                    "body that bad days get punished, which sets up a "
                    "worse pattern than the puff itself."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 19. why-does-the-same-weight-feel-different-as-you-age
    # ------------------------------------------------------------------
    "why-does-the-same-weight-feel-different-as-you-age": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why does the same weight feel different as you age?",
            "answer": (
                "Because the same number describes a different body. "
                "Across decades, untrained adults usually lose a small "
                "amount of muscle and add a small amount of fat each "
                "year, even at constant weight. Glycogen storage drops. "
                "Recovery slows. The scale stays still while the body it "
                "describes quietly shifts underneath."
            ),
        },
        "faqItems": [
            {
                "question": "What changes underneath the same number?",
                "answer": (
                    "Three things, slowly. Body composition shifts "
                    "toward less muscle and more fat unless training "
                    "fights it. Water and glycogen storage drops, "
                    "especially in untrained bodies. Recovery from a bad "
                    "week slows. Same scale weight, very different body. "
                    "The clothes know it before the scale does."
                ),
            },
            {
                "question": "Should I chase the weight I had a decade ago?",
                "answer": (
                    "Probably not, at least not as a single number. The "
                    "body that produced that number then was made of "
                    "different things than the body trying to produce it "
                    "now. Composition is the more useful target. A waist "
                    "measurement, a clothing size, a strength baseline "
                    "— those stay honest across decades."
                ),
            },
            {
                "question": "How much does training change this trajectory?",
                "answer": (
                    "A lot. Trained adults in their thirties and beyond "
                    "hold more lean mass, store more glycogen, and "
                    "recover faster than untrained adults of the same "
                    "age. The same scale number on a trained body looks "
                    "and behaves much closer to the younger version of itself."
                ),
            },
            {
                "question": "Why does the bad-week recovery take longer with age?",
                "answer": (
                    "Because the body has not changed its rules; it has "
                    "changed its speed. A heavy weekend that cleared by "
                    "Wednesday at 22 takes until Sunday at 32. Daily "
                    "fluctuations are larger and last longer. The fix is "
                    "not weighing less. It is reading the scale on a "
                    "longer timescale."
                ),
            },
            {
                "question": "What hasn't changed across decades?",
                "answer": (
                    "Energy balance still works. Strength training still "
                    "builds muscle. Protein still preserves lean mass "
                    "during a deficit. Sleep still amplifies recovery. "
                    "Walking still adds free expenditure. The basics did "
                    "not change. The tolerances around the basics "
                    "narrowed. The same plan is just less forgiving than it used to be."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 20. am-i-really-in-a-plateau-or-tracking-wrong
    # ------------------------------------------------------------------
    "am-i-really-in-a-plateau-or-tracking-wrong": {
        "answerBox": {
            "type": "answerBox",
            "question": "Am I really in a plateau or am I tracking wrong?",
            "answer": (
                "Most plateaus are real. A meaningful share are not — "
                "they are the food log refusing to admit what the day "
                "actually contained. Estimated rice portions, oil in the "
                "pan, taste-and-bite snacks, weekend narrative-logging. "
                "Run an honest week of clean tracking before changing "
                "the plan. The cheap diagnostic catches what the "
                "expensive interventions cannot."
            ),
        },
        "faqItems": [
            {
                "question": "What does an honest tracking week actually look like?",
                "answer": (
                    "Weighing every solid food. Logging every taste, "
                    "lick, and bite while cooking. Capturing every "
                    "drink, including coffee with milk and weekend wine. "
                    "Detailed item-level logging of restaurant and "
                    "social meals. No changes to the plan. Same target. "
                    "Just clean data for seven days."
                ),
            },
            {
                "question": "Why does tracking accuracy decay over time?",
                "answer": (
                    "Because almost no one's tracking gets more accurate "
                    "over weeks. Month one runs on novelty and weighing "
                    "everything. Month three runs on eyeballing portions "
                    "you 'know.' Sometimes you do, sometimes you don't. "
                    "The error compounds quietly until the body responds "
                    "to the actual numbers."
                ),
            },
            {
                "question": "What's weekend amnesia and why does it matter?",
                "answer": (
                    "Even honest weekday tracking misses the weekend. "
                    "Saturday dinner out gets logged as 'had dinner with "
                    "friends' instead of 4 oz steak, half cup mash, half "
                    "a glass of wine, dessert split. A typical "
                    "narrative-logged weekend can hide 1,500 to 3,000 "
                    "calories. Across four weekends, the monthly deficit is gone."
                ),
            },
            {
                "question": "Isn't metabolic adaptation real?",
                "answer": (
                    "Yes, but smaller than people think. Realistic "
                    "adaptation sits in the 100 to 300 calorie per day "
                    "range at the worst extreme. That is meaningful, but "
                    "not the entire 4-week stall most people attribute "
                    "to it. Most stalls have tracking drift layered on "
                    "top of a real adaptation."
                ),
            },
            {
                "question": "What if the honest week shows nothing changed?",
                "answer": (
                    "Then the plateau is real, and now you can intervene "
                    "with confidence. Pick one move at a time: a 7 to "
                    "14 day diet break at maintenance, a 100 to 200 "
                    "calorie reduction, or an increase in non-training "
                    "activity. Three weeks per move, then re-evaluate."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 21. how-to-stop-mirror-checking-on-a-diet
    # ------------------------------------------------------------------
    "how-to-stop-mirror-checking-on-a-diet": {
        "answerBox": {
            "type": "answerBox",
            "question": "How do I stop mirror checking on a diet?",
            "answer": (
                "Go on a mirror diet. Look less, look better, look in "
                "fewer states. Cut casual checks down to two a day under "
                "structured conditions — same time, same lighting, same "
                "posture, ideally morning and fasted. Skip the worst "
                "lighting. Skip the bathroom mirror at midnight. Two "
                "structured checks beat eight opportunistic ones."
            ),
        },
        "faqItems": [
            {
                "question": "Why does more checking make the mirror louder?",
                "answer": (
                    "Because each check is information that affects the "
                    "next check. A bad-mood morning loads the next "
                    "reading. By the seventh check of the day, the "
                    "mirror is reporting on the trajectory of your mood, "
                    "not your body. Cutting the count breaks that loop."
                ),
            },
            {
                "question": "When is the loud mirror phase usually worst?",
                "answer": (
                    "Somewhere between week six and week twelve of a "
                    "meaningful cut. By then the body has changed enough "
                    "that the mirror should be cooperating, but you are "
                    "also tired, hungry, sleep-thinned, and mood-thinner. "
                    "The mirror reads all of that and presents it as "
                    "evidence about the body."
                ),
            },
            {
                "question": "Should I cover my mirrors during this phase?",
                "answer": (
                    "If a specific mirror is loudest — the full-length "
                    "one you walk past ten times a day — yes. Cover it "
                    "for two or three weeks. Keep one structured mirror "
                    "up for the morning check. Fewer casual checks does "
                    "more for body image than any pep talk."
                ),
            },
            {
                "question": "Isn't this just avoiding my body?",
                "answer": (
                    "No. A mirror diet is not avoiding the body. It is "
                    "selecting the instruments giving you useful data "
                    "this week. The mirror is the noisiest one in the "
                    "loud phase. Clothes, tape measurements, weekly "
                    "weight averages, and four-week photos do the work "
                    "while the mirror calms down."
                ),
            },
            {
                "question": "When can I come off the mirror diet?",
                "answer": (
                    "When the loud phase ends. The morning check starts "
                    "agreeing with the trend. The evening check stops "
                    "being charged. A passing glance goes back to "
                    "neutral. The structure can loosen then. If the loud "
                    "phase comes back, the diet comes back. It is not a "
                    "permanent setting."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 22. why-adding-cardio-to-a-cut-backfires
    # ------------------------------------------------------------------
    "why-adding-cardio-to-a-cut-backfires": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why does adding cardio to a cut often backfire?",
            "answer": (
                "Because the body in a deficit answers exercise much "
                "louder than a fed body does. NEAT drops. Appetite "
                "rises. Fatigue makes the rest of the day sedentary. "
                "The 300 calories burned in the session often net 80 by "
                "bedtime. A stalled cut is rarely a movement deficit. "
                "Cardio is rarely the cheapest tool to fix it."
            ),
        },
        "faqItems": [
            {
                "question": "Why does the body compensate harder during a deficit?",
                "answer": (
                    "Because it has less spare energy. In maintenance, "
                    "the body has slack and meets a 300-calorie cardio "
                    "session with mild compensation. In a deficit, it "
                    "answers louder — NEAT drops noticeably, appetite "
                    "climbs, dinner gets bigger, the next workout feels "
                    "heavier. The session math overestimates the result."
                ),
            },
            {
                "question": "What should I try before adding cardio to break a stall?",
                "answer": (
                    "Almost anything else. Run an honest tracking week. "
                    "Take a 7 to 14 day diet break at maintenance. Add "
                    "daily walking instead of structured cardio. Adjust "
                    "the deficit by 100 to 200 calories. Hold the line "
                    "for two more weeks. All of those are cheaper than "
                    "added cardio."
                ),
            },
            {
                "question": "When does cardio actually help a cut?",
                "answer": (
                    "Three cases. When daily activity is genuinely low "
                    "and there is no other way to raise it. When the "
                    "cardio is low-intensity, low-duration, and not "
                    "adjacent to lifting days. When you would do it "
                    "anyway because you enjoy it. Outside those, cardio "
                    "additions tend to underperform."
                ),
            },
            {
                "question": "How is a daily walk different from a cardio session?",
                "answer": (
                    "A 30 minute walk in flat shoes does not trigger "
                    "the same fatigue compensation downstream. Steps "
                    "spread across the day cost almost nothing in "
                    "behavioral interest. A 60 minute run leaves the "
                    "rest of the day sedentary. Same calorie math on "
                    "paper. Different cost in real life."
                ),
            },
            {
                "question": "How do I know cardio is breaking the cut, not just failing it?",
                "answer": (
                    "When recovery debt is building, sleep is degrading, "
                    "lifts have stopped progressing, and the mood around "
                    "training has gone brittle. Around week three of "
                    "aggressive added cardio, the cut becomes "
                    "incompatible with the rest of life. That is the "
                    "threshold for stepping back to maintenance for a week."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 23. does-cutting-sodium-cause-water-retention
    # ------------------------------------------------------------------
    "does-cutting-sodium-cause-water-retention": {
        "answerBox": {
            "type": "answerBox",
            "question": "Does cutting sodium cause a water-retention rebound?",
            "answer": (
                "Yes, when you return to normal sodium intake. Cutting "
                "hard for two days drops 1 to 2 kg of water that comes "
                "back inside 48 to 72 hours of normal eating. The number "
                "rewarded the move. The body did not lose fat. Aggressive "
                "sodium restriction flatters bad systems and makes the "
                "rest of the diet brittle."
            ),
        },
        "faqItems": [
            {
                "question": "What is the fast scale drop actually measuring?",
                "answer": (
                    "Extracellular water. Sodium controls extracellular "
                    "water balance, and the body responds to intake "
                    "changes within 24 to 72 hours. Cutting from 3,000 "
                    "mg to 1,500 mg per day for two days drops 1 to 2 "
                    "kg of held water in most people. None of that is fat."
                ),
            },
            {
                "question": "Why does the system get harder to hold under low sodium?",
                "answer": (
                    "Food gets less satisfying. Cravings rise. Sleep "
                    "can fragment from extra bathroom trips. Performance "
                    "drops in hard sessions. None of those costs show up "
                    "on the scale. They show up in the rest of the day, "
                    "and the diet that started feeling more disciplined "
                    "ends up more brittle."
                ),
            },
            {
                "question": "Why do people keep doing it anyway?",
                "answer": (
                    "Because the feedback is fast, the number is real, "
                    "and the alternative is slow. Most diet "
                    "interventions take weeks to show. Sodium "
                    "manipulation shows in 48 hours. The brain rewards "
                    "fast feedback regardless of what the feedback "
                    "means. The slow path is unrewarding day to day."
                ),
            },
            {
                "question": "What does an honest sodium policy look like?",
                "answer": (
                    "Eat in your normal range most days, somewhere "
                    "between 2,300 and 4,000 mg depending on activity "
                    "and climate. Do not chase sodium drops as a "
                    "strategy. Use sodium awareness to interpret "
                    "fluctuation, not to control it. The scale is for "
                    "trend reading. Sodium is for taste."
                ),
            },
            {
                "question": "When is sodium control actually appropriate?",
                "answer": (
                    "Three legitimate cases. A clinician-prescribed "
                    "target for cardiovascular conditions. Bodybuilding "
                    "stage prep or weight-class athletes running a "
                    "planned protocol with a defined endpoint. Acute "
                    "medical edema. Outside those, aggressive "
                    "restriction flatters the scale and degrades the "
                    "rest of the diet for almost no real benefit."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 24. why-am-i-so-hungry-after-lifting-weights
    # ------------------------------------------------------------------
    "why-am-i-so-hungry-after-lifting-weights": {
        "answerBox": {
            "type": "answerBox",
            "question": "Why am I so hungry after lifting weights?",
            "answer": (
                "Because appetite tracks training volume and recovery, "
                "not body weight. The body's energy demand spikes 6 to "
                "36 hours after a real session and stays elevated "
                "through the recovery window. Add a poor night of sleep "
                "and the signal climbs further. Most diet hunger is not "
                "failure. It is a repair signal asking for fuel."
            ),
        },
        "faqItems": [
            {
                "question": "What variables actually drive day-to-day appetite?",
                "answer": (
                    "Three matter more than weight. Training volume in "
                    "the past 24 to 72 hours. Sleep across the past "
                    "three to five nights. The body's recent repair "
                    "load. A lifter who trained heavy yesterday and "
                    "slept six hours will be hungrier than a sedentary "
                    "person who slept eight."
                ),
            },
            {
                "question": "When does training-driven hunger actually show up?",
                "answer": (
                    "Six to 36 hours after the session. A heavy "
                    "lower-body Monday morning often shows up as "
                    "elevated hunger Tuesday afternoon and evening. A "
                    "long Sunday cardio session tends to peak Monday "
                    "afternoon. Sleep deprivation is faster — usually "
                    "the same day and the day after a poor night."
                ),
            },
            {
                "question": "Should I feed training-driven hunger or push through?",
                "answer": (
                    "Feed it, especially on hard training days. The "
                    "repair demand is real. Adding 100 to 200 calories "
                    "of protein-forward food on a heavy session day is "
                    "not breaking the diet. It is feeding the work the "
                    "diet is supposed to support. Pushing through "
                    "usually backfires by week's end."
                ),
            },
            {
                "question": "How can I tell if my hunger is training, sleep, or actual food shortage?",
                "answer": (
                    "Track training intensity and a rolling sleep "
                    "average alongside calories. Within three to four "
                    "weeks the pattern usually shows. Loud-appetite "
                    "weeks line up with high training and low sleep. "
                    "Quiet weeks line up with the opposite. Body weight "
                    "has almost no week-to-week relationship with how "
                    "hungry the body feels."
                ),
            },
            {
                "question": "Why don't more dieters know this?",
                "answer": (
                    "Because diet narratives frame appetite as a "
                    "function of body size and willpower. Athletes are "
                    "taught to read appetite through training and "
                    "recovery. The first framing maps onto the actual "
                    "physiology. The second produces 'the diet is "
                    "failing' diagnoses for what are really hard-training nights."
                ),
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Sanity assertions — kept inline so any edit accidentally breaking the
# 24-entry contract or the SCHEMA_TYPES alignment fails loudly at import.
# ---------------------------------------------------------------------------

assert len(FEATURED_SNIPPETS) == 24, (
    f"Expected 24 entries, got {len(FEATURED_SNIPPETS)}"
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

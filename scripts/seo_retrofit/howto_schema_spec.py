"""
HowTo schema content for action-oriented (`how-to-*`) blog posts.

Per `marketing/fitness_blogging/blog_strategy/seo_optimization_rules.md` and
the `BlogStructuredData` component:

- A post with `schemaType: 'howto'` and a `howToSteps` array gets HowTo
  JSON-LD emitted alongside its Article schema. Google rewards 5+ steps with
  HowTo carousel surfaces in SERP.
- Each step is `{name, text}`. The on-site rendering picks `post.title` for
  the schema's `name`, so the `"name"` here is identification metadata for
  the apply script and reviewer; the JSON-LD itself draws from posts.ts.

Voice rules (CRITICAL):
- Voice = pkang's: founder-led, anti-hype, observational, dry, direct.
- Forbidden words: ultimate, secret, shocking, life-changing,
  transform your body, guaranteed, fast results, you won't believe,
  crazy, insane.
- Each step text = 25-50 words, drawn from the source post's actual body
  (not invented). Concrete numbers and conditions where the post had them.
- Each post: 4-6 steps (Google rewards 5+).

Posts already carrying `schemaType: 'faq'` keep their FAQ schema — the
`BlogStructuredData` component emits FAQPage JSON-LD off `faqItems` even
when `schemaType` is `'howto'`, so both schemas coexist on those posts.
We're being conservative: HowTo only goes on `how-to-*` slugs, never on
question-shaped slugs (e.g. `should-i-weigh-myself-every-day-on-a-diet`)
even when their content is action-oriented.

The application script (apply_howto_schema.py, to be written) will:
1. Set `schemaType: 'howto'` on each post in posts.ts (overriding any
   prior `'faq'`; FAQ continues to emit because `faqItems` are auto-
   harvested from `type: 'faq'` sections regardless of `schemaType`).
2. Insert the `howToSteps` array on the matching post entry.

13 posts. All `how-to-*` slugs in `frontend/src/content/blog/posts.ts`.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# SCHEMA_TYPES — set every entry below to 'howto' so BlogStructuredData
# emits HowTo JSON-LD alongside the existing Article schema (and the
# FAQPage schema, on posts that also carry FAQ sections).
# ---------------------------------------------------------------------------

SCHEMA_TYPES: dict[str, str] = {
    "how-to-track-body-transformation-without-the-scale": "howto",
    "how-to-stick-to-a-diet-when-progress-slows": "howto",
    "how-to-know-youre-losing-weight-without-the-scale": "howto",
    "how-to-handle-hunger-pangs-on-a-diet": "howto",
    "how-to-break-a-weight-loss-plateau": "howto",
    "how-to-stop-using-exercise-as-punishment": "howto",
    "how-to-stop-a-binge-from-becoming-a-binge-week": "howto",
    "how-to-eat-at-social-events-on-a-diet": "howto",
    "how-to-stay-at-your-goal-weight-long-term": "howto",
    "how-to-tell-if-youre-hungry-or-bored": "howto",
    "how-to-trust-slow-weight-loss-progress": "howto",
    "how-to-get-back-on-track-after-a-bad-weekend": "howto",
    "how-to-stop-mirror-checking-on-a-diet": "howto",
}


# ---------------------------------------------------------------------------
# HOWTO_SCHEMAS — each slug maps to its HowTo payload (name, description,
# and 4-6 steps). The apply script reads `steps` and writes them to the
# `howToSteps` field on the matching posts.ts entry.
# ---------------------------------------------------------------------------

HOWTO_SCHEMAS: dict[str, dict] = {
    # ------------------------------------------------------------------
    # 1. how-to-track-body-transformation-without-the-scale
    # ------------------------------------------------------------------
    "how-to-track-body-transformation-without-the-scale": {
        "name": "How to Track Body Transformation Without the Scale",
        "description": (
            "Track body transformation without daily scale obsession. Use "
            "one honest baseline, weekly check-ins, and several signals "
            "together — photos, fit, posture, waist — instead of asking one "
            "morning number to do all the work."
        ),
        "steps": [
            {
                "name": "Set one honest baseline",
                "text": (
                    "Take one clear starting photo. Not a flattering angle. "
                    "Not your best lighting. Just an honest reference point "
                    "you can compare against. Without a baseline, every "
                    "future check-in becomes a guess instead of a real "
                    "comparison."
                ),
            },
            {
                "name": "Move to weekly check-ins",
                "text": (
                    "Stop reading the body daily. Switch to one weekly "
                    "check-in at roughly the same time, under similar "
                    "conditions. The body changes slower than emotion, so "
                    "daily tracking gives mood too many chances to interfere "
                    "with the read."
                ),
            },
            {
                "name": "Track multiple signals together",
                "text": (
                    "Use weekly photos, visual changes in waist, torso, "
                    "face, and posture, plus fit on familiar clothes. Each "
                    "signal alone is partial. Read together, they give a "
                    "more stable picture than the scale ever does on its "
                    "own."
                ),
            },
            {
                "name": "Demote the scale to a supporting metric",
                "text": (
                    "Keep weighing if you want, but treat the number as one "
                    "input, not the verdict. The scale is too noisy for "
                    "daily interpretation. Let it support the photo and fit "
                    "data instead of overruling it every morning."
                ),
            },
            {
                "name": "Compare check-ins in groups, not against yesterday",
                "text": (
                    "Save check-ins in one place and compare in groups, not "
                    "against yesterday. The four-photo comparison is where "
                    "the real story shows up. Direction matters more than "
                    "any single morning's reading."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 2. how-to-stick-to-a-diet-when-progress-slows
    # ------------------------------------------------------------------
    "how-to-stick-to-a-diet-when-progress-slows": {
        "name": (
            "The Most Reliable Way to Succeed at Dieting Is Still the "
            "Least Dramatic One"
        ),
        "description": (
            "Most diets do not end with a binge. They end with a quiet week "
            "and a mood. The way to stay in is to stop reading slower middle "
            "progress as proof the plan failed."
        ),
        "steps": [
            {
                "name": "Expect early progress to be misleadingly dramatic",
                "text": (
                    "Week one's fast scale drop is mostly water from refined "
                    "food, sodium, and carbohydrate changes. Treat it as a "
                    "one-time rebate, not the regular pace. If you anchor "
                    "expectations to that first week, every later week looks "
                    "like failure."
                ),
            },
            {
                "name": "Treat slower loss later as normal",
                "text": (
                    "After the easy water leaves, the body switches to slow "
                    "fat loss. That is the program working, not breaking. "
                    "Reframe slower middle weeks as evidence the diet has "
                    "moved into its actual phase, not a sign the plan "
                    "stopped."
                ),
            },
            {
                "name": "Do not answer scale noise with punishment",
                "text": (
                    "A 1 to 2 kg jump after a salty meal is water, not new "
                    "fat. Cutting harder in response usually triggers an "
                    "under-fed week and a binge. Hold the plan for five days "
                    "before deciding the rise meant anything."
                ),
            },
            {
                "name": "Build identity around staying in",
                "text": (
                    "Stop running the diet on motivation. Build a default — "
                    "same breakfast, same training cadence, same weighing "
                    "rhythm — that runs without inspiration. The people who "
                    "finish are not more disciplined. They are more boring "
                    "and more consistent."
                ),
            },
            {
                "name": "Take a planned diet break instead of quitting",
                "text": (
                    "On a long cut, run a one-to-two-week diet break at "
                    "maintenance calories every 4 to 8 weeks. Hunger "
                    "settles, head resets, and 12-month outcomes improve "
                    "versus continuous dieting. The break is part of the "
                    "program, not a quit."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 3. how-to-know-youre-losing-weight-without-the-scale
    # ------------------------------------------------------------------
    "how-to-know-youre-losing-weight-without-the-scale": {
        "name": (
            "Don't Trust the Scale—Here's What Actually Proves You're "
            "Losing Weight"
        ),
        "description": (
            "Real fat loss often shows up in shape, fit, and where the body "
            "softens or firms before the scale fully cooperates. Use signals "
            "beyond one morning number to read whether the body is actually "
            "changing."
        ),
        "steps": [
            {
                "name": "Stop asking only whether the scale moved",
                "text": (
                    "Drop 'am I lighter?' as the only question. Replace it "
                    "with 'what is changing?' That includes which part of "
                    "the body feels different, what looks less pushed out, "
                    "what hangs differently, and what fits differently this "
                    "week."
                ),
            },
            {
                "name": "Read shape, fit, and feel together",
                "text": (
                    "Use photos, clothing fit, where the body has softened "
                    "or firmed, and posture as a stack. One signal is "
                    "partial; together they give a more stable read than the "
                    "scale alone, which is one witness, not the whole case."
                ),
            },
            {
                "name": "Be specific about where changes show up",
                "text": (
                    "Notice if the upper abdomen feels less pushed out, if "
                    "the lower section softens, if the waistline on usual "
                    "clothes loosens. Naming the location of the change "
                    "makes it harder for the mirror to argue away on a bad "
                    "day."
                ),
            },
            {
                "name": "Don't let a quiet scale erase body evidence",
                "text": (
                    "If clothes fit looser and shape is changing while the "
                    "scale is flat, the body is recomposing — losing fat and "
                    "adding small amounts of muscle. The scale missed it "
                    "because that is not what scales measure."
                ),
            },
            {
                "name": "Track visually, compare over time",
                "text": (
                    "Take photos under similar conditions and compare in "
                    "monthly windows, not week to week. Real weight loss is "
                    "often visible before the scale officially approves. "
                    "Repeated visual comparison beats one number for telling "
                    "whether the work is paying off."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 4. how-to-handle-hunger-pangs-on-a-diet
    # ------------------------------------------------------------------
    "how-to-handle-hunger-pangs-on-a-diet": {
        "name": "You Do Not Need to Love Hunger. You Need to Understand It.",
        "description": (
            "Hunger on a diet is not one signal. Normal between-meal hunger "
            "is fine; aggressive food noise that ambushes the day usually "
            "points to a food pattern problem, not a willpower problem."
        ),
        "steps": [
            {
                "name": "Stop treating all hunger like one thing",
                "text": (
                    "Separate normal hunger — patient, general, stomach-"
                    "based — from food noise that arrives specific, urgent, "
                    "and head-based. Normal hunger is part of being a "
                    "person. Food noise is usually a system problem, not a "
                    "character flaw."
                ),
            },
            {
                "name": "Inspect the food pattern before your character",
                "text": (
                    "Before blaming willpower, audit the meals. Were they "
                    "too small, too refined, too repetitive, or too low in "
                    "protein and volume? Most aggressive hunger is a meal-"
                    "design problem the diet can fix without you suffering "
                    "through it."
                ),
            },
            {
                "name": "Build meals that hold appetite for hours",
                "text": (
                    "Aim for 30 to 45 grams of protein per meal with high-"
                    "volume vegetables and some fiber. Low-volume meals "
                    "heavy in refined carbs leave most people hungry two "
                    "hours later, regardless of the calorie count on paper."
                ),
            },
            {
                "name": "Don't make fasting a morality badge",
                "text": (
                    "If intermittent fasting works for you, fine. If the "
                    "long unfed window is amplifying an evening spike, the "
                    "schedule is not saving you. The food pattern has to be "
                    "stable first. The clock alone does not rescue chaos."
                ),
            },
            {
                "name": "Aim for quieter hunger, not heroic suffering",
                "text": (
                    "Track which meals leave appetite calmer and which leave "
                    "it loud. Adjust toward calmer. The goal is a system you "
                    "can actually live with, not a daily fight you keep "
                    "winning by force until the day you don't."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 5. how-to-break-a-weight-loss-plateau
    # ------------------------------------------------------------------
    "how-to-break-a-weight-loss-plateau": {
        "name": "A Plateau Is a Data Point, Not a Failure",
        "description": (
            "Most stalled weeks are not real plateaus. The fix is rarely "
            "more deficit. Confirm the stall first, then check eating, "
            "sleep, stress, and NEAT before cutting anything else."
        ),
        "steps": [
            {
                "name": "Confirm it is actually a plateau",
                "text": (
                    "Three weeks of stable weight under your usual "
                    "conditions is a plateau. Three days is noise. Most "
                    "stalls people complain about are slow weeks called the "
                    "wrong name. Do not act on a one-week flat reading."
                ),
            },
            {
                "name": "Re-check actual eating, not perceived eating",
                "text": (
                    "Weigh a few of your usual meals and count for three "
                    "honest days. Most plateaus reveal a 100 to 300 calorie "
                    "drift that crept in unnoticed. The same plan you ate "
                    "four months ago is not the same plan today."
                ),
            },
            {
                "name": "Check your sleep",
                "text": (
                    "Poor sleep can stall weight loss cleanly even when food "
                    "is unchanged. Hormonal signals shift, NEAT drops, and "
                    "appetite rises. Aim for consistent sleep before adding "
                    "cardio or cutting calories. The fix is often outside "
                    "the diet itself."
                ),
            },
            {
                "name": "Check stress and water retention",
                "text": (
                    "Cortisol from sustained stress can hold water for weeks "
                    "and mask actual fat loss. The scale stays flat while "
                    "the body is still moving. A lower-stress week often "
                    "reveals a few pounds that were hiding behind water."
                ),
            },
            {
                "name": "Check your NEAT",
                "text": (
                    "Many people unconsciously move less as the diet "
                    "continues — fewer steps, less fidgeting, less standing. "
                    "A 30-minute daily walk often outperforms an added "
                    "cardio session. Restore movement before you add "
                    "structured exercise."
                ),
            },
            {
                "name": "Take a diet break instead of cutting more",
                "text": (
                    "On a long cut, a planned 7 to 14 day maintenance break "
                    "every 4 to 8 weeks tends to break the stall. Hunger "
                    "settles, NEAT recovers, and the deficit becomes "
                    "possible again. Cutting harder usually extends the "
                    "plateau."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 6. how-to-stop-using-exercise-as-punishment
    # ------------------------------------------------------------------
    "how-to-stop-using-exercise-as-punishment": {
        "name": "When the Workout Becomes Therapy, Not Punishment",
        "description": (
            "Most people train as repayment for what they ate. The same "
            "workout starts working differently when you stop tying each "
            "session to the scale and the food it was supposed to "
            "compensate for."
        ),
        "steps": [
            {
                "name": "Stop weighing yourself right after training",
                "text": (
                    "Post-workout weigh-ins close the receipt loop between "
                    "effort and reward. The body retains water, the scale "
                    "ticks up, your mood crashes, and the next session comes "
                    "in angrier. Move the weigh-in to the morning after "
                    "instead."
                ),
            },
            {
                "name": "Decouple the session from the food it 'paid for'",
                "text": (
                    "Show up to training on the schedule you set, "
                    "regardless of what the previous day looked like. Do not "
                    "add minutes because of dinner. Do not skip if you ate "
                    "clean. The workout is not a price tag."
                ),
            },
            {
                "name": "Train at the same cadence even on rest days",
                "text": (
                    "Rest days are part of the program, not an unpaid debt. "
                    "If skipping a session feels morally dangerous, the "
                    "framing is doing the damage. Rest days exist for the "
                    "same reason training days do — to keep the system "
                    "functional."
                ),
            },
            {
                "name": "Stop scheduling the hardest sessions on the worst days",
                "text": (
                    "Punishment-training puts the heaviest workouts on the "
                    "worst sleep, most stress, and most under-eaten "
                    "mornings. Pick training intensity based on what the "
                    "body has, not on how guilty the previous day made you "
                    "feel."
                ),
            },
            {
                "name": "Let the workout work on the day, not the day on the workout",
                "text": (
                    "A calmer session leaves you steadier for the rest of "
                    "the day — sleep, appetite, stress all benefit. The body "
                    "changes more steadily once you stop using it as "
                    "collateral. Train consistently. Let the changes happen "
                    "while you are not watching."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 7. how-to-stop-a-binge-from-becoming-a-binge-week
    # ------------------------------------------------------------------
    "how-to-stop-a-binge-from-becoming-a-binge-week": {
        "name": "How Do I Stop a Binge From Becoming a Binge Week",
        "description": (
            "One binge is a meal. A binge week is a choice that gets made "
            "in the 24 hours after. The damage is the response to the food, "
            "not the food itself."
        ),
        "steps": [
            {
                "name": "Eat your normal breakfast",
                "text": (
                    "Not a smaller one. Not a skipped one. Skipping "
                    "breakfast as punishment drops blood sugar and makes a "
                    "second binge by late afternoon highly likely. Treat the "
                    "morning after as an ordinary morning, because that is "
                    "what it is."
                ),
            },
            {
                "name": "Drink water, but not punitively",
                "text": (
                    "A reasonable amount of water settles digestion and "
                    "reduces the gut-discomfort hangover. Chugging two "
                    "litres to 'flush it out' is theatre. Hydration is "
                    "maintenance, not penance. Stop trying to make water do "
                    "moral work."
                ),
            },
            {
                "name": "Don't weigh yourself for three to five days",
                "text": (
                    "The 1 to 2 kg jump the morning after is mostly water, "
                    "sodium, and food still moving through digestion. "
                    "Reading water as fat is what triggers the next bad "
                    "day. Skip the scale until the noise clears."
                ),
            },
            {
                "name": "Return to your normal plan at the next meal",
                "text": (
                    "Lunch is a normal lunch. Dinner is a normal dinner. Do "
                    "not start over Monday — Monday keeps moving. Acting as "
                    "if yesterday was yesterday and today is today is most "
                    "of the recovery in one sentence."
                ),
            },
            {
                "name": "Don't cut calories the rest of the week",
                "text": (
                    "Your normal deficit absorbs the binge into the weekly "
                    "total over 7 to 14 days without extra effort. "
                    "Compensation usually triggers another binge or stress "
                    "water retention that makes the scale worse, not "
                    "better. The math is fine."
                ),
            },
            {
                "name": "Take a maintenance week if it has happened twice",
                "text": (
                    "If you have binged twice in seven days, eat at "
                    "maintenance for 7 to 10 days. Hunger settles, head "
                    "resets, and a return to the deficit becomes possible "
                    "without another binge. This is intervention, not "
                    "quitting."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 8. how-to-eat-at-social-events-on-a-diet
    # ------------------------------------------------------------------
    "how-to-eat-at-social-events-on-a-diet": {
        "name": "How Do I Eat Normally at Social Events",
        "description": (
            "The dinner is rarely the threat. Under-eating before the event "
            "and over-correcting after it cause most of the damage. Eat "
            "normally around the meal, eat normally at it, eat normally the "
            "day after."
        ),
        "steps": [
            {
                "name": "Eat your normal meals during the day",
                "text": (
                    "Do not save calories. Arriving hungry, under-fueled, "
                    "and with appetite cranked up is the worst possible "
                    "state for choosing food at a large spread. Normal "
                    "breakfast, normal lunch, protein at each. Show up "
                    "not-hungry, not-full."
                ),
            },
            {
                "name": "Add a small protein snack 60 to 90 minutes before",
                "text": (
                    "If the event runs later than your usual dinner time, "
                    "eat a small, protein-forward snack about an hour "
                    "before. Not to fill up. To avoid arriving starved, "
                    "which makes everything that follows louder than it "
                    "needs to be."
                ),
            },
            {
                "name": "Eat slower than you do at home",
                "text": (
                    "Social eating is a marathon, not a sprint. You want "
                    "fullness signals to arrive while the food is still in "
                    "front of you, not 30 minutes after. Start with "
                    "vegetables, salad, or protein before bread or dessert."
                ),
            },
            {
                "name": "Drink water between drinks, if you drink",
                "text": (
                    "Alcohol suppresses hunger-regulation signals and tends "
                    "to make the rest of the night feel less metered. A "
                    "glass of water between rounds keeps the night from "
                    "running away from you without any speech about "
                    "discipline."
                ),
            },
            {
                "name": "Skip the avoidance frame",
                "text": (
                    "Deciding bread is forbidden then eating bread reads to "
                    "your brain as 'the diet is over.' Deciding bread is "
                    "fine and eating one piece reads as 'I had one piece.' "
                    "The frame is more dangerous than any specific food."
                ),
            },
            {
                "name": "Eat normally the day after",
                "text": (
                    "Normal breakfast. Drink water. Skip the scale for 3 to "
                    "5 days while the water settles. Return to your plan at "
                    "lunch as if the dinner were last week. The week "
                    "absorbs the event without theatrics."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 9. how-to-stay-at-your-goal-weight-long-term
    # ------------------------------------------------------------------
    "how-to-stay-at-your-goal-weight-long-term": {
        "name": "The Kind of Person Who Stays at Their Goal Weight",
        "description": (
            "People who hold weight off for years look more bored than "
            "disciplined. The maintaining version is quieter than the "
            "losing version. The work is becoming the ordinary week."
        ),
        "steps": [
            {
                "name": "Eat similar meals most days",
                "text": (
                    "Breakfast looks like breakfast. Lunch looks like "
                    "lunch. The variance is at dinner, on weekends, or "
                    "during travel. The base week has a shape that does not "
                    "require willpower because the defaults already do most "
                    "of the work."
                ),
            },
            {
                "name": "Train consistently three to four days a week",
                "text": (
                    "Most long-term maintainers train three or four times a "
                    "week, for years, without drama. Training is part of "
                    "the week, not a punishment project. Six-day-per-week "
                    "regimens rarely survive past the loss phase, and they "
                    "do not have to."
                ),
            },
            {
                "name": "Walk more, sleep enough",
                "text": (
                    "Walking is mostly lifestyle, not a program. Most "
                    "maintainers move more than they realize during "
                    "ordinary days. Sleep is enough, not perfect. Both are "
                    "unremarkable on any given day and decisive across "
                    "years."
                ),
            },
            {
                "name": "Stop chasing a goal weight",
                "text": (
                    "Treat the current weight as your weight now, not as "
                    "the next stop on the way down. The chase ending "
                    "matters more than any single number. Long-term "
                    "maintainers had stopped optimizing the body at all by "
                    "the time I met them."
                ),
            },
            {
                "name": "Run an emergency protocol for small drifts",
                "text": (
                    "If weight drifts up 2 to 3 kg over a stretch, tighten "
                    "for two weeks without drama and return to baseline. "
                    "The tightening is a correction, not a diet. It works "
                    "because it starts early, before the drift compounds."
                ),
            },
            {
                "name": "Weigh less often, in longer windows",
                "text": (
                    "Daily weigh-ins amplify noise during maintenance "
                    "because the trend is flat. Once or twice a week under "
                    "matched morning conditions, with a weekly average, "
                    "gives a cleaner signal than chasing daily readings "
                    "that mostly reflect water and food."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 10. how-to-tell-if-youre-hungry-or-bored
    # ------------------------------------------------------------------
    "how-to-tell-if-youre-hungry-or-bored": {
        "name": "Am I Actually Hungry or Am I Bored",
        "description": (
            "Most late-afternoon and evening 'hunger' is signal mismatch. "
            "The cue is rarely in the stomach. Use a few quick checks "
            "before reaching for a snack to see what is actually being "
            "asked."
        ),
        "steps": [
            {
                "name": "Run the apple test",
                "text": (
                    "Ask yourself: would I eat an apple right now? If yes, "
                    "you are probably hungry. If no, but you want ice "
                    "cream, you are probably bored or emotionally eating. "
                    "The craving is specific. The hunger is general."
                ),
            },
            {
                "name": "Wait five minutes",
                "text": (
                    "Not as a discipline test. As a signal test. Real "
                    "hunger grows steadily over five minutes. Boredom often "
                    "does not. If the pull fades while you wait, the body "
                    "was not asking for food in the first place."
                ),
            },
            {
                "name": "Drink water or tea, change location",
                "text": (
                    "A glass of water sometimes resets the signal entirely. "
                    "Walking out of the kitchen helps too — the trigger is "
                    "often the room, not the stomach. Both are crude. Both "
                    "work often enough to be worth trying first."
                ),
            },
            {
                "name": "If the pull persists, eat intentionally",
                "text": (
                    "Eat at the table, not standing at the fridge. "
                    "Intention is what separates 'I ate a snack' from '40 "
                    "minutes of unconscious grazing I do not remember.' "
                    "Make the eating deliberate even when the choice is not "
                    "perfect."
                ),
            },
            {
                "name": "Check whether under-fueling is the real issue",
                "text": (
                    "If the boredom shows up every day at the same time "
                    "with intensity, your meals there are too small. Move "
                    "calories into protein-forward lunches and larger "
                    "breakfasts. Often the boredom problem is actually a "
                    "macronutrient timing problem in disguise."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 11. how-to-trust-slow-weight-loss-progress
    # ------------------------------------------------------------------
    "how-to-trust-slow-weight-loss-progress": {
        "name": "The Quiet Erosion of Not Believing Your Progress",
        "description": (
            "Belief gets hungry daily. Results pay out monthly. The fix is "
            "not motivation — it is small, dated proof that belief can fall "
            "back on between checkpoints when daily noise tries to argue "
            "you out of the project."
        ),
        "steps": [
            {
                "name": "Take a weekly photo under matched conditions",
                "text": (
                    "Sunday morning, same room, same posture, even when you "
                    "do not want to take it. Not for social media. For the "
                    "file. Repeated under matched conditions, the photos "
                    "give belief something to fall back on later."
                ),
            },
            {
                "name": "Note context with each weigh-in",
                "text": (
                    "Add one sentence after the number — travel, sleep, "
                    "sodium, stress for that week. So the next time you "
                    "read it back, you have context. A 0.5 kg jump after a "
                    "salty travel day reads differently with the note."
                ),
            },
            {
                "name": "Compare in monthly side-by-sides, not weekly",
                "text": (
                    "Once a month, line up your photos against your own "
                    "four-week-old photos. Not against anyone else. Week-"
                    "to-week is mostly noise. Four-week comparisons are "
                    "where the real signal lives. Save the comparison so "
                    "you can return to it."
                ),
            },
            {
                "name": "Stop relying on belief; build evidence belief can use",
                "text": (
                    "Belief is a daily signal. Results are a monthly one. "
                    "If you wait for results to feed belief, belief runs "
                    "out between checkpoints. Daily proof — small, dated, "
                    "returnable — closes the cadence gap that quietly ends "
                    "most programs."
                ),
            },
            {
                "name": "Refuse to argue with evidence on doubtful days",
                "text": (
                    "On a bad day, look at the dated proof you collected "
                    "when you were calmer. Your job is not to feel certain. "
                    "Your job is to refuse to argue with what your earlier, "
                    "less-loaded self already documented."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 12. how-to-get-back-on-track-after-a-bad-weekend
    # ------------------------------------------------------------------
    "how-to-get-back-on-track-after-a-bad-weekend": {
        "name": "The Bad Weekend That Finally Taught Me Something",
        "description": (
            "A bad weekend is rarely the actual problem. The Monday-morning "
            "scale jump is mostly water, and the binary 'on plan or off "
            "plan' framing is usually what turns one Friday into a "
            "five-day spiral."
        ),
        "steps": [
            {
                "name": "Eat your normal Monday breakfast",
                "text": (
                    "Do not skip. Do not cut. Skipping breakfast or hard "
                    "restriction usually triggers another binge by "
                    "Wednesday. Treat Monday as an ordinary Monday. Your "
                    "normal breakfast is the start of recovery, not a "
                    "punishment for the weekend."
                ),
            },
            {
                "name": "Don't weigh in for three to five days",
                "text": (
                    "The 2 to 3 kg Monday spike is mostly water from carbs, "
                    "sodium, and alcohol — not fat. Reading it as fat is "
                    "what triggers the next bad week. Step off the scale "
                    "until the water clears on its own."
                ),
            },
            {
                "name": "Return to your regular plan at the next meal",
                "text": (
                    "Lunch is a normal lunch. Dinner is a normal dinner. Do "
                    "not 'start over Monday' next week — Monday keeps "
                    "moving. Acting as if yesterday was yesterday and today "
                    "is today is most of the recovery in one sentence."
                ),
            },
            {
                "name": "Stop grading days as binary",
                "text": (
                    "Replace 'on plan or off plan' with a tolerance band of "
                    "about 300 calories per day. A 1,400-over Friday "
                    "becomes a 1,100-over-band day, not a write-off. Binary "
                    "framing is what turns one slip into three days off "
                    "plan."
                ),
            },
            {
                "name": "Use the week as the unit, not the day",
                "text": (
                    "A normal weekly deficit absorbs the weekend's "
                    "overshoot over 7 to 14 days without compensation. Read "
                    "the week, not Monday. Most fat damage from a single "
                    "bad weekend is small enough to disappear into the "
                    "trend within ten days."
                ),
            },
            {
                "name": "Build a system with a recovery mode",
                "text": (
                    "A perfect-looking program with no recovery mode breaks "
                    "the first time something normal happens. A slightly "
                    "less elegant system that bends survives. Pick the one "
                    "that bends. The one that breaks does not actually "
                    "exist; it just hides."
                ),
            },
        ],
    },

    # ------------------------------------------------------------------
    # 13. how-to-stop-mirror-checking-on-a-diet
    # ------------------------------------------------------------------
    "how-to-stop-mirror-checking-on-a-diet": {
        "name": "How to Go on a Mirror Diet When the Real Diet Is Getting Loud",
        "description": (
            "When the diet is working but the mirror is getting loud, the "
            "answer is fewer checks under cleaner conditions. The mirror "
            "does not get more honest because you confront it more — it "
            "gets less useful."
        ),
        "steps": [
            {
                "name": "Cut the daily count to two structured checks",
                "text": (
                    "If you currently check six to eight times a day, drop "
                    "to two. One in the morning at the same time after the "
                    "same routine. One brief check at the end of the day. "
                    "Everything else gets averted, walked past, ignored."
                ),
            },
            {
                "name": "Look better — match the conditions of the checks",
                "text": (
                    "The two checks happen under the same time of day, same "
                    "lighting, same fasted state in the morning, and same "
                    "posture. Structured, not opportunistic. A controlled "
                    "check gives signal. A passing glance under random "
                    "light gives noise."
                ),
            },
            {
                "name": "Look in fewer states — skip the worst lighting",
                "text": (
                    "Avoid late evening with overhead light, the bathroom "
                    "at midnight, and dressing rooms with three angles of "
                    "fluorescent. Those are not honest mirrors. They are "
                    "theatre. A mirror diet skips them entirely instead of "
                    "arguing with them."
                ),
            },
            {
                "name": "Cover the loudest mirror in your home",
                "text": (
                    "If a full-length mirror in the bedroom or hallway is "
                    "catching most of the casual checks, cover it for a few "
                    "weeks. Not as avoidance — as instrument selection. The "
                    "trend keeps going without it. The mirror loses its "
                    "accumulated mood."
                ),
            },
            {
                "name": "Use one weekly photo, compared in 4-week windows",
                "text": (
                    "Take one photo per week under the same conditions. "
                    "Save it. Do not analyze it that day. Compare every "
                    "four weeks. Week-to-week photos are mostly noise. "
                    "Four-week comparisons are where the actual signal "
                    "lives."
                ),
            },
            {
                "name": "Lean on the scale's quiet honesty when the mirror is loud",
                "text": (
                    "In the loud phase, the scale weekly average often "
                    "becomes the cleanest instrument. If the trend is down, "
                    "trust the trend. The mirror is not the lead instrument "
                    "right now. There are weeks where it is wrong about "
                    "almost everything."
                ),
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Sanity checks — fail fast at import time if a step text or description
# falls outside the spec's word-count band, or if SCHEMA_TYPES and
# HOWTO_SCHEMAS get out of sync.
# ---------------------------------------------------------------------------

def _word_count(text: str) -> int:
    return len(text.split())


def _validate() -> None:
    schema_slugs = set(SCHEMA_TYPES.keys())
    howto_slugs = set(HOWTO_SCHEMAS.keys())
    missing_in_howto = schema_slugs - howto_slugs
    missing_in_schema = howto_slugs - schema_slugs
    if missing_in_howto or missing_in_schema:
        raise ValueError(
            f"SCHEMA_TYPES / HOWTO_SCHEMAS mismatch — "
            f"missing in HOWTO_SCHEMAS: {sorted(missing_in_howto)}; "
            f"missing in SCHEMA_TYPES: {sorted(missing_in_schema)}"
        )

    for slug, payload in HOWTO_SCHEMAS.items():
        desc_words = _word_count(payload["description"])
        if not (20 <= desc_words <= 45):
            raise ValueError(
                f"{slug}: description is {desc_words} words "
                f"(spec range 25-40, soft band 20-45)"
            )
        steps = payload["steps"]
        if not (4 <= len(steps) <= 6):
            raise ValueError(
                f"{slug}: has {len(steps)} steps (spec range 4-6)"
            )
        for index, step in enumerate(steps, 1):
            text_words = _word_count(step["text"])
            if not (20 <= text_words <= 55):
                raise ValueError(
                    f"{slug}: step {index} ({step['name']!r}) is "
                    f"{text_words} words (spec range 25-50, soft band 20-55)"
                )


_validate()

"""Hero image alt text rewrites for SEO + accessibility.

Each entry pairs a blog post slug with a rewritten ``heroAlt`` string.

Rules applied to every entry:

- 60-125 characters (Google's preferred image alt length window).
- Naturally weaves in the post's primary keyword (``keywords[0]``) without
  keyword stuffing.
- Describes what the image actually shows first, then layers SEO context.
- Never opens with "Image of" or "Photo of" (Google flags those as redundant).
- Voice-neutral — alt text is a description, not editorial.
- Unique across all 64 entries (image-search dedup signal).

Source of truth for the original strings: ``frontend/src/content/blog/posts.ts``.
This module is data-only; the retrofit script reads ``HERO_ALT`` and patches
``posts.ts`` in place.
"""

HERO_ALT: dict[str, str] = {
    "how-i-lost-50-kg-middle-of-diet": (
        "Composed outdoor hanok portrait of pkang after a major transformation, "
        "the visual anchor for how I lost 50 kg over five years"
    ),
    "why-cant-i-see-weight-loss-in-the-mirror": (
        "Honest mirror check-in of pkang mid-process, framing the question, why "
        "can't I see my weight loss in the mirror"
    ),
    "should-i-weigh-myself-every-day-on-a-diet": (
        "Founder mid-process body image, framing the question, should I weigh myself "
        "every day on a diet or step back"
    ),
    "how-to-track-body-transformation-without-the-scale": (
        "Founder physique proof shot showing how to track body transformation without "
        "the scale through visible composition change"
    ),
    "why-does-the-scale-go-up-when-i-barely-eat": (
        "Honest founder mirror shot from a discouraging weigh-in week, framing why "
        "does the scale go up when I barely eat"
    ),
    "what-counts-as-a-weight-loss-plateau": (
        "Founder mid-process check-in showing the slower middle that raises the "
        "question of what counts as a weight loss plateau"
    ),
    "is-losing-5kg-in-a-week-water-weight": (
        "Founder physique comparison shot used to ask, is losing 5kg in a week water "
        "weight or actual fat loss"
    ),
    "why-am-i-not-losing-weight-anymore": (
        "Founder check-in shot from the frustrating middle of a cut, the kind of "
        "stall behind why am I not losing weight anymore"
    ),
    "skinny-fat-normal-weight-high-body-fat": (
        "Founder composition proof shot showing how skinny fat normal weight but "
        "high body fat hides behind a healthy scale"
    ),
    "how-to-stick-to-a-diet-when-progress-slows": (
        "Editorial portrait of pkang, the founder, on how to stick to a diet when "
        "progress slows down through calm consistency"
    ),
    "progress-update-body-changes-slower-than-mind": (
        "Founder portrait from a personal progress update, capturing how body changes "
        "slower than mind during weight loss"
    ),
    "how-to-know-youre-losing-weight-without-the-scale": (
        "Founder proof image of visible fat loss, demonstrating how to know you're "
        "losing weight without the scale"
    ),
    "what-to-do-after-a-binge-on-a-diet": (
        "Founder check-in shot from a difficult slip-and-recovery moment, visual "
        "context for what to do after a binge on a diet"
    ),
    "how-to-handle-hunger-pangs-on-a-diet": (
        "Founder editorial shot used for a piece on how to handle hunger pangs on a "
        "diet without binging or quitting"
    ),
    "why-cant-i-sleep-on-a-calorie-deficit": (
        "Founder reflective shot by a window, framing the article on why can't I "
        "sleep on a calorie deficit and what to do"
    ),
    "are-cheat-days-bad-for-weight-loss": (
        "Founder check-in image from a rebound-eating week, framing the question, "
        "are cheat days bad for weight loss"
    ),
    "does-one-bad-day-ruin-a-diet": (
        "Founder portrait holding the emotional logic behind the question, does one "
        "bad day ruin a diet or just dent it"
    ),
    "do-obese-people-lose-weight-slower": (
        "Founder portrait from the long-game phase, framing the question, do obese "
        "people lose weight slower than others"
    ),
    "why-is-my-appetite-stronger-on-a-diet": (
        "Founder editorial shot from the loud-hunger middle of a cut, anchoring why "
        "is my appetite stronger on a diet"
    ),
    "why-am-i-working-out-but-not-losing-weight": (
        "Founder mid-training shot from the middle phase, framing why am I working "
        "out but not losing weight on the scale"
    ),
    "why-is-the-middle-of-weight-loss-the-hardest": (
        "Founder mid-transformation portrait, neither before nor after, showing why "
        "is the middle of weight loss the hardest"
    ),
    "is-my-stomach-bloat-or-fat": (
        "Founder composition shot used to illustrate how to tell if my stomach is "
        "bloat or fat after eating or by morning"
    ),
    "how-to-break-a-weight-loss-plateau": (
        "Founder reflecting during a plateau phase, the visual anchor for how to "
        "break a weight loss plateau without panic"
    ),
    "why-does-my-body-look-different-from-different-angles": (
        "Founder shot from behind, showing back and shoulder change, context for why "
        "does my body look different from different angles"
    ),
    "past-the-messy-middle-of-weight-loss": (
        "Founder composed portrait taken after coming through and now well past the "
        "messy middle of weight loss"
    ),
    "how-to-stop-using-exercise-as-punishment": (
        "Founder in a composed mid-session shot, anchoring a piece on how to stop "
        "using exercise as punishment and train calmer"
    ),
    "is-maintenance-hunger-different-from-diet-hunger": (
        "Founder editorial shot used for a piece asking, is maintenance hunger "
        "different from diet hunger or just quieter"
    ),
    "why-some-people-never-gain-weight-no-matter-what": (
        "Founder shot of the boring long-game habits behind why do some people never "
        "gain weight no matter what they eat"
    ),
    "how-do-you-know-youve-reached-set-point": (
        "Founder image of a steady-state body, framing how do you know you've reached "
        "your set point weight without chasing a number"
    ),
    "why-do-i-weigh-more-at-night": (
        "Honest scale reading image used to explain why do I weigh more at night than "
        "in the morning, day after day"
    ),
    "does-bad-sleep-ruin-weight-loss": (
        "Founder reflective portrait capturing the quiet cost of sleep debt, the "
        "visual anchor for, does bad sleep ruin weight loss"
    ),
    "do-vegetables-help-you-feel-full-on-a-diet": (
        "Founder portrait of a calm approach to plate composition, framing the "
        "question, do vegetables help you feel full on a diet"
    ),
    "how-to-stop-a-binge-from-becoming-a-binge-week": (
        "Founder image from the morning after a binge, the decision point behind how "
        "to stop a binge from becoming a binge week"
    ),
    "why-do-others-notice-my-weight-loss-before-me": (
        "Founder mid-transformation shot, anchoring the strange experience of why do "
        "others notice my weight loss before me"
    ),
    "why-do-you-lose-so-much-weight-first-week": (
        "Founder baseline image from the earliest start of the cut, framing why do "
        "you lose so much weight the first week of a diet"
    ),
    "difference-between-weight-loss-and-fat-loss": (
        "Founder body composition shot answering what's the difference between "
        "weight loss and fat loss on the same scale number"
    ),
    "why-do-i-gain-back-more-weight-than-i-lost": (
        "Founder portrait holding the long-game discipline behind why do I gain back "
        "more weight than I lost on past diets"
    ),
    "how-to-eat-at-social-events-on-a-diet": (
        "Founder reflective shot capturing a calm approach to food off-routine, "
        "anchor for how to eat at social events on a diet"
    ),
    "how-to-stay-at-your-goal-weight-long-term": (
        "Founder portrait from the post-transformation steady state, illustrating "
        "how to stay at your goal weight long term"
    ),
    "why-did-i-stop-losing-weight-at-3-months": (
        "Founder mid-plateau portrait, calmly reading the graph, the visual anchor "
        "for why did I stop losing weight at 3 months"
    ),
    "how-to-tell-if-youre-hungry-or-bored": (
        "Founder reflective shot at the pause before a snack, illustrating how to "
        "tell if you're hungry or bored in the moment"
    ),
    "how-much-protein-do-i-need-to-lose-fat": (
        "Founder portrait framing the basic question of how much protein do I need "
        "to lose fat without overthinking it"
    ),
    "why-are-my-workouts-harder-on-a-cut": (
        "Founder mid-training shot under low-fuel conditions, anchoring why are my "
        "workouts harder on a cut than at maintenance"
    ),
    "why-does-strength-increase-before-muscle-size": (
        "Founder mid-training shot from the quiet strength curve that explains why "
        "does strength increase before muscle size shows up"
    ),
    "how-to-trust-slow-weight-loss-progress": (
        "Founder portrait between progress checkpoints, holding the long-game posture "
        "behind how to trust slow weight loss progress"
    ),
    "why-progress-photos-dont-show-progress": (
        "Founder mid-stage check-in used as a counterpoint, illustrating why progress "
        "photos don't show progress on a noisy day"
    ),
    "why-does-restriction-make-cravings-worse": (
        "Founder calm post-cheat-day portrait, framing the difference behind why does "
        "restriction make cravings worse, not weaker"
    ),
    "why-does-the-same-weight-feel-different-as-you-age": (
        "Honest scale image grounding the observation that why does the same weight "
        "feel different as you age across decades"
    ),
    "non-scale-victories-weight-loss": (
        "Founder portrait at the quiet end-state, showing the small Wednesdays behind "
        "real non scale victories weight loss looks like"
    ),
    "first-month-of-maintenance-after-weight-loss": (
        "Founder long-game portrait at the handoff into the first month of "
        "maintenance after weight loss, calmer than the cut"
    ),
    "why-am-i-hungry-at-night-but-not-during-the-day": (
        "Founder mid-process check-in framing a clean weekday, anchor for why am I "
        "hungry at night but not during the day"
    ),
    "am-i-really-in-a-plateau-or-tracking-wrong": (
        "Founder mid-stage check-in capturing the moment to ask, am I really in a "
        "plateau or am I tracking wrong"
    ),
    "life-after-50kg-weight-loss": (
        "Founder portrait at the post-loss steady state, the visual anchor for what "
        "life after 50kg weight loss actually looks like"
    ),
    "clothes-fit-better-but-scale-is-the-same": (
        "Founder composition shot from the moment a single pair of jeans explains why "
        "my clothes fit better but scale is the same"
    ),
    "how-to-get-back-on-track-after-a-bad-weekend": (
        "Founder check-in shot from a real cheat-day moment, framing how to get back "
        "on track after a bad weekend"
    ),
    "how-to-stop-mirror-checking-on-a-diet": (
        "Founder portrait of stepping back from constant checking, the visual anchor "
        "for how to stop mirror checking on a diet"
    ),
    "do-i-have-to-meal-prep-to-lose-weight": (
        "Founder reflective shot of a simple weeknight food default, framing the "
        "question, do I have to meal prep to lose weight"
    ),
    "why-adding-cardio-to-a-cut-backfires": (
        "Founder body composition shot from a stalled cut, the visual anchor for why "
        "adding cardio to a cut can backfire"
    ),
    "daily-weighing-eating-disorder-risk": (
        "Founder before-state scale image from a morning the weigh-in became weather, "
        "framing the daily weighing eating disorder risk"
    ),
    "does-cutting-sodium-cause-water-retention": (
        "Founder water-weight proof shot from a fast scale drop, anchoring whether "
        "does cutting sodium cause water retention rebound"
    ),
    "appetite-returns-during-maintenance": (
        "Founder mid-progress check-in from the week appetite returns during "
        "maintenance after weight loss and asks to be heard"
    ),
    "does-one-bad-meal-ruin-a-diet": (
        "Founder calm post-cheat-day frame at the moment one meal lands, the visual "
        "anchor for does one bad meal ruin a diet"
    ),
    "why-am-i-so-hungry-after-lifting-weights": (
        "Founder reflective shot capturing appetite tracking repair load, the anchor "
        "for why am I so hungry after lifting weights"
    ),
    "when-does-a-diet-become-a-lifestyle": (
        "Founder portrait at the steady state where the program quietly disappeared, "
        "anchoring when does a diet become a lifestyle"
    ),
}

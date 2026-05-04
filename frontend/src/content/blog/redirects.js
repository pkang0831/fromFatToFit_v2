/* eslint-disable */
/**
 * Blog slug redirects (301 permanent).
 *
 * When a post's slug is renamed for SEO reasons, add an entry here so the
 * old URL redirects to the new one. Next.js consumes this via
 * `redirects()` in `next.config.js`. All entries are permanent (HTTP 301)
 * so link equity transfers cleanly and search engines update their index.
 *
 * Entry shape: { from: <old-slug>, to: <new-slug> }
 *
 * Only track slug changes here, not URL-structure changes (those go in
 * next.config.js directly). Keep entries forever — removing one breaks
 * any backlink or bookmark pointing to the old URL.
 *
 * Written as CommonJS so it can be imported from next.config.js (which
 * is CJS) without build gymnastics.
 */

/** @type {Array<{ from: string, to: string }>} */
const blogSlugRedirects = [
  { from: 'why-your-strength-increases-before-your-shape-changes', to: 'why-does-strength-increase-before-muscle-size' },
  { from: 'why-your-workouts-feel-harder-when-youre-dieting', to: 'why-are-my-workouts-harder-on-a-cut' },
  { from: 'how-much-protein-do-i-actually-need-to-lose-fat', to: 'how-much-protein-do-i-need-to-lose-fat' },
  { from: 'am-i-actually-hungry-or-am-i-bored', to: 'how-to-tell-if-youre-hungry-or-bored' },
  { from: 'why-you-stop-losing-weight-around-month-three', to: 'why-did-i-stop-losing-weight-at-3-months' },
  { from: 'the-kind-of-person-who-stays-at-their-goal-weight', to: 'how-to-stay-at-your-goal-weight-long-term' },
  { from: 'how-do-i-eat-normally-at-social-events', to: 'how-to-eat-at-social-events-on-a-diet' },
  { from: 'why-people-gain-more-back-than-they-lost', to: 'why-do-i-gain-back-more-weight-than-i-lost' },
  { from: 'losing-weight-is-not-the-same-as-getting-leaner', to: 'difference-between-weight-loss-and-fat-loss' },
  { from: 'the-first-week-of-any-diet-is-the-most-misleading-one', to: 'why-do-you-lose-so-much-weight-first-week' },
  { from: 'you-look-different-to-other-people-before-yourself', to: 'why-do-others-notice-my-weight-loss-before-me' },
  { from: 'how-do-i-stop-a-binge-from-becoming-a-binge-week', to: 'how-to-stop-a-binge-from-becoming-a-binge-week' },
  { from: 'the-quiet-role-vegetables-play-in-staying-full', to: 'do-vegetables-help-you-feel-full-on-a-diet' },
  { from: 'sleep-debt-ruins-a-week-of-dieting-in-three-nights', to: 'does-bad-sleep-ruin-weight-loss' },
  { from: 'the-scale-lies-differently-in-the-morning-than-in-the-evening', to: 'why-do-i-weigh-more-at-night' },
  { from: 'how-do-you-know-when-youve-reached-your-set-point', to: 'how-do-you-know-youve-reached-set-point' },
  { from: 'the-friend-who-never-diets-and-never-gains', to: 'why-some-people-never-gain-weight-no-matter-what' },
  { from: 'hunger-in-maintenance-is-different-from-hunger-on-a-diet', to: 'is-maintenance-hunger-different-from-diet-hunger' },
  { from: 'when-the-workout-becomes-therapy-not-punishment', to: 'how-to-stop-using-exercise-as-punishment' },
  { from: 'progress-update-3-past-the-messy-middle', to: 'past-the-messy-middle-of-weight-loss' },
  { from: 'the-body-looks-different-from-behind', to: 'why-does-my-body-look-different-from-different-angles' },
  { from: 'a-plateau-is-a-data-point-not-a-failure', to: 'how-to-break-a-weight-loss-plateau' },
  { from: 'is-it-bloat-or-is-it-fat', to: 'is-my-stomach-bloat-or-fat' },
  { from: 'the-unglamorous-middle-of-transformation', to: 'why-is-the-middle-of-weight-loss-the-hardest' },
  { from: 'exercise-isnt-shrinking-you-the-way-you-expected', to: 'why-am-i-working-out-but-not-losing-weight' },
  { from: 'the-day-i-realized-the-program-was-just-my-life-now', to: 'when-does-a-diet-become-a-lifestyle' },
  { from: 'your-appetite-scales-with-training-volume-not-with-weight', to: 'why-am-i-so-hungry-after-lifting-weights' },
  { from: 'when-does-one-bad-meal-actually-become-a-slip', to: 'does-one-bad-meal-ruin-a-diet' },
  { from: 'the-week-my-appetite-came-back-during-maintenance', to: 'appetite-returns-during-maintenance' },
  { from: 'why-cutting-sodium-too-hard-can-backfire', to: 'does-cutting-sodium-cause-water-retention' },
  { from: 'weighing-yourself-every-day-can-be-a-trap-not-a-discipline', to: 'daily-weighing-eating-disorder-risk' },
  { from: 'why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think', to: 'why-adding-cardio-to-a-cut-backfires' },
  { from: 'do-i-actually-have-to-meal-prep-to-lose-weight', to: 'do-i-have-to-meal-prep-to-lose-weight' },
  { from: 'how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud', to: 'how-to-stop-mirror-checking-on-a-diet' },
  { from: 'the-bad-weekend-that-finally-taught-me-something', to: 'how-to-get-back-on-track-after-a-bad-weekend' },
  { from: 'clothes-tell-you-the-truth-the-mirror-cannot', to: 'clothes-fit-better-but-scale-is-the-same' },
  { from: 'progress-update-4-the-body-finally-stopped-being-the-loud-thing', to: 'life-after-50kg-weight-loss' },
  { from: 'the-plateau-that-was-actually-an-honesty-problem', to: 'am-i-really-in-a-plateau-or-tracking-wrong' },
  { from: 'why-does-my-hunger-spike-at-night-when-i-was-fine-all-day', to: 'why-am-i-hungry-at-night-but-not-during-the-day' },
  { from: 'the-first-month-of-maintenance-feels-nothing-like-the-diet', to: 'first-month-of-maintenance-after-weight-loss' },
  { from: 'the-small-wins-between-progress-updates-are-the-real-program', to: 'non-scale-victories-weight-loss' },
  { from: 'the-same-number-on-the-scale-feels-different-at-30-than-at-20', to: 'why-does-the-same-weight-feel-different-as-you-age' },
  { from: 'is-this-craving-the-food-or-the-deprivation-talking', to: 'why-does-restriction-make-cravings-worse' },
  { from: 'progress-photos-can-lie-as-much-as-the-mirror-does', to: 'why-progress-photos-dont-show-progress' },
  { from: 'the-quiet-erosion-of-not-believing-your-progress', to: 'how-to-trust-slow-weight-loss-progress' },
  { from: 'do-people-who-have-been-obese-for-years-lose-weight-more-slowly', to: 'do-obese-people-lose-weight-slower' },
  { from: 'youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth', to: 'does-one-bad-day-ruin-a-diet' },
  { from: 'if-your-diet-broke-your-sleep-it-is-not-discipline-anymore', to: 'why-cant-i-sleep-on-a-calorie-deficit' },
  { from: 'you-do-not-need-to-love-hunger-you-need-to-understand-it', to: 'how-to-handle-hunger-pangs-on-a-diet' },
  { from: 'dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight', to: 'how-to-know-youre-losing-weight-without-the-scale' },
  { from: 'progress-update-2-the-body-changed-slower-than-my-head-did', to: 'progress-update-body-changes-slower-than-mind' },
  { from: 'the-scale-can-say-normal-and-still-tell-you-nothing-useful', to: 'skinny-fat-normal-weight-high-body-fat' },
  { from: 'the-most-important-reason-you-think-youre-not-losing-weight', to: 'why-am-i-not-losing-weight-anymore' },
  { from: 'why-losing-5kg-in-a-week-usually-means-water-not-fat', to: 'is-losing-5kg-in-a-week-water-weight' },
  { from: 'what-actually-counts-as-a-weight-loss-plateau', to: 'what-counts-as-a-weight-loss-plateau' },
  { from: 'why-it-feels-like-you-gain-weight-even-when-you-barely-eat', to: 'why-does-the-scale-go-up-when-i-barely-eat' },
  { from: 'how-to-track-body-transformation-without-obsessing-over-the-scale', to: 'how-to-track-body-transformation-without-the-scale' },
  { from: 'why-appetite-feels-stronger-the-longer-you-diet', to: 'why-is-my-appetite-stronger-on-a-diet' },
  { from: 'cheat-days-do-not-expose-your-character-they-expose-your-system', to: 'are-cheat-days-bad-for-weight-loss' },
  { from: 'read-this-before-you-try-to-fix-your-diet-slip', to: 'what-to-do-after-a-binge-on-a-diet' },
  { from: 'one-emotional-weigh-in-can-wreck-a-good-week', to: 'should-i-weigh-myself-every-day-on-a-diet' },
  { from: 'why-the-mirror-can-make-real-progress-feel-fake', to: 'why-cant-i-see-weight-loss-in-the-mirror' },
  { from: 'why-i-built-devenira-for-the-weeks-where-you-want-to-quit', to: 'how-i-lost-50-kg-middle-of-diet' },
  { from: 'the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one', to: 'how-to-stick-to-a-diet-when-progress-slows' },
  // Short "import friendly" slugs used in Medium manual publish packages (`devenira.com/blog/...`).
  // These are not generateStaticParams slugs; without redirects they 404 on production.
  { from: 'consistency', to: 'how-to-stick-to-a-diet-when-progress-slows' },
  { from: 'founder-story', to: 'how-i-lost-50-kg-middle-of-diet' },
  { from: 'mirror', to: 'why-cant-i-see-weight-loss-in-the-mirror' },
  { from: 'weighin', to: 'should-i-weigh-myself-every-day-on-a-diet' },
  { from: 'binge-repair', to: 'what-to-do-after-a-binge-on-a-diet' },
  { from: 'cheat-day', to: 'are-cheat-days-bad-for-weight-loss' },
  { from: 'appetite-louder', to: 'why-is-my-appetite-stronger-on-a-diet' },
  // Add entries as slugs change. Example:
  // { from: 'old-slug-name', to: 'new-seo-optimized-slug' },
];

/**
 * Expand into Next.js redirects() format.
 * @returns {Array<{ source: string, destination: string, permanent: true }>}
 */
function buildBlogRedirects() {
  return blogSlugRedirects.map(({ from, to }) => ({
    source: `/blog/${from}`,
    destination: `/blog/${to}`,
    permanent: true,
  }));
}

module.exports = { blogSlugRedirects, buildBlogRedirects };

export type BlogSection =
  | {
      type: 'paragraphs';
      title?: string;
      paragraphs: string[];
    }
  | {
      type: 'list';
      title?: string;
      intro?: string;
      items: string[];
      outro?: string;
    }
  | {
      type: 'quote';
      quote: string;
      attribution?: string;
    };

export interface BlogPost {
  slug: string;
  title: string;
  description: string;
  socialDescription: string;
  date: string;
  readingTime: string;
  tags: string[];
  heroImage: string;
  heroAlt: string;
  deck: string;
  ctaTitle: string;
  ctaBody: string;
  sections: BlogSection[];
}

const posts: BlogPost[] = [
  {
    slug: 'why-i-built-devenira-for-the-weeks-where-you-want-to-quit',
    title: 'Why I Built Devenira for the Weeks Where You Want to Quit',
    description:
      'I lost 50kg, but the hardest part was not starting. It was the slow middle where progress was real, but hard to trust. That is why I built Devenira around weekly proof.',
    socialDescription:
      'Most people do not quit because nothing is happening. They quit because panic gets there before proof. This is the story behind Devenira.',
    date: '2026-04-15',
    readingTime: '8 min read',
    tags: ['Founder Story', 'Weight Loss', 'Transformation', 'Body Image'],
    heroImage: '/founder/founder-story-hanok-20260119.jpg',
    heroAlt: 'Founder standing outdoors in a composed hanok portrait after a major transformation',
    deck:
      'I did not build Devenira because I wanted another fitness app. I built it because the hardest part of losing 50kg was not starting. It was the long middle where the work was real, but the mirror still made it feel fake.',
    ctaTitle: 'Start with one body check-in.',
    ctaBody:
      'If the mirror is louder than the evidence right now, begin with one scan and build a weekly record you can trust.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'I did not build Devenira because AI is interesting.',
          'I built it because the mirror can become a liar when you see it every day.',
          'People like to talk about weight loss as if the hard part is starting. Eat better. Train harder. Stay disciplined.',
          'That is part of it, yes. But for me, the hardest part was never the beginning. It was the middle.',
        ],
      },
      {
        type: 'quote',
        quote: 'Maybe nothing is changing.',
      },
      {
        type: 'paragraphs',
        paragraphs: [
          'That thought is more dangerous than people realize.',
          'Because once your brain starts believing that the effort is invisible, quitting starts sounding rational. Not lazy. Rational.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Is Where the Story Actually Starts',
        paragraphs: [
          'At the start, the problem is obvious. You know you need to change. You know how uncomfortable you feel. You know the current version of yourself is not where you want to stay.',
          'That part is painful, but at least it is clear. The strange thing about body change is that clarity gets weaker before the results get stronger.',
          'You can lose weight. You can train consistently. You can clean up your habits. And still wake up one morning feeling like your body looks exactly the same.',
          'That is when people do stupid things. They overreact to one weigh-in. They assume one flat-looking mirror day means the process failed. They start changing the plan every week because they need proof faster than their body is willing to show it.',
          'That is where a lot of transformations quietly die. Not because the body stopped changing. Because belief did.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Middle Looked Ordinary',
        paragraphs: [
          'The middle of my own transformation did not look cinematic. It did not feel like a movie montage. It looked ordinary.',
          'That was the problem. Ordinary progress is easy to dismiss.',
          'The final result is obvious in hindsight. But while you are still inside the process, change is subtle. It shows up in pieces. A little more shape here. A little less softness there. A slightly different waistline. A slightly different face.',
          'The mirror is bad at telling that story. It only shows you one emotional frame at a time. And if you are tired, stressed, bloated, flat, or second-guessing yourself, that frame can become a false verdict.',
          'That is what I mean when I say the mirror gets loud before the proof does.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'It Changed in Phases',
        paragraphs: [
          'What I wish I had back then was not more motivation.',
          'I did not need another quote. I did not need another calorie target. I did not need another app trying to be everything at once. I needed better evidence.',
          'I needed a way to see that the process was moving, even before it looked dramatic.',
          'That is what people misunderstand about transformation stories. They think the most important contrast is before and after. It is not. The most important stretch is before and during.',
          'That is the stretch where belief is fragile. That is where the whole thing is most likely to collapse. And that is exactly why I care so much about weekly check-ins.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'One Photo Is a Moment. A Weekly Record Is a Story',
        paragraphs: [
          'A single photo can help. But a single photo still leaves too much room for denial.',
          'One good angle can flatter you. One bad angle can crush you. One good weigh-in can make you overconfident. One bad weigh-in can make you want to disappear.',
          'What changed the way I think about progress is this: one measurement is data. A repeated record is evidence.',
          'That is the difference between chasing reassurance and building proof.',
          'If you return weekly, under roughly the same conditions, the story gets harder to distort. You stop relying on memory. You stop relying on one emotional morning. You stop asking the mirror to carry a job it was never good at.',
          'You build a record. And once a record exists, panic has less room to improvise.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Why Devenira Exists',
        paragraphs: [
          'That is the gap Devenira is meant to fill. Not as another giant fitness dashboard. Not as a medical device. Not as a fake instant-transformation machine.',
          'But as a weekly proof loop.',
          'You check in. You see where you are. You come back. You compare. And over time, the process becomes harder to gaslight yourself about.',
          'That matters more than people think. Most people do not fail because nothing is happening. They fail because panic gets there before proof.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Proof Over Panic',
        paragraphs: [
          'That phrase is not just branding to me. It is the reason the product exists at all.',
          'I know what it feels like to be in the middle of a cut, or in the middle of a long body change, and to wonder whether the whole thing is a delusion. I know what it feels like to need evidence, not encouragement.',
          'So if Devenira does its job well, it should not just collect information. It should make the hard middle easier to survive. It should help you trust the process long enough to let the process become visible.',
          'If you are in that phase right now, the one where you are doing the work but struggling to believe it, start with one body check-in. One scan is a number. Weekly check-ins are proof.',
        ],
      },
    ],
  },
  {
    slug: 'why-the-mirror-can-make-real-progress-feel-fake',
    title: 'Why the Mirror Can Make Real Progress Feel Fake',
    description:
      'The mirror is one of the worst tools for judging body change in real time. Here is why progress can be real even when it still feels invisible.',
    socialDescription:
      'Progress can be real before it feels obvious. The mirror is often the last place to give clear feedback.',
    date: '2026-04-16',
    readingTime: '6 min read',
    tags: ['Body Image', 'Progress Tracking', 'Weight Loss', 'Dieting'],
    heroImage: '/founder/mirror-middle-checkin-20250716.jpg',
    heroAlt: 'Founder mirror check-in image showing the honest middle stage of body change',
    deck:
      'If you see your body every day, the mirror is often the last place that will give you reassurance. That does not mean progress is not happening. It means the mirror is a terrible historian.',
    ctaTitle: 'Start with one body check-in.',
    ctaBody:
      'If the mirror is noisy right now, use one scan as a baseline and start building a visual record you can actually trust.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'The mirror is one of the worst places to look for reassurance during body change.',
          'Not because it always lies. But because it adapts too well.',
          'When you see your body every day, small differences stop feeling like differences. That is why people can be making real progress and still feel stuck.',
          'This is where a lot of diets actually fail. Not in physiology. In interpretation.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Mirror Only Shows One Emotional Frame',
        paragraphs: [
          'The mirror does not show trend. It does not show context. It does not show comparison. It shows one moment.',
          'And that one moment is easy to misread.',
          'If you are flat, tired, bloated, stressed, underslept, or disappointed, the mirror becomes an amplifier for whatever story you are already telling yourself.',
          'That is why the same body can look “better” one day and “worse” the next, even when almost nothing meaningful has changed.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Daily Exposure Makes Change Harder To Notice',
        paragraphs: [
          'People underestimate how much familiarity distorts perception.',
          'The body changes slowly. The eyes adapt quickly. That is a bad combination.',
          'When the change is gradual, your brain normalizes it before your confidence catches up. So even when the process is working, the visible reward can feel delayed.',
          'That delay is dangerous. Because once you start thinking nothing is happening, the next bad meal, bad weigh-in, or bad mirror day suddenly feels like proof that the whole thing failed.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Is Why Progress Often Feels Fake In The Middle',
        paragraphs: [
          'The beginning is clear. You know you want change. You know why you started.',
          'The ending is also clear. You can look back and say, yes, that was real.',
          'But the middle is where doubt lives. The middle is subtle. The middle looks ordinary. The middle is easy to dismiss.',
          'That is exactly why so many people quit there. Not because nothing is happening. Because they cannot trust what is happening.',
        ],
      },
      {
        type: 'list',
        title: 'What Works Better Than The Mirror',
        intro:
          'If you want to judge progress more honestly, you need better evidence than one emotional look in the bathroom mirror.',
        items: [
          'progress photos across real time gaps',
          'weekly comparison, not daily obsession',
          'stable conditions as often as possible',
          'a visual record you can revisit',
        ],
        outro:
          'One photo is still just one moment. But repeated photos become a story. And stories are harder to distort than moods.',
      },
      {
        type: 'paragraphs',
        title: 'One Moment Is Data. A Record Is Evidence',
        paragraphs: [
          'A single look in the mirror is data. A stored visual timeline is evidence.',
          'Evidence matters because it protects you from panic. It keeps you from overreacting to one bad day. It reminds you that change can be real before it feels dramatic. And it gives you something more stable than memory to rely on.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'That Is Why Weekly Check-Ins Matter',
        paragraphs: [
          'I care much more about weekly proof than daily reassurance. Daily reassurance is fragile. Weekly proof compounds.',
          'When you check in on a weekly cadence, you give your body enough time to show direction. That direction is what keeps people going.',
          'Not hype. Not discipline theater. Not pretending doubt never shows up. Just better evidence.',
          'If the mirror feels discouraging right now, that does not automatically mean the process is failing. It may just mean you are too close to the change to see it clearly yet.',
          'That is why one of the best things you can do is stop asking the mirror to tell the whole story. Build a record instead. One scan is a number. Weekly check-ins are proof.',
        ],
      },
    ],
  },
  {
    slug: 'one-emotional-weigh-in-can-wreck-a-good-week',
    title: 'One Emotional Weigh-In Can Wreck a Good Week',
    description:
      'One weigh-in can trigger panic even when your fat loss is still on track. Here is why scale spikes happen and how to interpret them better.',
    socialDescription:
      'A single scale increase can ruin a good week if you let panic tell the story. Better interpretation matters as much as better habits.',
    date: '2026-04-17',
    readingTime: '6 min read',
    tags: ['Scale Weight', 'Fat Loss', 'Dieting', 'Weight Loss'],
    heroImage: '/founder/weighin-middle-progress-20240801.jpg',
    heroAlt: 'Founder progress image representing the vulnerable middle of a weight-loss process',
    deck:
      'The scale is not useless. But one loud reading can trigger a lot of bad decisions if you let it become a verdict instead of a data point.',
    ctaTitle: 'Use better evidence than one weigh-in.',
    ctaBody:
      'Start with one body check-in, then compare week by week instead of letting one loud scale reading define the whole process.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Most people do not ruin a good week because of one number.',
          'They ruin it because of the story they attach to that number.',
          'The scale goes up. Panic starts. And suddenly one careful week feels fake.',
          'That is how people turn noise into a conclusion.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Dangerous Part Is Not The Reading',
        paragraphs: [
          'The dangerous part is interpretation.',
          'A scale spike feels absolute. It feels objective. It feels like the body is delivering a verdict.',
          'But scale weight is not body fat.',
          'It is body fat, yes, but also water, digestion, food volume, sodium, timing, inflammation, stress, sleep, bowel movement timing, and a dozen other temporary variables.',
          'That is why you can eat less and still weigh more the next day. Not because your body broke the laws of physics. Because the scale measures more than the story you want it to tell.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'One Reading Is Too Small To Carry A Verdict',
        paragraphs: [
          'One weigh-in can be useful. But it is too small to carry a conclusion about whether your whole process is working.',
          'Think about how often people do this: one up day means I am gaining fat, one flat day means nothing is changing, one low day means finally it is working.',
          'That is emotional accounting, not analysis. The scale becomes dangerous when you ask it to explain more than it can explain.',
        ],
      },
      {
        type: 'list',
        title: 'Why People Spiral After A Scale Spike',
        intro: 'The scale itself is not the whole problem. The problem is what usually comes next.',
        items: [
          'restriction',
          'punishment cardio',
          'bingeing because the week is ruined anyway',
          'changing the whole plan too early',
        ],
        outro:
          'That is how one noisy morning turns into several genuinely bad days. The irony is that the original spike often did less damage than the overreaction that followed it.',
      },
      {
        type: 'list',
        title: 'Better Questions To Ask',
        intro: 'When the scale goes up, ask better questions before you panic.',
        items: [
          'How have the last 7 days looked, not just today?',
          'Was yesterday high in sodium or food volume?',
          'Am I more stressed or less rested than usual?',
          'Have I actually gathered enough data to call this a trend?',
        ],
        outro:
          'Most of the time, the answer is no. And that matters. Because not enough data yet is a much healthier conclusion than this is not working.',
      },
      {
        type: 'list',
        title: 'The Scale Needs Context',
        intro: 'The scale becomes far more useful when you pair it with other signals.',
        items: [
          'weekly averages',
          'photos across real time gaps',
          'visual changes in the waist, face, and torso',
          'whether your routine is still consistent',
        ],
        outro:
          'That is what keeps one weigh-in from becoming an emotional referendum on your whole effort.',
      },
      {
        type: 'paragraphs',
        title: 'Why Visual Proof Helps',
        paragraphs: [
          'If the scale is noisy, visual proof helps calm interpretation.',
          'A progress record does not remove uncertainty completely. But it gives you something steadier than one morning number.',
          'It lets you zoom out. It helps you see whether the direction is real. And it protects you from treating every fluctuation like a crisis.',
          'This is one of the reasons weekly check-ins matter so much. They create enough space for change to become visible, and enough structure to stop panic from making the call.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'The scale can be noisy without being useless.',
          'The mistake is turning one noisy reading into a verdict.',
          'If you want better decisions, you need better evidence than one emotional morning.',
          'One scan is a number. Weekly check-ins are proof.',
        ],
      },
    ],
  },
  {
    slug: 'how-to-track-body-transformation-without-obsessing-over-the-scale',
    title: 'How to Track Body Transformation Without Obsessing Over the Scale',
    description:
      'If you want to track body transformation more accurately, you need better signals than daily scale obsession. Here is a simpler way to do it.',
    socialDescription:
      'You do not need more data. You need a better system for judging whether your body is actually changing.',
    date: '2026-04-18',
    readingTime: '7 min read',
    tags: ['Transformation', 'Progress Photos', 'Body Composition', 'Fat Loss'],
    heroImage: '/founder/transformation-proof-20251119.jpg',
    heroAlt: 'Founder physique image showing clear transformation proof beyond the scale',
    deck:
      'If you want to know whether your body is actually changing, you need a better system than checking the scale and the mirror every day. A simple weekly evidence loop works better.',
    ctaTitle: 'Track transformation with better evidence.',
    ctaBody:
      'Start with one body check-in and build a weekly record that is harder to distort than a single mirror glance or scale reading.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Most people try to track transformation with the same two tools: the scale and the mirror.',
          'The problem is not that those tools are useless. The problem is that people use them badly.',
          'They look too often. They react too quickly. And they ask each tool to do more than it is good at.',
          'That is how progress becomes confusing, even when the process is working.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What Most People Get Wrong',
        paragraphs: [
          'The most common mistake is turning a body transformation into a daily judgment ritual.',
          'You weigh yourself. You look in the mirror. You decide how hopeful or hopeless to feel.',
          'That is not tracking. That is emotional volatility with numbers attached to it.',
          'The scale is too noisy for daily interpretation. The mirror is too familiar for subtle change.',
          'If you rely on those two alone, you will keep bouncing between overconfidence and discouragement.',
        ],
      },
      {
        type: 'list',
        title: 'What Better Tracking Actually Looks Like',
        intro:
          'A useful transformation-tracking system does three things.',
        items: [
          'it creates a baseline',
          'it compares over meaningful gaps',
          'it reduces the room for panic-driven interpretation',
        ],
        outro:
          'That is why a weekly system works so well. It is frequent enough to stay relevant, but slow enough to let your body show direction.',
      },
      {
        type: 'paragraphs',
        title: 'Start With A Real Baseline',
        paragraphs: [
          'You need one honest starting point.',
          'Not a flattering photo. Not your best angle. Not the version of your body you wish were true.',
          'Just a clear starting point.',
          'That is what gives every future check-in meaning. Without a baseline, every new photo becomes a guess. With a baseline, each new check-in becomes comparison.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Why Weekly Check-Ins Work Better',
        paragraphs: [
          'Weekly check-ins are better than daily obsession for one simple reason: the body usually changes slower than emotion.',
          'Daily tracking gives emotion too many chances to interfere. Weekly tracking gives the body more room to tell a real story.',
          'That does not mean every week looks dramatic. It means weekly data is more likely to mean something.',
          'Because one of the biggest reasons people quit is not lack of discipline. It is lack of believable evidence.',
        ],
      },
      {
        type: 'list',
        title: 'The Best Signals To Track',
        items: [
          'weekly progress photos',
          'visual changes in waist, torso, face, and posture',
          'repeated check-ins under roughly similar conditions',
          'the scale as a supporting metric, not the main judge',
        ],
        outro:
          'This gives you a more stable read on reality. You stop trying to squeeze certainty out of one daily number.',
      },
      {
        type: 'paragraphs',
        title: 'Progress Photos Matter More Than People Admit',
        paragraphs: [
          'A lot of people avoid progress photos because they feel awkward or discouraging. That is understandable.',
          'But the uncomfortable truth is that progress photos often become useful before they become flattering.',
          'That is exactly why they matter. They capture what memory edits. They preserve what the mirror normalizes. And over time, they become one of the clearest ways to see whether the work is paying off.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'You Do Not Need More Data. You Need Better Interpretation',
        paragraphs: [
          'Most people are not short on information. They are short on structure.',
          'They do not need more dashboards. They do not need a more dramatic chart. They do not need to check five times a day.',
          'They need a system that makes panic less persuasive. That is what a weekly proof loop does.',
          'It gives you enough information to see direction. And it keeps that direction visible long enough for your confidence to catch up.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If you want to track body transformation without obsessing over the scale, simplify the system.',
          'Start with one baseline. Check in weekly. Store the record. Compare over time.',
          'That is a much better way to judge whether your body is changing.',
          'One scan is a number. Weekly check-ins are proof.',
        ],
      },
    ],
  },
  {
    slug: 'why-it-feels-like-you-gain-weight-even-when-you-barely-eat',
    title: 'Why It Feels Like You Gain Weight Even When You Barely Eat',
    description:
      'Sometimes the scale goes up even when you feel like you are eating less. Here is why body-weight fluctuation can feel like fat gain, and why that misunderstanding wrecks good weeks.',
    socialDescription:
      'A rude weigh-in can make your whole week feel fake. The real problem is often not the number itself, but the way you read it.',
    date: '2026-04-19',
    readingTime: '7 min read',
    tags: ['Scale Weight', 'Weight Illusions', 'Dieting', 'Women’s Health'],
    heroImage: '/founder/scale-rude-before-20240130.jpg',
    heroAlt: 'Honest founder mirror image representing a discouraging weigh-in week',
    deck:
      'A rude weigh-in can turn one morning into a small identity crisis. But scale weight and fat gain are not always the same story.',
    ctaTitle: 'Get a calmer read than one rude weigh-in.',
    ctaBody:
      'If one unfair-looking number can hijack your mood, use a body check-in to get another reference point before panic starts freelancing.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Did you really gain body fat from water?',
          'That is the kind of sentence people say when they are one rude weigh-in away from losing their mind.',
          'You wake up, step on the scale, and get a number that feels insulting. Now your whole morning has a villain.',
          'You start replaying yesterday like security footage. What did I eat? Was it the late snack? Was it the rice? Was it the fact that my body clearly enjoys humiliating me?',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Scale Measures Weight, Not Your Moral Character',
        paragraphs: [
          'This is where people get themselves into trouble. They say “I gained weight” when what they mean is “the number on the scale went up.”',
          'Those are not always the same story.',
          'Body weight is a crowded number. It is not just fat. It includes water, digestive contents, stored carbohydrates, and all the ordinary moving parts of being a human body instead of a spreadsheet.',
          'So when the scale rises, the first question should not be “How badly did I fail?” It should be “What changed?”',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Yes, People Often Misread How Much They Eat',
        paragraphs: [
          'Let me be fair before I get more specific. Some people really do underestimate intake.',
          'They say they barely ate, and then you look closer and find out their version of barely eating still included bites, snacks, drinks, or meals they mentally filed under “not that much.”',
          'That happens. Food logging has embarrassed entire generations for a reason.',
          'But if we stop there, we miss the part that actually wrecks a lot of women during dieting.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Sometimes the Scale Goes Up for Reasons That Are Not the Same as Fat Gain',
        paragraphs: [
          'There are periods in the monthly cycle when body weight can rise even if food intake has not suddenly exploded.',
          'During ovulation and the days around it, some women can notice temporary increases. Not because they built meaningful fat overnight, but because the body can hold more water and feel heavier.',
          'That is an important difference. The scale does not announce that difference for you. It just gets loud.',
          'And when people do not understand why it got loud, they start writing the ugliest explanation available.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Problem Is Not Just the Number. It Is the Interpretation.',
        paragraphs: [
          'This is where perfectly decent diets die.',
          'You work hard all week. You eat with more structure. You expect a reward. Then the scale goes up anyway.',
          'For a lot of people, the answer is not curiosity. It is punishment. Fine, I will eat even less. Fine, I will do extra cardio. Fine, clearly I cannot trust myself around food.',
          'That sequence feels disciplined when you are inside it. From the outside, it often just looks like panic wearing activewear.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead of Panicking',
        items: [
          'Stop treating one weigh-in like a verdict.',
          'Look for timing, not just shock.',
          'Do not build a punishment plan off a temporary fluctuation.',
          'Use more than one lens: weekly trends, photos, fit, and behavior.',
          'If symptoms feel extreme or unusual, get proper medical attention.',
        ],
        outro:
          'Most people do not need more drama around the scale. They need one calmer read on what is happening.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If one number can hijack your mood, your meals, and your training plan, the problem is not only the number. It is that the number has too much authority.',
          'That is where a better check-in helps. Instead of letting one weigh-in narrate the whole week, use another reference point and judge your current body state with more context.',
          'Not as punishment. Not as obsession. Just as a way to stop panic from making your decisions for you.',
          'One scan is a number. Weekly check-ins are proof.',
        ],
      },
    ],
  },
  {
    slug: 'what-actually-counts-as-a-weight-loss-plateau',
    title: 'What Actually Counts as a Weight Loss Plateau?',
    description:
      'A slower scale does not always mean a real plateau. Here is how to tell the difference between slower progress, body recomposition, and an actual stall.',
    socialDescription:
      'People use the word plateau way too early. Sometimes what they really mean is: I am scared the dramatic part ended.',
    date: '2026-04-20',
    readingTime: '7 min read',
    tags: ['Plateau', 'Weight Loss', 'Progress Tracking', 'Body Recomposition'],
    heroImage: '/founder/plateau-middle-checkin-20250711.jpg',
    heroAlt: 'Founder check-in image representing a slower middle stage that can feel like a plateau',
    deck:
      'A slower scale is not automatically a plateau. Sometimes progress just stopped flattering you and started looking like real life.',
    ctaTitle: 'Check whether you are actually stuck.',
    ctaBody:
      'Before you call it a plateau, get one calmer read on what your body is actually doing and stop letting a flat number run management.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'I used to call anything slower than week one a plateau.',
          'That is how impatient people talk when the scale stops flattering them.',
          'Week three arrives, the number barely moves, and suddenly you are acting like the whole plan entered hospice care.',
          'People use the word plateau way too early.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Slower Is Not the Same as Stuck',
        paragraphs: [
          'If your weight is still going down, just not at the absurdly flattering rate it did at the beginning, that is not automatically a plateau.',
          'That is often just the end of the loud phase.',
          'Early dieting is noisy. Water moves fast. Motivation is still fresh. The scale is weirdly generous and makes people think this is what doing well is supposed to look like forever.',
          'Then real life resumes. The drop gets slower. The excitement fades. That is not a plateau. That is adulthood.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'A Flat Scale Is Not Always a Bad Sign Either',
        paragraphs: [
          'Sometimes weight stays the same while the body is still changing.',
          'That can happen when body fat is going down while muscle mass is increasing. The scale sees equal amounts of loss and gain and gives you a boring answer.',
          'Your body does not necessarily agree with that answer. This is why some people say, “My weight has not changed,” while their waist, shape, or photos tell a more interesting story.',
          'That is exactly why one number should not be treated like a final verdict.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Look Longer and Look Wider',
        paragraphs: [
          'A lot of people ask the wrong question. They ask, “Did my body change today?”',
          'That is a terrible question. Bodies are not customer service desks. They do not issue neat daily updates just because you had a disciplined Tuesday.',
          'A better question is: what has happened over the last week?',
          'That is where photos matter. That is where weekly comparisons matter. That is where a calmer check-in matters.',
        ],
      },
      {
        type: 'list',
        title: 'So What Is a Real Plateau?',
        intro: 'A real plateau is not:',
        items: [
          'slower progress than the first week',
          'one or two flat weigh-ins',
          'a moody Thursday',
          'a number that did not validate your effort quickly enough',
        ],
        outro:
          'A real plateau is closer to this: weight is not changing, body shape is not changing, and that pattern continues long enough to matter.',
      },
      {
        type: 'paragraphs',
        title: 'Why This Misunderstanding Ruins Diets',
        paragraphs: [
          'The moment people use the word plateau, they start behaving like something has gone wrong.',
          'Now the response becomes: eat less, cut more carbs, add more cardio, maybe I need to get serious now.',
          'That is how decent plans get punished for not being dramatic enough.',
          'Most people do not need a harsher reaction to a flat scale. They need another lens before panic starts freelancing.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Ask whether progress actually stopped or just slowed.',
          'Check whether the body is changing even if the number is flat.',
          'Stop letting week one define success forever.',
          'Only troubleshoot what is actually happening.',
        ],
        outro:
          'Do not use a real-plateau response on a fake plateau. That is like bringing bolt cutters to a door that was never locked.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If one number keeps deciding your mood, your meals, and your training plan, you are not just tracking progress. You are letting the scale run management.',
          'That is a bad workplace.',
          'A better check-in helps you see whether you are actually stuck or just annoyed.',
          'Before you call it a plateau, get one calmer read on what your body is actually doing.',
        ],
      },
    ],
  },
  {
    slug: 'why-losing-5kg-in-a-week-usually-means-water-not-fat',
    title: 'Why Losing 5kg in a Week Usually Means Water, Not Fat',
    description:
      'Fast weekly weight loss is usually more about water and timing than miracle fat loss. The timeline matters more than the headline.',
    socialDescription:
      'When someone says they lost 5kg in a week, the number lands before the context does. That is why these stories scramble people.',
    date: '2026-04-21',
    readingTime: '7 min read',
    tags: ['Water Weight', 'Rapid Weight Loss', 'Scale Weight', 'Fat Loss'],
    heroImage: '/founder/water-weight-proof-20251031.jpg',
    heroAlt: 'Founder physique image used to discuss water weight versus fat loss',
    deck:
      'Rapid weight loss sounds impressive, but most short-term scale drops are driven by water, not miracle fat loss. The timescale matters more than the headline.',
    ctaTitle: 'Do not benchmark yourself against a highlight reel.',
    ctaBody:
      'If a flashy one-week number is making your own progress look broken, check your actual body state before you start copying someone else’s crisis routine.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'No, someone losing 5kg in a week is usually not the miracle story your brain thinks it is.',
          'You know this already, which is what makes it so irritating.',
          'You see the thumbnail. You see the title. You see someone cheerfully announcing that they lost 5kg in a week by doing fasted cardio and eating one meal a day.',
          'And even if you know better, some ugly little part of your mind still says: then why is my progress so boring?',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Scale Is Measuring More Than Fat',
        paragraphs: [
          'This is the first thing internet before-and-after logic pretends not to know.',
          'Body weight is not just body fat. It includes water. It includes the contents moving through your digestive system. It includes muscle, which does not magically disappear and regrow every few days because someone filmed a vlog.',
          'Muscle and fat are usually slower movers. Water is the dramatic one.',
          'So when the scale changes fast, what should make you skeptical first? Fat. Because fat usually does not move with that kind of speed. Water does.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Fast Loss Often Starts With a Temporarily Inflated Number',
        paragraphs: [
          'A lot of rapid-loss stories start after overeating.',
          'And overeating does not just increase body fat over time. It can also temporarily increase body water, especially when sodium and carbohydrates go up with it.',
          'Imagine someone’s usual weight is 60 kg. They overeat for a stretch, hold more water, and now the scale says 63 kg. Then they slash food, do fasted cardio, eat one meal a day, and a week later the scale says 58 kg.',
          'Now the headline says: I lost 5kg in a week. Sounds incredible. But incredible compared to what? Compared to their temporarily inflated 63 kg? Compared to their normal 60 kg? That is a very different story.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Timeline Tells You More Than the Headline',
        paragraphs: [
          'This is why I care more about the time than the number.',
          'If weight drops fast over a very short window, a lot of that drop is usually water. If the method depends on one meal a day, fasted cardio, and living like you owe money to a treadmill, that tells you something too.',
          'It tells you the result may be intense. It does not tell you it is useful.',
          'Because once normal eating resumes, some of that water comes back. More food volume comes back. A more normal sodium intake comes back. And suddenly the dramatic weekly headline starts shrinking into something much less magical.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Why These Videos Mess With People So Badly',
        paragraphs: [
          'Because the number lands before the context does.',
          'You are not comparing your real life to their real life. You are comparing your boring, sustainable timeline to their loudest possible week.',
          'Of course that shakes people up. Of course it makes sensible progress feel embarrassing for a minute.',
          'That is how one stupid headline can damage a perfectly decent plan. Not because it taught you science. Because it taught you impatience.',
        ],
      },
      {
        type: 'list',
        title: 'What to Focus on Instead',
        items: [
          'respect the speed difference between water and fat',
          'compare timelines, not highlight reels',
          'stop using the loudest story online as your benchmark',
          'read your own body with more context',
        ],
        outro:
          'Weekly trends beat one-off spikes. Consistent check-ins beat emotional comparison. Actual body state beats internet theater.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If someone else’s one-week number is making your own progress feel broken, you do not need a more dramatic plan.',
          'You need a calmer read on reality.',
          'That is what most people are missing. Not intensity. Interpretation.',
          'If a flashy short-term result is making you question everything, check your actual body state before you start copying someone else’s crisis routine.',
        ],
      },
    ],
  },
  {
    slug: 'the-most-important-reason-you-think-youre-not-losing-weight',
    title: "The Most Important Reason You Think You're Not Losing Weight",
    description:
      'A lot of people think their diet stopped working when what actually stopped was the fast, flattering phase. Impatience ruins more diets than bad plans do.',
    socialDescription:
      'Sometimes the diet did not fail. The dramatic part ended, your patience failed first, and the scale got far too much authority.',
    date: '2026-04-22',
    readingTime: '6 min read',
    tags: ['Plateau', 'Patience', 'Weight Loss', 'Dieting'],
    heroImage: '/founder/patience-middle-checkin-20250731.jpg',
    heroAlt: 'Founder check-in image representing the frustrating middle of a diet',
    deck:
      'Many people think they are not losing weight because the process failed. More often, the dramatic early phase ended and their patience failed first.',
    ctaTitle: 'Do not let a slower week rewrite the story.',
    ctaBody:
      'If the scale still holds too much power in your process, start with one calmer body check-in before you decide the plan is broken.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          "The most important reason many people think they are not losing weight is not that the diet failed.",
          'It is that their patience failed first.',
          'That sounds rude. I do not mean it rudely. I mean it accurately.',
          'When people start a diet, they usually get spoiled early. The scale moves fast. The body looks less swollen. Even the suffering feels productive because it is paying rent immediately.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Beginning Teaches the Wrong Lesson',
        paragraphs: [
          'A lot of people start dieting after a period of eating plenty of processed food. That usually means more sodium, more refined carbohydrates, and more body water.',
          'Then they clean things up. Processed food drops. Sodium drops. Carbohydrate load changes. Body water drops with it.',
          'The scale moves fast and the body tightens up quickly enough to make people think: excellent, so this is what success looks like.',
          'No. That is what the early, flattering phase looks like.',
          'Body fat usually comes off more slowly than body water. The problem is that people get emotionally attached to the loud phase and then accuse the quieter phase of betrayal.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Impatience Makes People Do Expensive Things',
        paragraphs: [
          'Once the rapid early drop slows down, the mind gets weird.',
          'Now people start thinking: maybe I should eat even less. Maybe I should train longer. Maybe I have one of those cursed bodies that refuses to lose weight.',
          'A slower week becomes evidence. A flat weigh-in becomes identity. A normal delay becomes proof that they are different from the lucky people.',
          'That is how impatience turns a process problem into a character problem.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Stress Loves This Kind of Thinking',
        paragraphs: [
          'If you weigh yourself constantly, worry constantly, and keep interpreting every tiny change like a referendum on your future, you do not just become impatient. You become stressed.',
          'And stressed people do not usually make calmer, cleaner food decisions. They become more reactive. They tighten too hard. They start experimenting on themselves in stupid ways. Or they give up and call the whole thing unfair.',
          'A decent diet plus relentless impatience can still fail beautifully.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Cursed-Body Theory Is Lazy and Seductive',
        paragraphs: [
          'This is the story people tell themselves when they want an explanation that feels emotionally satisfying: maybe my body just does not lose weight.',
          'It is seductive because it explains everything and requires no further thinking. It is also one of the quickest ways to poison your effort.',
          'If you decide your body is fundamentally against you, then every hard moment becomes confirmation. Now you are not just dieting. You are auditioning evidence for a verdict you already chose.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Stop comparing every week to the first dramatic week.',
          'Reduce scale obsession before it turns into stress.',
          'Do not make emergency changes every time progress gets less exciting.',
          'Treat patience like part of the method, not just a personality trait.',
        ],
        outro:
          'When people think they are not losing weight, a lot of the time they do not need a harsher plan. They need a calmer interpretation.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If one number can still hijack your whole day, then the scale is holding too much power in your process.',
          'A better check-in helps you see whether the plan is actually off or whether you are just fighting the end of the dramatic phase.',
          'Before you decide your body is broken, get one calmer read on what it is actually doing.',
        ],
      },
    ],
  },
  {
    slug: 'the-scale-can-say-normal-and-still-tell-you-nothing-useful',
    title: 'The Scale Can Say “Normal” and Still Tell You Nothing Useful',
    description:
      'A normal body weight does not guarantee that someone feels lean, strong, or at ease in their body. Weight and body composition are not the same story.',
    socialDescription:
      'The scale can say normal while the mirror still feels expensive. Weight and body composition are not identical, and chasing smaller can make the wrong problem worse.',
    date: '2026-04-23',
    readingTime: '6 min read',
    tags: ['Body Image', 'Body Composition', 'Scale Weight', 'Mirror'],
    heroImage: '/founder/body-composition-proof-20251221.jpg',
    heroAlt: 'Founder proof image representing body composition change beyond scale weight',
    deck:
      'A normal weight does not guarantee that someone feels lean, strong, or at ease in their body. The scale is often too crude to explain what they are actually struggling with.',
    ctaTitle: 'Use a better lens than one number.',
    ctaBody:
      'If the scale keeps deciding whether your body feels acceptable, use a weekly visual check-in and track the pattern instead of the panic.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'This is one of the most awkward moments in weight-loss culture.',
          'Someone says, “I am at a normal weight, but I still hate how my body looks.” And the internet immediately responds like a bored uncle: then just stop dieting, you are already skinny, be grateful.',
          'Very warm. Very helpful. Also not always correct.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'A Normal Number and a Satisfying Physique Are Not Identical',
        paragraphs: [
          'The number can be normal. The experience can still feel wrong.',
          'Not because the person is automatically delusional. Not because every insecurity is fake. But because body weight and body composition are not the same story.',
          'Two people can weigh the same and look wildly different. Different muscle mass. Different fat distribution. Different posture. Different history.',
          'The scale does not explain any of that. It just arrives, says a number, and leaves you to ruin your own day with it.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Gets Even Messier After Crash Dieting',
        paragraphs: [
          'If someone got lighter by starving, there is a good chance they did not just lose fat. They also lost muscle.',
          'And when muscle is low, the body can look softer, less stable, and less like the lean fantasy the person thought they were buying.',
          'So now they are trapped in a miserable loop: the weight is already low, the mirror still feels disappointing, and they assume the answer must be even lower weight.',
          'That is how people keep chasing smaller when the real problem may be composition, not just mass.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Sometimes “I Just Want To Be Lighter” Is Grief Wearing a Diet Plan',
        paragraphs: [
          'People are not only chasing a number. They are chasing a feeling.',
          'Relief. Control. Safety. Proof that they are not back there again.',
          'And when the mirror does not cooperate, they assume the number failed.',
          'Maybe. Or maybe the number was never detailed enough to solve the thing they were actually worried about.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Scale Is Sometimes Giving You the Wrong Assignment',
        paragraphs: [
          'I understand why people keep bargaining with lower numbers. It feels cleaner. It feels measurable. It feels like one more small cut might finally make the body cooperate.',
          'But sometimes the scale is just giving you the wrong assignment.',
          'Not be smaller. Build a different body. Treat the body differently. Stop using starvation as your main design tool.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Stop assuming lower weight automatically means a better look.',
          'Separate body weight from body composition.',
          'Be suspicious of goals built entirely on mirror panic.',
          'Ask whether the real job is stronger, steadier, and better fueled.',
        ],
        outro:
          'Track changes visually and consistently. Look at the body as a pattern over time, not a daily verdict.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          '“Normal weight” is not the same as “problem solved.”',
          'And chasing an even smaller number is not always wisdom. Sometimes it is just fear with a calculator.',
          'If you keep using one scale number to decide whether your body is safe, attractive, or acceptable, the interpretation tool is too crude.',
        ],
      },
    ],
  },
  {
    slug: 'the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one',
    title: 'The Most Reliable Way to Succeed at Dieting Is Still the Least Dramatic One',
    description:
      'Most people do not quit dieting because they are lazy. They quit because early fast results create false expectations, later progress slows, and one noisy weigh-in feels like proof of failure.',
    socialDescription:
      'Most diets do not end with one giant disaster. They end with a mood. Usually some version of: what is the point?',
    date: '2026-04-24',
    readingTime: '7 min read',
    tags: ['Consistency', 'Weight Loss', 'Mindset', 'Dieting'],
    heroImage: '/founder/consistency-editorial-20251229.jpg',
    heroAlt: 'Founder editorial portrait representing calm, long-term consistency',
    deck:
      'Most diets do not end with one giant disaster. They end with a mood. The least dramatic success strategy is still the one most people avoid: staying in long enough to let the quiet phase work.',
    ctaTitle: 'Do not let one loud week end a quiet process.',
    ctaBody:
      'If the scale is still deciding your mood and your plan, use a weekly check-in to zoom out and see whether the process is actually moving.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Most diets do not end with one giant disaster.',
          'They end with a mood. An ugly little mood. Some version of: what is the point?',
          'That line has killed more progress than birthday cake ever did.',
          'And most of the time, it does not show up because the person suddenly became lazy. It shows up because the story of the diet changed.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Beginning of a Diet Is a Terrible Teacher',
        paragraphs: [
          'Early on, the scale often drops fast. People feel electric. Motivation is high. The plan is still new enough to seem noble.',
          'And the body is shedding water from changes in refined food, sodium, and carbohydrate intake.',
          'So the person learns the wrong lesson. They think this is how dieting works: fast drops, clean feedback, immediate rewards.',
          'No. That is what the early flattering phase looks like.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Diet Gets Harder Right When the Feedback Gets Quieter',
        paragraphs: [
          'This is the part that breaks people. The novelty wears off. The effort feels heavier. Food gets more annoying. Workouts feel less cute.',
          'And right when the job starts demanding more patience, the scale stops being generous.',
          'Week one was a hype man. Week six is an accountant.',
          'No wonder people feel cheated.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Cheat-Day Spikes Make the Whole Thing Feel Personal',
        paragraphs: [
          'Then comes the perfect little insult. One salty meal. One carb-heavy night. One social weekend. And the scale jumps 1 or 2 kg.',
          'Now the person does not just feel discouraged. They feel betrayed.',
          'But most of that sudden jump is not instant fat gain. It is often water, glycogen, food volume, and a loud misreading of the moment.',
          'The scale got noisy. That does not mean it got honest.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Is Where People Make the Fatal Move',
        paragraphs: [
          'They respond to slower progress and temporary scale noise by escalating the plan.',
          'Eat less. Train harder. Panic faster.',
          'Now the diet becomes even harder to live with. And when that harder version also fails to deliver the fantasy of early rapid loss, they do not just feel disappointed. They feel stupid.',
          'That is usually when they quit.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Expect early progress to be misleadingly dramatic.',
          'Treat slower loss later as normal, not insulting.',
          'Do not answer scale noise with punishment.',
          'Build your identity around staying in, not around feeling inspired.',
        ],
        outro:
          'The most reliable way to succeed is still embarrassingly simple: do not keep leaving.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If your whole relationship with dieting depends on whether the scale gives you a little emotional reward every morning, you need a better interpretation tool.',
          'Track the body more intelligently. Zoom out. See the weekly pattern. Stop giving one loud weigh-in the authority to rewrite the whole story.',
          'Because the most certain way to succeed at dieting is still the least dramatic one: do not keep leaving.',
        ],
      },
    ],
  },
  {
    slug: 'progress-update-2-the-body-changed-slower-than-my-head-did',
    title: 'Progress Update #2: The Body Changed Slower Than My Head Did',
    description:
      'A personal progress update on what actually changed after the first stretch of weight-loss lessons: not just the body, but the way panic, appetite, and self-judgment started to quiet down.',
    socialDescription:
      'The body changed, yes. But the bigger win was that my reading of the body finally started catching up.',
    date: '2026-04-25',
    readingTime: '6 min read',
    tags: ['Founder Story', 'Transformation', 'Progress Update', 'Mindset'],
    heroImage: '/founder/progress-update-hanok-20260119.jpg',
    heroAlt: 'Founder portrait used for a personal progress update in a polished outdoor setting',
    deck:
      'The biggest visible change was not actually the most important one. The body changed, yes, but the bigger shift was that panic became less convincing.',
    ctaTitle: 'The goal is not just to be lighter.',
    ctaBody:
      'Start with one body check-in and build the kind of weekly record that helps your reading of the body catch up with what is actually changing.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'There is a version of me who thought every bad weigh-in meant I was becoming my old self again.',
          'That version of me was exhausting.',
          'Not evil. Not lazy. Just permanently one rude scale number away from a full identity crisis.',
          'If you have been reading this series from the start, you already know the pattern: the scale gets loud, appetite gets blamed, food becomes moral, and one bad day starts sounding like a character flaw.',
          'What I did not understand back then was that the body was not the only thing changing. My interpretation of the body had to change too.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Biggest Visible Change Was Not Actually the Most Important One',
        paragraphs: [
          'Yes, the body changed.',
          'Over time I lost 50 kg. I ended up doing professional modelling work. Photos that would have felt absurd to me years earlier became real.',
          'That part is visible. It is easy to package. It looks good in a before-and-after comparison.',
          'But the bigger change was quieter.',
          'The panic became less convincing. The all-or-nothing voice got weaker. Food stopped feeling like a courtroom.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'I Used To Think Success Meant Becoming Stricter',
        paragraphs: [
          'That was one of the dumbest beliefs I carried for years.',
          'I thought successful people must just be better at suffering. Better at saying no. Better at enduring hunger. Better at treating food like a suspicious person at the border.',
          'Turns out that was not the real shift.',
          'The real shift was becoming less dramatic around the same problems.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Body Got Leaner. The System Got Calmer.',
        paragraphs: [
          'That is probably the clearest way to say it.',
          'I did not build a life by staying in emergency mode forever. I built a system that slowly made emergency mode less necessary.',
          'More stable food. More honest tracking. Less weird punishment. More respect for what the body was actually telling me.',
          'That is also why I care so much about this blog not turning into generic fitness noise. I am not interested in shouting at people to try harder. I am interested in helping them stop getting fooled by the same handful of traps.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'If You Are Still in the Ugly Middle',
        paragraphs: [
          'You may not feel transformed yet. You may still feel like the same person with better intentions and worse snacks.',
          'That is okay. A lot of change looks unimpressive while it is still happening.',
          'The body changes. The pattern changes. The self-story changes. Usually not on the same day.',
          'So if you are in that awkward middle where the progress feels real but your head still acts like you are failing, you are not uniquely broken. You are just earlier in the process than your panic wants to admit.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'Part of why I am building around better tracking and better body interpretation is because I know what it costs when all you have is a noisy scale and a fragile mood.',
          'The goal is not just to be lighter. It is to see more clearly. To react less stupidly. To stop turning every fluctuation into a verdict.',
          'That is what changed for me. The body changed, yes. But the bigger win was that my reading of the body finally started catching up.',
        ],
      },
    ],
  },
  {
    slug: 'dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight',
    title: 'Don’t Trust the Scale—Here’s What Actually Proves You’re Losing Weight',
    description:
      'If the scale keeps confusing you, look for better evidence. Real fat-loss signs often show up in body shape, fit, firmness, and where the body starts changing first.',
    socialDescription:
      'The scale is one witness. It is not the whole case. If you want proof, look at shape, fit, softness, firmness, and visual change over time.',
    date: '2026-04-26',
    readingTime: '6 min read',
    tags: ['Scale Weight', 'Progress Tracking', 'Fat Loss', 'Body Image'],
    heroImage: '/founder/scale-proof-20250919.jpg',
    heroAlt: 'Founder proof image representing visible fat-loss progress beyond the scale',
    deck:
      'A lot of people want fat loss to come with a receipt. But the scale is one witness, not the whole case. Real proof often shows up in shape, fit, firmness, and repeated visual change.',
    ctaTitle: 'Use a better lens than one loud number.',
    ctaBody:
      'If the scale keeps changing its personality, use one body check-in as a calmer baseline and build proof from repeated visual change instead.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'A lot of people want fat loss to come with a receipt.',
          'One clean number. One obvious answer. One cheerful little dashboard that says: yes, congratulations, your body is changing correctly.',
          'Instead, they get this: the scale moves weirdly, the mirror feels moody, and the belly looks different on some days and rude on others.',
          'So now they ask the question I hear constantly: how do I know this is real weight loss and not fake progress?',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Not All Belly Change Looks the Same',
        paragraphs: [
          'Fat does not always sit or show up the same way.',
          'Some people carry more around the organs and upper abdomen. Some carry more in softer, lower, more subcutaneous areas. Some have posture and muscle issues that change how the midsection projects.',
          'So if you are waiting for weight loss to look identical on every body, you are going to stay confused for a long time.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Better Question Is Not “Am I Lighter?”',
        paragraphs: [
          'One of the best clues is not “am I lighter?” but “what is changing?”',
          'That is the grown-up question.',
          'What part of my body feels different? What looks less pushed out? What hangs differently? What fits differently?',
          'People ignore these clues because they are messier than a scale reading. Too bad. Messier data is still data.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Softness, Firmness, Shape, and Fit All Tell Stories',
        paragraphs: [
          'If the upper abdomen starts feeling less pushed out, that matters. If the lower section softens and shifts differently, that matters. If the waistline on your usual clothes changes before the scale fully cooperates, that matters too.',
          'People often want proof while dismissing the exact body evidence that would calm them down, because it is not as neat as a number.',
          'I understand that. I also think it keeps them trapped longer than necessary.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Scale Is One Witness. It Is Not the Whole Case',
        paragraphs: [
          'The scale can tell you something. It just cannot tell you everything.',
          'And if you treat one witness like the full trial, you will keep missing what the body is actually showing you in shape, tension, softness, posture, and fit.',
          'Then people say there are no signs of progress. There are. They just wanted the lazy kind.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Stop asking only whether your total weight changed.',
          'Use photos, fit, feel, and shape together.',
          'Be specific about where changes are showing up.',
          'Do not let a quiet scale erase obvious body evidence.',
        ],
        outro:
          'Track the body visually. Compare over time. Notice what your shape is doing, not just what gravity says on one morning.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'Real weight loss is often visible before it feels official.',
          'And people who wait for the scale to approve it first waste a lot of peace.',
          'If your only proof of progress is a number that keeps changing its personality, you are missing too much.',
          'Use a better lens. One scan is a number. Weekly check-ins are proof.',
        ],
      },
    ],
  },
  {
    slug: 'read-this-before-you-try-to-fix-your-diet-slip',
    title: 'Read This Before You Try to “Fix” Your Diet Slip',
    description:
      'The first thing to do after a binge is usually not punishment. Most of the sudden weight spike is water, and the real job is finding what made the binge happen in the first place.',
    socialDescription:
      'After a binge, the second mistake is usually trying to punish it out of existence. The real job is understanding the setup.',
    date: '2026-04-27',
    readingTime: '6 min read',
    tags: ['Binge Eating', 'Diet Slips', 'Recovery', 'Appetite'],
    heroImage: '/founder/diet-slip-checkin-20250725.jpg',
    heroAlt: 'Founder check-in image representing a difficult diet slip and recovery moment',
    deck:
      'The first thing to do after a binge is usually not damage control. It is pattern detection. Panic usually makes the sequel easier to write.',
    ctaTitle: 'Do not answer a binge with theater.',
    ctaBody:
      'Start with one calmer read on the pattern, not a punishment fantasy. Better evidence beats a dramatic reset.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'The binge is over.',
          'The wrappers are still there. Your stomach feels ridiculous. And now your brain has entered full courtroom mode.',
          'No carbs tomorrow. Two workouts. I need to erase this.',
          'That is usually the second mistake. The first mistake already happened. The second one is trying to punish it out of existence.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Scale Jump After a Binge Is Usually Louder Than the Actual Damage',
        paragraphs: [
          'People panic because the number moves fast.',
          'They overeat for a day or two, then the scale is suddenly up 2, 3, sometimes even 4 kg.',
          'So they assume the body managed to build a cartoonish amount of fat over one messy stretch of eating.',
          'Usually, no. Most of that immediate jump is water, food volume, and glycogen being stored with water after a lot of processed, carbohydrate-heavy food.',
          'That does not mean the binge was harmless. It means the panic story is usually worse than the physics.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The First Job Is Not Damage Control. It Is Cause Detection.',
        paragraphs: [
          'This is where people waste months. They think the emergency is the weight. Often the emergency is the pattern.',
          'If you binge, crash-restrict, binge, crash-restrict, and call that getting back on track, you are not fixing anything. You are rehearsing the same problem in different clothes.',
          'The smarter question is brutally unglamorous: why did the binge happen?',
          'Not the fake answer. Not because I am weak. The useful answer. What set it up?',
        ],
      },
      {
        type: 'list',
        title: 'Most Binges Are Not Random',
        items: [
          'the diet got too restrictive',
          'a specific craving kept getting ignored',
          'meals got too small',
          'carbohydrates got treated like a criminal class',
          'stress stacked up and food was the first fast exit',
        ],
        outro:
          'Sometimes the body is not asking for more volume. It is asking for what the plan has been refusing to give it.',
      },
      {
        type: 'paragraphs',
        title: 'If You Binge and Then Punish Harder, You Usually Teach the Next Binge How To Happen',
        paragraphs: [
          'This is the part people hate because it ruins the fantasy of heroic recovery.',
          'If the binge came from over-restriction, and your response is even more restriction, what exactly do you think you solved?',
          'You just made a sequel. A very predictable sequel.',
          'It sounded like discipline. It was usually just panic wearing gym clothes.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Do not try to starve the binge away.',
          'Let the water settle before you make identity-level conclusions.',
          'Audit the setup honestly.',
          'Fix the system, not just the symptom.',
        ],
        outro:
          'You do not need a more theatrical reset. You need fewer reasons to binge again.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'After a binge, most people do not need a harsher lecture. They need a cleaner read on what actually happened.',
          'Track the real meals. See the actual pattern. Figure out whether the slip came from hunger, restriction, stress, or food chaos instead of just calling yourself a disaster.',
          'You do not need a more theatrical reset. You need fewer reasons to binge again.',
        ],
      },
    ],
  },
  {
    slug: 'you-do-not-need-to-love-hunger-you-need-to-understand-it',
    title: 'You Do Not Need to Love Hunger. You Need to Understand It.',
    description:
      'You do not need to romanticize hunger to diet well. The real skill is learning the difference between normal appetite, chaotic cravings, and the kind of food pattern that keeps making hunger louder than it needs to.',
    socialDescription:
      'Hunger is not a personality test. The goal is not heroic suffering. The goal is a food pattern that makes appetite less chaotic.',
    date: '2026-04-28',
    readingTime: '6 min read',
    tags: ['Hunger', 'Dieting', 'Appetite', 'Fasting'],
    heroImage: '/founder/hunger-editorial-20260106.jpg',
    heroAlt: 'Founder editorial image used for an article about hunger and appetite during dieting',
    deck:
      'You do not need to enjoy hunger to diet well. You need to understand what kind of hunger you are dealing with, and what kind of food pattern keeps making it louder.',
    ctaTitle: 'Aim for quieter hunger, not heroic suffering.',
    ctaBody:
      'Track the pattern that makes appetite louder or calmer. The goal is not drama. It is a system you can actually live with.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'There is a weird kind of diet advice that always sounds impressive online: learn to enjoy hunger.',
          'Right. And while we are at it, should we learn to enjoy airport security and low battery notifications too?',
          'Hunger is not a personality test. You do not win points for making it dramatic.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Problem Is Not That People Hate Hunger',
        paragraphs: [
          'Of course they do.',
          'If you have been on a diet and found yourself opening the fridge one hour after eating, you were not failing some sacred exam. You were reacting to a sensation that felt urgent, distracting, and annoyingly persuasive.',
          'That is the real issue. Not that hunger exists. That it can become so noisy that everything starts to sound like food.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'There Is a Difference Between Normal Hunger and Chaos',
        paragraphs: [
          'Normal hunger is not the enemy. It is part of being a person with a body.',
          'You go a while without eating. Your appetite rises. You eat. It settles. That is not dysfunction. That is ordinary life.',
          'What people are usually describing when they say, I cannot handle hunger, is something messier.',
          'It is the kind of appetite that feels aggressive, jumpy, and weirdly hard to satisfy.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Is Why Fasting Advice Gets Misunderstood',
        paragraphs: [
          'Intermittent fasting can help some people. It can also get turned into diet theater.',
          'People hear “fast for 16 hours” and imagine the number itself is the magic, as if suffering has a stopwatch.',
          'But if your food pattern keeps swinging your appetite around, the schedule alone does not save you.',
          'You do not need to be spiritually in love with hunger. You need a system where hunger does not feel deranged.',
        ],
      },
      {
        type: 'list',
        title: 'Some Hunger Is Fine. Fake Urgency Is What Wrecks People.',
        items: [
          'highly refined food',
          'not enough satisfying meals',
          'long stretches of white-knuckling',
          'treating appetite like an enemy instead of a signal',
        ],
        outro:
          'A lot of people spend years blaming themselves for the second kind of hunger when the pattern itself is what trained the day to feel unstable.',
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Stop treating all hunger like one thing.',
          'Inspect the food pattern before you inspect your character.',
          'Do not make fasting into a morality badge.',
          'Aim for quieter hunger, not heroic suffering.',
        ],
        outro:
          'You do not need to become someone who loves being hungry. You need to become someone who is no longer getting ambushed by appetite all day.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If you are still deciding what to eat based on whether you can out-argue your cravings, the system is too fragile.',
          'Log the meal. Track the pattern. See what actually makes hunger louder and what makes it calmer.',
          'You do not need to love hunger. You need to understand it.',
        ],
      },
    ],
  },
  {
    slug: 'if-your-diet-broke-your-sleep-it-is-not-discipline-anymore',
    title: 'If Your Diet Broke Your Sleep, It Is Not Discipline Anymore',
    description:
      'If dieting and training hard left you exhausted but unable to sleep, the plan may be under-fueling you. Persistent insomnia deserves real attention, not more self-blame.',
    socialDescription:
      'Diet culture loves flattering breakdown. If your plan leaves you exhausted and awake at 4 a.m., that is not a badge of honor.',
    date: '2026-04-29',
    readingTime: '6 min read',
    tags: ['Sleep', 'Overcorrection', 'Dieting', 'Training Stress'],
    heroImage: '/founder/sleep-reflective-window-20241217.jpg',
    heroAlt: 'Founder reflective image by a window used for an article about diet-related insomnia and overcorrection',
    deck:
      'If dieting and training hard left you exhausted but unable to sleep, the answer is probably not to become even stricter. Sometimes the plan is not impressive. It is just under-fueling a body asked to do too much.',
    ctaTitle: 'Do not romanticize a plan that is breaking signals.',
    ctaBody:
      'If your body is filing complaints, step back and get a clearer read on the pattern instead of answering distress with more discipline theater.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'You went to bed tired. Not cute tired. Not “I crushed my workout” tired. The ugly kind.',
          'Heavy eyes. No energy. The whole body asking for a refund.',
          'Then 4:00 a.m. shows up and you are wide awake for no respectable reason.',
          'Now you are lying there doing exhausted math: I am eating clean. I am training hard. I am doing everything right. So why does my body feel like it is filing a complaint?',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Diet Culture Loves Flattering Breakdown',
        paragraphs: [
          'No appetite? Wow, so disciplined. Cannot sleep? Must be the grind. Running on fumes? At least you are serious.',
          'No. Sometimes the plan is not impressive. Sometimes it is under-fueling a body that is being asked to do too much.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'If Your Output Went Up, Your Support Needs Probably Did Too',
        paragraphs: [
          'If you are lifting several times a week, layering in cardio, and generally trying to be good, your body is using fuel.',
          'If the plan keeps stripping food down while training volume stays high, the body does not always thank you with better results. Sometimes it gets noisier. Sometimes it gets more fragile. Sometimes sleep is one of the first things that starts acting strange.',
          'That does not mean every case of insomnia is caused by dieting. It does mean severe fatigue plus aggressive dieting plus a lot of training is not something to romanticize.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'A Plan Can Look Clean on Paper and Still Be Wrong for the Body Doing It',
        paragraphs: [
          'This happens all the time.',
          'The meals look disciplined. The portions look controlled. The workouts look admirable. And the person is miserable.',
          'They are freezing. They are waking up too early. They are dragging themselves through the day.',
          'But because the plan photographs well, they assume the body is the problem. Or did the plan quietly turn into a low-grade emergency?',
        ],
      },
      {
        type: 'paragraphs',
        title: '“Not Hungry” Is Not the Same Thing as “Well Fueled”',
        paragraphs: [
          'People love this because it sounds efficient: my appetite is down, so the diet must be working.',
          'Not always.',
          'Appetite can get weird when the system is pushed too hard. Feeling less hungry does not automatically mean the body is happy.',
          'And if performance is high, fatigue is high, and sleep is getting wrecked, you do not get to call that success just because the food looks virtuous.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Stop calling obvious distress commitment.',
          'Look at the full setup: food, carbs, training load, energy, sleep, and stress.',
          'Do not ignore persistent insomnia.',
          'Make the plan more livable before you make it more extreme.',
        ],
        outro:
          'When the plan is making you feel wrecked, vague self-blame is useless. You need a clearer read on the pattern.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'Track the behavior. Track the signals. Do not let “I am trying hard” become the only evidence you trust.',
          'Because if your diet broke your sleep, the answer is probably not to try even harder.',
        ],
      },
    ],
  },
  {
    slug: 'cheat-days-do-not-expose-your-character-they-expose-your-system',
    title: 'Cheat Days Do Not Expose Your Character. They Expose Your System.',
    description:
      'Some people binge on cheat days and some do not. The difference is often not willpower. It is whether the body and the food environment are still primed for rebound.',
    socialDescription:
      'Cheat days are not great judges of character. Most of the time they reveal how unstable the weekly setup still is.',
    date: '2026-04-30',
    readingTime: '6 min read',
    tags: ['Cheat Day', 'Binge Eating', 'Relapse', 'Dieting'],
    heroImage: '/founder/cheat-day-checkin-20250719.jpg',
    heroAlt: 'Founder check-in image representing rebound eating and cheat-day instability',
    deck:
      'Cheat days get marketed like rewards, but for a lot of people they function more like release valves. The real question is not whether you are strong. It is whether the system is still built for rebound.',
    ctaTitle: 'Cheat day is not the real question.',
    ctaBody:
      'Track what the week looked like before the binge and use better pattern visibility instead of treating one food event like a morality test.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Cheat days have a terrible publicist.',
          'They get marketed like a reward. A cute little break. A well-earned treat.',
          'Then half the people who try them end up face-first in a buffet wondering why one meal turned into a full emotional incident.',
          'So now they make the obvious conclusion: I have no self-control.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Maybe It Is Not Character. Maybe It Is System Instability.',
        paragraphs: [
          'One person has a cheat meal and spirals. Another person eats the thing they used to obsess over and goes: huh, that was fine.',
          'Same pizza. Different aftermath.',
          'Why? Because the body and the brain are not meeting that food from the same place.',
          'For some people, the system is still primed for rebound. Appetite is still loud. Restriction is still intense. Forbidden food still carries a huge emotional charge.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'A Cheat Day Often Turns Into a Payback Event',
        paragraphs: [
          'When the body has been pushed, restricted, or deprived for a while, it tends to respond when food gets easy again.',
          'Not because you are morally inferior. Because compensation is real. The body likes restoring what felt depleted.',
          'Which means a cheat day can become less like a relaxed meal and more like a delayed reaction.',
          'Now add emotional permission on top: I already broke the rule. Might as well keep going. I will start clean tomorrow.',
          'You can see how this movie ends.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Better Outcome Is Not “Survive Cheat Day”',
        paragraphs: [
          'Some people stop binging on cheat days because the food lost some of its power.',
          'When food patterns change, appetite gets steadier, and highly processed food is no longer the main romance in the week, cheat food does not always hit with the same force.',
          'Sometimes it tastes good and that is all.',
          'That is not fake discipline. That is a different system.',
          'And that is the real goal. Not be strong enough to survive cheat day. Become less dependent on cheat day as a psychological event.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Stop using cheat days to test your morality.',
          'Look at whether the weekly setup is creating rebound.',
          'Watch the emotional charge around forbidden food.',
          'Build a pattern where enjoyable food no longer needs its own holiday.',
        ],
        outro:
          'If your cheat day keeps turning into a crime scene, the answer is not another motivational speech. It is better pattern visibility.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'Track what the week looked like before the binge. Track hunger. Track restriction. Track what foods still have too much power over you.',
          'Cheat days do not usually expose your character. They expose what your system still cannot absorb calmly.',
        ],
      },
    ],
  },
  {
    slug: 'youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth',
    title: 'You’ve Been Told “One Bad Day Won’t Hurt”—But That’s Only Half the Truth',
    description:
      'One binge day usually does less damage than several days of overeating, but that does not make cheat-day logic harmless. The real danger is how quickly a “once in a while” escape starts expanding.',
    socialDescription:
      'One bad day usually does less damage than several bad days. The danger starts when people hear that and turn it into a strategy.',
    date: '2026-05-01',
    readingTime: '6 min read',
    tags: ['Cheat Day', 'Binge Eating', 'Habits', 'Weight Loss'],
    heroImage: '/founder/cheat-day-founder-20251221.jpg',
    heroAlt: 'Founder portrait representing the emotional logic behind cheat-day overcorrection',
    deck:
      'One bad day usually does less damage than several bad days in a row. The problem is how quickly that technically true idea turns into behaviorally disastrous cheat-day logic.',
    ctaTitle: 'Use the truth to stay calm, not to get clever.',
    ctaBody:
      'Track whether the occasional release valve is quietly turning into a structure and use pattern visibility before panic or permission takes over.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'This is one of those diet questions people ask with a smile that already sounds guilty.',
          'Be honest. If I eat a ridiculous amount in one day, is that actually less damaging than overeating more moderately across several days?',
          'Short answer? Usually, yes.',
          'Longer answer? That fact has ruined a lot of diets when people misunderstand what it means.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'One Wild Day Is Often Less Damaging Than Stretching the Chaos Out',
        paragraphs: [
          'This part is real. The body has limits. Digestion has limits. Absorption has limits. And obesity is not built from one dramatic day alone. It is built from patterns that stick around long enough to matter.',
          'So if you compare one ugly day to several ugly days in a row, the several ugly days are usually the bigger problem.',
          'No, this is not permission to treat your weekend like an arson hobby. It is just reality.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Trap Starts When People Hear That and Turn It Into Strategy',
        paragraphs: [
          'This is where the wheels come off.',
          'They think: perfect. I will just hold on, then unload.',
          'Now the cheat day becomes emotional life support. At first, that can feel weirdly helpful. You can tolerate the plan because relief is scheduled.',
          'But over time something ugly tends to happen. The cheat day gets bigger. The list gets longer. The anticipation gets more obsessive.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Real Risk Is Not One Bad Day. It Is Expansion.',
        paragraphs: [
          'The cheat meal becomes a cheat day. The cheat day becomes a cheat weekend. The weekend becomes I will reset Monday.',
          'Then Monday becomes a grief ritual with extra cardio.',
          'That is how a technically true idea becomes behaviorally disastrous.',
        ],
      },
      {
        type: 'paragraphs',
        title: '“One Bad Day Won’t Hurt” Is Only Useful If It Leads to Calm',
        paragraphs: [
          'That is the missing half.',
          'If hearing that helps you avoid panic and simply return to normal structure, good.',
          'If hearing that makes you turn bingeing into a semi-official coping system, not good.',
          'Now the sentence is helping the wrong person inside your head.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do Instead',
        items: [
          'Use the truth to stay calm, not to get clever.',
          'Watch for cheat-day expansion early.',
          'Return to normal faster than you return to guilt.',
          'Build a weekly pattern that does not need a scheduled explosion.',
        ],
        outro:
          'If your entire recovery logic still depends on whether you can estimate the damage of a binge correctly, you are too deep in improvisation.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'Track what happened. Track how often it is happening. Track whether the occasional release valve is quietly turning into a structure.',
          'Because yes, one bad day usually does less than several bad days.',
          'The problem is that people who need that sentence most are often one step away from turning it into a lifestyle.',
        ],
      },
    ],
  },
  {
    slug: 'do-people-who-have-been-obese-for-years-lose-weight-more-slowly',
    title: 'Do People Who Have Been Obese for Years Lose Weight More Slowly?',
    description:
      'Weight gained quickly is often water and leaves quickly. Weight gained slowly over years is usually more fat, so it takes longer to change. But that does not mean your body is uniquely doomed.',
    socialDescription:
      'This question sounds scientific, but underneath it is really a fairness question: am I just stuck with a worse deal because I waited too long?',
    date: '2026-05-02',
    readingTime: '6 min read',
    tags: ['Long-Term Obesity', 'Weight Loss', 'Habits', 'Mindset'],
    heroImage: '/founder/long-game-founder-20251221.jpg',
    heroAlt: 'Founder portrait used for a long-game perspective on weight loss',
    deck:
      'If weight came on slowly over years, more of it is usually true fat rather than temporary water. That can make the process feel heavier, but it does not mean your body is uniquely cursed.',
    ctaTitle: 'If the long game is your game, use long-game tools.',
    ctaBody:
      'When the process is slower, the answer is not more shame. It is better weekly interpretation and better pattern-reading.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'This question usually sounds scientific on the surface.',
          'Underneath, it is often a fairness question.',
          'If I have been overweight for a long time, am I just stuck with a worse deal? Did I wait too long? Is this going to take forever because I was this size for years?',
          'That is what people really want to know.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Quick Gain and Quick Loss Are Usually Talking About Water',
        paragraphs: [
          'There is a reason people say weight gained quickly is lost quickly. Sometimes that is true. But usually it is true because the weight was not mostly fat in the first place.',
          'Holiday eating. Travel. Several days of more sodium and carbohydrates than usual. The scale goes up 3, 4, 5 kg and everyone starts speaking in apocalyptic language.',
          'A lot of that is water. And because it is water, it can leave relatively quickly too.',
          'That is not the same story as body fat built up over a year, or five years, or ten.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Fat Gained Slowly Is Usually Slower To Remove Because It Is Fat',
        paragraphs: [
          'This is the plain answer nobody likes because it refuses to be dramatic.',
          'If weight came on slowly over a long period, more of it is likely to be actual body fat rather than temporary water. And body fat usually changes more slowly than water.',
          'So yes, in a practical sense, long-term weight gain can take longer to change than a short-term water spike.',
          'But that does not mean slowly accumulated fat burns with some mystical reluctance because it has tenure.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Longer the Pattern, the Harder the Pattern Is to Change',
        paragraphs: [
          'This is the real issue.',
          'If you gained weight over years, then your eating habits, routines, stress responses, and comfort behaviors had years to become normal.',
          'That is why long-term obesity often feels harder to undo. Not because your body signed a secret contract against you. Because your habits got furniture.',
          'What gets sticky is not just the fat. It is the lifestyle that kept feeding it.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Is Also Why People Get Too Hopeless Too Early',
        paragraphs: [
          'They assume their current thoughts are permanent facts.',
          'I hate exercise. I will always crave this stuff. I could never live differently for the long term.',
          'Maybe. Or maybe that is just how your mind sounds in the body and routine you have now.',
          'Because when the body changes, the mind often changes with it.',
        ],
      },
      {
        type: 'list',
        title: 'What to Do With This Information',
        items: [
          'Stop comparing fat loss to water loss.',
          'Treat habit change as part of the fat-loss job.',
          'Do not assume your current cravings are your permanent identity.',
        ],
        outro:
          'People who have been overweight for a long time often do not need more shame. They need proof that long-term change is still readable.',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If the long game is your game, then you need tools that reward reading patterns, not panicking over one week.',
          'A better weekly check-in matters here because the process is slower and easier to misjudge emotionally.',
          'This is harder, yes. But harder is not the same as hopeless.',
        ],
      },
    ],
  },
  {
    slug: 'why-appetite-feels-stronger-the-longer-you-diet',
    title: 'Why Appetite Feels Stronger the Longer You Diet',
    description:
      'If dieting has made food feel louder, that does not automatically mean you are weak. Appetite often gets more chaotic when the system becomes too restrictive, repetitive, or emotionally brittle.',
    socialDescription:
      'If food started sounding louder the longer you dieted, that is not always a character problem. Sometimes it is a system problem.',
    date: '2026-05-03',
    readingTime: '7 min read',
    tags: ['Appetite', 'Dieting', 'Cravings', 'Weight Loss'],
    heroImage: '/founder/hunger-editorial-20260106.jpg',
    heroAlt: 'Founder editorial image used for an article about appetite getting louder during dieting',
    deck:
      'If food has started sounding louder the longer you have been dieting, that does not automatically mean you failed. Sometimes it means the system got too restrictive, too repetitive, or too emotionally brittle to stay quiet.',
    ctaTitle: 'Track what makes appetite louder.',
    ctaBody:
      'If food has started sounding louder than it used to, start with one body check-in and a calmer read on the weekly pattern instead of treating every craving like a character flaw.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'The strange part is that dieting often feels easier at the beginning.',
          'That is what confuses people.',
          'The first stretch can feel clean. You are motivated. The rules still feel noble. The meals still feel like evidence that you are finally getting serious.',
          'Then a few weeks later, something uglier starts happening. Food gets louder. Not just hunger. Food.',
          'You are thinking about snacks in the afternoon, dessert at night, bread at dinner, and some stupid hyper-specific thing you were not even craving three weeks ago.',
          'Now your brain starts writing the usual insult: maybe I am just weak. Maybe I do not want this badly enough.',
          'That explanation is emotionally convenient. It is also often lazy.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Early Phase Feels Easier For Reasons People Misread',
        paragraphs: [
          'At the beginning of a diet, there is usually more momentum than insight.',
          'You are running on novelty. The plan is still fresh enough to feel meaningful. The scale may even be flattering you a little.',
          'That combination makes people think they have finally become disciplined. Maybe. Or maybe they are still in the phase where the system has not started arguing back yet.',
          'The beginning is a bad teacher. It makes people think the hard part of dieting is saying no for a few days.',
          'A lot of the time, the hard part is what happens after several weeks of saying no in a fragile, repetitive, underfed way.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Appetite Is Not Just Hunger',
        paragraphs: [
          'This is where people flatten the whole problem.',
          'They say, “I am hungry” when what they really mean is something messier.',
          'Sometimes it is normal physical hunger. Sometimes it is food noise. Sometimes it is that strange agitated appetite where your stomach is not even the loudest part of the experience anymore. Your head is.',
          'That is the version that wrecks people.',
          'You eat, but the thought of food does not quiet down properly. You try to be disciplined, but the whole day starts sounding like negotiation.',
          'Now the diet is not just physically tiring. It is mentally expensive.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Restriction Can Make Food Feel More Important Than It Actually Is',
        paragraphs: [
          'The more dramatic the restriction gets, the more dramatic ordinary food can start to feel.',
          'This is one of the stupid little ironies of dieting. You cut enough things out, moralize enough foods, and tighten hard enough that a completely normal snack starts glowing like forbidden treasure.',
          'Then people misread that glow as proof. Proof that they are addicted. Proof that the food is uniquely dangerous. Proof that they cannot be trusted.',
          'Sometimes the food is not the whole story. Sometimes you just made it emotionally radioactive.',
          'And once food becomes radioactive, appetite stops behaving like a simple biological signal. It becomes anticipation, fantasy, compensation, and resentment all stacked together.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'This Is Why Cheat Meals Start Sounding Romantic',
        paragraphs: [
          'People think cheat meals become appealing because they are weak. No.',
          'A lot of the time, cheat meals become appealing because the rest of the week became psychologically joyless.',
          'Now relief is scheduled. Now bread feels symbolic. Now dessert is not just dessert. It is freedom, revenge, and a tiny vacation from the personality you have been forced to perform all week.',
          'That is a very unstable setup.',
          'The same thing happens with bingeing. A binge rarely feels like a random event when you zoom out honestly.',
          'It usually feels like a delayed answer to a system that kept asking for obedience without giving much stability back.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Goal Is Not To Become Someone Who Never Wants Food',
        paragraphs: [
          'That is not a serious adult goal.',
          'The better goal is simpler and harder: you want a body, routine, and appetite that can tolerate enjoyable food without the whole week collapsing around it.',
          'That is different from pretending cravings should disappear. It is different from worshipping hunger. And it is different from measuring success by how scared you are of bread.',
          'A calmer system is not a perfect system. It is just one where food stops sounding like a daily emergency.',
        ],
      },
      {
        type: 'list',
        title: 'What Usually Helps',
        intro: 'If food has started feeling louder over time, the answer is usually not more theater.',
        items: [
          'meals that are actually satisfying',
          'less emotional mythology around specific foods',
          'fewer all-or-nothing swings',
          'a structure you can stay inside without fantasizing about escape all day',
          'better pattern-reading instead of constant self-judgment',
        ],
        outro:
          'Once you stop treating every loud craving like a character verdict, you finally get enough space to ask the useful question: what keeps making my appetite louder than it needs to be?',
      },
      {
        type: 'paragraphs',
        title: 'Closing',
        paragraphs: [
          'If dieting has made food feel louder, that does not automatically mean you are weak.',
          'It may mean the system got too restrictive, too repetitive, or too emotionally brittle to stay quiet.',
          'That is good news, even if it is annoying. Because systems can be changed.',
          'And if you can track what makes appetite louder and what makes it calmer, you stop treating every craving like a moral emergency.',
          'That is where better dieting actually starts.',
        ],
      },
    ],
  },
  {
    slug: 'exercise-isnt-shrinking-you-the-way-you-expected',
    title: 'Exercise Is Not Shrinking You the Way You Expected',
    description:
      'If you are working out consistently and still not shrinking, the problem probably is not the workout. It is what the workout is actually doing.',
    socialDescription:
      'Exercise is not a shrinking machine. It is a body-composition machine. The scale catches up last.',
    date: '2026-05-04',
    readingTime: '5 min read',
    tags: ['Exercise', 'Weight Loss', 'Body Composition', 'Fitness Myths'],
    heroImage: '/founder/body-composition-proof-20251221.jpg',
    heroAlt: 'Founder mid-training session during the middle phase of transformation',
    deck:
      'Exercise is not a shrinking machine. It is a body-composition machine, a metabolism-shaping machine, a stress-processing machine. What it is not, consistently, is a quick way to remove fat.',
    ctaTitle: 'Separate training from shrinkage.',
    ctaBody:
      'The workout builds the engine. The plate decides what the engine runs on. Start with a weekly check-in that shows both, not just the scale.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'You have been showing up.',
          'Four days a week. Sometimes five. The workouts feel hard. Your clothes feel about the same.',
          'That is the part nobody warns you about.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Principle',
        paragraphs: [
          'Exercise is not a shrinking machine.',
          'It is a body-composition machine, a metabolism-shaping machine, a stress-processing machine. It is many things. What it is not, consistently, is a quick way to remove fat.',
          'A full hour of cardio burns less than people think. Maybe 300 to 500 calories, depending on intensity and your actual body mass. Most people eat that back in a single post-workout snack they did not register as a snack.',
          'This is not a motivational problem. It is an arithmetic problem.',
        ],
      },
      {
        type: 'list',
        title: 'The Mechanism',
        intro: 'When you exercise seriously, three things happen at once.',
        items: [
          'You burn a modest amount of additional calories.',
          'Your body retains more water in the recovering tissue.',
          'Your appetite tends to quietly nudge up.',
        ],
        outro:
          'The first is small. The second makes the scale lie for a few days. The third is the real reason most working-out-but-not-losing-weight stories exist. Your body tends to be very good at protecting its current weight. The workout asks it to change. Its first response is usually to give you more hunger so you can keep training. That is not sabotage. That is homeostasis.',
      },
      {
        type: 'paragraphs',
        title: 'What This Means For You',
        paragraphs: [
          'It means the workout alone does not do the shrinking. The workout builds the engine. The plate decides what the engine runs on.',
        ],
      },
      {
        type: 'list',
        title: 'If You Are Training Hard And Not Changing Shape',
        items: [
          'Keep training.',
          'Stop expecting the scale to move because of the training.',
          'Watch what your appetite does in the two hours after a session.',
          'Make the post-workout window a structure, not a reward.',
        ],
        outro:
          'The people who get leanest from exercise are not the ones who train hardest. They are the ones whose eating does not respond dramatically to the training.',
      },
      {
        type: 'paragraphs',
        title: 'The Quieter Truth',
        paragraphs: [
          'Exercise reshapes you slowly, from the inside. Posture. Stamina. How your shoulders sit. How your gait looks. How quickly you recover from stairs.',
          'If the mirror is not showing it yet, the mirror is behind. The work is there. You can feel it in the stairs.',
          'The scale will catch up. It usually catches up last.',
        ],
      },
    ],
  },
  {
    slug: 'the-unglamorous-middle-of-transformation',
    title: 'The Unglamorous Middle of a Transformation',
    description:
      'Before-and-after photos make transformations look linear. The middle is where most people quit. This is what it actually looked like.',
    socialDescription:
      'The before photo is easy. The after photo is easy. The six months between them is where everybody quits.',
    date: '2026-05-05',
    readingTime: '6 min read',
    tags: ['Founder Story', 'Transformation', 'Weight Loss', 'Consistency'],
    heroImage: '/founder/patience-middle-checkin-20250731.jpg',
    heroAlt: 'Founder during the middle phase of transformation, not before, not after',
    deck:
      'The before photo is easy. The after photo is easy. The six months between them is where everybody quits.',
    ctaTitle: 'Stay inside the middle.',
    ctaBody:
      'The middle does not need motivation. It needs structure that keeps going while you are tired. Start with a weekly check-in you can stay inside without staring at the scale.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'The before photo is easy. The after photo is easy.',
          'The six months between them is where everybody quits.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Photograph Problem',
        paragraphs: [
          'Transformation content is lying to you structurally.',
          'Not intentionally. Just by format. Two images side by side. One blurry. One composed. The middle gets cropped out because the middle does not photograph well.',
          'In the middle you look mostly the same. Slightly less bloated. Slightly more tired. Your face has started to change before your body does, which makes photos of yourself feel dishonest in both directions.',
          'The photo I never posted was the one from July. I was down about 8 kg from my highest. My face looked thinner. My clothes fit worse than before because the fat had shifted but not left. I looked somehow worse than the beginning.',
          'That is the middle.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What The Middle Actually Is',
        paragraphs: [
          'The middle is not a plateau.',
          'It is the phase where the easy wins are over, the novelty is gone, and the real work has become boring. The first 5 kg often come off from water, better sleep, and accidental protein increases. The middle is when the body starts negotiating.',
          'You stop losing visibly. You start noticing the diet. You start noticing your friends eating again. You start wondering whether this is actually going to work.',
          'Everyone who transforms goes through it.',
          'Most transformation content skips it, because it is not a story.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What I Did With It',
        paragraphs: [
          'I kept showing up in the boring way. I did not chase a new plan. I did not add a supplement. I did not cut further.',
          'I logged weight. Some days up. Some days down. I let the graph tell me nothing for three weeks at a time.',
          'I took photos I did not post. I wrote down the exact meals I could eat without thinking.',
          'I let the middle be the middle.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What The Middle Taught Me',
        paragraphs: [
          'The middle is where the habit becomes structure. The body is not changing much, because the body is learning what the new normal is.',
          'If you quit in the middle, you do not quit the diet. You quit the thing that was about to start working.',
          'The after photo is produced by a boring middle. There is no shortcut past it. There are only people who got through it and people who restarted.',
        ],
      },
    ],
  },
  {
    slug: 'is-it-bloat-or-is-it-fat',
    title: 'Is It Bloat or Is It Fat',
    description:
      'A practical guide to distinguishing temporary bloat from real fat gain, so you stop reacting to noise as if it is signal.',
    socialDescription:
      'The body generally cannot synthesize 1.5 kg of fat in one day. Whatever you are panicking about is almost always water.',
    date: '2026-05-06',
    readingTime: '5 min read',
    tags: ['Body Composition', 'Scale', 'Water Weight', 'Daily Fluctuation'],
    heroImage: '/founder/water-weight-proof-20251031.jpg',
    heroAlt: 'Founder image illustrating difference between water-weight fluctuation and real fat',
    deck:
      'This is one of the most useful questions anyone can ask. It is also one of the most mis-answered.',
    ctaTitle: 'Wait before you react.',
    ctaBody:
      'Almost everything that makes the scale move quickly is not fat. A rolling average tells a truer story than today is number. Start with a weekly read that filters daily noise.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'This is one of the most useful questions anyone can ask.',
          'It is also one of the most mis-answered.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: I Gained 1.5 kg Overnight. Is That Fat?',
        paragraphs: [
          'No.',
          'The body generally cannot synthesize 1.5 kg of fat in one day. To store that much fat you would need to eat roughly 11,000 calories above maintenance in 24 hours. You would remember doing it.',
          'What you are seeing is almost always water, glycogen, salt balance, bowel contents, or some combination of the four.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: Then What Does Real Fat Gain Look Like On The Scale?',
        paragraphs: [
          'Slow. Quiet. Unglamorous.',
          'Real fat gain usually looks like a gradual, unexplained drift of 0.5 to 1 kg over 2 to 4 weeks that does not reverse after a normal day. The daily noise is still there, but the trendline is moving in one direction.',
          'If the scale is up today and back to baseline in three days, it was not fat.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: How Can I Tell Which Is Which In The Moment?',
        paragraphs: [
          'You usually cannot, in the moment. That is the point.',
          'Waiting is the answer.',
          'Fat does not appear overnight. Water does. Salt does. Carbs do. Periods do. Poor sleep does. Travel does. Stress does. Almost everything that makes the scale move quickly is not fat.',
          'If the scale spikes, wait four days and weigh again under your usual conditions. If it is still up, and up for three consecutive measurements under usual conditions, then it is worth looking at.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: What About The Mirror?',
        paragraphs: [
          'The mirror is worse than the scale for this.',
          'Bloat changes how you look dramatically in the mirror within hours. Fat changes how you look slowly over weeks. If you thought you looked smaller yesterday and larger today, you are looking at bloat.',
          'A week of mirror-same is more meaningful than a week of mirror-changes.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: Is It Ever Worth Panicking About One Day?',
        paragraphs: [
          'No.',
          'There is no decision you make on a one-day spike that a patient decision three days later would not also catch. The cost of over-reacting is emotional, behavioral, and usually leads to a binge or a skipped meal that does more damage than the original blip.',
          'The honest answer is: it is almost always bloat, and even when it is not, waiting does not cost you anything.',
        ],
      },
    ],
  },
  {
    slug: 'a-plateau-is-a-data-point-not-a-failure',
    title: 'A Plateau Is a Data Point, Not a Failure',
    description:
      'A plateau is the body telling you something specific. Most people read it as rejection and quit. That is not what it is saying.',
    socialDescription:
      'A plateau is the cleanest feedback your body ever gives you. Most people are too frustrated to read it.',
    date: '2026-05-07',
    readingTime: '6 min read',
    tags: ['Plateau', 'Consistency', 'Weight Loss', 'Dieting'],
    heroImage: '/founder/plateau-middle-checkin-20250711.jpg',
    heroAlt: 'Founder reflecting during a plateau phase',
    deck:
      'Most people read a plateau as their body firing them. It is not. A plateau is the cleanest feedback your body ever gives you. Most people are too frustrated to read it.',
    ctaTitle: 'Read the plateau instead of breaking it.',
    ctaBody:
      'Most plateaus break by fixing the thing that drifted, not by cutting more. Start with a weekly trendline that lets you see the shape instead of reacting to a single reading.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Most people read a plateau as their body firing them.',
          'It is not.',
          'A plateau is the cleanest feedback your body ever gives you. Most people are too frustrated to read it.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What A Plateau Actually Is',
        paragraphs: [
          'Three weeks of the same weight, under the same conditions, is a plateau. Less than that is noise.',
          'Real plateaus happen for specific reasons and each one points to something. They are not random. They are not the body quitting on you.',
          'A plateau is your body telling you that the current inputs and the current outputs have matched.',
          'Whatever you are doing is now maintenance for this weight.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What The Plateau Is Saying',
        paragraphs: [
          'It depends on where you are.',
          'Early plateau, first 3 kg in. The easy water and glycogen are gone. Your body is now asking you to actually be in a deficit to continue. Usually means you were not quite as in-deficit as you thought, and now it shows.',
          'Middle plateau, 6 to 12 kg in. Your maintenance calories have dropped because you weigh less. A deficit that worked at the start is not a deficit anymore. The same plan has quietly become a maintenance plan.',
          'Late plateau, near goal. Your body is close to the weight it will most naturally defend. Appetite may increase. NEAT can drop. Metabolism tends to compress. This plateau is loud and takes longer to break.',
          'Each one is a different message. Each one has a different response.',
        ],
      },
      {
        type: 'list',
        title: 'How To Respond',
        intro: 'First, confirm it is actually a plateau. Three weeks of stable weight. Not three days. Then, not panic. Not cut more. Not add cardio. Instead:',
        items: [
          'Check your actual eating, not your perceived eating. Weigh a few meals. Count for three days.',
          'Check your sleep. Poor sleep can stall weight loss cleanly.',
          'Check your stress. Cortisol may retain water and mask fat loss for weeks.',
          'Check your NEAT. Many people unconsciously move less as the diet continues.',
        ],
        outro:
          'Most plateaus break without cutting calories. Most plateaus break by fixing the thing that drifted.',
      },
      {
        type: 'paragraphs',
        title: 'What A Plateau Is Not',
        paragraphs: [
          'It is not punishment.',
          'It is not a sign you should eat more drastically.',
          'It is not a sign the plan does not work.',
          'It is not permanent. A plateau is a report, not a verdict.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Longer Frame',
        paragraphs: [
          'Plateaus are part of the architecture of fat loss. Bodies do not lose weight linearly. They lose in steps and long plateaus. The plateau you are in right now is the ledge between the last step and the next step.',
          'The people who break plateaus are almost always the ones who stopped trying to break them and just kept going.',
        ],
      },
    ],
  },
  {
    slug: 'the-body-looks-different-from-behind',
    title: 'The Body Looks Different From Behind',
    description:
      'Most people only look at themselves from the front. That is why progress feels invisible. The back view is where the body often changes first.',
    socialDescription:
      'I spent eight months watching the front of my body in a mirror and thinking nothing was happening. Then my brother took a photo of me from behind at a wedding. It was a different body.',
    date: '2026-05-08',
    readingTime: '6 min read',
    tags: ['Mirror', 'Body Image', 'Progress Photos', 'Transformation'],
    heroImage: '/founder/transformation-proof-20251119.jpg',
    heroAlt: 'Founder viewed from behind, showing back and shoulder change over time',
    deck:
      'I spent eight months watching the front of my body in a mirror and thinking nothing was happening. Then my brother took a photo of me from behind at a wedding. It was a different body.',
    ctaTitle: 'Give the back mirror a turn.',
    ctaBody:
      'If you only look at yourself from one angle, you miss every change that does not happen at that angle. Take one photo from behind every two weeks. Look at them in groups of four.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'I spent eight months watching the front of my body in a mirror and thinking nothing was happening.',
          'Then my brother took a photo of me from behind at a wedding.',
          'It was a different body.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Front Mirror Lies',
        paragraphs: [
          'The front mirror is the one you see every morning. It is the one in the bathroom, the one in the hallway, the one in every shop fitting room. You see your face. You see your chest. You see your abdomen.',
          'You never see your back. You never see the slope from your hip to your ribs. You never see how your shoulders sit.',
          'So you spent weeks looking at the same mirror and kept asking the same question. Am I smaller?',
          'The mirror you were looking at could not answer that question.',
        ],
      },
      {
        type: 'list',
        title: 'What The Back View Shows',
        intro: 'The back view shows things the front never will.',
        items: [
          'The dip between your shoulder blades.',
          'The slope from your waist out to your hip.',
          'Whether your lats have any shape.',
          'How your glute sits versus how your thigh sits.',
          'Where fat loss is starting, or not starting.',
        ],
        outro:
          'Most people carry fat differently on the front and the back. For many people — and often for women or East Asian builds — the back can change first. Shoulders sharpen. The line from ribcage to waist starts to show. The bra line loosens. The glute lifts slightly as the surrounding fat thins. None of this is visible in the front mirror.',
      },
      {
        type: 'paragraphs',
        title: 'What I Did',
        paragraphs: [
          'I started taking one photo from behind every two weeks. Same spot. Same shirt, or no shirt. Same lighting. No posing.',
          'I did not look at them one by one. I looked at them in groups of four.',
          'The four-photo comparison is where the real story is.',
          'I noticed the back was the first thing that changed. My waistline showed up from behind before it showed up from the front. The shoulders got a line. The posture straightened, which made the whole silhouette look different.',
          'The front mirror was still reporting nothing-happening for another six weeks.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Why The Back May Change First',
        paragraphs: [
          'Different bodies carry fat differently. For many people the visceral fat and lower-belly fat are stubborn, so the front reports last. The back often has less of that buffer. Small changes can show up faster there.',
          'The part I am more certain about is the measurement error. If you only ever look at yourself from one angle, you will miss every change that does not happen at that angle.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Practical Version',
        paragraphs: [
          'Take one photo from behind every two weeks. Same spot. Same lighting. Same clothing or lack of it. Save them in a hidden folder. Look at them in groups of four.',
          'Do not look at them daily. Do not look at them if you are in a bad mood. Do not compare yourself to anyone else from behind.',
          'Just give the back mirror a turn.',
        ],
      },
    ],
  },
  {
    slug: 'progress-update-3-past-the-messy-middle',
    title: 'Progress Update 3: Past the Messy Middle',
    description:
      'The body after the messy middle. What changed, what did not, and what the past four months actually looked like from the inside.',
    socialDescription:
      'This is a check-in, not a before-and-after. Before-and-afters are for people who are finished. I am not finished. What I am is past the messy middle.',
    date: '2026-05-09',
    readingTime: '6 min read',
    tags: ['Progress Update', 'Transformation', 'Founder Story', 'Weight Loss'],
    heroImage: '/founder/progress-update-hanok-20260119.jpg',
    heroAlt: 'Founder composed portrait after coming through the middle phase of transformation',
    deck:
      'Four months past the messy middle. Down roughly 15 kg from the highest. The head is still catching up to the body. This is what that actually feels like.',
    ctaTitle: 'Refuse to renegotiate the plan every three weeks.',
    ctaBody:
      'The middle does not need motivation. It needs a weekly record you can stay inside without staring at the scale every day. Start with one weekly check-in.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'This is a check-in, not a before-and-after.',
          'Before-and-afters are for people who are finished. I am not finished. What I am is past the messy middle.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What The Numbers Say',
        paragraphs: [
          'Down from the highest by roughly 15 kg since the last update.',
          'Training four days a week. Not five. Not six. Four, for months, without negotiation.',
          'Waist down two pant sizes. Shoulders about the same circumference but a noticeably different shape. Face calmer. Feet hurt less.',
          'The scale is not the most honest record of the past four months. What changed more than the weight is what the weight feels like.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What The Middle Did To The Head',
        paragraphs: [
          'The middle is where the emotional story actually happens. I wrote about this in the last update, and it is still true.',
          'The head adapts slower than the body.',
          'I spent the entire middle phase still mentally carrying the old body. Every mirror trip was calibrated against a person who was not quite there anymore. Every shop trip still reached for the size that used to fit. Every compliment still felt early.',
          'Getting through the middle did not fix that. What getting through the middle did was stop me from treating the body as the problem.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What The Middle Did To The Plan',
        paragraphs: [
          'I did not cut calories in the middle. I did not change my training. I did not add cardio. I did not try a new diet.',
          'I stayed bored.',
          'Looking back, staying bored was the skill. The middle keeps asking for novelty because novelty feels like progress when the scale is not moving. It is not progress. It is distraction.',
          'I let the graph do nothing for three weeks at a time. Then nothing again. Then, quietly, it moved.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What Happens Past The Middle',
        paragraphs: [
          'A few things change that nobody warns you about.',
          'Clothes fit differently from the back before they fit differently from the front. Compliments start landing from people who saw you recently, not just people who have not seen you in a year. The appetite calms down in a way that feels almost suspicious. Meals you used to engineer now feel easy.',
          'Also, you start noticing other people in the middle. Friends who are four months into something and wondering if it is working. That part is harder than I expected.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What Still Has Not Changed',
        paragraphs: [
          'My relationship with the scale is better but not clean. My relationship with mirrors is calmer but still uneven. My hunger is less loud but not silent.',
          'The body is further along than the head. I am told that is normal and it takes another six to twelve months past goal for the head to catch up.',
          'I believe it. I am going to keep going.',
        ],
      },
    ],
  },
  {
    slug: 'when-the-workout-becomes-therapy-not-punishment',
    title: 'When the Workout Becomes Therapy, Not Punishment',
    description:
      'Most people train to make up for something. The workouts that change you are the ones that stopped being repayment.',
    socialDescription:
      'For most of my life, the workout was a receipt. That kind of training can still produce results. It cannot produce peace.',
    date: '2026-05-10',
    readingTime: '6 min read',
    tags: ['Exercise', 'Mental Health', 'Body Image', 'Consistency'],
    heroImage: '/founder/consistency-editorial-20251229.jpg',
    heroAlt: 'Founder in a composed mid-session moment representing calmer training',
    deck:
      'For most of my life, the workout was a receipt. I overate on Saturday. I earned the treadmill on Monday. That kind of training can still produce results. It cannot produce peace.',
    ctaTitle: 'Stop training as repayment.',
    ctaBody:
      'When the workout is repayment, you train more and change less. When the workout is maintenance of your nervous system, your body changes while you are not watching. Track both without coupling them.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'For most of my life, the workout was a receipt.',
          'I overate on Saturday. I earned the treadmill on Monday. I felt bloated after dinner. I did twenty more minutes than I planned. Every session was a small repayment for a small crime.',
          'That kind of training can still produce results. It cannot produce peace.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What Punishment-Training Actually Costs You',
        paragraphs: [
          'When exercise is payment, three things happen that nobody talks about.',
          'First, your rest days feel morally dangerous. You skip a session and your brain starts reading the skipped session as an unpaid debt. Then you overcompensate on the next session, or you undereat, or both.',
          'Second, you start training more when you feel worse about yourself, not when your body is ready. So your hardest workouts end up happening on your worst sleep days, your most stressed weeks, your most underfed mornings. That is the arithmetic nobody fixes.',
          'Third, you quietly start to dislike your body more, not less. Because every session is evidence of something you did wrong. Nothing in that loop teaches you to see yourself neutrally.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Switch',
        paragraphs: [
          'At some point in the middle of the diet, I stopped checking my weight right after training.',
          'That sounds trivial. It was not.',
          'Checking the scale post-workout is the most receipt-shaped thing you can do. It closes the loop between effort and reward. The body gives you water retention. The scale gives you a small increase. The mood tanks. The next session gets angrier.',
          'I broke that loop by not weighing until the morning after. Some days the scale moved. Some days it did not. None of it was tied to how the session felt.',
          'Within a few weeks, the training changed shape. I still did four days. I still did the same lifts. But the sessions stopped feeling like apology.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What Therapy-Training Looks Like',
        paragraphs: [
          'It is boring. That is the honest answer.',
          'The workouts became calmer. Not easier. Calmer.',
          'I walked into sessions with no specific mood to regulate. I walked out of sessions without needing the scale to validate me. The sessions started working on the rest of the day, instead of the rest of the day working on the sessions.',
          'Appetite calmed down. Sleep got better. Stress processed itself inside the gym instead of leaking into the evening.',
          'Body changes came more steadily once I stopped using the body as collateral.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What This Is Not',
        paragraphs: [
          'This is not a claim that exercise is free of effort. It is not. The lifts were heavy. The intervals were hard. The recovery was real.',
          'It is a claim that the emotional function of the session changes how the session lands.',
          'When the workout is repayment, you train more and change less.',
          'When the workout is maintenance of your nervous system, you train consistently and your body changes while you are not watching.',
        ],
      },
    ],
  },
  {
    slug: 'hunger-in-maintenance-is-different-from-hunger-on-a-diet',
    title: 'Hunger in Maintenance Is Different from Hunger on a Diet',
    description:
      'Maintenance hunger is not the same signal as dieting hunger. Most people misread it as regression. It is not.',
    socialDescription:
      'The hunger you feel on a diet and the hunger you feel in maintenance are physiologically different. Reading them the same way is one of the main reasons people regain within six months.',
    date: '2026-05-11',
    readingTime: '7 min read',
    tags: ['Appetite', 'Maintenance', 'Dieting', 'Weight Loss'],
    heroImage: '/founder/hunger-editorial-20260106.jpg',
    heroAlt: 'Founder editorial image used for an article about hunger signals in maintenance',
    deck:
      'Maintenance hunger is not the same signal as dieting hunger. Reading them the same way is one of the main reasons people regain weight within six months of reaching their goal.',
    ctaTitle: 'Read the shape of your hunger, not the volume.',
    ctaBody:
      'Waiting out the recalibration window is the actual skill of early maintenance. Log the shape of your hunger over weeks and stop treating maintenance like a failed diet.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Most people treat hunger like it is one thing.',
          'It is not.',
          'The hunger you feel on a diet and the hunger you feel in maintenance are physiologically and behaviorally different. Reading them the same way is one of the main reasons people regain weight within six months of reaching their goal.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Two Different Hungers',
        paragraphs: [
          'Dieting hunger is loud, urgent, often food-specific, and frequently emotional. It tends to cluster around the times you are eating below maintenance. It can spike at night. It can ambush you after exercise. It often feels like the body complaining.',
          'Maintenance hunger is quieter, more mechanical, and usually more rhythmic. It shows up on time. It responds to ordinary meals. It often does not come with cravings. If your meals are structured, maintenance hunger tends to stay in the background.',
          'The confusing part is the transition. Most people come off a diet still hearing the louder hunger and assume they will always be hungry. They will not. But for most people, it takes a few weeks to months for the signal to recalibrate.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Why The Signals Shift',
        paragraphs: [
          'When you lose a meaningful amount of weight, several hormonal systems recalibrate. Leptin, ghrelin, and other satiety and hunger signals adjust to the new weight. This recalibration is not instant. For many people, it often takes weeks to months.',
        ],
      },
      {
        type: 'list',
        title: 'During That Window',
        items: [
          'Appetite cues may remain louder than the new caloric need actually justifies.',
          'The body may still be defending the old weight for a while.',
          'Food noise can stay high even after the deficit has ended.',
        ],
        outro:
          'This is where people misread themselves. They interpret the residual dieting-hunger as evidence that maintenance is not working. They either over-restrict again (triggering the same louder hunger) or they overeat (because they assume they will always be this hungry, so why fight it). Both responses ignore the fact that the hunger signal itself is in transit.',
      },
      {
        type: 'paragraphs',
        title: 'How To Tell Which Hunger You Are Reading',
        paragraphs: [
          'A rough heuristic, not a rule.',
          'Dieting hunger tends to cluster around the times you are eating least, feel emotionally expensive, come with food-specific cravings, and be temporarily silenced by a small amount of food then return quickly.',
          'Maintenance hunger tends to arrive on a predictable schedule, respond to normal-sized meals, leave you alone between meals, and not carry the same emotional weight.',
          'If your hunger still feels like dieting hunger after you have moved to maintenance calories, you are probably in the recalibration window.',
          'Waiting out the recalibration window is the actual skill of early maintenance.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What Most People Do Wrong',
        paragraphs: [
          'They panic at weeks 3 to 8 of maintenance, when hunger is still loud.',
          'They decide they are going to regain everything, so they either tighten the reins (returning to deficit, which resets the loud hunger) or abandon the plan entirely.',
          'The people who hold maintenance are not the ones with less hunger. They are the ones who understand that the hunger signal is temporarily miscalibrated and does not require a plan change.',
        ],
      },
      {
        type: 'list',
        title: 'What Helps',
        intro: 'A handful of quiet things.',
        items: [
          'Keep meal structure consistent. Regular eating times reduce the noise.',
          'Protein and fiber at most meals. They flatten the hunger curve.',
          'Sleep. Poor sleep amplifies every hunger signal.',
          'Time. This is the one nobody wants to hear.',
        ],
        outro:
          'Three to four months into maintenance, for most people who hold the weight, hunger settles into something manageable.',
      },
    ],
  },
  {
    slug: 'the-friend-who-never-diets-and-never-gains',
    title: 'The Friend Who Never Diets and Never Gains',
    description:
      'The friend who never diets and never gains is not lucky in the way you think. What is actually going on is usually boring and almost always invisible.',
    socialDescription:
      'The friend who stays slim without trying is running a set of invisible habits that happen to balance. The interesting question is which of those habits is genuinely learnable for you.',
    date: '2026-05-12',
    readingTime: '6 min read',
    tags: ['Body Composition', 'NEAT', 'Habits', 'Weight Stability'],
    heroImage: '/founder/long-game-founder-20251221.jpg',
    heroAlt: 'Founder image representing the boring long-game habits that actually keep bodies stable',
    deck:
      'Everyone has that friend. Eats whatever. Never seems to gain. Never goes to the gym except in theory. Has the same body in September that they had in May. You do not, and you are furious about it.',
    ctaTitle: 'Learn the invisible habits, not the conscious effort.',
    ctaBody:
      'You are comparing a diet to a personality. That comparison is rigged. Track the small patterns your naturally stable days already have, and build from there.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'Everyone has that friend.',
          'Eats whatever. Never seems to gain. Never goes to the gym except in theory. Has the same body in September that they had in May.',
          'You do not, and you are furious about it.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Myth',
        paragraphs: [
          'The assumption is usually one of three things.',
          'Genetics. Metabolism. Luck.',
          'None of these are quite the story.',
          'The friend who stays slim without trying is usually not doing nothing. They are doing a lot of small, invisible things that add up to a stable energy balance, and they are doing them without naming them as effort.',
          'You are looking at the outcome and calling it magic because the process is not visible to you.',
        ],
      },
      {
        type: 'list',
        title: 'What They Actually Do, Without Calling It Anything',
        intro: 'Watch a naturally slim friend for a week. Not at meals. Between meals.',
        items: [
          'They stand more.',
          'They fidget more.',
          'They sleep a relatively consistent number of hours.',
          'They eat the same kinds of things most days and do not dramatize food.',
          'They stop eating when they are full and forget the rest of the plate without treating it as discipline.',
          'They do not snack mindlessly while watching television. They do sometimes. But not the way you think.',
        ],
        outro:
          'None of this looks like a diet. None of it looks like effort. Because to them, it is not effort. It is the default pattern they happen to have.',
      },
      {
        type: 'paragraphs',
        title: 'The Boring Physiology Piece',
        paragraphs: [
          'There are a few physiological factors that genuinely differ between people.',
          'NEAT, or non-exercise activity thermogenesis, varies significantly. Some people unconsciously move hundreds more calories a day than others. Fidgeting, posture shifts, walking around on phone calls, going up one flight of stairs for no reason. This is real, and it is mostly unconscious.',
          'Satiety signaling also varies. Some people reach fullness faster and stay full longer. This is partly genetic, partly habitual.',
          'Gut microbiome, hormonal differences, sleep architecture, and a half-dozen other factors can tilt the baseline.',
          'All of these can make someone look like they are eating without consequence, when they are actually eating within a tighter range than they realize.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'What This Means For You',
        paragraphs: [
          'Two things.',
          'First, stop comparing your conscious effort to their unconscious default. You are comparing a diet to a personality. That comparison is rigged.',
          'Second, some of what they do unconsciously is learnable. Not all of it. But more than people assume.',
          'The stand-more, sleep-consistent, do-not-dramatize-food pattern can be installed. It takes a year, roughly. It does not look like weight loss. It looks like a different relationship with eating and moving.',
          'People who reach their goal and hold it for five years are almost always the ones who installed that pattern, not the ones who dieted hardest.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'The Quiet Truth',
        paragraphs: [
          'The friend who stays slim without trying is the blueprint, not the insult.',
          'They are not cheating. They are running a set of invisible habits that happen to balance. The interesting question is not why does my body not do that. The interesting question is which of those habits is genuinely learnable for me.',
          'The answer is usually: more of them than you think.',
        ],
      },
    ],
  },
  {
    slug: 'how-do-you-know-when-youve-reached-your-set-point',
    title: 'How Do You Know When You Have Reached Your Set Point',
    description:
      'Questions and honest answers about what a set point actually is, how to know you are at one, and what it means if you want to go lower.',
    socialDescription:
      'The set point is not a fixed number handed to you at birth. It is not a verdict. It is information.',
    date: '2026-05-13',
    readingTime: '7 min read',
    tags: ['Set Point', 'Maintenance', 'Weight Loss', 'Body Composition'],
    heroImage: '/founder/scale-proof-20250919.jpg',
    heroAlt: 'Founder image representing reading the body is steady state, not chasing a lower number',
    deck:
      'A set point is one of the more misused ideas in dieting conversations. It is useful when understood correctly. It becomes an excuse when it is not.',
    ctaTitle: 'Read the set point as information, not verdict.',
    ctaBody:
      'If you are at your set point, the question is no longer am I losing. The question is am I staying. Those require different reads.',
    sections: [
      {
        type: 'paragraphs',
        paragraphs: [
          'A set point is one of the more misused ideas in dieting conversations.',
          'It is useful when understood correctly. It becomes an excuse when it is not.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: What Is A Set Point, Actually?',
        paragraphs: [
          'A set point is the weight range your body most naturally defends, given your current habits, sleep, stress, training, and eating pattern.',
          'It is not a fixed number handed to you at birth.',
          'It is not immune to change.',
          'It is a rolling equilibrium that shifts as your inputs shift. The word "set" makes it sound more permanent than it is.',
        ],
      },
      {
        type: 'list',
        title: 'Q: How Do I Know I Have Reached Mine?',
        intro: 'A few signals, in combination.',
        items: [
          'Your weight has been stable within roughly a 2 to 3 kg range for 8 to 12 weeks.',
          'You have stopped actively dieting. You are eating in a way that feels sustainable, not restrictive.',
          'Your hunger has normalized. It arrives on time, responds to normal meals, and does not dominate your day.',
          'Your energy, sleep, and mood are reasonable. You are not running on fumes.',
          'Small deviations (a heavier weekend, a lighter week of travel) do not send the weight permanently up or down.',
        ],
        outro:
          'If most of those are true, the weight you are at is probably a set point for your current life.',
      },
      {
        type: 'paragraphs',
        title: 'Q: Why Does It Feel Like I Cannot Lose More?',
        paragraphs: [
          'Because your maintenance calories have adjusted downward as you lost weight, your body is defending the current state, and your signals for hunger and fullness are tuned to this range.',
          'To go lower, you would need to either create a new deficit below your current maintenance (which will temporarily raise hunger again) or change the inputs by adding muscle, improving sleep, or shifting activity (which can lower the defended weight over time).',
          'Neither of these is free. Both are possible. The question is whether the cost is worth the change.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: Is The Set Point Really Immovable?',
        paragraphs: [
          'No. But it is sticky.',
          'Research on weight regulation suggests the body defends recent weights more strongly than older weights. If you hold a new weight for 12 to 24 months, that weight often becomes the new defended range.',
          'This is why maintenance is the real skill. Not because reaching a lower number is the hard part. Because holding it long enough for your body to accept it is the hard part.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: If I Am At A Set Point, Should I Stop Trying To Lose More?',
        paragraphs: [
          'This is the question most people will not let themselves ask.',
          'The honest answer is: sometimes yes.',
          'If you are at a weight where your habits are sustainable, your health markers are reasonable, and your life functions well, the marginal benefit of another 3 to 5 kg down is often smaller than the cost of continuing to diet.',
          'If you want to lose more for reasons that are yours, not reasons inherited from a magazine or a photo, that is a fine decision. But it is a decision, not an obligation.',
          'The set point is not a verdict. It is information.',
        ],
      },
      {
        type: 'paragraphs',
        title: 'Q: What Should I Do Once I Know I Am At One?',
        paragraphs: [
          'Hold it with boring discipline for at least six months. Let the body accept this weight as the new normal.',
          'Then decide if you want to change the inputs.',
          'That sequence, in that order, is what separates people who lose and hold from people who lose and yo-yo.',
        ],
      },
    ],
  },
];

export function getAllBlogPosts() {
  return [...posts].sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getBlogPostBySlug(slug: string) {
  return posts.find((post) => post.slug === slug);
}

export function getRelatedBlogPosts(slug: string, limit = 3) {
  return getAllBlogPosts()
    .filter((post) => post.slug !== slug)
    .slice(0, limit);
}

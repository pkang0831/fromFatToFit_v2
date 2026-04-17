# Medium Operating System

This file is the practical operating system for publishing founder-led writing on Medium without relying on memory.

Core rule:

- publish manually on Medium
- automate reminders and distribution around that manual publish step
- do not wait for perfect tooling before publishing

## Source Of Truth

Use this folder as the Medium publishing base:

- `marketing/fitness_blogging/blog_strategy/medium_launch/`

Primary files:

- `first_6_launch_plan.md`
- `publish_checklist.md`
- `wave_01_01_consistency_medium_manual_publish_package.md`
- `wave_01_02_founder_story_medium_manual_publish_package.md`
- `wave_01_03_mirror_medium_manual_publish_package.md`
- `wave_01_04_weighin_medium_manual_publish_package.md`
- `wave_01_05_binge_repair_medium_manual_publish_package.md`
- `wave_01_06_cheat_day_medium_manual_publish_package.md`
- `wave_01_tracker.md`

## Publishing Principle

Do not publish all 6 at once.

Use this model instead:

- one article at a time
- but each article gets a short concentrated push window
- publish cadence stays consistent

Best starter cadence:

- Monday
- Wednesday
- Friday

That gives 6 posts over 2 weeks.

## Recommended Wave 01 Order

1. `The Most Reliable Way to Succeed at Dieting Is Still the Least Dramatic One`
2. `Why I Built Devenira for the Weeks Where You Want to Quit`
3. `Why the Mirror Can Make Real Progress Feel Fake`
4. `One Emotional Weigh-In Can Wreck a Good Week`
5. `Read This Before You Try to “Fix” Your Diet Slip`
6. `Cheat Days Do Not Expose Your Character. They Expose Your System.`

## Manual Publish Workflow

For each post:

1. Open the matching `wave_01_0X_..._medium_manual_publish_package.md`
2. Copy:
   - Title
   - Subtitle / Description
   - 5 tags
   - Cover direction
   - `## Markdown` block
3. Create Medium draft manually
4. Paste the title and body
5. Add subtitle and tags
6. Set canonical URL to the owned-site article
7. Add cover image if using one
8. Final read for spacing, headers, and links
9. Publish
10. Paste final Medium URL into `wave_01_tracker.md`

## What Must Stay Manual

Medium itself should be treated as manual-first.

Why:

- Medium's official API is deprecated / unsupported for new integrations
- browser automation is fragile and can break on login, editor, or captcha changes
- the one action that must not fail silently is the actual publish step

So the operating model is:

- human presses publish
- system remembers everything around that publish

## What Can Be Automated Reliably

### 1. Reminders

Use either:

- Google Calendar
- Todoist
- Notion recurring tasks

Minimum reminder setup:

- Monday 10:00: publish Medium post
- Wednesday 10:00: publish Medium post
- Friday 10:00: publish Medium post

Each reminder should include:

- post title
- package filename
- owned-site canonical URL
- checklist link

### 2. Post-Publish Tracking

Immediately after publishing, update:

- `wave_01_tracker.md`

Fields to fill:

- publish status
- Medium URL
- publish date
- whether shared to X / LinkedIn / Facebook

### 3. Distribution Automation

Recommended stack:

- Medium RSS
- Zapier
- Buffer

Flow:

1. You publish manually on Medium
2. RSS updates
3. Zapier detects new item
4. Zapier sends item to Buffer as:
   - queue item, or
   - draft / idea for manual polish
5. Buffer holds scheduled social distribution

## Recommended Automation Setup

### Option A: Safer

Use Zapier to send new Medium RSS items to Buffer drafts / ideas.

Why this is best:

- you do not forget the post exists
- you still get one manual review pass before social publishing
- it avoids low-quality auto-post text on social

### Option B: Faster

Use Zapier to add new Medium RSS items directly to the Buffer queue.

Use this only if:

- your share copy format is stable
- you are comfortable with semi-automatic distribution

## Medium RSS -> Buffer Setup

### Trigger

- `RSS by Zapier`
- event: `New Item in Feed`
- feed URL: your Medium profile or publication RSS feed

### Action

- `Buffer`
- event: `Add to Queue` or equivalent draft/idea action

### Suggested default message format

`New on Medium: {{title}}

{{url}}`

Better version if custom formatting is available:

`{{title}}

A new piece in the Devenira writing system.
{{url}}`

### Best practice

Do not blast all networks at once with the exact same raw message.

Better:

- Buffer queue item created automatically
- you manually tweak the copy per platform before it goes live

## Minimal Weekly Ritual

### Monday

- publish the scheduled Medium article
- update tracker
- queue or review social distribution

### Wednesday

- publish next article
- update tracker
- review reactions on the previous one

### Friday

- publish next article
- update tracker
- note what subject line / opening performed best

## Anti-Forgetting Rules

- never rely on remembering the next post mentally
- every post must have a row in `wave_01_tracker.md`
- every publish date must exist in calendar or task manager
- if a post slips, move the date in the tracker immediately
- do not stack missed posts on one day just to catch up

## Recommended Status Labels

Use these labels in the tracker:

- `ready`
- `scheduled`
- `published`
- `shared`
- `completed`

Definition:

- `ready`: package finished
- `scheduled`: publish date assigned
- `published`: live on Medium
- `shared`: distributed externally
- `completed`: fully done and logged

## Best Immediate Operating Mode

Right now, use this exact rule:

- publish one Medium article per scheduled slot
- update the tracker immediately after publishing
- let the system remind you, not your memory

That is enough automation to make the workflow sustainable without depending on a broken Medium API.

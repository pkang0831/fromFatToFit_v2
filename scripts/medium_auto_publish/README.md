# Medium Auto-Publish — Playwright Automation

Medium's official Import-from-URL **does not auto-import cover images**
(confirmed after four HTML/OG/redirect fixes on 2026-04-23). This
script sidesteps that by driving the Medium editor UI with Playwright:
imports the story, uploads the cover image from disk, sets tags,
clicks Publish, returns the published URL.

One-time manual login. Subsequent publishes fully automated.

## Install

```bash
pip3 install --break-system-packages playwright
python3 -m playwright install chromium
```

## First-time login

```bash
cd <repo-root>
python3 scripts/medium_auto_publish/medium_auto_publish.py --setup
```

A Chromium window opens at Medium's login page. Log in with whichever
method works (Google SSO, Apple, or email/password). When you see your
Medium home feed, press Enter in the terminal. Session cookies are
saved to `~/.medium_auto_publish_profile`.

## Publish one story

```bash
python3 scripts/medium_auto_publish/medium_auto_publish.py \
  --slug why-did-i-stop-losing-weight-at-3-months
```

This:

1. Opens Medium's Import-from-URL with `https://www.devenira.com/blog/<slug>`
2. Waits for import to finish (Medium converts H1/H2/lists/answerBox)
3. Uploads the cover image (`frontend/public/founder/<hero>.webp`)
4. Opens Publish flow
5. Types the 5 tags from posts.ts
6. Clicks Publish
7. Waits for the story URL and prints it

Copy the printed URL into `frontend/src/content/blog/posts.ts` on
the matching post's `mediumUrl:` field. (Or let a follow-up script
do that for you — not automated yet.)

## Dry run

```bash
python3 scripts/medium_auto_publish/medium_auto_publish.py \
  --slug why-did-i-stop-losing-weight-at-3-months --dry-run
```

Imports + uploads cover + sets up tags but **does not click Publish**.
Browser stays open for manual review. Useful for the first test.

## Known caveats

- **Medium's DOM changes periodically.** If selectors stop working,
  the script will fail noisily (you'll see "could not find Publish
  button" etc). Run with `--dry-run` to debug.
- **Canonical URL handling**: Medium's import auto-sets canonical to
  `devenira.com/blog/<slug>`. The script does NOT currently clear it.
  TODO: add a step to navigate to Story settings → SEO → clear
  canonical before Publish. For now, after each publish:
    1. Open the published story on Medium
    2. ⋯ menu → Story settings → SEO
    3. Clear Canonical URL field, save
- **Rate limits**: Medium's anti-spam threshold for new accounts is
  ~5–10 publishes per hour. Don't batch all 64 at once. Space them
  out (use the 30-day publish calendar).

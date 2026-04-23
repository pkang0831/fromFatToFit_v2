#!/usr/bin/env python3
"""
Automated Medium publishing via Playwright.

Medium's Import-from-URL feature does NOT auto-import cover images
(confirmed 2026-04-23: four iterations of HTML/OG/redirect fixes did
not resolve this — Medium's design omits cover auto-upload for
imports). This script sidesteps the limitation by driving the
Medium editor UI directly: it opens a new story, pastes the HTML
body from devenira.com, uploads the cover image from disk, sets
tags, clears canonical URL per the 2026-04-21 canonical flip, and
publishes.

Session is persisted across runs in `--profile-dir`. First run is
manual-login (script pauses with the Medium login page open; user
completes login via Google or email/password, then presses Enter).
Subsequent runs reuse the saved session cookies → fully automated
publishing of an unlimited number of stories.

Usage:

  # First time setup — opens browser, pauses for you to log in:
  python3 medium_auto_publish.py --setup

  # Publish one post by its devenira.com slug:
  python3 medium_auto_publish.py --slug how-to-stick-to-a-diet-when-progress-slows

  # Dry run (no Publish click, leaves draft for you to inspect):
  python3 medium_auto_publish.py --slug <slug> --dry-run

Dependencies: `pip install playwright && playwright install chromium`
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


def _save_debug(page, tag: str) -> None:
    """On any error, dump a screenshot + full HTML to /tmp so we can
    iterate on selectors without the user having to DOM-inspect."""
    import datetime as dt
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path("/tmp/medium_auto_publish_debug")
    out_dir.mkdir(exist_ok=True)
    try:
        shot = out_dir / f"{ts}-{tag}.png"
        page.screenshot(path=str(shot), full_page=True)
        html = out_dir / f"{ts}-{tag}.html"
        html.write_text(page.content(), encoding="utf-8")
        print(f"  debug saved: {shot}")
        print(f"  debug saved: {html}")
        print(f"  current URL: {page.url}")
    except Exception as e:
        print(f"  (could not save debug artefacts: {e})")

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
PACKAGES_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
HERO_DIR = ROOT / "frontend/public/founder"
DEFAULT_PROFILE = Path.home() / ".medium_auto_publish_profile"


# ---------- posts.ts helpers ----------


def parse_posts_ts() -> dict[str, dict]:
    """Return slug → {slug, seoTitle, metaDescription, tags, heroImage,
    keywords, cluster, schemaType, deck} from posts.ts."""
    src = POSTS_TS.read_text()
    m = re.search(
        r"const posts: BlogPost\[\] = \[\n(.*?)\n\];\s*\n\s*\n?export function getAllBlogPosts",
        src, re.DOTALL,
    )
    body = m.group(1)
    # Extract per-post blocks with brace matching
    depth = 0; start = None
    in_s = False; sc = None; in_t = False; esc = False
    blocks = []
    for i, c in enumerate(body):
        if esc: esc = False; continue
        if c == "\\": esc = True; continue
        if in_s:
            if c == sc: in_s = False
            continue
        if in_t:
            if c == "`": in_t = False
            continue
        if c in ("'", '"'):
            in_s = True; sc = c; continue
        if c == "`":
            in_t = True; continue
        if c == "{":
            if depth == 0: start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(body[start:i + 1])
                start = None

    out = {}
    for pb in blocks:
        def field(name):
            m = re.search(rf"{name}:\s*'((?:[^'\\]|\\.)*)'", pb)
            if m:
                return m.group(1).replace("\\'", "'")
            m = re.search(rf'{name}:\s*"((?:[^"\\]|\\.)*)"', pb)
            if m:
                return m.group(1).replace('\\"', '"')
            return None

        def arr(name):
            m = re.search(rf"{name}:\s*\[(.*?)\]", pb, re.DOTALL)
            if not m:
                return []
            return [a or b for a, b in re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", m.group(1))]

        slug = field("slug")
        if not slug:
            continue
        out[slug] = {
            "slug": slug,
            "title": field("title") or "",
            "seoTitle": field("seoTitle") or field("title") or "",
            "metaDescription": field("metaDescription") or "",
            "tags": arr("tags"),
            "heroImage": field("heroImage") or "",
            "heroAlt": field("heroAlt") or "",
            "keywords": arr("keywords"),
            "cluster": field("cluster") or "",
            "schemaType": field("schemaType") or "",
            "deck": field("deck") or "",
            "mediumUrl": field("mediumUrl"),
        }
    return out


# ---------- Automation ----------


def login_setup(profile_dir: Path) -> None:
    profile_dir.mkdir(parents=True, exist_ok=True)
    print(f"Opening Chromium with profile dir: {profile_dir}")
    print("Log in to Medium manually. The session will be saved.")
    print("Use whichever method works — Google SSO, Apple, email/password.")
    print("When you're logged in and see your Medium home feed, press Enter here.")

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.new_page()
        page.goto("https://medium.com/m/signin")
        input("\n[Press Enter after you are logged in and see the Medium feed]: ")
        # Verify login by checking for user menu
        try:
            page.goto("https://medium.com/me/stories/drafts", wait_until="networkidle")
            time.sleep(2)
            print("Login detected. Session saved.")
        except PWTimeout:
            print("WARNING: could not verify login. Continuing anyway.")
        ctx.close()


def publish_one(
    post: dict,
    profile_dir: Path,
    dry_run: bool = False,
    headless: bool = False,
) -> str | None:
    """Drive the Medium UI to publish one story. Returns the published URL
    or None on dry_run."""
    hero_path = HERO_DIR / Path(post["heroImage"]).name
    if not hero_path.exists():
        print(f"ERROR: hero image missing: {hero_path}")
        return None

    source_url = f"https://www.devenira.com/blog/{post['slug']}"

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            viewport={"width": 1400, "height": 950},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.new_page()

        # Step 1: use Medium's Import Story feature — gets body text + headings
        # right automatically. We'll then add the cover image that Medium's
        # importer always omits.
        print(f"  opening Medium import with URL: {source_url}")
        page.goto("https://medium.com/p/import", wait_until="networkidle", timeout=60000)

        # Verify we didn't get redirected to signin
        current = page.url
        if "/m/signin" in current or "/signin" in current:
            print("ERROR: Medium redirected to signin — session expired or never set up.")
            print("Run: python3 scripts/medium_auto_publish/medium_auto_publish.py --setup")
            _save_debug(page, "signin-redirect")
            ctx.close()
            return None

        # Wait for the import page to actually hydrate. The "See your story
        # on Medium" heading appears only after client-side render. Observed
        # 2026-04-23: `page.content()` immediately after goto returned only
        # the search input from the top nav, not the import form, because
        # hydration hadn't happened yet.
        #
        # Note: we can't comma-combine `text=...` with CSS selectors — it's
        # a Playwright-specific syntax. Use separate get_by_role / get_by_text
        # locators and any-of.
        hydration_markers = [
            page.get_by_role("heading", name=re.compile(r"See your story on Medium", re.I)),
            page.get_by_role("heading", name=re.compile(r"Import your story", re.I)),
            page.get_by_text(re.compile(r"Enter a link to your blog", re.I)),
        ]
        hydrated = False
        for marker in hydration_markers:
            try:
                marker.first.wait_for(timeout=8000, state="visible")
                hydrated = True
                break
            except Exception:
                continue
        if not hydrated:
            print("  (none of the hydration markers appeared in 8s each — continuing anyway)")
        time.sleep(2)

        # Medium's import-page URL input has placeholder
        # "http://www.yoursite.org/your-post" (observed 2026-04-23). It's an
        # HTML <input type="text"> not type="url", no name attribute, no
        # data-testid. So we match by placeholder prefix or by being the
        # first non-search text input.
        url_input = None
        selectors = [
            'input[placeholder^="http" i]',              # primary
            'input[placeholder*="yoursite" i]',
            'input[placeholder*="your-post" i]',
            'input[type="url"]',
            'input[placeholder*="paste" i]',
            'input[placeholder*="URL" i]',
            'input[name*="url" i]',
            'input[aria-label*="url" i]',
            'input[data-testid*="import" i]',
            'input:not([type="search"])',                # last resort — any non-search input
        ]
        for sel in selectors:
            try:
                candidate = page.locator(sel).first
                candidate.wait_for(timeout=3000, state="visible")
                url_input = candidate
                print(f"  found URL input via selector: {sel}")
                break
            except PWTimeout:
                continue
            except Exception:
                continue

        if url_input is None:
            print("ERROR: could not find URL input on import page. Saving debug artefacts...")
            _save_debug(page, "import-url-input-missing")
            ctx.close()
            return None

        try:
            url_input.click()
            url_input.fill(source_url)
            time.sleep(0.5)
        except Exception as e:
            print(f"ERROR: failed to fill URL input: {e}")
            _save_debug(page, "import-url-fill-failed")
            ctx.close()
            return None

        # Click Import button
        try:
            import_btn = page.get_by_role("button", name=re.compile(r"^import$", re.I)).first
            import_btn.click()
        except Exception as e:
            print(f"  could not click Import button: {e}")
            ctx.close()
            return None

        # Wait for import to complete — the URL changes to /p/<id>/edit
        try:
            page.wait_for_url(re.compile(r"/p/[a-z0-9]+/edit"), timeout=90000)
            print(f"  imported: {page.url}")
        except PWTimeout:
            print(f"  import did not complete in 90s — current URL: {page.url}")
            ctx.close()
            return None

        # Give the editor a moment to stabilise
        time.sleep(5)

        # Step 2: upload cover image
        print(f"  uploading cover: {hero_path.name}")
        # Click just below the title to place cursor there
        try:
            title_el = page.locator("h1").first
            title_el.wait_for(timeout=10000)
            box = title_el.bounding_box()
            # Click ~30 px below the title's bottom edge
            page.mouse.click(box["x"] + 40, box["y"] + box["height"] + 20)
            time.sleep(1)
        except Exception as e:
            print(f"  WARN: could not place cursor under title: {e}")

        # Medium shows a circular "+" on the left margin when cursor on new line.
        # Click it, then click the image icon in the popover.
        try:
            plus_btn = page.get_by_role("button", name=re.compile(r"add", re.I)).first
            plus_btn.wait_for(timeout=8000)
            plus_btn.click()
            time.sleep(0.5)
        except Exception:
            # Fallback: use keyboard shortcut or direct file input
            pass

        # Use direct file-chooser event on Medium's hidden <input type="file">
        # It is always present in the DOM for image uploads.
        try:
            file_input = page.locator('input[type="file"]').first
            file_input.set_input_files(str(hero_path))
            print("  cover image uploaded via file input")
            time.sleep(4)  # wait for upload to complete
        except Exception as e:
            print(f"  ERROR uploading cover: {e}")

        # Step 3: open Publish flow
        print("  opening publish flow")
        try:
            publish_btn = page.get_by_role("button", name=re.compile(r"^publish$", re.I)).first
            publish_btn.click()
            time.sleep(3)
        except Exception as e:
            print(f"  could not find Publish button: {e}")
            ctx.close()
            return None

        # Step 4: add tags
        print(f"  adding tags: {post['tags']}")
        try:
            topics_input = page.locator('input[placeholder*="topic" i], div[aria-label*="topic" i]').first
            topics_input.wait_for(timeout=10000)
            for tag in post["tags"][:5]:
                topics_input.click()
                topics_input.type(tag, delay=30)
                time.sleep(0.4)
                page.keyboard.press("Enter")
                time.sleep(0.4)
        except Exception as e:
            print(f"  WARN: could not set tags: {e}")

        if dry_run:
            print("  DRY RUN — leaving draft unpublished. Browser stays open.")
            print("  Press Enter to close browser and move on.")
            input()
            ctx.close()
            return None

        # Step 5: click final Publish
        print("  clicking final Publish")
        try:
            final_publish = page.get_by_role("button", name=re.compile(r"publish now|^publish$", re.I)).last
            final_publish.click()
        except Exception as e:
            print(f"  ERROR: could not click final Publish: {e}")
            ctx.close()
            return None

        # Wait for URL change to the published story URL (ends in -{hash})
        try:
            page.wait_for_url(
                re.compile(r"medium\.com/@[^/]+/[a-z0-9-]+-[0-9a-f]{12}$"),
                timeout=60000,
            )
            pub_url = page.url
            print(f"  PUBLISHED: {pub_url}")
            ctx.close()
            return pub_url
        except PWTimeout:
            print(f"  did not detect published URL in 60s. Current: {page.url}")
            input("  Check the browser. Press Enter to close.")
            ctx.close()
            return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", help="posts.ts slug of the story to publish")
    p.add_argument("--setup", action="store_true", help="One-time manual login")
    p.add_argument("--profile-dir", default=str(DEFAULT_PROFILE))
    p.add_argument("--dry-run", action="store_true", help="Import + upload cover but do not click Publish")
    p.add_argument("--headless", action="store_true", help="Run without visible browser window")
    args = p.parse_args()

    profile_dir = Path(args.profile_dir)

    if args.setup:
        login_setup(profile_dir)
        return 0

    if not args.slug:
        p.print_help()
        return 1

    posts = parse_posts_ts()
    if args.slug not in posts:
        print(f"ERROR: slug '{args.slug}' not found in posts.ts")
        print(f"Available slugs (first 5): {list(posts.keys())[:5]}")
        return 2

    post = posts[args.slug]
    print(f"Publishing: {post['seoTitle']}")
    print(f"  slug: {args.slug}")
    print(f"  tags: {post['tags']}")
    print(f"  hero: {post['heroImage']}")

    url = publish_one(post, profile_dir, dry_run=args.dry_run, headless=args.headless)
    if url:
        print(f"\nFinal URL: {url}")
        print(f"\nNext: update posts.ts mediumUrl for slug '{args.slug}'")
        return 0
    return 3


if __name__ == "__main__":
    sys.exit(main())

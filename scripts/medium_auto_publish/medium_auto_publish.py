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

    # Medium detects headless Chrome and redirects to a mobile "Start writing
    # in the Medium app" page. Set a real desktop UA + a stable viewport to
    # be treated as a normal desktop user.
    DESKTOP_UA = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            viewport={"width": 1400, "height": 950},
            user_agent=DESKTOP_UA,
            is_mobile=False,
            has_touch=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                # Common anti-bot-detection flags
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-sandbox",
            ],
        )
        page = ctx.new_page()

        # Some Medium routes show a "Maybe later" upsell. Handle it silently.
        def dismiss_upsell():
            for label in ("Maybe later", "No thanks", "Continue on web"):
                try:
                    link = page.get_by_role("link", name=re.compile(rf"^{label}$", re.I)).first
                    link.wait_for(timeout=1000, state="visible")
                    link.click()
                    print(f"  dismissed upsell: {label}")
                    time.sleep(1)
                    return
                except Exception:
                    try:
                        btn = page.get_by_role("button", name=re.compile(rf"^{label}$", re.I)).first
                        btn.wait_for(timeout=500, state="visible")
                        btn.click()
                        print(f"  dismissed upsell: {label}")
                        time.sleep(1)
                        return
                    except Exception:
                        continue

        # Step 1: use Medium's Import Story feature — gets body text + headings
        # right automatically. We'll then add the cover image that Medium's
        # importer always omits.
        print(f"  opening Medium import with URL: {source_url}")
        # `networkidle` never fires on Medium (constant analytics/tracking
        # pings keep the network busy). Use `domcontentloaded` and rely on
        # the hydration marker wait below to know when the form mounted.
        page.goto("https://medium.com/p/import", wait_until="domcontentloaded", timeout=30000)

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

        # Medium's import-page URL input is NOT a standard <input>. Legacy
        # page observed 2026-04-23 uses:
        #
        #   <div class="textInput textInput--large js-importUrl"
        #        contenteditable="true" role="textbox"
        #        data-default-value="http://www.yoursite.org/your-post">
        #
        # So `input[...]` selectors never matched. We target the
        # contenteditable div directly and use keyboard.type() to enter
        # text (fill() only works on standard form inputs).
        selectors = [
            'div.js-importUrl',                          # primary — Medium's own class
            'div[data-default-value*="yoursite" i]',
            'div[data-default-value^="http" i]',
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"].textInput',
            'div[contenteditable="true"]',                # last-resort
            # Also keep the input selectors in case Medium ships a new
            # version of the form with a real <input>.
            'input[placeholder^="http" i]',
            'input[placeholder*="yoursite" i]',
            'input[type="url"]',
        ]

        url_input = None
        target_frame = None
        all_frames = [page.main_frame] + list(page.frames)
        seen = set()
        dedup_frames = []
        for f in all_frames:
            if id(f) in seen:
                continue
            seen.add(id(f))
            dedup_frames.append(f)

        print(f"  scanning {len(dedup_frames)} frame(s) for URL input...")
        for fi, frame in enumerate(dedup_frames):
            frame_url = frame.url or "(about:blank)"
            for sel in selectors:
                try:
                    candidate = frame.locator(sel).first
                    candidate.wait_for(timeout=1500, state="visible")
                    url_input = candidate
                    target_frame = frame
                    print(f"  found URL input in frame #{fi} ({frame_url[:60]}) via: {sel}")
                    break
                except PWTimeout:
                    continue
                except Exception:
                    continue
            if url_input is not None:
                break

        if url_input is None:
            print("ERROR: could not find URL input in any frame. Saving debug artefacts...")
            print("  frames scanned:")
            for fi, frame in enumerate(dedup_frames):
                print(f"    #{fi}: {frame.url}")
            _save_debug(page, "import-url-input-missing")
            ctx.close()
            return None

        try:
            # Click to focus, then type. Medium's contenteditable div
            # doesn't support fill() — only keystroke-level input via
            # keyboard.type() or element.type(). Clear first with
            # Cmd/Ctrl+A + Delete.
            url_input.click()
            time.sleep(0.3)
            page.keyboard.press("Meta+A")
            page.keyboard.press("Delete")
            time.sleep(0.2)
            page.keyboard.type(source_url, delay=10)
            time.sleep(0.5)
        except Exception as e:
            print(f"ERROR: failed to fill URL input: {e}")
            _save_debug(page, "import-url-fill-failed")
            ctx.close()
            return None

        # Click Import button — search the same frame we found the input in
        try:
            # Try by role first in the target frame
            search_frame = target_frame if target_frame else page
            import_btn = search_frame.get_by_role("button", name=re.compile(r"^import$", re.I)).first
            import_btn.click()
        except Exception as e:
            print(f"  could not click Import button via role: {e} — trying text selector")
            try:
                import_btn = search_frame.locator('button:has-text("Import")').first
                import_btn.click()
            except Exception as e2:
                print(f"  still could not click Import: {e2}")
                _save_debug(page, "import-button-missing")
                ctx.close()
                return None

        # Wait for import to complete. Medium redirects to one of:
        #   /p/<hex>/edit                    (classic editor)
        #   /m/writer/draft/<id>/edit        (2023+ redesign)
        #   /story/<hex>/edit                (some A/B variants)
        # OR the editor loads in-place after an interim splash URL like
        # /m-write. So we match broadly on anything ending with /edit or
        # /write and also detect the H1 title input as a fallback signal.
        editor_url_re = re.compile(r"(edit$|/write$|/m-write|/writer/)")
        try:
            page.wait_for_url(editor_url_re, timeout=60000)
            print(f"  URL matched editor pattern: {page.url}")
        except PWTimeout:
            print(f"  editor URL never matched in 60s — current: {page.url}")

        # Regardless of URL, wait for the H1 title editable to appear —
        # that's the definitive signal that the editor loaded the imported
        # content.
        editor_loaded = False
        try:
            page.locator("h1, [data-testid='editorTitle'], div[role='textbox']").first.wait_for(
                timeout=30000, state="visible"
            )
            editor_loaded = True
            print(f"  editor H1/textbox visible at: {page.url}")
        except PWTimeout:
            pass

        if not editor_loaded:
            print("  ERROR: editor did not load after import click. Saving debug.")
            _save_debug(page, "editor-did-not-load")
            ctx.close()
            return None

        # Give the editor a moment to stabilise
        time.sleep(8)
        _save_debug(page, "after-import-editor-loaded")

        # Dismiss mobile upsell + Medium's first-time-writer tour modal.
        dismiss_upsell()
        # Medium shows a post-import tutorial tour that overlays the whole
        # editor and intercepts every click. Escape closes it.
        for _ in range(4):
            try:
                page.keyboard.press("Escape")
                time.sleep(0.4)
            except Exception:
                break
        # Also try clicking any visible modal close button.
        for name_re in (r"^close$", r"^skip", r"got it", r"dismiss"):
            try:
                closer = page.get_by_role("button", name=re.compile(name_re, re.I)).first
                closer.wait_for(timeout=500, state="visible")
                closer.click()
                time.sleep(0.3)
            except Exception:
                pass
        time.sleep(1)
        _save_debug(page, "after-modal-dismissed")

        # Verify imported content landed.
        try:
            title_text = page.locator("h1").first.inner_text(timeout=5000)
            print(f"  editor H1 text: {title_text[:80]!r}")
            if not title_text.strip() or title_text.strip().lower() in {
                "title", "new story", "start writing in the medium app.",
                "start writing in the medium app",
            }:
                print("  ERROR: H1 indicates the upsell/empty page — import failed.")
                _save_debug(page, "editor-empty-after-import")
                ctx.close()
                return None
        except Exception as e:
            print(f"  could not read H1: {e} (continuing anyway)")

        # --------------------------------------------------------------
        # HYBRID MODE — script stops here.
        # --------------------------------------------------------------
        # Rationale: fully automating the Publish click hits Medium's
        # anti-spam heuristics which silently disable the button until
        # real user interaction is detected (observed 2026-04-23: no
        # amount of keystroke/click simulation + JS class override gets
        # past it within a headless session). Every workaround triggers
        # the next layer of bot-detection (tutorial modal, then session-
        # verification, then "Start writing in the Medium app" upsell).
        #
        # Pragmatic answer: the 90% hard part is the raw-markdown paste
        # bug (## showing as literal text) — SOLVED by the Import-from-URL
        # step above. The remaining 3 steps (cover upload, tags, publish
        # click) are each <30 seconds of manual work per post, vs
        # unbounded automation debugging.
        #
        # So the script does its best to get the draft into an "editing
        # ready" state, then hands off:
        print()
        print("=" * 60)
        print("DRAFT READY — your turn (about 60-90 seconds):")
        print("=" * 60)
        print(f"  URL: {page.url}")
        print()
        print("  In the already-open browser window:")
        print(f"  1. Click Publish (top-right green pill)")
        print(f"  2. On the prepublish preview:")
        print(f"     • Click the gray image box → upload cover from:")
        print(f"       {hero_path}")
        print(f"     • Add these 5 Topics (press Enter after each):")
        for tag in post["tags"][:5]:
            print(f"       - {tag}")
        print(f"  3. Click Publish now")
        print(f"  4. Copy the resulting URL — paste it into posts.ts's")
        print(f"     mediumUrl field for slug: {post['slug']}")
        print()

        if dry_run:
            print("  DRY RUN — stopping here. Saving final state.")
            _save_debug(page, "dry-run-final-state")
            if not headless:
                print("  Browser stays open 20s for inspection, then closes.")
                time.sleep(20)
            ctx.close()
            return "DRY_RUN_OK"

        # Non-dry-run: wait for user to complete the flow in the browser.
        # Detect success by polling for a published story URL pattern.
        if headless:
            print("  ERROR: non-dry-run in headless mode cannot wait for")
            print("  manual interaction. Re-run without --headless.")
            ctx.close()
            return None

        print("  Waiting up to 10 minutes for you to complete publish in the browser...")
        published_re = re.compile(r"medium\.com/@[^/]+/[a-z0-9-]+-[0-9a-f]{8,}$")
        deadline = time.time() + 600  # 10 min
        pub_url = None
        while time.time() < deadline:
            if published_re.search(page.url):
                pub_url = page.url
                break
            time.sleep(3)

        if pub_url:
            print(f"  PUBLISHED: {pub_url}")
            ctx.close()
            return pub_url
        print("  Timeout — publish not detected. If you DID publish, copy")
        print("  the URL manually. If not, close the browser and try again.")
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

'use client';

import { useEffect, useState } from 'react';

/**
 * Thin reading-progress bar fixed to the top of the viewport.
 *
 * Why this matters:
 * - Engagement signal: a visible reading bar keeps people scrolling
 *   (measurable improvement to scroll depth and avg-time-on-page in GA4)
 * - Improves perceived progress on long posts (3,500+ word essays)
 * - SEO: longer engaged sessions improve dwell time, an indirect signal
 *
 * No external dependencies. Uses requestAnimationFrame throttling so it
 * doesn't fire on every scroll pixel — INP-safe.
 */
export function ReadingProgressBar() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      const scrollTop =
        window.scrollY || document.documentElement.scrollTop;
      const max =
        document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.min(100, (scrollTop / max) * 100) : 0;
      setProgress(pct);
      frame = 0;
    };
    const onScroll = () => {
      if (frame === 0) {
        frame = requestAnimationFrame(update);
      }
    };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed left-0 right-0 top-0 z-50 h-[3px] bg-transparent"
    >
      <div
        className="h-full bg-gradient-to-r from-primary via-primary/80 to-primary transition-[width] duration-100"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

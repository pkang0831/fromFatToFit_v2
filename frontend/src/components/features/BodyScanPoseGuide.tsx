'use client';

import {
  IDEAL_BODY_SCAN_POSE_IMAGE,
  BODY_SCAN_SAMPLE_PHOTO_FALLBACK,
  BODY_SCAN_GUIDE_SVG_FALLBACK,
} from '@/lib/constants/bodyScanGuide';

type BodyScanPoseGuideProps = {
  /** `/try` dark theme vs dashboard light cards */
  variant?: 'dark' | 'light';
  className?: string;
};

/**
 * Shared “ideal pose” panel: diagram + copy. Matches backend checks (front-facing, not side/back).
 */
export function BodyScanPoseGuide({ variant = 'dark', className = '' }: BodyScanPoseGuideProps) {
  const isDark = variant === 'dark';
  const box = isDark
    ? 'rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 sm:p-5'
    : 'rounded-xl border border-border bg-surfaceAlt p-4 sm:p-5';
  const title = isDark ? 'text-sm font-medium text-white/90' : 'text-sm font-medium text-text';
  const body = isDark ? 'text-xs leading-relaxed text-white/45 sm:text-sm' : 'text-xs leading-relaxed text-text-secondary sm:text-sm';
  const accent = isDark ? 'text-white/70' : 'text-text';

  return (
    <div className={`${box} ${className}`}>
      <p className={`${title} mb-4`}>Take your photo like this</p>

      {/* Image — full width, natural aspect ratio */}
      <div
        className={`relative mx-auto w-full overflow-hidden rounded-xl border mb-4 ${
          isDark ? 'border-white/15' : 'border-border'
        }`}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={IDEAL_BODY_SCAN_POSE_IMAGE}
          alt="Ideal pose: full body, facing the camera straight-on, shoulders square — not side or back"
          className="w-full h-auto block"
          onError={(ev) => {
            const el = ev.currentTarget;
            if (el.src.includes('ideal-body-scan-pose')) {
              el.src = BODY_SCAN_SAMPLE_PHOTO_FALLBACK;
            } else if (el.src.includes('sample_image')) {
              el.src = BODY_SCAN_GUIDE_SVG_FALLBACK;
            }
          }}
        />
      </div>

      {/* Instructions — below image */}
      <div className={`space-y-2 ${body}`}>
        <p>
          Match this <span className={accent}>front-facing</span> pose — camera at chest height,
          shoulders parallel to the frame. We reject side profiles and back-only shots.
        </p>
        <ul className="list-disc space-y-1 pl-4">
          <li><span className={accent}>Shirtless</span> — remove your top so your upper body is clearly visible.</li>
          <li>Square to the camera (not turned sideways).</li>
          <li>Fill the frame without tiny figures in huge backgrounds.</li>
          <li><span className={accent}>Good lighting</span> — use bright, even light so your body is clearly visible. Avoid dark rooms.</li>
          <li>Mirror selfies are fine if you match this orientation.</li>
        </ul>
      </div>
    </div>
  );
}

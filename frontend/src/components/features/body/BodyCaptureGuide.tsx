'use client';

import { useCallback, useEffect, useId, useRef, useState } from 'react';
import Image from 'next/image';
import { X, Camera } from 'lucide-react';
import { Button } from '@/components/ui';
import {
  IDEAL_BODY_SCAN_POSE_IMAGE,
  BODY_SCAN_SAMPLE_PHOTO_FALLBACK,
  BODY_SCAN_GUIDE_SVG_FALLBACK,
} from '@/lib/constants/bodyScanGuide';

export type BodyCaptureFacing = 'environment' | 'user';

type BodyCaptureGuideProps = {
  open: boolean;
  onClose: () => void;
  /**
   * Validate + apply the capture. Return true to close the guide, false to stay open (retake).
   */
  onCapture: (file: File) => Promise<boolean>;
  /** Rear camera is best for full-body at arm's length */
  defaultFacing?: BodyCaptureFacing;
  /**
   * Ideal pose diagram — must match upload hint (`/ideal-body-scan-pose.png` in `public/`).
   */
  guideImageSrc?: string;
  /** Server / parent validation message (e.g. after `validatePhoto` fails). */
  validationMessage?: string | null;
};

/** viewBox 0 0 100 100 — simple centered frame (upper-body / mirror selfie). */
const FRAME_RECT = { x: 19, y: 14, w: 62, h: 72 } as const;

const DEFAULT_GUIDE_IMG = IDEAL_BODY_SCAN_POSE_IMAGE;

/**
 * Full-screen camera view: dimmed overlay with a rectangular cut-out, center
 * line, and capture CTA.
 */
export function BodyCaptureGuide({
  open,
  onClose,
  onCapture,
  defaultFacing = 'environment',
  guideImageSrc = DEFAULT_GUIDE_IMG,
  validationMessage = null,
}: BodyCaptureGuideProps) {
  const maskId = useId().replace(/:/g, '');
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [captureBusy, setCaptureBusy] = useState(false);
  const [guideSrc, setGuideSrc] = useState(guideImageSrc);

  useEffect(() => {
    setGuideSrc(guideImageSrc);
  }, [guideImageSrc]);

  const onGuideImageError = useCallback(() => {
    setGuideSrc((prev) => {
      if (prev.includes('ideal-body-scan-pose')) return BODY_SCAN_SAMPLE_PHOTO_FALLBACK;
      if (prev.includes('sample_image')) return BODY_SCAN_GUIDE_SVG_FALLBACK;
      return prev;
    });
  }, []);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  const startStream = useCallback(async () => {
    setError(null);
    setReady(false);
    stopStream();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode:
            defaultFacing === 'environment' ? { ideal: 'environment' } : { ideal: 'user' },
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      });
      streamRef.current = stream;
      const v = videoRef.current;
      if (v) {
        v.srcObject = stream;
        await v.play();
        setReady(true);
      }
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : 'Camera access denied or unavailable. Allow camera or upload a photo instead.',
      );
    }
  }, [defaultFacing, stopStream]);

  useEffect(() => {
    if (!open) {
      stopStream();
      setReady(false);
      setError(null);
      setCaptureBusy(false);
      return;
    }
    startStream();
    return () => {
      stopStream();
    };
  }, [open, defaultFacing, startStream, stopStream]);

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video || video.videoWidth === 0) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], 'body-capture.jpg', { type: 'image/jpeg' });
        void (async () => {
          setCaptureBusy(true);
          try {
            const ok = await onCapture(file);
            if (ok) {
              stopStream();
              onClose();
            }
          } finally {
            setCaptureBusy(false);
          }
        })();
      },
      'image/jpeg',
      0.92,
    );
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex flex-col bg-black">
      <div className="flex shrink-0 items-center justify-between px-3 py-2 bg-black/90 text-white">
        <button
          type="button"
          onClick={() => {
            stopStream();
            onClose();
          }}
          className="p-2 rounded-full hover:bg-white/10"
          aria-label="Close"
        >
          <X className="h-6 w-6" />
        </button>
        <span className="text-xs text-white/35 sm:text-sm">Camera</span>
        <div className="h-10 w-10 shrink-0" aria-hidden />
      </div>

      {/* Hinge-style: sample + how-to copy (replace image via guideImageSrc, e.g. /sample_image.jpg) */}
      <div className="shrink-0 border-b border-white/10 bg-zinc-950 px-3 py-3 sm:px-4">
        <div className="mx-auto flex max-w-lg gap-3 sm:gap-4">
          <div className="relative h-28 w-24 shrink-0 overflow-hidden rounded-xl border border-white/15 bg-black sm:h-32 sm:w-28">
            <Image
              key={guideSrc}
              src={guideSrc}
              alt="Ideal pose: full body facing the camera straight-on, not side or back"
              fill
              sizes="(max-width: 640px) 96px, 112px"
              className="object-contain object-center"
              onError={onGuideImageError}
              priority
            />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-serif text-base text-white sm:text-lg">How it works</p>
            <p className="mt-2 rounded-lg border border-amber-500/35 bg-amber-500/10 px-2.5 py-2 text-[11px] leading-snug text-amber-100 sm:text-xs">
              <span className="font-semibold text-amber-50">Match the diagram — front view, full body.</span>{' '}
              Side profiles and back-only shots are rejected. Don&apos;t crop to face only; feet should stay in
              frame when possible.
            </p>
            <p className="mt-2 text-xs leading-snug text-white/70 sm:text-sm">
              Align your live view with the illustration above, then fit yourself in the purple frame below.
            </p>
            <ul className="mt-2 space-y-1.5 text-[11px] leading-relaxed text-white/85 sm:text-xs">
              <li className="flex gap-2">
                <span className="text-primary" aria-hidden>
                  •
                </span>
                <span>Square to the camera — shoulders parallel to the frame (not sideways).</span>
              </li>
              <li className="flex gap-2">
                <span className="text-primary" aria-hidden>
                  •
                </span>
                <span>Center in the purple outline; dashed line on your midline from head toward feet.</span>
              </li>
              <li className="flex gap-2">
                <span className="text-primary" aria-hidden>
                  •
                </span>
                <span>Even lighting on your body; avoid heavy shadow on one side of the torso.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="relative flex-1 min-h-0 bg-black">
        <video
          ref={videoRef}
          className="absolute inset-0 h-full w-full object-cover"
          playsInline
          muted
        />

        {/* Overlay: rectangular frame, scales with viewport */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center px-2 pb-32 pt-2 sm:px-4 sm:pb-40">
          <svg
            className="aspect-square w-[min(92vw,min(85dvh,960px))] max-h-full max-w-full shrink-0"
            viewBox="0 0 100 100"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <mask id={`bodyStencilHole-${maskId}`}>
                <rect width="100" height="100" fill="white" />
                <rect
                  x={FRAME_RECT.x}
                  y={FRAME_RECT.y}
                  width={FRAME_RECT.w}
                  height={FRAME_RECT.h}
                  fill="black"
                />
              </mask>
            </defs>
            <rect
              width="100"
              height="100"
              fill="rgba(0,0,0,0.5)"
              mask={`url(#bodyStencilHole-${maskId})`}
            />
            <rect
              x={FRAME_RECT.x}
              y={FRAME_RECT.y}
              width={FRAME_RECT.w}
              height={FRAME_RECT.h}
              fill="none"
              stroke="rgba(168,85,247,0.95)"
              strokeWidth="0.5"
            />
            <line
              x1="50"
              y1={FRAME_RECT.y + 0.5}
              x2="50"
              y2={FRAME_RECT.y + FRAME_RECT.h - 0.5}
              stroke="rgba(255,255,255,0.55)"
              strokeWidth="0.35"
              strokeDasharray="2 2"
            />
          </svg>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 pb-8 bg-gradient-to-t from-black/90 to-transparent">
          {error && (
            <p className="text-center text-sm text-red-300 mb-3 px-2">{error}</p>
          )}
          {validationMessage && (
            <p className="text-center text-sm text-amber-200 mb-3 px-2">{validationMessage}</p>
          )}
          <p className="text-center text-sm text-white/90 mb-4 px-2">
            When you&apos;re ready, match the live view to the guide above — then capture.
          </p>
          <Button
            type="button"
            variant="primary"
            size="lg"
            className="w-full"
            disabled={!ready || !!error || captureBusy}
            isLoading={captureBusy}
            onClick={handleCapture}
          >
            <Camera className="h-5 w-5 mr-2" />
            Capture photo
          </Button>
        </div>
      </div>
    </div>
  );
}

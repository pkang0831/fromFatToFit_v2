'use client';

import { useEffect, useState, useRef } from 'react';
import { cn } from '@/lib/utils/cn';

export interface ProcessingStep {
  label: string;
  /** Estimated duration in ms for this step */
  duration: number;
}

interface ProcessingOverlayProps {
  active: boolean;
  steps: ProcessingStep[];
  className?: string;
  /** Dark theme (for try page dark bg) */
  dark?: boolean;
}

export const SCAN_STEPS: ProcessingStep[] = [
  { label: 'Uploading & validating photo…', duration: 3000 },
  { label: 'Analyzing body composition…', duration: 6000 },
  { label: 'Estimating body fat percentage…', duration: 5000 },
  { label: 'Calculating your percentile ranking…', duration: 4000 },
  { label: 'Finalizing results…', duration: 3000 },
];

export const JOURNEY_STEPS: ProcessingStep[] = [
  { label: 'Validating photo quality…', duration: 3000 },
  { label: 'Analyzing your current physique…', duration: 5000 },
  { label: 'Planning transformation stages…', duration: 4000 },
  { label: 'Generating Stage 1 preview…', duration: 18000 },
  { label: 'Generating Stage 2 preview…', duration: 18000 },
  { label: 'Generating Stage 3 preview…', duration: 18000 },
  { label: 'Generating Stage 4 preview…', duration: 18000 },
  { label: 'Building your diet & workout plan…', duration: 6000 },
  { label: 'Finalizing your journey…', duration: 4000 },
];

export const GUEST_SCAN_STEPS: ProcessingStep[] = [
  { label: 'Analyzing your photo…', duration: 4000 },
  { label: 'Estimating body composition…', duration: 6000 },
  { label: 'Calculating body fat percentage…', duration: 5000 },
  { label: 'Preparing your results…', duration: 3000 },
];

export function ProcessingOverlay({ active, steps, className, dark }: ProcessingOverlayProps) {
  const [progress, setProgress] = useState(0);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const rafRef = useRef<number>(0);
  const startTimeRef = useRef(0);

  const totalDuration = steps.reduce((sum, s) => sum + s.duration, 0);

  useEffect(() => {
    if (!active) {
      setProgress(0);
      setCurrentStepIdx(0);
      return;
    }

    startTimeRef.current = Date.now();

    const tick = () => {
      const elapsed = Date.now() - startTimeRef.current;
      const raw = elapsed / totalDuration;
      // Asymptotic curve: approaches 95% but never reaches 100%
      const eased = raw < 0.8
        ? raw * (95 / 0.8)
        : 95 + (1 - Math.exp(-(raw - 0.8) * 5)) * 4;
      setProgress(Math.min(eased, 99));

      // Determine current step
      let acc = 0;
      for (let i = 0; i < steps.length; i++) {
        acc += steps[i].duration;
        if (elapsed < acc) {
          setCurrentStepIdx(i);
          break;
        }
        if (i === steps.length - 1) {
          setCurrentStepIdx(i);
        }
      }

      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [active, steps, totalDuration]);

  if (!active) return null;

  const currentStep = steps[Math.min(currentStepIdx, steps.length - 1)];
  const completedSteps = currentStepIdx;
  const totalSteps = steps.length;

  return (
    <div className={cn(
      'flex flex-col items-center justify-center py-16 px-6 rounded-2xl',
      dark
        ? 'bg-white/[0.02] border border-white/[0.08]'
        : 'bg-surface border border-border',
      className,
    )}>
      {/* Spinner */}
      <div className="relative mb-8">
        <div className={cn(
          'w-20 h-20 rounded-full border-[3px] animate-spin',
          dark
            ? 'border-white/10 border-t-cyan-400'
            : 'border-border border-t-primary',
        )} />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn(
            'text-sm font-bold font-number',
            dark ? 'text-white/80' : 'text-text',
          )}>
            {Math.round(progress)}%
          </span>
        </div>
      </div>

      {/* Current step label */}
      <p className={cn(
        'text-base font-medium mb-2 text-center transition-opacity duration-300',
        dark ? 'text-white/80' : 'text-text',
      )}>
        {currentStep.label}
      </p>

      {/* Step counter */}
      <p className={cn(
        'text-xs mb-6',
        dark ? 'text-white/30' : 'text-text-light',
      )}>
        Step {completedSteps + 1} of {totalSteps}
      </p>

      {/* Progress bar */}
      <div className={cn(
        'w-full max-w-xs h-2 rounded-full overflow-hidden',
        dark ? 'bg-white/[0.06]' : 'bg-black/[0.06] dark:bg-white/[0.06]',
      )}>
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-primary transition-all duration-700 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step dots */}
      <div className="flex items-center gap-1.5 mt-5">
        {steps.map((_, i) => (
          <div
            key={i}
            className={cn(
              'h-1.5 rounded-full transition-all duration-500',
              i < completedSteps
                ? 'w-4 bg-primary'
                : i === completedSteps
                  ? cn('w-6 animate-pulse', dark ? 'bg-cyan-400' : 'bg-primary')
                  : cn('w-1.5', dark ? 'bg-white/10' : 'bg-black/10 dark:bg-white/10'),
            )}
          />
        ))}
      </div>

      {/* Subtle hint */}
      <p className={cn(
        'text-[11px] mt-6',
        dark ? 'text-white/20' : 'text-text-light/60',
      )}>
        Please keep this page open
      </p>
    </div>
  );
}

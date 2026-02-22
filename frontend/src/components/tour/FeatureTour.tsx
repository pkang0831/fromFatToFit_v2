'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, X } from 'lucide-react';

const TOURED_PAGES_KEY = 'toured_pages';
export const TOUR_START_EVENT = 'start-feature-tour';

interface TourStep {
  target: string;
  title: string;
  description: string;
  placement: 'right' | 'bottom' | 'left' | 'top';
}

const PAGE_TOURS: Record<string, TourStep[]> = {
  '/home': [
    {
      target: '[data-tour="home-stats"]',
      title: 'Daily Stats',
      description:
        "Today's calorie intake, protein, and total calories burned. The progress bar fills as you approach your daily goal.",
      placement: 'bottom',
    },
    {
      target: '[data-tour="home-chart"]',
      title: 'Calorie Balance Trend',
      description:
        "Solid line = intake, dashed line = goal. If solid stays below dashed, you're in a deficit — great for fat loss! Toggle 7-day or 30-day view.",
      placement: 'bottom',
    },
    {
      target: '[data-tour="home-actions"]',
      title: 'Quick Actions',
      description:
        'Jump to any feature from here — log calories, scan food with AI, track workouts, or analyze your body.',
      placement: 'top',
    },
  ],
  '/calories': [
    {
      target: '[data-tour="cal-summary"]',
      title: 'Daily Nutrition',
      description:
        'Calories, protein, carbs, fat, and your progress toward the daily goal — all in one row.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="cal-logform"]',
      title: 'Log a Meal',
      description:
        'Enter food name, meal type, and macros. Or use the Food Camera in the sidebar for automatic AI detection.',
      placement: 'bottom',
    },
  ],
  '/food-camera': [
    {
      target: '[data-tour="camera-credits"]',
      title: 'Credit Cost',
      description:
        'Each scan costs 1 credit. Your current balance is shown here.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="camera-upload"]',
      title: 'Scan Your Food',
      description:
        'Take a photo or upload one. AI identifies the food, estimates calories and macros, and tells you whether to eat it.',
      placement: 'bottom',
    },
  ],
  '/workouts': [
    {
      target: '[data-tour="workout-stats"]',
      title: 'Workout Stats',
      description:
        'Total workouts this month, weekly average, and how many exercises logged today.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="workout-library"]',
      title: 'Exercise Library',
      description:
        'Browse by Cardio or Strength. Tap any exercise for form instructions, then log sets, reps, and weight.',
      placement: 'top',
    },
  ],
  '/progress': [
    {
      target: '[data-tour="progress-actions"]',
      title: 'Set Goal & Log Weight',
      description:
        '"Set Goal" defines your target weight. "Log Weight" records daily weigh-ins. Consistent logging = more accurate projections.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="progress-chart"]',
      title: 'Goal Projection',
      description:
        'Green line = actual weight. Dashed line = projected path to your goal. Set a target deficit (e.g. 500 kcal/day) to see your estimated goal date.',
      placement: 'top',
    },
  ],
  '/body-scan': [
    {
      target: '[data-tour="scan-types"]',
      title: 'Choose a Scan',
      description:
        'Body Fat (10 cr) estimates your BF%. Percentile (10 cr) compares you to others. Transformation (30 cr) previews your goal physique. Enhancement (50 cr) polishes your photo.',
      placement: 'bottom',
    },
  ],
  '/chat': [
    {
      target: '[data-tour="chat-input"]',
      title: 'Ask Your AI Coach',
      description:
        'Type any question about diet, nutrition, or exercise. Trained on hundreds of expert coaching sessions. Free — 15 messages per day.',
      placement: 'top',
    },
  ],
  '/profile': [
    {
      target: '[data-tour="profile-credits"]',
      title: 'Credits & Costs',
      description:
        'Your credit balance and how much each feature costs. Buy more or upgrade to Premium for unlimited access.',
      placement: 'bottom',
    },
  ],
};

const PADDING = 6;
const TOOLTIP_WIDTH = 320;
const MARGIN = 16;

function getTouredPages(): string[] {
  try {
    return JSON.parse(localStorage.getItem(TOURED_PAGES_KEY) || '[]');
  } catch {
    return [];
  }
}

function markPageToured(page: string) {
  try {
    const toured = getTouredPages();
    if (!toured.includes(page)) {
      toured.push(page);
      localStorage.setItem(TOURED_PAGES_KEY, JSON.stringify(toured));
    }
  } catch {}
}

export function resetAllTours() {
  try {
    localStorage.removeItem(TOURED_PAGES_KEY);
  } catch {}
}

function getTooltipPosition(rect: DOMRect, placement: TourStep['placement']) {
  const gap = 14;
  const vh = window.innerHeight;
  const vw = window.innerWidth;
  const MIN_USEFUL = 200;

  const spaces = {
    top: rect.top - PADDING,
    bottom: vh - rect.bottom - PADDING,
    right: vw - rect.right - PADDING,
    left: rect.left - PADDING,
  };

  // Pick the best placement: prefer the requested one, but fall back to
  // whichever side has the most room if the requested side is too tight.
  let resolved = placement;
  if (spaces[resolved] < MIN_USEFUL) {
    const ranked = ([...(['top', 'bottom', 'right', 'left'] as const)]).sort(
      (a: 'top' | 'bottom' | 'right' | 'left', b: 'top' | 'bottom' | 'right' | 'left') => spaces[b] - spaces[a],
    );
    resolved = ranked[0];
  }

  const style: React.CSSProperties = { position: 'fixed' };

  switch (resolved) {
    case 'right':
      style.left = rect.right + PADDING + gap;
      style.top = rect.top + rect.height / 2;
      style.transform = 'translateY(-50%)';
      break;
    case 'left':
      style.right = vw - rect.left + PADDING + gap;
      style.top = rect.top + rect.height / 2;
      style.transform = 'translateY(-50%)';
      break;
    case 'bottom':
      style.left = rect.left + rect.width / 2;
      style.top = rect.bottom + PADDING + gap;
      style.transform = 'translateX(-50%)';
      break;
    case 'top':
      style.left = rect.left + rect.width / 2;
      style.bottom = vh - rect.top + PADDING + gap;
      style.transform = 'translateX(-50%)';
      break;
  }

  // Clamp horizontally
  if (style.left !== undefined && typeof style.left === 'number') {
    style.left = Math.max(MARGIN, Math.min(style.left, vw - TOOLTIP_WIDTH - MARGIN));
  }

  // Clamp vertically for side placements
  if ((resolved === 'right' || resolved === 'left') && typeof style.top === 'number') {
    style.top = Math.max(MARGIN, Math.min(style.top, vh - MIN_USEFUL));
  }

  return style;
}

function buildClipPath(rect: DOMRect): string {
  const x = rect.left - PADDING;
  const y = rect.top - PADDING;
  const w = rect.width + PADDING * 2;
  const h = rect.height + PADDING * 2;

  return `polygon(
    0% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%,
    ${x}px ${y}px,
    ${x}px ${y + h}px,
    ${x + w}px ${y + h}px,
    ${x + w}px ${y}px,
    ${x}px ${y}px
  )`;
}

export function FeatureTour() {
  const pathname = usePathname();
  const [active, setActive] = useState(false);
  const [step, setStep] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const [currentPage, setCurrentPage] = useState<string | null>(null);
  const retryRef = useRef<NodeJS.Timeout | null>(null);

  const steps = currentPage ? PAGE_TOURS[currentPage] || [] : [];
  const currentStep = steps[step];
  const totalSteps = steps.length;

  const findAndMeasure = useCallback(() => {
    if (!currentStep) return;
    const el = document.querySelector<HTMLElement>(currentStep.target);
    if (!el) {
      retryRef.current = setTimeout(findAndMeasure, 200);
      return;
    }
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => {
      setTargetRect(el.getBoundingClientRect());
    }, 300);
  }, [currentStep]);

  const finish = useCallback(() => {
    if (currentPage) markPageToured(currentPage);
    setActive(false);
    setStep(0);
    setTargetRect(null);
    setCurrentPage(null);
    if (retryRef.current) clearTimeout(retryRef.current);
  }, [currentPage]);

  const next = useCallback(() => {
    if (retryRef.current) clearTimeout(retryRef.current);
    if (step < totalSteps - 1) {
      setStep((s) => s + 1);
    } else {
      finish();
    }
  }, [step, totalSteps, finish]);

  const prev = useCallback(() => {
    if (retryRef.current) clearTimeout(retryRef.current);
    if (step > 0) setStep((s) => s - 1);
  }, [step]);

  // Auto-start on first visit to a page
  useEffect(() => {
    if (!pathname || !PAGE_TOURS[pathname]) return;

    const toured = getTouredPages();
    if (!toured.includes(pathname)) {
      const timer = setTimeout(() => {
        setCurrentPage(pathname);
        setStep(0);
        setActive(true);
      }, 600);
      return () => clearTimeout(timer);
    }
  }, [pathname]);

  // Manual start via event — replays current page's tour
  useEffect(() => {
    const handler = () => {
      if (pathname && PAGE_TOURS[pathname]) {
        setCurrentPage(pathname);
        setStep(0);
        setActive(true);
      }
    };
    window.addEventListener(TOUR_START_EVENT, handler);
    return () => window.removeEventListener(TOUR_START_EVENT, handler);
  }, [pathname]);

  // Measure target when step changes
  useEffect(() => {
    if (active && currentStep) findAndMeasure();
    return () => {
      if (retryRef.current) clearTimeout(retryRef.current);
    };
  }, [active, step, findAndMeasure, currentStep]);

  // Follow scroll & resize
  useEffect(() => {
    if (!active || !currentStep) return;
    const remeasure = () => {
      const el = document.querySelector<HTMLElement>(currentStep.target);
      if (el) setTargetRect(el.getBoundingClientRect());
    };
    window.addEventListener('scroll', remeasure, true);
    window.addEventListener('resize', remeasure);
    return () => {
      window.removeEventListener('scroll', remeasure, true);
      window.removeEventListener('resize', remeasure);
    };
  }, [active, currentStep]);

  // Keyboard
  useEffect(() => {
    if (!active) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') finish();
      if (e.key === 'ArrowRight' || e.key === 'Enter') next();
      if (e.key === 'ArrowLeft') prev();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [active, next, prev, finish]);

  if (!active || !targetRect || !currentStep) return null;

  const tooltipStyle = getTooltipPosition(targetRect, currentStep.placement);

  const spotlightStyle: React.CSSProperties = {
    position: 'fixed',
    left: targetRect.left - PADDING,
    top: targetRect.top - PADDING,
    width: targetRect.width + PADDING * 2,
    height: targetRect.height + PADDING * 2,
    borderRadius: 12,
    border: '3px solid rgba(217, 119, 6, 0.7)',
    pointerEvents: 'none',
    zIndex: 10001,
  };

  return createPortal(
    <AnimatePresence>
      <motion.div
        key="tour-root"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.25 }}
      >
        {/* Overlay with cutout */}
        <div
          onClick={finish}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 10000,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            clipPath: buildClipPath(targetRect),
          }}
        />

        {/* Spotlight ring */}
        <div style={spotlightStyle} />

        {/* Tooltip */}
        <motion.div
          key={`tooltip-${step}`}
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.92 }}
          transition={{ duration: 0.2, delay: 0.1 }}
          style={{ ...tooltipStyle, zIndex: 10002 }}
          className="w-80 max-w-[calc(100vw-32px)]"
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            {/* Progress bar */}
            {totalSteps > 1 && (
              <div className="h-1 bg-gray-100 dark:bg-gray-700 flex-shrink-0">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${((step + 1) / totalSteps) * 100}%` }}
                />
              </div>
            )}

            {/* Body */}
            <div className="p-5 pb-3">
              <div className="flex items-start justify-between mb-2">
                <div>
                  {totalSteps > 1 && (
                    <p className="text-xs font-medium text-primary mb-1">
                      {step + 1} of {totalSteps}
                    </p>
                  )}
                  <h3 className="text-base font-bold text-gray-900 dark:text-white">
                    {currentStep.title}
                  </h3>
                </div>
                <button
                  onClick={finish}
                  className="p-1 text-gray-300 hover:text-gray-500 transition-colors flex-shrink-0"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                {currentStep.description}
              </p>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between px-5 py-3 border-t border-gray-50 dark:border-gray-700">
              <button
                onClick={finish}
                className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
              >
                {totalSteps === 1 ? 'Dismiss' : 'Skip'}
              </button>
              <div className="flex items-center gap-2">
                {step > 0 && (
                  <button
                    onClick={prev}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <ChevronLeft className="w-3.5 h-3.5" />
                    Back
                  </button>
                )}
                <button
                  onClick={next}
                  className="flex items-center gap-1 px-4 py-1.5 text-sm font-semibold text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
                >
                  {step < totalSteps - 1 ? (
                    <>
                      Next
                      <ChevronRight className="w-3.5 h-3.5" />
                    </>
                  ) : (
                    'Got it'
                  )}
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body,
  );
}

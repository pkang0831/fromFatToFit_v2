'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Scan, ArrowRight, Clock, TrendingDown, Trophy } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

interface ScanHistory {
  lastScanDate: string | null;
  currentBodyFat: number | null;
  previousBodyFat: number | null;
  scanCount: number;
}

function getScanHistory(): ScanHistory {
  try {
    return {
      lastScanDate: localStorage.getItem('devenira_last_scan_date'),
      currentBodyFat: (() => {
        const v = localStorage.getItem('devenira_current_bodyfat');
        return v ? parseFloat(v) : null;
      })(),
      previousBodyFat: (() => {
        const v = localStorage.getItem('devenira_prev_bodyfat');
        return v ? parseFloat(v) : null;
      })(),
      scanCount: parseInt(localStorage.getItem('devenira_scan_count') || '0'),
    };
  } catch {
    return { lastScanDate: null, currentBodyFat: null, previousBodyFat: null, scanCount: 0 };
  }
}

function daysSince(dateStr: string): number {
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24));
}

type PromptState = 'first_scan' | 'too_early' | 'ready' | 'overdue';

function getPromptState(history: ScanHistory): PromptState {
  if (history.scanCount === 0 || !history.lastScanDate) return 'first_scan';
  const days = daysSince(history.lastScanDate);
  if (days < 5) return 'too_early';
  if (days >= 5 && days <= 10) return 'ready';
  return 'overdue';
}

interface WeeklyRescanPromptProps {
  variant?: 'full' | 'compact';
}

export function WeeklyRescanPrompt({ variant = 'full' }: WeeklyRescanPromptProps) {
  const { t } = useLanguage();
  const [history, setHistory] = useState<ScanHistory | null>(null);
  const [state, setState] = useState<PromptState>('first_scan');

  useEffect(() => {
    const h = getScanHistory();
    setHistory(h);
    setState(getPromptState(h));
  }, []);

  if (!history) return null;

  // Don't show anything if scanned recently (too_early) in compact mode
  if (variant === 'compact' && state === 'too_early') return null;

  const daysAgo = history.lastScanDate ? daysSince(history.lastScanDate) : 0;
  const daysUntilReady = Math.max(0, 7 - daysAgo);
  const delta = history.previousBodyFat && history.currentBodyFat
    ? history.previousBodyFat - history.currentBodyFat
    : null;

  if (variant === 'compact') {
    return (
      <Link
        href="/body-scan"
        className={`flex items-center gap-4 p-4 rounded-2xl border transition-all hover:-translate-y-0.5 ${
          state === 'ready' || state === 'overdue'
            ? 'border-primary/30 bg-primary/[0.04] hover:border-primary/50 hover:shadow-glow-cyan'
            : state === 'first_scan'
            ? 'border-white/[0.08] bg-white/[0.02] hover:border-primary/30'
            : 'border-white/[0.06] bg-white/[0.02]'
        }`}
      >
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
          state === 'ready' || state === 'overdue'
            ? 'bg-primary/20'
            : 'bg-white/[0.06]'
        }`}>
          {state === 'ready' || state === 'overdue' ? (
            <Scan className="w-6 h-6 text-primary animate-pulse" />
          ) : state === 'first_scan' ? (
            <Scan className="w-6 h-6 text-primary" />
          ) : (
            <Clock className="w-6 h-6 text-text-light" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-text">
            {state === 'first_scan' && 'Get your first body scan'}
            {state === 'ready' && 'Weekly scan ready!'}
            {state === 'overdue' && `${daysAgo} days since last scan`}
            {state === 'too_early' && `Next scan in ${daysUntilReady} days`}
          </p>
          <p className="text-xs text-text-secondary truncate">
            {state === 'first_scan' && 'AI body fat estimation from a photo'}
            {state === 'ready' && 'Track your week-over-week progress'}
            {(state === 'overdue') && 'Scan now to stay on track'}
            {state === 'too_early' && history.currentBodyFat && `Current: ${history.currentBodyFat.toFixed(1)}% body fat`}
          </p>
        </div>

        {(state === 'ready' || state === 'overdue' || state === 'first_scan') && (
          <ArrowRight className="w-5 h-5 text-primary flex-shrink-0" />
        )}
      </Link>
    );
  }

  // Full variant (for body-scan page top)
  return (
    <div className={`rounded-2xl border p-6 ${
      state === 'ready' || state === 'overdue'
        ? 'border-primary/30 bg-gradient-to-r from-primary/[0.06] to-transparent'
        : 'border-border bg-surface'
    }`}>
      <div className="flex items-start gap-4">
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 ${
          state === 'ready' || state === 'overdue' ? 'bg-primary/20' : 'bg-surfaceAlt'
        }`}>
          {state === 'ready' || state === 'overdue' ? (
            <Scan className="w-7 h-7 text-primary" />
          ) : state === 'first_scan' ? (
            <Scan className="w-7 h-7 text-text-secondary" />
          ) : (
            <Clock className="w-7 h-7 text-text-light" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          {state === 'first_scan' && (
            <>
              <h3 className="text-lg font-bold text-text mb-1">Start your transformation journey</h3>
              <p className="text-sm text-text-secondary">
                Upload a full-body photo to get your AI body fat estimate. Come back weekly to track real changes.
              </p>
            </>
          )}

          {state === 'too_early' && (
            <>
              <h3 className="text-lg font-bold text-text mb-1">
                Next scan in {daysUntilReady} day{daysUntilReady !== 1 ? 's' : ''}
              </h3>
              <p className="text-sm text-text-secondary">
                Weekly scans give the most accurate progress tracking. Your body needs time to show changes.
              </p>
              {history.currentBodyFat && (
                <div className="mt-3 flex items-center gap-4">
                  <div className="px-3 py-1.5 rounded-lg bg-surfaceAlt">
                    <span className="text-xs text-text-light">Current</span>
                    <span className="text-sm font-bold text-text ml-2 font-number">{history.currentBodyFat.toFixed(1)}%</span>
                  </div>
                  {delta !== null && (
                    <div className="flex items-center gap-1">
                      {delta > 0 ? (
                        <TrendingDown className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-rose-400 rotate-180" />
                      )}
                      <span className={`text-sm font-bold font-number ${delta > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {delta > 0 ? '-' : '+'}{Math.abs(delta).toFixed(1)}%
                      </span>
                      <span className="text-xs text-text-light ml-1">vs last week</span>
                    </div>
                  )}
                </div>
              )}
              <div className="mt-3">
                <div className="w-full h-2 rounded-full bg-surfaceAlt overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-primary to-cyan-400 transition-all duration-500"
                    style={{ width: `${Math.min(100, (daysAgo / 7) * 100)}%` }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-text-light">Last scan</span>
                  <span className="text-[10px] text-text-light">7 days</span>
                </div>
              </div>
            </>
          )}

          {(state === 'ready' || state === 'overdue') && (
            <>
              <h3 className="text-lg font-bold text-text mb-1">
                {state === 'overdue'
                  ? `It's been ${daysAgo} days — time for your weekly scan!`
                  : 'Your weekly scan is ready!'}
              </h3>
              <p className="text-sm text-text-secondary">
                {history.scanCount > 1
                  ? `Week ${history.scanCount + 1} check-in. See how your body has changed since your last scan.`
                  : 'Get your second data point and start seeing real trends.'}
              </p>
              {history.currentBodyFat && (
                <div className="mt-3 flex items-center gap-4">
                  <div className="px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20">
                    <span className="text-xs text-primary/70">Last result</span>
                    <span className="text-sm font-bold text-primary ml-2 font-number">{history.currentBodyFat.toFixed(1)}%</span>
                  </div>
                  {history.scanCount > 1 && (
                    <div className="flex items-center gap-1.5">
                      <Trophy className="w-4 h-4 text-amber-400" />
                      <span className="text-xs text-text-secondary">{history.scanCount} scans completed</span>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

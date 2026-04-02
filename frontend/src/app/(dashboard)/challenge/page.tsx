'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { Zap, Scale, Activity, ChevronRight, ArrowRight } from 'lucide-react';
import { Card, CardContent, Button } from '@/components/ui';
import { challengeApi } from '@/lib/api/services';
import { trackRetentionEvent } from '@/lib/analytics';

export default function ChallengePage() {
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [data, setData] = useState<Awaited<ReturnType<typeof challengeApi.getSevenDay>>['data'] | null>(null);
  const [weight, setWeight] = useState('');
  const [bf, setBf] = useState('');
  const challenge = data?.challenge as { status?: string } | null | undefined;
  const checkins = data?.checkins ?? [];

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(false);
    try {
      const res = await challengeApi.getSevenDay();
      setData(res.data);
    } catch {
      setLoadError(true);
      toast.error('Could not load challenge');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const checkIn = async () => {
    setSubmitting(true);
    trackRetentionEvent('progress_checkin_started', {
      surface: 'challenge_page',
      challenge_status: challenge?.status || 'active',
      has_weight: Boolean(weight),
      has_body_fat: Boolean(bf),
      checkin_count: checkins.length,
    });
    try {
      const res = await challengeApi.checkinSevenDay({
        weight_kg: weight ? Number(weight) : undefined,
        body_fat_pct: bf ? Number(bf) : undefined,
      });
      if (res.data.duplicate) toast(res.data.message || 'Already logged today');
      else {
        toast.success(res.data.message || 'Checked in');
      }
      trackRetentionEvent('progress_checkin_completed', {
        surface: 'challenge_page',
        challenge_status: challenge?.status || 'active',
        has_weight: Boolean(weight),
        has_body_fat: Boolean(bf),
        checkin_count: checkins.length + (res.data.duplicate ? 0 : 1),
        duplicate: Boolean(res.data.duplicate),
      });
      setWeight('');
      setBf('');
      await load();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      trackRetentionEvent('progress_checkin_failed', {
        surface: 'challenge_page',
        challenge_status: challenge?.status || 'active',
        has_weight: Boolean(weight),
        has_body_fat: Boolean(bf),
        reason: err?.response?.data?.detail || 'checkin_failed',
      });
      toast.error(err?.response?.data?.detail || 'Check-in failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-lg mx-auto py-16 text-center text-text-secondary text-sm">Loading…</div>
    );
  }
  if (loadError || !data) {
    return (
      <div className="max-w-lg mx-auto py-16 text-center text-sm text-text-secondary">
        Could not load. <button type="button" className="text-primary underline" onClick={() => void load()}>Retry</button>
      </div>
    );
  }

  const { day_index, identity_message, week_one_compare } = data;
  const hasActive = challenge && challenge.status === 'active';

  return (
    <div className="max-w-lg mx-auto space-y-6 pb-16">
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-xl bg-gradient-primary flex items-center justify-center">
          <Zap className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-text">7-day loop</h1>
          <p className="text-sm text-text-secondary">Minimum input. Immediate feedback. Identity over information.</p>
        </div>
      </div>

      {!hasActive ? (
        <Card>
          <CardContent className="p-6 space-y-4 text-center">
            <p className="text-sm text-text-secondary">
              No active challenge. Generate a transformation, then start the loop from the result screen — or open Goal Planner and save a plan first.
            </p>
            <Link href="/body-scan">
              <Button type="button" variant="primary" className="w-full">
                Body scan &amp; journey <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
            <Link href="/goal-planner">
              <Button type="button" variant="outline" className="w-full">
                Goal Planner
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card>
            <CardContent className="p-6 space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Today</p>
              {identity_message && (
                <p className="text-sm text-text leading-relaxed border-l-2 border-primary pl-3">{identity_message}</p>
              )}
              <p className="text-sm text-text-secondary">
                Day <span className="font-number font-semibold text-text">{day_index}</span> of 7 ·{' '}
                {checkins.length} check-in{checkins.length === 1 ? '' : 's'} logged
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6 space-y-4">
              <p className="text-sm font-medium text-text">30-second check-in</p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-text-secondary flex items-center gap-1 mb-1">
                    <Scale className="h-3 w-3" /> Weight (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    placeholder="Optional"
                    className="w-full px-3 py-2 bg-surfaceAlt border border-border rounded-lg text-sm text-text"
                  />
                </div>
                <div>
                  <label className="text-xs text-text-secondary flex items-center gap-1 mb-1">
                    <Activity className="h-3 w-3" /> Body fat %
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={bf}
                    onChange={(e) => setBf(e.target.value)}
                    placeholder="Optional"
                    className="w-full px-3 py-2 bg-surfaceAlt border border-border rounded-lg text-sm text-text"
                  />
                </div>
              </div>
              <Button
                type="button"
                variant="primary"
                className="w-full"
                onClick={checkIn}
                disabled={submitting}
                isLoading={submitting}
              >
                Check in for today
              </Button>
              <p className="text-[11px] text-text-light text-center">Skip fields you don&apos;t have — one tap still counts.</p>
            </CardContent>
          </Card>

          {week_one_compare && (
            <Card>
              <CardContent className="p-6 space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Week 1 · AI vs you</p>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {(week_one_compare as { message?: string }).message}
                </p>
              </CardContent>
            </Card>
          )}

          {day_index >= 7 && checkins.length >= 7 && (
            <Card>
              <CardContent className="p-6 space-y-4 text-center">
                <p className="text-xs font-semibold uppercase tracking-wider text-emerald-400">7-Day Loop Complete</p>
                <p className="text-sm text-text-secondary leading-relaxed">
                  You&apos;ve built the habit. Keep the momentum going with weekly body scans and progress tracking.
                </p>
                <Link href="/progress">
                  <Button type="button" variant="primary" className="w-full">
                    Continue with weekly check-ins <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
                <Link href="/body-scan">
                  <Button type="button" variant="outline" className="w-full">
                    New body scan
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  CalendarClock,
  Camera,
  Crown,
  Sparkles,
  Target,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { homeApi } from '@/lib/api/services';
import { Card, CardContent, Badge, Button } from '@/components/ui';
import { StreakBadge } from '@/components/features/StreakBadge';
import { SkeletonCard, SkeletonStats } from '@/components/ui/Skeleton';
import { trackReengagementSession } from '@/lib/analytics';
import type { HomeSummaryResponse } from '@/types/api';

function buildRelativeLabel(value: string | null | undefined): string {
  if (!value) return 'Not yet';
  const days = Math.floor((Date.now() - new Date(value).getTime()) / (1000 * 60 * 60 * 24));
  if (days <= 0) return 'Today';
  if (days === 1) return '1 day ago';
  return `${days} days ago`;
}

function formatDateLabel(value: string | null | undefined): string {
  if (!value) return 'Not yet';
  return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

export default function HomePage() {
  const router = useRouter();
  const { user } = useAuth();
  const { isPremium } = useSubscription();

  const [summary, setSummary] = useState<HomeSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadHomeSummary() {
      setLoading(true);
      try {
        const res = await homeApi.getSummary();
        if (!cancelled) setSummary(res.data);
      } catch {
        if (!cancelled) setSummary(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadHomeSummary();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (loading || !summary) return;

    trackReengagementSession({
      surface: 'home',
      entry_state: summary.entry_state,
      has_saved_plan: summary.goal_summary.has_saved_plan,
      has_goal_image: Boolean(summary.goal_summary.goal_image_url),
      has_transformation: Boolean(summary.scan_summary.latest_transformation),
      has_progress_photo: summary.progress_summary.photo_count > 0,
      scan_count: summary.scan_summary.scan_count,
      challenge_active: summary.challenge_summary.is_active,
    });
  }, [loading, summary]);

  if (loading) {
    return (
      <div className="space-y-6">
        <SkeletonStats count={3} />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <h1 className="text-2xl font-bold text-text">Home</h1>
            <p className="mt-2 text-sm text-text-secondary">
              We could not load your next step right now. Try again in a moment.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const latestTransformation = summary.scan_summary.latest_transformation;
  const progressHref = summary.progress_summary.compare_ready
    ? '/progress?tab=photos&focus=compare&from=home_progress_card'
    : '/progress?tab=photos&focus=upload&from=home_progress_card';

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text">
            {getGreeting()}, <span className="gradient-text">{user?.full_name || 'there'}</span>
          </h1>
          <p className="text-text-secondary mt-1">Your home screen should tell you what to do next, not just what the app can do.</p>
        </div>
        <div className="flex items-center gap-3">
          <StreakBadge />
          {isPremium && (
            <Badge variant="premium" className="text-base px-4 py-2">
              <Crown className="h-4 w-4 mr-2" />
              Pro
            </Badge>
          )}
        </div>
      </div>

      <Card variant="elevated" className="border border-primary/20 bg-gradient-to-r from-primary/[0.06] to-secondary/[0.04]">
        <CardContent className="p-6 md:p-8">
          <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
            <div className="space-y-4 max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-white/60 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                <CalendarClock className="h-3.5 w-3.5" />
                Next action
              </div>
              <div>
                <h2 className="text-2xl font-bold text-text">{summary.primary_cta.title}</h2>
                <p className="mt-2 text-sm leading-6 text-text-secondary">{summary.primary_cta.description}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="info">Goal {summary.goal_summary.target_bf != null ? `${summary.goal_summary.target_bf.toFixed(1)}%` : 'not saved'}</Badge>
                <Badge variant="default">Gap {summary.goal_summary.gap != null ? `${summary.goal_summary.gap.toFixed(1)}%` : 'unknown'}</Badge>
                <Badge variant="success">Next check-in {summary.scan_summary.next_check_in_label}</Badge>
              </div>
            </div>

            <div className="md:min-w-[220px]">
              <Button
                variant="primary"
                size="lg"
                className="w-full justify-center"
                onClick={() => router.push(summary.primary_cta.href)}
              >
                {summary.primary_cta.label}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <p className="mt-3 text-xs text-center text-text-light">
                One clear next step. Everything else stays secondary.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card hover>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-text-secondary">Current goal</p>
                <h3 className="text-xl font-bold text-text mt-1">
                  {summary.goal_summary.target_bf != null ? `${summary.goal_summary.target_bf.toFixed(1)}% target` : 'No saved goal yet'}
                </h3>
              </div>
              <div className="p-3 rounded-xl bg-primary/10">
                <Target className="h-5 w-5 text-primary" />
              </div>
            </div>
            <div className="space-y-2 text-sm text-text-secondary">
              <p>{summary.goal_summary.gap != null ? `${summary.goal_summary.gap.toFixed(1)}% left to close` : 'Gap-to-goal starts after you set a target and log a scan.'}</p>
              <p>{summary.goal_summary.has_saved_plan ? `Plan saved ${buildRelativeLabel(summary.goal_summary.plan_updated_at)}` : 'No planner snapshot saved yet.'}</p>
              {summary.goal_summary.selected_tier_calories != null && (
                <p>{summary.goal_summary.selected_tier_calories} kcal/day selected in planner.</p>
              )}
            </div>
            <Button variant="ghost" className="px-0" onClick={() => router.push('/goal-planner')}>
              Open planner
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card hover>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-text-secondary">Journey</p>
                <h3 className="text-xl font-bold text-text mt-1">
                  {latestTransformation ? 'Latest transformation saved' : 'No transformation saved yet'}
                </h3>
              </div>
              <div className="p-3 rounded-xl bg-violet-500/10">
                <Sparkles className="h-5 w-5 text-violet-500" />
              </div>
            </div>
            <div className="space-y-2 text-sm text-text-secondary">
              <p>{latestTransformation ? latestTransformation.result_summary : 'Run a transformation to create a future-body reference point.'}</p>
              <p>{latestTransformation ? `Updated ${formatDateLabel(latestTransformation.date)}` : 'Nothing in journey history yet.'}</p>
              <p>{summary.goal_summary.goal_image_url ? 'Goal image is saved to your profile.' : 'No saved goal image yet.'}</p>
            </div>
            <Button variant="ghost" className="px-0" onClick={() => router.push('/body-scan?tab=journey#transformation')}>
              Open journey
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card hover>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-text-secondary">Progress proof</p>
                <h3 className="text-xl font-bold text-text mt-1">
                  {summary.progress_summary.photo_count > 0
                    ? `${summary.progress_summary.photo_count} photo${summary.progress_summary.photo_count === 1 ? '' : 's'} logged`
                    : 'No proof photos yet'}
                </h3>
              </div>
              <div className="p-3 rounded-xl bg-emerald-500/10">
                <Camera className="h-5 w-5 text-emerald-500" />
              </div>
            </div>
            <div className="space-y-2 text-sm text-text-secondary">
              <p>{summary.progress_summary.latest_photo_date ? `Last proof added ${buildRelativeLabel(summary.progress_summary.latest_photo_date)}` : 'Upload a progress photo when you want something more concrete than a scan result.'}</p>
              <p>{summary.progress_summary.compare_ready ? 'You have enough photos for side-by-side comparison.' : 'You need two photos before comparison becomes useful.'}</p>
              <p>{summary.scan_summary.scan_count ? `${summary.scan_summary.scan_count} scan data point${summary.scan_summary.scan_count === 1 ? '' : 's'} behind this journey.` : 'No scan history behind the proof yet.'}</p>
            </div>
            <Button variant="ghost" className="px-0" onClick={() => router.push(progressHref)}>
              Open progress
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {!isPremium && (
        <Card variant="elevated" className="bg-gradient-to-r from-primary/[0.06] to-secondary/[0.06] border border-primary/20">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-2xl font-bold text-text mb-2 flex items-center justify-center md:justify-start">
                  <Crown className="h-6 w-6 text-premium mr-2" />
                  Unlimited Weekly Scans. No Credit Cost.
                </h3>
                <p className="text-text-secondary mb-4">
                  Pro removes the friction from the weekly loop. The planner, proof, and scan habit work better when the check-in is easy to repeat.
                </p>
              </div>
              <Button variant="primary" size="lg" onClick={() => router.push('/upgrade')}>
                <Crown className="h-5 w-5 mr-2" />
                Go Pro
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

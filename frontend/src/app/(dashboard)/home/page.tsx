'use client';

import dynamic from 'next/dynamic';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';

import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { homeApi, weeklyCheckinsApi } from '@/lib/api/services';
import { trackReengagementSession } from '@/lib/analytics';
import { Card, CardContent, ProcessingOverlay } from '@/components/ui';
import { SkeletonCard } from '@/components/ui/Skeleton';
import type { HomeSummaryResponse, WeeklyCheckinAnalysisResponse } from '@/types/api';
import { cn } from '@/lib/utils/cn';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { formatApiError } from '@/lib/utils/apiError';
import {
  coerceDemoWeeklyScenario,
  createDemoWeeklyAnalysis,
  readWeeklyAnalysisOverride,
  WEEKLY_ANALYSIS_OVERRIDE_STORAGE_KEY,
  writeWeeklyAnalysisOverride,
} from '@/lib/debug/weeklyAnalysisOverride';

const HologramBodyScanner = dynamic(
  () =>
    import('@/components/features/HologramBodyScanner').then((module) => ({
      default: module.HologramBodyScanner,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-[560px] rounded-[34px] border border-white/[0.06] bg-[#0e0d0a] dark:bg-[#0e0d0a]" />
    ),
  },
);

const HOME_SUMMARY_CACHE_PREFIX = 'home_summary_cache';
const WEEKLY_DEMO_ENABLED = process.env.NEXT_PUBLIC_ENABLE_WEEKLY_DEMO === 'true';
const WEEKLY_ANALYSIS_STEPS = [
  { label: 'Uploading weekly photo…', duration: 1400 },
  { label: 'Extracting visual observations…', duration: 5200 },
  { label: 'Comparing with your last check-in…', duration: 2600 },
  { label: 'Updating your hologram…', duration: 1400 },
];

function getHomeSummaryCacheKey(userId: string, source?: string) {
  return `${HOME_SUMMARY_CACHE_PREFIX}:${userId}:${source ?? 'default'}`;
}

function readCachedHomeSummary(cacheKey: string): HomeSummaryResponse | null {
  try {
    const raw = sessionStorage.getItem(cacheKey);
    return raw ? (JSON.parse(raw) as HomeSummaryResponse) : null;
  } catch {
    return null;
  }
}

function writeCachedHomeSummary(cacheKey: string, summary: HomeSummaryResponse) {
  try {
    sessionStorage.setItem(cacheKey, JSON.stringify(summary));
  } catch {
    /* noop */
  }
}

function formatDateLabel(value?: string | null, locale: string = 'en') {
  if (!value) return 'Not yet';
  return new Date(value).toLocaleDateString(locale, { month: 'short', day: 'numeric' });
}

function formatSignedDelta(value?: number | null) {
  if (value == null) return 'No baseline';
  if (Math.abs(value) < 0.05) return '0.0';
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}`;
}

function formatConfidence(value?: number | null) {
  if (value == null) return 'Not scored';
  return `${Math.round(value * 100)}%`;
}

function formatBodyFatValue(
  current?: number | null,
  target?: number | null,
  targetLabel?: string,
  trackingLabel: string = 'Tracking',
) {
  if (current != null) return `${current.toFixed(1)}%`;
  if (target != null) return targetLabel ?? `${target.toFixed(1)}%`;
  return trackingLabel;
}

function weeklyStatusLabel(t: (key: string, params?: Record<string, string | number>) => string, analysis: WeeklyCheckinAnalysisResponse | null) {
  if (!analysis) return t('dashboardHome.awaitingFirstCheckin');
  if (analysis.is_first_checkin) return t('dashboardHome.baselineRecorded');
  switch (analysis.weekly_status) {
    case 'improved':
      return t('dashboardHome.statusImproved');
    case 'regressed':
      return t('dashboardHome.statusRegressed');
    case 'low_confidence':
      return t('dashboardHome.statusLowConfidence');
    case 'stable':
    default:
      return t('dashboardHome.statusStable');
  }
}

function weeklyHeadline(
  t: (key: string, params?: Record<string, string | number>) => string,
  analysis: WeeklyCheckinAnalysisResponse | null,
  fallbackPromptState?: string,
) {
  if (!analysis) {
    return '';
  }

  if (analysis.is_first_checkin) return t('dashboardHome.baselineRecorded');
  switch (analysis.weekly_status) {
    case 'improved':
      return t('dashboardHome.improvedThisWeek');
    case 'regressed':
      return t('dashboardHome.needsReview');
    case 'low_confidence':
      return t('dashboardHome.lowConfidenceCheckin');
    case 'stable':
    default:
      return t('dashboardHome.holdingSteady');
  }
}

function weeklySummaryLines(
  t: (key: string, params?: Record<string, string | number>) => string,
  analysis: WeeklyCheckinAnalysisResponse | null,
  summary: HomeSummaryResponse,
  locale: string,
) {
  if (!analysis) {
    return [
      t('dashboardHome.noAnalysisLine1'),
      summary.scan_summary.last_scan_date
        ? t('dashboardHome.noAnalysisLine2WithDate', { date: formatDateLabel(summary.scan_summary.last_scan_date, locale) })
        : t('dashboardHome.noAnalysisLine2NoDate'),
    ];
  }

  if (analysis.weekly_status === 'low_confidence') {
    return [
      ...analysis.qualitative_summary.slice(0, 2),
      t('dashboardHome.lowConfidenceLine', { confidence: formatConfidence(analysis.comparison_confidence) }),
    ];
  }

  return analysis.qualitative_summary.slice(0, 3);
}

function buildWorkflowRows(
  t: (key: string, params?: Record<string, string | number>) => string,
  analysis: WeeklyCheckinAnalysisResponse | null,
) {
  if (!analysis) {
    return [
      { index: '01', label: t('dashboardHome.uploadPhoto'), value: t('common.next') },
      { index: '02', label: t('dashboardHome.extractObservations'), value: t('dashboardHome.waiting') },
      { index: '03', label: t('dashboardHome.compareChanges'), value: t('dashboardHome.afterUpload') },
      { index: '04', label: t('dashboardHome.saveReport'), value: t('dashboardHome.finalStep') },
    ];
  }

  return [
    { index: '01', label: t('dashboardHome.uploadPhoto'), value: t('dashboardHome.done') },
    { index: '02', label: t('dashboardHome.extractObservations'), value: t('dashboardHome.done') },
    {
      index: '03',
      label: t('dashboardHome.compareChanges'),
      value: analysis.is_first_checkin ? t('dashboardHome.baseline') : analysis.weekly_status === 'low_confidence' ? t('dashboardHome.statusLowConfidence') : t('dashboardHome.done'),
    },
    { index: '04', label: t('dashboardHome.saveReport'), value: t('dashboardHome.done') },
  ];
}

export default function HomePage() {
  const searchParams = useSearchParams();
  const params = useMemo(() => searchParams ?? new URLSearchParams(), [searchParams]);
  const { user } = useAuth();
  const { t, locale } = useLanguage();
  const source = params.get('from') || undefined;
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [summary, setSummary] = useState<HomeSummaryResponse | null>(null);
  const [latestAnalysis, setLatestAnalysis] = useState<WeeklyCheckinAnalysisResponse | null>(null);
  const [analysisOverride, setAnalysisOverride] = useState<WeeklyCheckinAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.id) return;
    let cancelled = false;
    const cacheKey = getHomeSummaryCacheKey(user.id, source);
    const cachedSummary = readCachedHomeSummary(cacheKey);

    if (cachedSummary) {
      setSummary(cachedSummary);
      setLatestAnalysis(cachedSummary.latest_weekly_checkin ?? null);
      setDashboardError(null);
      setLoading(false);
    } else {
      setLoading(true);
    }

    async function loadHomeSummary() {
      try {
        const res = await homeApi.getSummary(source);
        if (!cancelled) {
          setSummary(res.data);
          setLatestAnalysis(res.data.latest_weekly_checkin ?? null);
          setDashboardError(null);
          writeCachedHomeSummary(cacheKey, res.data);
        }
      } catch {
        if (!cancelled) {
          if (!cachedSummary) {
            setSummary(null);
            setLatestAnalysis(null);
          }
          setDashboardError('Live dashboard data is temporarily unavailable. Showing the latest available view.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadHomeSummary();

    return () => {
      cancelled = true;
    };
  }, [source, user?.id]);

  useEffect(() => {
    if (loading || !summary) return;

    trackReengagementSession({
      surface: 'home',
      source: params.get('from') || undefined,
      entry_state: summary.entry_state,
      reentry_state: summary.reentry_state,
      surface_state: summary.surface_state,
      has_saved_plan: summary.goal_summary.has_saved_plan,
      has_goal_image: Boolean(summary.goal_summary.goal_image_url),
      has_transformation: Boolean(summary.scan_summary.latest_transformation),
      has_progress_photo: summary.progress_summary.photo_count > 0,
      scan_count: summary.scan_summary.scan_count,
      challenge_active: summary.challenge_summary.is_active,
    });
  }, [loading, params, summary]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    if (!WEEKLY_DEMO_ENABLED) {
      writeWeeklyAnalysisOverride(null);
      setAnalysisOverride(null);
      return;
    }

    const scenario = coerceDemoWeeklyScenario(params.get('demoWeekly'));
    if (scenario) {
      const scenarioAnalysis = createDemoWeeklyAnalysis(scenario, summary);
      writeWeeklyAnalysisOverride(scenarioAnalysis);
      setAnalysisOverride(scenarioAnalysis);
      return;
    }

    const customOverride = readWeeklyAnalysisOverride();
    if (customOverride) {
      setAnalysisOverride(customOverride);
      return;
    }

    setAnalysisOverride(null);
  }, [params, summary]);

  const handlePickWeeklyPhoto = () => {
    if (isAnalyzing) return;
    fileInputRef.current?.click();
  };

  const handleRetryDashboard = () => {
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  const handleWeeklyPhotoSelected = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    setAnalysisError(null);
    setIsAnalyzing(true);

    try {
      const image_base64 = await compressAndConvertToBase64(file);
      const response = await weeklyCheckinsApi.analyze({
        image_base64,
        ownership_confirmed: true,
      });

      setLatestAnalysis(response.data);
      setSummary((current) => {
        if (!current) return current;
        const nextSummary: HomeSummaryResponse = {
          ...current,
          latest_weekly_checkin: response.data,
          progress_summary: {
            ...current.progress_summary,
            photo_count: Math.max(current.progress_summary.photo_count + 1, 1),
            latest_photo_date: response.data.taken_at,
            compare_ready: true,
          },
        };

        if (user?.id) {
          writeCachedHomeSummary(getHomeSummaryCacheKey(user.id, source), nextSummary);
        }

        return nextSummary;
      });
    } catch (error) {
      setAnalysisError(formatApiError(error));
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (!summary) {
    return (
      <Card>
        <CardContent className="space-y-2 p-6">
          <h1 className="text-2xl font-bold text-text dark:text-white">{t('dashboardHome.navDashboard')}</h1>
          <p className="text-sm text-text-secondary dark:text-white/60">
            {t('dashboardHome.dashboardUnavailableBody')}
          </p>
          <button
            type="button"
            onClick={handleRetryDashboard}
            className="mt-4 inline-flex items-center rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-medium text-text transition-colors hover:bg-white/[0.08] dark:text-white"
          >
            Retry
          </button>
        </CardContent>
      </Card>
    );
  }

  const effectiveAnalysis = analysisOverride ?? latestAnalysis;

  const title = weeklyHeadline(t, effectiveAnalysis, summary.scan_summary.prompt_state);
  const summaryLines = weeklySummaryLines(t, effectiveAnalysis, summary, locale);
  const workflowRows = buildWorkflowRows(t, effectiveAnalysis);

  const leftMetrics = [
    {
      label: t('dashboardHome.goalProximity'),
      value: effectiveAnalysis ? `${effectiveAnalysis.derived_scores.goal_proximity_score.toFixed(1)}` : t('dashboardHome.notYet'),
    },
    {
      label: t('dashboardHome.weeklyDelta'),
      value: effectiveAnalysis
        ? effectiveAnalysis.is_first_checkin
          ? t('dashboardHome.baseline')
          : formatSignedDelta(effectiveAnalysis.delta_from_previous?.goal_proximity_score)
        : t('dashboardHome.noBaseline'),
    },
    {
      label: t('dashboardHome.status'),
      value: weeklyStatusLabel(t, effectiveAnalysis),
    },
    {
      label: t('dashboardHome.confidence'),
      value: effectiveAnalysis ? formatConfidence(effectiveAnalysis.comparison_confidence) : t('dashboardHome.waiting'),
    },
  ];

  const fallbackRegionalCards: import('@/types/api').RegionVisualization[] = [
    {
      region: 'chest',
      label: t('dashboardHome.bodyFat'),
      value: formatBodyFatValue(
        summary.goal_summary.current_bf,
        summary.goal_summary.target_bf,
        summary.goal_summary.target_bf != null ? t('dashboardHome.targetPercent', { value: summary.goal_summary.target_bf.toFixed(1) }) : undefined,
        t('dashboardHome.goalTargetPending'),
      ),
      note:
        summary.goal_summary.target_bf != null
          ? t('dashboardHome.targetPercent', { value: summary.goal_summary.target_bf.toFixed(1) })
          : t('dashboardHome.goalTargetPending'),
      status: 'stable',
      intensity: 0.42,
    },
    {
      region: 'abdomen',
      label: t('dashboardHome.remainingToGoal'),
      value: summary.goal_summary.gap != null ? t('dashboardHome.remainingValue', { value: summary.goal_summary.gap.toFixed(1) }) : t('dashboardHome.setGoal'),
      note:
        summary.goal_summary.target_bf != null
          ? t('dashboardHome.towardTarget', { value: summary.goal_summary.target_bf.toFixed(1) })
          : t('dashboardHome.goalTargetPending'),
      status: 'stable',
      intensity: 0.46,
    },
    {
      region: 'arms',
      label: t('dashboardHome.progressPhoto'),
      value: t('dashboardHome.savedCount', { count: summary.progress_summary.photo_count }),
      note: summary.progress_summary.latest_photo_date
        ? t('dashboardHome.lastAdded', { date: formatDateLabel(summary.progress_summary.latest_photo_date, locale) })
        : t('dashboardHome.addReferencePhoto'),
      status: summary.progress_summary.photo_count > 0 ? 'improved' : 'stable',
      intensity: summary.progress_summary.photo_count > 0 ? 0.52 : 0.36,
    },
  ];

  const regionalCards = effectiveAnalysis?.regional_visualization?.length
    ? effectiveAnalysis.regional_visualization
    : fallbackRegionalCards;
  const hologramVisualization = effectiveAnalysis?.hologram_visualization;

  return (
    <div className="space-y-5">
      <section aria-label="Weekly body-check dashboard">
        <h1 className="sr-only">Weekly body-check dashboard</h1>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleWeeklyPhotoSelected}
        />

        <Card className="overflow-hidden rounded-[34px] border-border/40 bg-white shadow-sm dark:border-white/[0.05] dark:bg-[#0b0a08]">
          <CardContent className="relative p-0">
            <div className="absolute inset-0 bg-[radial-gradient(720px_460px_at_72%_44%,rgba(204,190,150,0.06),transparent_48%),linear-gradient(180deg,rgba(255,255,255,0.012),transparent_22%,transparent_65%)] opacity-0 dark:opacity-100" />
            <div className="grid gap-0 xl:grid-cols-[380px_minmax(0,1fr)]">
              <aside className="relative z-10 flex flex-col border-b border-border/60 px-6 py-6 md:px-8 md:py-8 xl:min-h-[760px] xl:border-b-0 xl:border-r xl:border-border/60 dark:border-white/[0.06]">
                <div className="space-y-6">
                  {dashboardError ? (
                    <p className="max-w-[18rem] text-sm leading-6 text-amber-700 dark:text-amber-300">
                      {dashboardError}
                    </p>
                  ) : null}
                  <div className="flex items-center gap-3">
                    <span
                      className={cn(
                        'inline-flex items-center rounded-full border px-3 py-1 text-[12px] font-medium',
                        effectiveAnalysis?.weekly_status === 'improved'
                          ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
                          : effectiveAnalysis?.weekly_status === 'regressed'
                            ? 'border-amber-500/20 bg-amber-500/10 text-amber-700 dark:text-amber-300'
                            : effectiveAnalysis?.weekly_status === 'low_confidence'
                              ? 'border-orange-500/20 bg-orange-500/10 text-orange-700 dark:text-orange-300'
                              : 'border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-300',
                      )}
                    >
                      {weeklyStatusLabel(t, effectiveAnalysis)}
                    </span>
                    <span className="text-sm text-text-secondary dark:text-white/44">
                      {effectiveAnalysis?.taken_at ? formatDateLabel(effectiveAnalysis.taken_at, locale) : t('dashboardHome.thisWeek')}
                    </span>
                  </div>

                  <div className="space-y-3">
                    {title ? (
                      <h2 className="max-w-[14rem] text-[3rem] font-semibold leading-[0.9] tracking-[-0.07em] text-text dark:text-white">
                        {title}
                      </h2>
                    ) : null}
                    <div className="space-y-2">
                      {summaryLines.map((line) => (
                        <p key={line} className="max-w-[18rem] text-sm leading-6 text-text-secondary dark:text-white/58">
                          {line}
                        </p>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <button
                      type="button"
                      onClick={handlePickWeeklyPhoto}
                      disabled={isAnalyzing}
                      className="inline-flex min-h-[58px] items-center justify-center rounded-[20px] bg-[rgb(var(--color-primary))] px-6 text-base font-semibold text-[#17130e] transition-transform duration-200 hover:scale-[1.01] focus:outline-none focus:ring-2 focus:ring-[rgb(var(--color-primary-light))] disabled:cursor-default disabled:opacity-60 disabled:hover:scale-100 dark:text-[#16110b]"
                      aria-label="Upload weekly progress photo"
                    >
                      {isAnalyzing ? t('dashboardHome.analyzing') : effectiveAnalysis ? t('dashboardHome.uploadWeeklyPhoto') : t('dashboardHome.uploadFirstCheckinPhoto')}
                    </button>
                    {analysisError ? (
                      <p className="max-w-[18rem] text-sm leading-6 text-red-600 dark:text-red-300">
                        {analysisError}
                      </p>
                    ) : null}
                    {WEEKLY_DEMO_ENABLED && analysisOverride ? (
                      <p className="max-w-[18rem] text-xs leading-5 text-sky-700 dark:text-sky-300">
                        Demo result override is active. Remove `demoWeekly` from the URL or clear the
                        localStorage key {WEEKLY_ANALYSIS_OVERRIDE_STORAGE_KEY} to return to live analysis.
                      </p>
                    ) : null}
                  </div>
                </div>

                <div className="mt-10 grid gap-8 xl:mt-auto">
                  <div className="grid gap-3 border-t border-border/60 pt-6 dark:border-white/[0.06]">
                    <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-secondary dark:text-white/36">
                      Current goal
                    </p>
                    {leftMetrics.map((item) => (
                      <div key={item.label} className="flex items-baseline justify-between gap-4">
                        <dt className="text-sm text-text-secondary dark:text-white/46">{item.label}</dt>
                        <dd className="text-sm font-medium text-text dark:text-white">{item.value}</dd>
                      </div>
                    ))}
                  </div>

                  <div className="grid gap-3 border-t border-border/60 pt-6 dark:border-white/[0.06]">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-secondary dark:text-white/36">
                        Journey
                      </p>
                      <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-secondary dark:text-white/36">
                        {t('dashboardHome.flow')}
                      </p>
                    </div>
                    <ol className="grid gap-3">
                      {workflowRows.map((item) => (
                        <li key={item.index} className="grid grid-cols-[32px_minmax(0,1fr)_auto] items-center gap-3">
                          <span className="text-[11px] font-medium tracking-[0.08em] text-text-secondary dark:text-white/34">
                            {item.index}
                          </span>
                          <span className="text-sm text-text dark:text-white">{item.label}</span>
                          <span className="text-xs text-text-secondary dark:text-white/46">{item.value}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                </div>
              </aside>

              <div className="relative z-10 px-4 py-4 md:px-6 md:py-6 xl:min-h-[760px] xl:px-8 xl:py-8">
                <p className="mb-4 text-[11px] font-medium uppercase tracking-[0.08em] text-text-secondary dark:text-white/36">
                  Progress proof
                </p>
                <HologramBodyScanner
                  className="h-full min-h-[560px] xl:min-h-[700px]"
                  size={0.92}
                  autoRotateSpeed={0.08}
                  glowIntensity={hologramVisualization?.glow_intensity ?? 0.82}
                  bodyClarity={hologramVisualization?.body_clarity ?? 0.74}
                  pedestalProgress={hologramVisualization?.pedestal_progress ?? 0.32}
                  scanlineSpeed={1}
                  regionalCards={regionalCards}
                />

                <div className="pointer-events-none absolute inset-0 flex items-center justify-center p-6">
                  <ProcessingOverlay
                    active={isAnalyzing}
                    steps={WEEKLY_ANALYSIS_STEPS}
                    className="w-full max-w-[420px] bg-[#0c0b09]/94"
                    dark
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

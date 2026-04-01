'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Image from 'next/image';
import dynamic from 'next/dynamic';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import WeightLogForm from '@/components/features/WeightLogForm';
import GoalSettingForm from '@/components/features/GoalSettingForm';

const GoalProjectionChart = dynamic(
  () => import('@/components/features/GoalProjectionChart'),
  { loading: () => <div className="h-[400px] bg-surfaceAlt animate-pulse rounded-lg" />, ssr: false }
);
import { Modal } from '@/components/ui/Modal';
import { homeApi, progressPhotoApi, proofShareApi } from '@/lib/api/services';
import { getRetentionSessionId, trackRetentionEvent } from '@/lib/analytics';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { Camera, ImageIcon, ArrowLeftRight, Trash2, X, Plus, Check, ArrowRight, CalendarClock, Share2, Copy, ExternalLink, Shield } from 'lucide-react';
import { coerceHomeEntryState } from '@/types/api';
import type { HomeSummaryResponse, ProgressPhoto, ProgressPhotoCompareResponse, ProofShareResponse } from '@/types/api';

type Tab = 'goals' | 'photos';

export default function ProgressPage() {
  const router = useRouter();
  const { t } = useLanguage();
  const searchParams = useSearchParams();
  const [activeTab, setActiveTab] = useState<Tab>(searchParams.get('tab') === 'photos' ? 'photos' : 'goals');
  const [showWeightLogModal, setShowWeightLogModal] = useState(false);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const historyTrackedRef = useRef<{ photos: boolean; goals: boolean }>({ photos: false, goals: false });
  const focusAppliedRef = useRef<string | null>(null);
  const compareTrackedRef = useRef<string | null>(null);
  const reminderTrackedRef = useRef(false);

  // Photo state
  const [photos, setPhotos] = useState<ProgressPhoto[]>([]);
  const [loadingPhotos, setLoadingPhotos] = useState(false);
  const [homeSummary, setHomeSummary] = useState<HomeSummaryResponse | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadNotes, setUploadNotes] = useState('');
  const [uploadWeight, setUploadWeight] = useState('');
  const [uploadBodyFat, setUploadBodyFat] = useState('');
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Compare state
  const [compareMode, setCompareMode] = useState(false);
  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([]);
  const [compareData, setCompareData] = useState<ProgressPhotoCompareResponse | null>(null);
  const [loadingCompare, setLoadingCompare] = useState(false);

  // Full-size view
  const [viewingPhoto, setViewingPhoto] = useState<ProgressPhoto | null>(null);
  const [loadingFullPhoto, setLoadingFullPhoto] = useState(false);

  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [proofShares, setProofShares] = useState<ProofShareResponse[]>([]);
  const [loadingProofShares, setLoadingProofShares] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareWeekMarker, setShareWeekMarker] = useState('');
  const [creatingShare, setCreatingShare] = useState(false);
  const [revokingShareId, setRevokingShareId] = useState<string | null>(null);
  const [copiedShareUrl, setCopiedShareUrl] = useState(false);

  const reminderSource = searchParams.get('from') || undefined;
  const reminderEventId = searchParams.get('reminder_event_id') || undefined;
  const reminderReentryState = reminderSource === 'weekly_reminder'
    ? coerceHomeEntryState(searchParams.get('reentry_state'), 'weekly_scan')
    : undefined;
  const reminderLandingSurfaceState = reminderSource === 'weekly_reminder'
    ? coerceHomeEntryState(searchParams.get('surface_state'))
    : undefined;

  const buildProofLoopAnalytics = useCallback((
    sourceFallback: string | undefined,
    surfaceState: 'progress_proof' | 'review_progress',
    extra: Record<string, string | number | boolean | null | undefined> = {},
  ) => ({
    source: reminderSource === 'weekly_reminder' ? 'weekly_reminder' : sourceFallback,
    reentry_state: reminderReentryState,
    surface_state: surfaceState,
    reminder_event_id: reminderEventId,
    session_id: getRetentionSessionId() || undefined,
    ...extra,
  }), [reminderEventId, reminderReentryState, reminderSource]);

  const handleWeightLogSuccess = () => {
    setShowWeightLogModal(false);
    setRefreshKey(prev => prev + 1);
  };

  const handleGoalSuccess = () => {
    setShowGoalModal(false);
    setRefreshKey(prev => prev + 1);
  };

  const fetchPhotos = useCallback(async (): Promise<ProgressPhoto[]> => {
    setLoadingPhotos(true);
    try {
      const res = await progressPhotoApi.getAll();
      setPhotos(res.data);
      return res.data as ProgressPhoto[];
    } catch {
      console.error('Failed to fetch photos');
      return [];
    } finally {
      setLoadingPhotos(false);
    }
  }, []);

  const fetchHomeSummary = useCallback(async () => {
    try {
      const res = await homeApi.getSummary(reminderSource);
      setHomeSummary(res.data);
      return res.data as HomeSummaryResponse;
    } catch {
      setHomeSummary(null);
      return null;
    }
  }, [reminderSource]);

  const fetchProofShares = useCallback(async () => {
    setLoadingProofShares(true);
    try {
      const res = await proofShareApi.getAll();
      setProofShares(res.data);
      return res.data as ProofShareResponse[];
    } catch {
      setProofShares([]);
      return [];
    } finally {
      setLoadingProofShares(false);
    }
  }, []);

  useEffect(() => {
    const requestedTab = searchParams.get('tab') === 'photos' ? 'photos' : 'goals';
    setActiveTab(requestedTab);
  }, [searchParams]);

  const openUploadModal = useCallback((source: string) => {
    setShowUpload(true);
    trackRetentionEvent('progress_proof_started', buildProofLoopAnalytics(
      source,
      'progress_proof',
      {
        surface: 'progress_page',
        entry_state: reminderReentryState || 'progress_proof',
        photo_count: photos.length,
      },
    ));
  }, [buildProofLoopAnalytics, photos.length, reminderReentryState]);

  const loadLatestCompare = useCallback(async (photoList: ProgressPhoto[]) => {
    if (photoList.length < 2) {
      setCompareData(null);
      return null;
    }

    setLoadingCompare(true);
    try {
      const res = await progressPhotoApi.compare(photoList[1].id, photoList[0].id);
      setCompareData(res.data);
      return res.data as ProgressPhotoCompareResponse;
    } catch {
      console.error('Compare failed');
      return null;
    } finally {
      setLoadingCompare(false);
    }
  }, []);

  const resetUploadState = () => {
    setShowUpload(false);
    setUploadPreview(null);
    setUploadFile(null);
    setUploadNotes('');
    setUploadWeight('');
    setUploadBodyFat('');
  };

  useEffect(() => {
    if (activeTab === 'photos') {
      void fetchPhotos();
      void fetchHomeSummary();
      void fetchProofShares();
    }
  }, [activeTab, fetchPhotos, fetchHomeSummary, fetchProofShares]);

  useEffect(() => {
    if (historyTrackedRef.current[activeTab]) return;
    historyTrackedRef.current[activeTab] = true;
    trackRetentionEvent('history_viewed', {
      surface: 'progress_page',
      target: activeTab === 'photos' ? 'progress_proof' : 'goals',
    });
  }, [activeTab]);

  useEffect(() => {
    if (reminderTrackedRef.current) return;
    if (searchParams.get('from') !== 'weekly_reminder') return;
    if (activeTab !== 'photos') return;

    reminderTrackedRef.current = true;
    trackRetentionEvent('reengagement_session', buildProofLoopAnalytics(
      'weekly_reminder',
      reminderLandingSurfaceState === 'review_progress' ? 'review_progress' : 'progress_proof',
      {
        surface: 'progress_page',
        entry_state: reminderReentryState || 'weekly_scan',
      },
    ));
  }, [activeTab, buildProofLoopAnalytics, reminderLandingSurfaceState, reminderReentryState, searchParams]);

  useEffect(() => {
    if (activeTab !== 'photos' || compareMode) return;
    if (photos.length >= 2) {
      void loadLatestCompare(photos);
      return;
    }
    setCompareData(null);
  }, [activeTab, compareMode, photos, loadLatestCompare]);

  useEffect(() => {
    if (activeTab !== 'photos') return;

    const focus = searchParams.get('focus');
    if (!focus || focusAppliedRef.current === focus) return;

    if (focus === 'upload') {
      focusAppliedRef.current = focus;
      openUploadModal(searchParams.get('from') || 'progress_focus_upload');
      return;
    }

    if (focus === 'compare' && photos.length >= 2) {
      focusAppliedRef.current = focus;
      void loadLatestCompare(photos);
    }
  }, [activeTab, searchParams, photos, openUploadModal, loadLatestCompare]);

  useEffect(() => {
    if (!compareData) return;

    const compareKey = `${compareData.before.id}:${compareData.after.id}`;
    if (compareTrackedRef.current === compareKey) return;
    compareTrackedRef.current = compareKey;

    trackRetentionEvent('progress_compare_viewed', buildProofLoopAnalytics(
      reminderSource,
      'review_progress',
      {
        surface: 'progress_page',
        entry_state: reminderReentryState || 'review_progress',
        before_photo_id: compareData.before.id,
        after_photo_id: compareData.after.id,
        days_between: compareData.days_between,
        weight_change: compareData.weight_change,
        bf_change: compareData.bf_change,
        goal_gap: homeSummary?.goal_summary.gap,
        prompt_state: homeSummary?.scan_summary.prompt_state,
      },
    ));
  }, [buildProofLoopAnalytics, compareData, homeSummary, reminderReentryState, reminderSource]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadFile(file);
    const reader = new FileReader();
    reader.onload = () => setUploadPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!uploadFile) return;
    setUploading(true);
    try {
      const base64 = await compressAndConvertToBase64(uploadFile);
      await progressPhotoApi.upload(
        base64,
        uploadNotes || undefined,
        uploadWeight ? parseFloat(uploadWeight) : undefined,
        uploadBodyFat ? parseFloat(uploadBodyFat) : undefined
      );
      resetUploadState();
      const refreshedPhotos = await fetchPhotos();
      await fetchHomeSummary();
      await fetchProofShares();
      trackRetentionEvent('progress_proof_completed', buildProofLoopAnalytics(
        reminderSource || 'progress_upload',
        refreshedPhotos.length >= 2 ? 'review_progress' : 'progress_proof',
        {
          surface: 'progress_page',
          entry_state: reminderReentryState || 'progress_proof',
          photo_count: refreshedPhotos.length,
          has_compare_ready: refreshedPhotos.length >= 2,
        },
      ));
      if (refreshedPhotos.length >= 2) {
        await loadLatestCompare(refreshedPhotos);
      }
    } catch {
      trackRetentionEvent('proof_upload_failed', buildProofLoopAnalytics(
        reminderSource || 'progress_upload',
        'progress_proof',
        {
          surface: 'progress_page',
          entry_state: reminderReentryState || 'progress_proof',
          photo_count: photos.length,
        },
      ));
      console.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDeletePhoto = async (photoId: string) => {
    setDeletingId(photoId);
    try {
      await progressPhotoApi.delete(photoId);
      setPhotos(prev => prev.filter(p => p.id !== photoId));
      setProofShares(prev => prev.filter(share => share.progress_photo_id !== photoId));
      if (viewingPhoto?.id === photoId) setViewingPhoto(null);
      await fetchHomeSummary();
    } catch {
      console.error('Delete failed');
    } finally {
      setDeletingId(null);
    }
  };

  const handleViewPhoto = async (photo: ProgressPhoto) => {
    setLoadingFullPhoto(true);
    setViewingPhoto(photo);
    try {
      const res = await progressPhotoApi.getOne(photo.id);
      setViewingPhoto(res.data);
    } catch {
      console.error('Failed to load photo');
    } finally {
      setLoadingFullPhoto(false);
    }
  };

  const togglePhotoSelection = (photoId: string) => {
    setSelectedPhotos(prev => {
      if (prev.includes(photoId)) return prev.filter(id => id !== photoId);
      if (prev.length >= 2) return [prev[1], photoId];
      return [...prev, photoId];
    });
  };

  const handleCompare = async () => {
    if (selectedPhotos.length !== 2) return;
    setLoadingCompare(true);
    try {
      const res = await progressPhotoApi.compare(selectedPhotos[0], selectedPhotos[1]);
      setCompareData(res.data);
    } catch {
      console.error('Compare failed');
    } finally {
      setLoadingCompare(false);
    }
  };

  const exitCompareMode = () => {
    setCompareMode(false);
    setSelectedPhotos([]);
    if (photos.length >= 2) {
      void loadLatestCompare(photos);
      return;
    }
    setCompareData(null);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getPhotoSrc = (photo: ProgressPhoto | null | undefined) => {
    if (!photo) return null;
    if (photo.image_url) return photo.image_url;
    if (photo.image_base64) return `data:image/jpeg;base64,${photo.image_base64}`;
    return null;
  };

  const latestPhoto = photos[0] ?? null;
  const shareSourcePhoto = compareData?.after ?? latestPhoto;
  const activeProofShare = shareSourcePhoto
    ? proofShares.find(
        share => share.status === 'active' && share.progress_photo_id === shareSourcePhoto.id,
      ) ?? null
    : null;
  const suggestedWeekMarker = compareData?.days_between != null
    ? Math.max(1, Math.round(compareData.days_between / 7))
    : null;
  const proofBranch = photos.length === 0 ? 'empty' : photos.length === 1 ? 'single' : 'compare';
  const shouldShowShareManager = Boolean(shareSourcePhoto) || Boolean(activeProofShare);
  const latestScanLabel = homeSummary?.goal_summary.current_bf != null
    ? `${homeSummary.goal_summary.current_bf.toFixed(1)}% BF`
    : 'No recent scan yet';
  const latestScanDateLabel = homeSummary?.scan_summary.last_scan_date
    ? formatDate(homeSummary.scan_summary.last_scan_date)
    : 'No scan date yet';
  const goalGapLabel = homeSummary?.goal_summary.gap != null
    ? `${homeSummary.goal_summary.gap.toFixed(1)}% to goal`
    : 'Gap unknown';

  const openShareModal = () => {
    if (!shareSourcePhoto) return;
    setShareWeekMarker(suggestedWeekMarker ? String(suggestedWeekMarker) : '');
    setShowShareModal(true);
  };

  const handleCreateShare = async () => {
    if (!shareSourcePhoto) return;
    setCreatingShare(true);
    try {
      const weekMarker = shareWeekMarker ? Number(shareWeekMarker) : undefined;
      const res = await proofShareApi.create(
        shareSourcePhoto.id,
        weekMarker,
        {
          sessionId: getRetentionSessionId() || undefined,
          source: reminderSource === 'weekly_reminder' ? 'weekly_reminder' : undefined,
          reentryState: reminderReentryState,
          surfaceState: compareData ? 'review_progress' : 'progress_proof',
          reminderEventId,
        },
      );
      setProofShares(prev => {
        const next = prev.filter(share => share.id !== res.data.id);
        return [res.data, ...next];
      });
      setShowShareModal(false);
    } catch {
      console.error('Failed to create share');
    } finally {
      setCreatingShare(false);
    }
  };

  const handleCopyShareLink = async (url: string) => {
    await navigator.clipboard.writeText(url);
    setCopiedShareUrl(true);
    window.setTimeout(() => setCopiedShareUrl(false), 2000);
  };

  const handleRevokeShare = async (share: ProofShareResponse) => {
    if (!window.confirm('Revoke this public proof card? Anyone with the link will lose access.')) return;
    setRevokingShareId(share.id);
    try {
      await proofShareApi.revoke(share.id);
      setProofShares(prev => prev.map(existing => (
        existing.id === share.id
          ? { ...existing, status: 'revoked', revoked_at: new Date().toISOString() }
          : existing
      )));
    } catch {
      console.error('Failed to revoke share');
    } finally {
      setRevokingShareId(null);
    }
  };

  const progressAction = (() => {
    if (proofBranch === 'empty') {
      return {
        label: 'Upload progress proof',
        description: 'Lock this week with a proof photo before the next scan replaces the feeling.',
        onClick: () => openUploadModal(searchParams.get('from') || 'progress_empty_state'),
      };
    }

    if (proofBranch === 'single') {
      return {
        label: 'Upload next proof',
        description: 'One proof photo is a start. Two gives you an actual before/after story.',
        onClick: () => openUploadModal('progress_second_proof'),
      };
    }

    if (homeSummary?.scan_summary.prompt_state === 'ready' || homeSummary?.scan_summary.prompt_state === 'overdue') {
      return {
        label: 'Do weekly check-in',
        description: 'Your proof is in place. Refresh the next scan so the loop stays current.',
        onClick: () => router.push('/body-scan?tab=scan'),
      };
    }

    if (homeSummary?.scan_summary.latest_transformation) {
      return {
        label: 'Open journey',
        description: 'Compare the proof against the goal image before the next weekly check-in.',
        onClick: () => router.push('/body-scan?tab=journey#transformation'),
      };
    }

    return {
      label: 'Open planner',
      description: 'Use the proof with a concrete goal so the next scan has context.',
      onClick: () => router.push('/goal-planner'),
    };
  })();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('progress.title')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {t('progress.subtitle')}
          </p>
        </div>

        <div data-tour="progress-actions" className="flex gap-3">
          {activeTab === 'goals' && (
            <>
              <button
                onClick={() => setShowGoalModal(true)}
                className="px-4 py-2 bg-white dark:bg-gray-800 border-2 border-emerald-600 text-emerald-600 rounded-lg hover:bg-emerald-50 dark:hover:bg-gray-700 transition-colors font-medium"
              >
                🎯 {t('progress.setGoal')}
              </button>
              <button
                onClick={() => setShowWeightLogModal(true)}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
              >
                ⚖️ {t('progress.logWeight')}
              </button>
            </>
          )}
          {activeTab === 'photos' && (
            <>
              <button
                onClick={() => compareMode ? exitCompareMode() : setCompareMode(true)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  compareMode
                    ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-2 border-amber-400'
                    : 'bg-white dark:bg-gray-800 border-2 border-emerald-600 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-gray-700'
                }`}
              >
                <ArrowLeftRight className="w-4 h-4" />
                {compareMode ? t('progress.cancelCompare') : t('progress.compare')}
              </button>
              <button
                onClick={() => openUploadModal('progress_header_button')}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium flex items-center gap-2"
              >
                <Camera className="w-4 h-4" />
                {t('progress.addPhoto')}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        <button
          onClick={() => { setActiveTab('goals'); exitCompareMode(); }}
          className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
            activeTab === 'goals'
              ? 'bg-white dark:bg-gray-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
          }`}
        >
          📊 {t('progress.goals')}
        </button>
        <button
          onClick={() => setActiveTab('photos')}
          className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
            activeTab === 'photos'
              ? 'bg-white dark:bg-gray-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
          }`}
        >
          📸 {t('progress.photos')}
        </button>
      </div>

      {/* ==================== GOALS TAB ==================== */}
      {activeTab === 'goals' && (
        <>
          {/* Info Card */}
          <div className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950 dark:to-teal-950 border border-emerald-200 dark:border-emerald-800 rounded-lg p-6">
            <div className="flex items-start gap-4">
              <div className="text-4xl">📊</div>
              <div>
                <h3 className="font-semibold text-emerald-800 dark:text-emerald-300 mb-2">
                  {t('progress.movingAvgPrediction')}
                </h3>
                <p className="text-sm text-emerald-700 dark:text-emerald-400">
                  {t('progress.movingAvgDesc')}
                </p>
                <p className="text-xs text-emerald-600 dark:text-emerald-500 mt-2">
                  💡 {t('progress.weighTip')}
                </p>
              </div>
            </div>
          </div>

          {/* Goal Projection Chart */}
          <div data-tour="progress-chart">
            <GoalProjectionChart key={refreshKey} daysHistory={30} />
          </div>
        </>
      )}

      {/* ==================== PHOTOS TAB ==================== */}
      {activeTab === 'photos' && (
        <div data-tour="progress-photos" className="space-y-6">
          <div
            data-testid="progress-proof-loop"
            data-proof-branch={proofBranch}
            className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/50 dark:to-teal-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl p-5"
          >
            <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
              <div className="space-y-2 max-w-2xl">
                <div className="inline-flex items-center gap-2 rounded-full border border-emerald-300/60 bg-white/70 dark:bg-black/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300">
                  <CalendarClock className="h-3.5 w-3.5" />
                  Progress proof loop
                </div>
                <div>
                  <h3
                    data-testid={`progress-proof-branch-${proofBranch}`}
                    className="text-xl font-bold text-gray-900 dark:text-white"
                  >
                    {proofBranch === 'empty'
                      ? 'Your scan needs visual proof'
                      : proofBranch === 'single'
                        ? 'You have one proof shot'
                        : 'Your proof loop is active'}
                  </h3>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {proofBranch === 'empty'
                      ? 'A scan tells you where you stand. A proof photo gives you something concrete to compare later.'
                      : proofBranch === 'single'
                        ? 'You have a starting point. The next proof photo turns this into a real comparison, not a memory.'
                        : 'Use the latest scan, proof photo, and goal gap together so the next action is based on evidence.'}
                  </p>
                </div>
              </div>
              <div className="lg:min-w-[240px]">
                <button
                  data-testid="progress-proof-primary-action"
                  onClick={progressAction.onClick}
                  className="w-full px-5 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium inline-flex items-center justify-center gap-2"
                >
                  {progressAction.label}
                  <ArrowRight className="w-4 h-4" />
                </button>
                <p className="mt-2 text-xs text-center text-emerald-800/80 dark:text-emerald-300/80">
                  {progressAction.description}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mt-5">
              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 border border-white/80 dark:border-gray-800 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Latest scan summary</p>
                <p className="mt-2 text-lg font-bold text-gray-900 dark:text-white">{latestScanLabel}</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{latestScanDateLabel}</p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
                  {homeSummary?.scan_summary.scan_count
                    ? `${homeSummary.scan_summary.scan_count} scan data point${homeSummary.scan_summary.scan_count === 1 ? '' : 's'} logged`
                    : 'No scan history connected yet'}
                </p>
              </div>

              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 border border-white/80 dark:border-gray-800 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Latest progress photo</p>
                {latestPhoto && getPhotoSrc(latestPhoto) ? (
                  <div className="mt-3 flex items-center gap-3">
                    <div className="relative h-16 w-12 overflow-hidden rounded-md border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800">
                      <Image src={getPhotoSrc(latestPhoto)!} alt="Latest proof" fill className="object-cover" unoptimized />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{formatDate(latestPhoto.taken_at)}</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {latestPhoto.weight_kg != null ? `${latestPhoto.weight_kg} kg` : 'No weight logged'}
                        {latestPhoto.body_fat_pct != null ? ` · ${latestPhoto.body_fat_pct}% BF` : ''}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">No proof photo uploaded yet.</p>
                )}
              </div>

              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 border border-white/80 dark:border-gray-800 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Goal and gap</p>
                <p className="mt-2 text-lg font-bold text-gray-900 dark:text-white">
                  {homeSummary?.goal_summary.target_bf != null ? `${homeSummary.goal_summary.target_bf.toFixed(1)}% target` : 'No saved target'}
                </p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{goalGapLabel}</p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
                  {homeSummary?.goal_summary.goal_image_url ? 'Goal image saved' : 'No goal image saved'}
                </p>
              </div>

              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 border border-white/80 dark:border-gray-800 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Next recommended action</p>
                <p className="mt-2 text-lg font-bold text-gray-900 dark:text-white">{progressAction.label}</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{progressAction.description}</p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
                  {homeSummary?.scan_summary.next_check_in_label
                    ? `Next check-in: ${homeSummary.scan_summary.next_check_in_label}`
                    : 'Next check-in unknown'}
                </p>
              </div>
            </div>

            {shouldShowShareManager && (
              <div
                data-testid="proof-share-manager"
                className="mt-5 rounded-xl border border-emerald-200/80 dark:border-emerald-800 bg-white/80 dark:bg-gray-900/50 p-4"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="space-y-2">
                    <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300">
                      <Share2 className="h-3.5 w-3.5" />
                      Public-safe share
                    </div>
                    <div>
                      <h4 className="text-base font-semibold text-gray-900 dark:text-white">
                        {activeProofShare
                          ? 'Manage your public proof card'
                          : proofBranch === 'single'
                            ? 'Create a public proof card from your first proof photo'
                            : 'Create a public proof card from your proof loop'}
                      </h4>
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        {activeProofShare
                          ? 'This public card is already live. The image stays proxied through Denevira, and you can revoke access anytime.'
                          : proofBranch === 'single'
                            ? 'Share a public-safe card built from your latest proof photo and current goal gap. You can upgrade it later with compare-ready proof.'
                            : 'Share a public-safe card built from your latest proof visual and goal gap summary. You can revoke access anytime.'}
                      </p>
                    </div>
                    {shareSourcePhoto && (
                      <p className="text-xs text-gray-500 dark:text-gray-500">
                        Selected visual: {formatDate(shareSourcePhoto.taken_at)}
                        {suggestedWeekMarker ? ` · suggested week ${suggestedWeekMarker}` : ''}
                      </p>
                    )}
                  </div>

                  {activeProofShare ? (
                    <div className="lg:min-w-[320px] space-y-3">
                      <div className="rounded-lg bg-gray-50 dark:bg-gray-950/50 border border-gray-200 dark:border-gray-800 px-3 py-2">
                        <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Public route</p>
                        <p data-testid="proof-share-public-url" className="mt-1 text-sm text-gray-800 dark:text-gray-200 break-all">
                          {activeProofShare.public_url}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => handleCopyShareLink(activeProofShare.public_url)}
                          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium inline-flex items-center gap-2"
                        >
                          {copiedShareUrl ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                          {copiedShareUrl ? 'Copied' : 'Copy link'}
                        </button>
                        <a
                          href={activeProofShare.public_url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors font-medium inline-flex items-center gap-2"
                        >
                          <ExternalLink className="w-4 h-4" />
                          Open share
                        </a>
                        <button
                          type="button"
                          onClick={() => handleRevokeShare(activeProofShare)}
                          disabled={revokingShareId === activeProofShare.id}
                          className="px-4 py-2 rounded-lg border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors font-medium inline-flex items-center gap-2 disabled:opacity-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          {revokingShareId === activeProofShare.id ? 'Revoking…' : 'Revoke'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      type="button"
                      data-testid="open-proof-share-modal"
                      onClick={openShareModal}
                      disabled={!shareSourcePhoto || loadingProofShares}
                      className="px-5 py-3 bg-gray-900 text-white dark:bg-white dark:text-gray-900 rounded-lg hover:opacity-90 transition-opacity font-medium inline-flex items-center gap-2 disabled:opacity-50"
                    >
                      <Share2 className="w-4 h-4" />
                      Create public proof card
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Compare mode banner */}
          {compareMode && !compareData && (
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 flex items-center gap-3">
              <ArrowLeftRight className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
                  {t('progress.selectToCompare')}
                </p>
                <p className="text-xs text-amber-600 dark:text-amber-500">
                  {t('progress.selected', { count: selectedPhotos.length })}
                </p>
              </div>
              {selectedPhotos.length === 2 && (
                <button
                  onClick={handleCompare}
                  disabled={loadingCompare}
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium text-sm disabled:opacity-50"
                >
                  {loadingCompare ? t('common.loading') : t('progress.compareNow')}
                </button>
              )}
            </div>
          )}

          {/* Compare View */}
          {compareData && (
            <div
              data-testid="progress-compare-surface"
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-white flex items-center gap-2">
                  <ArrowLeftRight className="w-5 h-5 text-emerald-600" />
                  {t('progress.sideByComparison')}
                </h3>
                {compareMode ? (
                  <button
                    onClick={exitCompareMode}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <X className="w-5 h-5" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => setCompareMode(true)}
                    className="text-sm font-medium text-emerald-700 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    Choose photos
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/40">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Elapsed</p>
                  <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">
                    {compareData.days_between != null ? `${compareData.days_between} days` : 'Unknown'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Weight change</p>
                  <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">
                    {compareData.weight_change != null ? `${compareData.weight_change > 0 ? '+' : ''}${compareData.weight_change.toFixed(1)} kg` : 'Not logged'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Body fat change</p>
                  <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">
                    {compareData.bf_change != null ? `${compareData.bf_change > 0 ? '+' : ''}${compareData.bf_change.toFixed(1)}%` : 'Not logged'}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-0.5 bg-gray-200 dark:bg-gray-700">
                {[compareData.before, compareData.after].map((photo, idx) => (
                  <div key={photo.id} className="bg-white dark:bg-gray-800 p-4 space-y-3">
                    <div className="text-center">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        idx === 0
                          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                          : 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
                      }`}>
                        {idx === 0 ? t('progress.before') : t('progress.after')}
                      </span>
                    </div>
                    {getPhotoSrc(photo) && (
                      <div className="relative aspect-[3/4] w-full rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-900">
                        <Image
                          src={getPhotoSrc(photo)!}
                          alt={idx === 0 ? 'Before' : 'After'}
                          fill
                          className="object-cover"
                          unoptimized
                        />
                      </div>
                    )}
                    <div className="text-center space-y-1">
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
                        {formatDate(photo.taken_at)}
                      </p>
                      {photo.weight_kg && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{photo.weight_kg} {t('progress.kg')}</p>
                      )}
                      {photo.body_fat_pct && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{photo.body_fat_pct}{t('progress.bodyFatPct')}</p>
                      )}
                      {photo.notes && (
                        <p className="text-xs text-gray-400 dark:text-gray-500 italic">{photo.notes}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-900/40 border-t border-gray-200 dark:border-gray-700">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Latest scan</p>
                  <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">{latestScanLabel}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{latestScanDateLabel}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Goal / gap-to-goal</p>
                  <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">
                    {homeSummary?.goal_summary.target_bf != null ? `${homeSummary.goal_summary.target_bf.toFixed(1)}% target` : 'No saved target'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{goalGapLabel}</p>
                </div>
                <div className="flex flex-col items-start md:items-end gap-2">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Next recommended action</p>
                    <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">{progressAction.label}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{progressAction.description}</p>
                  </div>
                  <button
                    type="button"
                    onClick={progressAction.onClick}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium inline-flex items-center gap-2"
                  >
                    {progressAction.label}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Photo Grid */}
          {loadingPhotos ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="aspect-[3/4] rounded-xl bg-gray-200 dark:bg-gray-700 animate-pulse" />
              ))}
            </div>
          ) : photos.length === 0 ? (
            <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
              <ImageIcon className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-2">
                {t('progress.noPhotos')}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
                {t('progress.noPhotosHint')}
              </p>
              <button
                onClick={() => openUploadModal('progress_empty_state')}
                className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium inline-flex items-center gap-2"
              >
                <Camera className="w-5 h-5" />
                {t('progress.uploadFirst')}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {photos.map(photo => {
                const isSelected = selectedPhotos.includes(photo.id);
                return (
                  <div
                    key={photo.id}
                    className={`group relative aspect-[3/4] rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 border-2 transition-all cursor-pointer ${
                      isSelected
                        ? 'border-emerald-500 ring-2 ring-emerald-500/30'
                        : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                    onClick={() => compareMode ? togglePhotoSelection(photo.id) : handleViewPhoto(photo)}
                  >
                    {getPhotoSrc(photo) ? (
                      <div className="absolute inset-0">
                        <Image
                          src={getPhotoSrc(photo)!}
                          alt={`Progress photo from ${formatDate(photo.taken_at)}`}
                          fill
                          className="object-cover"
                          unoptimized
                        />
                      </div>
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800">
                        <ImageIcon className="w-10 h-10 text-gray-400 dark:text-gray-500" />
                      </div>
                    )}

                    {/* Compare checkbox */}
                    {compareMode && (
                      <div className={`absolute top-2 right-2 w-6 h-6 rounded-full border-2 flex items-center justify-center z-10 ${
                        isSelected
                          ? 'bg-emerald-500 border-emerald-500 text-white'
                          : 'border-white bg-black/30 text-transparent'
                      }`}>
                        <Check className="w-4 h-4" />
                      </div>
                    )}

                    {/* Overlay info */}
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent p-3 pt-8">
                      <p className="text-white text-sm font-medium">
                        {formatDate(photo.taken_at)}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {photo.weight_kg && (
                          <span className="text-white/80 text-xs">{photo.weight_kg} kg</span>
                        )}
                        {photo.body_fat_pct && (
                          <span className="text-white/80 text-xs">{photo.body_fat_pct}% BF</span>
                        )}
                      </div>
                      {photo.notes && (
                        <p className="text-white/60 text-xs mt-1 truncate">{photo.notes}</p>
                      )}
                    </div>

                    {/* Delete button */}
                    {!compareMode && (
                      <button
                        onClick={e => { e.stopPropagation(); handleDeletePhoto(photo.id); }}
                        disabled={deletingId === photo.id}
                        className="absolute top-2 right-2 p-1.5 rounded-full bg-black/40 text-white/80 opacity-0 group-hover:opacity-100 hover:bg-red-600 hover:text-white transition-all z-10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ==================== UPLOAD MODAL ==================== */}
      <Modal isOpen={showUpload} onClose={resetUploadState} title={t('progress.uploadModal')} size="lg">
        <div data-testid="progress-upload-modal" className="space-y-4">
          {/* File picker */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="relative border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center cursor-pointer hover:border-emerald-400 dark:hover:border-emerald-500 transition-colors"
          >
            {uploadPreview ? (
              <div className="relative aspect-[3/4] max-h-64 mx-auto overflow-hidden rounded-lg">
                <Image
                  src={uploadPreview}
                  alt="Preview"
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
            ) : (
              <div>
                <Camera className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-3" />
                <p className="text-gray-600 dark:text-gray-400 font-medium">
                  {t('progress.clickToSelect')}
                </p>
                <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">
                  {t('progress.photoFormat')}
                </p>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Optional metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('progress.weightKg')}
              </label>
              <input
                type="number"
                step="0.1"
                value={uploadWeight}
                onChange={e => setUploadWeight(e.target.value)}
                placeholder="e.g. 75.5"
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('progress.bodyFat')}
              </label>
              <input
                type="number"
                step="0.1"
                value={uploadBodyFat}
                onChange={e => setUploadBodyFat(e.target.value)}
                placeholder="e.g. 18.5"
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('progress.notes')}
            </label>
            <textarea
              value={uploadNotes}
              onChange={e => setUploadNotes(e.target.value)}
              placeholder={t('progress.notesPlaceholder')}
              rows={2}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
              <button
                data-testid="progress-upload-cancel"
                onClick={resetUploadState}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium"
            >
              {t('common.cancel')}
            </button>
            <button
              data-testid="progress-upload-submit"
              onClick={handleUpload}
              disabled={!uploadFile || uploading}
              className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {t('progress.uploading')}
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  {t('progress.upload')}
                </>
              )}
            </button>
          </div>
        </div>
      </Modal>

      {/* ==================== PUBLIC SHARE MODAL ==================== */}
      <Modal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        title="Create public proof card"
        size="md"
      >
        <div className="space-y-4">
          <div className="rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50/80 dark:bg-emerald-950/30 p-4">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-emerald-700 dark:text-emerald-300 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-200">
                  This is opt-in and revocable
                </p>
                <p className="mt-1 text-sm text-emerald-800/85 dark:text-emerald-300/85">
                  The public card shows one selected proof visual, your goal/gap summary, and an optional week marker.
                  It does not expose the private storage URL.
                </p>
              </div>
            </div>
          </div>

          {shareSourcePhoto && (
            <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Selected proof visual</p>
              <p className="mt-1 text-sm text-gray-900 dark:text-white">{formatDate(shareSourcePhoto.taken_at)}</p>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
                {shareSourcePhoto.weight_kg != null ? `${shareSourcePhoto.weight_kg} kg` : 'No weight logged'}
                {shareSourcePhoto.body_fat_pct != null ? ` · ${shareSourcePhoto.body_fat_pct}% BF` : ''}
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Optional week marker
            </label>
            <input
              data-testid="proof-share-week-marker-input"
              type="number"
              min={1}
              max={52}
              value={shareWeekMarker}
              onChange={event => setShareWeekMarker(event.target.value)}
              placeholder={suggestedWeekMarker ? `Suggested: ${suggestedWeekMarker}` : 'Leave empty'}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => setShowShareModal(false)}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium"
            >
              Cancel
            </button>
            <button
              type="button"
              data-testid="create-proof-share-button"
              onClick={handleCreateShare}
              disabled={!shareSourcePhoto || creatingShare}
              className="px-5 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:opacity-50"
            >
              {creatingShare ? 'Creating…' : 'Create public proof card'}
            </button>
          </div>
        </div>
      </Modal>

      {/* ==================== FULL PHOTO VIEW MODAL ==================== */}
      <Modal
        isOpen={!!viewingPhoto}
        onClose={() => setViewingPhoto(null)}
        title={t('progress.progressPhoto')}
        size="lg"
      >
        {viewingPhoto && (
          <div className="space-y-4">
            {loadingFullPhoto ? (
              <div className="aspect-[3/4] rounded-lg bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
                <div className="w-8 h-8 border-3 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
              </div>
            ) : getPhotoSrc(viewingPhoto) ? (
              <div className="relative aspect-[3/4] w-full rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-900">
                <Image
                  src={getPhotoSrc(viewingPhoto)!}
                  alt="Progress photo"
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
            ) : (
              <div className="aspect-[3/4] rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <ImageIcon className="w-16 h-16 text-gray-400" />
              </div>
            )}

            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formatDate(viewingPhoto.taken_at)}
                </p>
                <div className="flex items-center gap-3 mt-1">
                  {viewingPhoto.weight_kg && (
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {viewingPhoto.weight_kg} {t('progress.kg')}
                    </span>
                  )}
                  {viewingPhoto.body_fat_pct && (
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {viewingPhoto.body_fat_pct}{t('progress.bodyFatPct')}
                    </span>
                  )}
                </div>
                {viewingPhoto.notes && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 italic">
                    {viewingPhoto.notes}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleDeletePhoto(viewingPhoto.id)}
                disabled={deletingId === viewingPhoto.id}
                className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors flex items-center gap-1.5 text-sm font-medium"
              >
                <Trash2 className="w-4 h-4" />
                {t('common.delete')}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Weight Log Modal */}
      <Modal
        isOpen={showWeightLogModal}
        onClose={() => setShowWeightLogModal(false)}
        title={t('progress.logWeight')}
      >
        <WeightLogForm
          onSuccess={handleWeightLogSuccess}
          onCancel={() => setShowWeightLogModal(false)}
        />
      </Modal>

      {/* Goal Setting Modal */}
      <Modal
        isOpen={showGoalModal}
        onClose={() => setShowGoalModal(false)}
        title={t('progress.setGoal')}
      >
        <GoalSettingForm
          onSuccess={handleGoalSuccess}
          onCancel={() => setShowGoalModal(false)}
        />
      </Modal>
    </div>
  );
}

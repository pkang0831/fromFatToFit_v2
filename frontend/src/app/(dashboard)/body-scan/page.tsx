'use client';

import { useState, useRef, ChangeEvent, useEffect, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Scan, Crown, Sparkles, Coins, ArrowRight, Dumbbell, Camera } from 'lucide-react';
import Image from 'next/image';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Input, Select, ProcessingOverlay, SCAN_STEPS, JOURNEY_STEPS } from '@/components/ui';
import { WeeklyRescanPrompt } from '@/components/features/WeeklyRescanPrompt';
import { JourneyResult } from '@/components/features/JourneyResult';
import { BodyCaptureGuide } from '@/components/features/BodyCaptureGuide';
import { BodyScanPoseGuide } from '@/components/features/BodyScanPoseGuide';
import { IDEAL_BODY_SCAN_POSE_IMAGE } from '@/lib/constants/bodyScanGuide';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { bodyApi, paymentApi } from '@/lib/api/services';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { formatApiError } from '@/lib/utils/apiError';
import { getRetentionSessionId, trackEvent, trackRetentionEvent } from '@/lib/analytics';
import { AxiosError } from 'axios';
import dynamic from 'next/dynamic';
import { coerceHomeEntryState } from '@/types/api';
import type { BodyScanRequest, BodyFatEstimateResponse, PercentileResponse, TransformationJourneyResponse, GapToGoalResponse } from '@/types/api';

const BellCurveChart = dynamic(
  () => import('@/components/charts/BellCurveChart').then(m => m.BellCurveChart),
  { loading: () => <div className="h-[200px] bg-surfaceAlt animate-pulse rounded-lg" />, ssr: false }
);

type ActiveTab = 'scan' | 'journey';

export default function BodyScanPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useMemo(() => searchParams ?? new URLSearchParams(), [searchParams]);
  const { user } = useAuth();
  const { t } = useLanguage();
  const { isPremium, refreshLimits } = useSubscription();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const journeyFileInputRef = useRef<HTMLInputElement>(null);

  const [activeTab, setActiveTab] = useState<ActiveTab>('scan');

  // Body Scan state
  const [scanImage, setScanImage] = useState<string | null>(null);
  const [scanFile, setScanFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<{
    bodyfat?: BodyFatEstimateResponse;
    percentile?: PercentileResponse;
  }>({});

  // Journey state
  const [journeyImage, setJourneyImage] = useState<string | null>(null);
  const [journeyFile, setJourneyFile] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [journeyResult, setJourneyResult] = useState<TransformationJourneyResponse | null>(null);

  // Muscle gain inputs
  const [muscleGains, setMuscleGains] = useState({
    arms: 0, chest: 0, back: 0, shoulders: 0, legs: 0, core: 0,
  });

  const [creditBalance, setCreditBalance] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [photoConfirmed, setPhotoConfirmed] = useState(false);
  const [gapData, setGapData] = useState<GapToGoalResponse | null>(null);

  const [showScanGuide, setShowScanGuide] = useState(false);
  const [showJourneyGuide, setShowJourneyGuide] = useState(false);
  const [validatingScan, setValidatingScan] = useState(false);
  const [validatingJourney, setValidatingJourney] = useState(false);
  const [scanQualityOk, setScanQualityOk] = useState<boolean | null>(null);
  const [journeyQualityOk, setJourneyQualityOk] = useState<boolean | null>(null);
  const historyTrackedRef = useRef<{ journey: boolean }>({ journey: false });
  const reminderTrackedRef = useRef(false);

  const reminderSource = params.get('from') || undefined;
  const reminderEventId = params.get('reminder_event_id') || undefined;
  const reminderReentryState = reminderSource === 'weekly_reminder'
    ? coerceHomeEntryState(params.get('reentry_state'), 'weekly_scan')
    : undefined;
  const reminderSurfaceState = reminderSource === 'weekly_reminder'
    ? coerceHomeEntryState(params.get('surface_state'))
    : undefined;

  const scanCost = isPremium ? 0 : 10;
  const journeyCost = 30;

  const [formDefaults, setFormDefaults] = useState({
    gender: '', age: '', height_cm: '', ethnicity: '', weight_kg: '', activity_level: '',
  });

  useEffect(() => {
    if (user) {
      setFormDefaults({
        gender: user.gender ? user.gender.toLowerCase() : '',
        age: user.age ? String(user.age) : '',
        height_cm: user.height_cm ? String(user.height_cm) : '',
        ethnicity: user.ethnicity || '',
        weight_kg: user.weight_kg ? String(user.weight_kg) : '',
        activity_level: user.activity_level || '',
      });
    }
  }, [user]);

  useEffect(() => {
    const syncActiveTab = () => {
      const hash = typeof window !== 'undefined' ? window.location.hash.replace('#', '') : '';
      const requestedTab = params.get('tab') || hash;
      if (requestedTab === 'journey' || requestedTab === 'transformation') {
        setActiveTab('journey');
      } else if (requestedTab === 'scan') {
        setActiveTab('scan');
      }
    };

    syncActiveTab();

    if (typeof window === 'undefined') return;
    const handleHashChange = () => syncActiveTab();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [params]);

  useEffect(() => {
    if (activeTab !== 'journey' || historyTrackedRef.current.journey) return;
    historyTrackedRef.current.journey = true;
    trackRetentionEvent('history_viewed', {
      surface: 'body_scan_page',
      target: 'journey',
    });
  }, [activeTab]);

  useEffect(() => {
    if (reminderTrackedRef.current) return;
    if (params.get('from') !== 'weekly_reminder') return;
    if (activeTab !== 'journey') return;

    reminderTrackedRef.current = true;
    trackRetentionEvent('reengagement_session', {
      surface: 'body_scan_page',
      source: 'weekly_reminder',
      entry_state: reminderReentryState || 'weekly_scan',
      reentry_state: reminderReentryState || 'weekly_scan',
      surface_state: reminderSurfaceState || 'weekly_scan',
      reminder_event_id: reminderEventId,
      session_id: getRetentionSessionId() || undefined,
      target_tab: activeTab,
    });
  }, [params, activeTab, reminderEventId, reminderReentryState, reminderSurfaceState]);

  useEffect(() => {
    if (!journeyResult) return;
    trackEvent('transformation_viewed', {
      surface: 'body_scan',
      mode: journeyResult.mode,
      stage_count: journeyResult.stages.length,
      target_bf: journeyResult.target_bf,
    });
  }, [journeyResult]);

  const updateLocationForTab = (nextTab: ActiveTab) => {
    setActiveTab(nextTab);
    if (typeof window === 'undefined') return;

    const url = new URL(window.location.href);
    url.searchParams.set('tab', nextTab);
    url.hash = nextTab === 'journey' ? 'transformation' : '';
    window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  };

  const fetchCredits = async () => {
    try {
      const res = await paymentApi.getCreditBalance();
      setCreditBalance(res.data.total_credits);
    } catch {
      setCreditBalance(null);
    }
  };

  const fetchGapData = () => {
    bodyApi.getGapToGoal()
      .then(res => setGapData(res.data))
      .catch(() => {});
  };

  useEffect(() => { fetchCredits(); fetchGapData(); }, []);

  const processScanFile = async (file: File): Promise<boolean> => {
    if (!file.type.startsWith('image/')) return false;
    setScanResult({});
    setError(null);
    setScanQualityOk(null);
    setPhotoConfirmed(false);
    setValidatingScan(true);
    trackEvent('photo_upload_started', {
      surface: 'body_scan',
      flow: 'authenticated',
      file_size_bytes: file.size,
    });

    try {
      const base64 = await compressAndConvertToBase64(file);
      const res = await bodyApi.validatePhoto({ image_base64: base64, framing: 'upper_body' });
      setScanQualityOk(res.data.ok);
      if (!res.data.ok) {
        setError(res.data.messages.join(' '));
        trackEvent('photo_upload_failed', {
          surface: 'body_scan',
          flow: 'authenticated',
          reason: res.data.failure_codes.join(',') || 'validation_failed',
        });
        return false;
      }
      setScanFile(file);
      const reader = new FileReader();
      await new Promise<void>((resolve, reject) => {
        reader.onloadend = () => {
          setScanImage(reader.result as string);
          resolve();
        };
        reader.onerror = () => reject(new Error('Failed to read image'));
        reader.readAsDataURL(file);
      });
      trackEvent('photo_upload_succeeded', {
        surface: 'body_scan',
        flow: 'authenticated',
      });
      return true;
    } catch (err) {
      setScanQualityOk(false);
      setError(formatApiError(err));
      trackEvent('photo_upload_failed', {
        surface: 'body_scan',
        flow: 'authenticated',
        reason: err instanceof Error ? err.message : 'unknown_error',
      });
      return false;
    } finally {
      setValidatingScan(false);
    }
  };

  const handleScanFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) void processScanFile(file);
    e.target.value = '';
  };

  const processJourneyFile = async (file: File): Promise<boolean> => {
    if (!file.type.startsWith('image/')) return false;
    setJourneyResult(null);
    setError(null);
    setJourneyQualityOk(null);
    setPhotoConfirmed(false);
    setValidatingJourney(true);
    trackEvent('photo_upload_started', {
      surface: 'transformation_journey',
      flow: 'authenticated',
      file_size_bytes: file.size,
    });

    try {
      const base64 = await compressAndConvertToBase64(file);
      const res = await bodyApi.validatePhoto({ image_base64: base64, framing: 'upper_body' });
      setJourneyQualityOk(res.data.ok);
      if (!res.data.ok) {
        setError(res.data.messages.join(' '));
        trackEvent('photo_upload_failed', {
          surface: 'transformation_journey',
          flow: 'authenticated',
          reason: res.data.failure_codes.join(',') || 'validation_failed',
        });
        return false;
      }
      setJourneyFile(file);
      const reader = new FileReader();
      await new Promise<void>((resolve, reject) => {
        reader.onloadend = () => {
          setJourneyImage(reader.result as string);
          resolve();
        };
        reader.onerror = () => reject(new Error('Failed to read image'));
        reader.readAsDataURL(file);
      });
      trackEvent('photo_upload_succeeded', {
        surface: 'transformation_journey',
        flow: 'authenticated',
      });
      return true;
    } catch (err) {
      setJourneyQualityOk(false);
      setError(formatApiError(err));
      trackEvent('photo_upload_failed', {
        surface: 'transformation_journey',
        flow: 'authenticated',
        reason: err instanceof Error ? err.message : 'unknown_error',
      });
      return false;
    } finally {
      setValidatingJourney(false);
    }
  };

  const handleJourneyFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) void processJourneyFile(file);
    e.target.value = '';
  };

  // Combined body fat + percentile scan
  const handleBodyScan = async (formData: Record<string, FormDataEntryValue>) => {
    if (!scanFile) { setError('No file selected'); return; }
    if (!formData.gender || !formData.age) { setError('Gender and age are required'); return; }

    if (scanCost > 0 && creditBalance !== null && creditBalance < scanCost) {
      setError(`Not enough credits. Scan costs ${scanCost} credits.`);
      return;
    }

    setIsScanning(true);
    setError(null);

    try {
      const base64 = await compressAndConvertToBase64(scanFile);
      const v = await bodyApi.validatePhoto({ image_base64: base64, framing: 'upper_body' });
      if (!v.data.ok) {
        setError(v.data.messages.join(' '));
        setScanQualityOk(false);
        setIsScanning(false);
        return;
      }
      setScanQualityOk(true);

      const requestData: BodyScanRequest = {
        image_base64: base64,
        scan_type: 'percentile',
        source: reminderSource,
        session_id: getRetentionSessionId() || undefined,
        reminder_event_id: reminderEventId,
        reentry_state: reminderReentryState,
        surface_state: reminderSource === 'weekly_reminder'
          ? (reminderSurfaceState || 'weekly_scan')
          : undefined,
        gender: formData.gender as 'male' | 'female',
        age: Number(formData.age),
        ethnicity: (formData.ethnicity as string) || 'Other',
        height_cm: formData.height_cm ? Number(formData.height_cm) : undefined,
        ownership_confirmed: photoConfirmed,
      };

      const response = await bodyApi.calculatePercentile(requestData);
      const percData = response.data as PercentileResponse;

      const newResult: typeof scanResult = { percentile: percData };

      if (percData.percentile_data?.body_fat_percentage) {
        newResult.bodyfat = {
          body_fat_percentage: percData.percentile_data.body_fat_percentage,
          confidence: 'medium',
          recommendations: [],
          scan_id: percData.scan_id,
          usage_remaining: percData.usage_remaining,
        };

        try {
          const prevBf = localStorage.getItem('devenira_current_bodyfat');
          if (prevBf) localStorage.setItem('devenira_prev_bodyfat', prevBf);
          localStorage.setItem('devenira_current_bodyfat', String(percData.percentile_data.body_fat_percentage));
          localStorage.setItem('devenira_last_scan_date', new Date().toISOString());
          const count = parseInt(localStorage.getItem('devenira_scan_count') || '0') + 1;
          localStorage.setItem('devenira_scan_count', String(count));
        } catch {}
      }

      setScanResult(newResult);
      await refreshLimits();
      await fetchCredits();
      fetchGapData();
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail || '';
        if (err.response?.status === 402) {
          setError(`Not enough credits (${scanCost} needed). Buy more or upgrade to Pro.`);
        } else {
          setError(detail || 'Scan failed. Please try again.');
        }
      } else {
        setError(err instanceof Error ? err.message : 'Scan failed');
      }
    } finally {
      setIsScanning(false);
    }
  };

  // Transformation journey
  const handleGenerateJourney = async (formData: Record<string, FormDataEntryValue>) => {
    if (!journeyFile) { setError('No file selected'); return; }
    if (!formData.gender) { setError('Gender is required'); return; }
    if (!formData.target_bf) { setError('Target body fat % is required'); return; }

    if (creditBalance !== null && creditBalance < journeyCost) {
      setError(`Not enough credits. Journey costs ${journeyCost} credits.`);
      return;
    }

    setIsGenerating(true);
    setError(null);
    trackEvent('transformation_generation_started', {
      surface: 'body_scan',
      target_bf: Number(formData.target_bf),
      credit_cost: journeyCost,
    });

    try {
      const base64 = await compressAndConvertToBase64(journeyFile);
      const v = await bodyApi.validatePhoto({ image_base64: base64, framing: 'upper_body' });
      if (!v.data.ok) {
        setError(v.data.messages.join(' '));
        setJourneyQualityOk(false);
        setIsGenerating(false);
        return;
      }
      setJourneyQualityOk(true);

      const requestData: BodyScanRequest = {
        image_base64: base64,
        scan_type: 'transformation',
        source: reminderSource,
        session_id: getRetentionSessionId() || undefined,
        reminder_event_id: reminderEventId,
        reentry_state: reminderReentryState,
        surface_state: reminderSource === 'weekly_reminder'
          ? (reminderSurfaceState || 'weekly_scan')
          : undefined,
        gender: formData.gender as 'male' | 'female',
        age: formData.age ? Number(formData.age) : undefined,
        target_bf: Number(formData.target_bf),
        weight_kg: formData.weight_kg ? Number(formData.weight_kg) : undefined,
        height_cm: formData.height_cm ? Number(formData.height_cm) : undefined,
        activity_level: (formData.activity_level as string) || undefined,
        muscle_gains: muscleGains,
        ownership_confirmed: photoConfirmed,
      };

      const response = await bodyApi.generateTransformation(requestData);
      setJourneyResult(response.data);
      trackEvent('transformation_generated', {
        surface: 'body_scan',
        mode: response.data.mode,
        stage_count: response.data.stages.length,
        target_bf: response.data.target_bf,
      });

      fetchGapData();
      await refreshLimits();
      await fetchCredits();
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        if (err.response?.status === 402) {
          setError('Not enough credits for journey generation.');
        } else {
          setError(formatApiError(err));
        }
        trackEvent('transformation_failed', {
          surface: 'body_scan',
          status: err.response?.status ?? 0,
          reason: formatApiError(err),
        });
      } else {
        setError(err instanceof Error ? err.message : 'Journey generation failed');
        trackEvent('transformation_failed', {
          surface: 'body_scan',
          reason: err instanceof Error ? err.message : 'unknown_error',
        });
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const canScan = scanCost === 0 || (creditBalance !== null && creditBalance >= scanCost);
  const canJourney = creditBalance !== null && creditBalance >= journeyCost;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <WeeklyRescanPrompt variant="full" />

      {/* Tab Navigation */}
      <div className="flex gap-2">
        <button
          onClick={() => updateLocationForTab('scan')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            activeTab === 'scan'
              ? 'bg-gradient-primary text-white shadow-glow-cyan'
              : 'bg-surface border border-border text-text-secondary hover:bg-surfaceAlt'
          }`}
        >
          <Scan className="h-5 w-5" />
          Body Scan
          {scanCost === 0 && (
            <Badge variant="success" className="text-[10px] ml-1">Free</Badge>
          )}
        </button>
        <button
          onClick={() => updateLocationForTab('journey')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            activeTab === 'journey'
              ? 'bg-gradient-primary text-white shadow-glow-cyan'
              : 'bg-surface border border-border text-text-secondary hover:bg-surfaceAlt'
          }`}
        >
          <Sparkles className="h-5 w-5" />
          Transformation Journey
          <Badge variant="info" className="text-[10px] ml-1">{journeyCost} cr</Badge>
        </button>
      </div>

      {/* Credit Balance */}
      <div className="flex items-center gap-3 p-3 bg-surface border border-border rounded-xl">
        <Coins className="h-5 w-5 text-amber-500" />
        <span className="text-sm text-text-secondary">Credits:</span>
        <span className="font-bold text-text">{creditBalance ?? '—'}</span>
        <Button variant="secondary" size="sm" onClick={() => router.push('/upgrade')} className="ml-auto text-xs">
          {isPremium ? 'Buy More' : 'Upgrade'}
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-error/10 border border-error rounded-lg">
          <p className="text-sm text-error">{error}</p>
        </div>
      )}

      {/* ==================== BODY SCAN TAB ==================== */}
      {activeTab === 'scan' && (
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-text">Body Scan</h1>
            <p className="text-text-secondary mt-1">
              AI body fat estimate + percentile ranking in one scan
            </p>
          </div>

          <Card variant="elevated">
            <CardContent className="p-6">
              {!scanImage ? (
                <div>
                  {validatingScan ? (
                    <div className="flex flex-col items-center justify-center py-16">
                      <div className="w-16 h-16 rounded-full border-[3px] border-border border-t-primary animate-spin mb-6" />
                      <p className="text-base font-medium text-text">Checking framing and pose…</p>
                      <p className="text-sm text-text-light mt-2">This may take a moment</p>
                    </div>
                  ) : (
                    <>
                      <BodyScanPoseGuide variant="light" className="mb-4" />
                      <input ref={fileInputRef} type="file" accept="image/*" onChange={handleScanFileSelect} className="hidden" />
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-border rounded-xl p-12 text-center cursor-pointer hover:border-primary transition-colors"
                      >
                        <Scan className="h-16 w-16 text-text-light mx-auto mb-4" />
                        <p className="text-lg font-medium text-text mb-2">Upload a full-body photo</p>
                        <p className="text-sm text-text-secondary">Get your body fat estimate and see where you rank</p>
                      </div>
                      <Button
                        type="button"
                        variant="secondary"
                        className="w-full mt-4"
                        onClick={() => setShowScanGuide(true)}
                      >
                        <Camera className="h-4 w-4 mr-2" />
                        Use camera with guide
                      </Button>
                    </>
                  )}
                </div>
              ) : !scanResult.percentile ? (
                <div className="space-y-6">
                  {isScanning ? (
                    <ProcessingOverlay active={isScanning} steps={SCAN_STEPS} />
                  ) : (
                    <>
                      <Image src={scanImage} alt="Selected" width={800} height={600} className="w-full max-h-80 object-contain rounded-lg" unoptimized />
                      {validatingScan && (
                        <p className="text-sm text-text-secondary">Checking framing and pose…</p>
                      )}
                      <form
                        key={JSON.stringify(formDefaults)}
                        onSubmit={(e) => {
                          e.preventDefault();
                          handleBodyScan(Object.fromEntries(new FormData(e.currentTarget)));
                        }}
                        className="space-y-4"
                      >
                        <div className="grid grid-cols-2 gap-4">
                          <Select name="gender" label="Gender" required defaultValue={formDefaults.gender}>
                            <option value="">Select...</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                          </Select>
                          <Input name="age" label="Age" type="number" placeholder="30" defaultValue={formDefaults.age} required />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <Select name="ethnicity" label="Ethnicity" defaultValue={formDefaults.ethnicity || 'Other'}>
                            <option value="Asian">Asian</option>
                            <option value="Caucasian">Caucasian</option>
                            <option value="African">African</option>
                            <option value="Hispanic">Hispanic</option>
                            <option value="Other">Other</option>
                          </Select>
                          <Input name="height_cm" label="Height (cm)" type="number" placeholder="170" defaultValue={formDefaults.height_cm} />
                        </div>

                        <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                          <div className="flex items-start gap-3">
                            <input type="checkbox" id="scanConfirm" checked={photoConfirmed} onChange={(e) => setPhotoConfirmed(e.target.checked)} className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer" />
                            <label htmlFor="scanConfirm" className="text-xs text-amber-800 dark:text-amber-200 cursor-pointer">
                              I confirm this is my photo or I have permission to upload it. Results are AI approximations, not medical assessments.
                            </label>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          variant="primary"
                          size="lg"
                          disabled={!canScan || !photoConfirmed || scanQualityOk !== true || validatingScan}
                          className="w-full"
                        >
                          <Scan className="h-5 w-5 mr-2" />
                          {scanCost === 0 ? 'Scan (Pro: Free)' : `Scan (${scanCost} credits)`}
                        </Button>
                      </form>
                    </>
                  )}
                </div>
              ) : (
                /* Combined Result: Body Fat + Percentile */
                <div className="space-y-8">
                  {/* Body Fat Result */}
                  {scanResult.bodyfat && (
                    <div className="text-center">
                      <p className="text-sm text-text-secondary mb-1">Estimated Body Fat</p>
                      <p className="text-6xl font-bold text-primary mb-2">
                        {scanResult.bodyfat.body_fat_percentage.toFixed(1)}%
                      </p>
                      <Badge variant={scanResult.bodyfat.confidence === 'high' ? 'success' : scanResult.bodyfat.confidence === 'medium' ? 'warning' : 'error'}>
                        {scanResult.bodyfat.confidence} confidence
                      </Badge>
                    </div>
                  )}

                  {/* Percentile Ranking */}
                  {scanResult.percentile?.percentile_data && (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-primary/10 rounded-xl border border-primary/20">
                          <p className="text-sm text-text-secondary mb-1">Your Ranking</p>
                          <p className="text-3xl font-bold text-primary">
                            Top {(100 - scanResult.percentile.percentile_data.percentile).toFixed(0)}%
                          </p>
                          <p className="text-sm text-primary/80">{scanResult.percentile.percentile_data.rank_text}</p>
                        </div>
                        <div className="text-center p-4 bg-surfaceAlt rounded-xl border border-border">
                          <p className="text-sm text-text-secondary mb-1">Comparison Group</p>
                          <p className="text-lg font-semibold text-text">{scanResult.percentile.percentile_data.comparison_group}</p>
                        </div>
                      </div>

                      {scanResult.percentile.distribution_data && (
                        <BellCurveChart
                          mean={scanResult.percentile.distribution_data.mean}
                          std={scanResult.percentile.distribution_data.std}
                          userValue={scanResult.percentile.distribution_data.user_value}
                          percentile={scanResult.percentile.distribution_data.better_than_percent || scanResult.percentile.percentile_data.percentile}
                          unit="%"
                        />
                      )}
                    </>
                  )}

                  {/* Side-by-side: Current vs Goal (if goal exists) */}
                  {gapData?.goal_image_url && scanResult.bodyfat && (
                    <div className="pt-6 border-t border-border">
                      <h3 className="font-semibold text-text mb-4 text-center">Your Scan vs Your Goal</h3>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-xs text-text-secondary mb-2">Current ({scanResult.bodyfat.body_fat_percentage.toFixed(1)}%)</p>
                          <Image src={scanImage!} alt="Current" width={400} height={300} className="w-full rounded-lg border border-border" unoptimized />
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-primary mb-2">Goal ({gapData.target_bf?.toFixed(1)}%)</p>
                          <Image src={gapData.goal_image_url} alt="Goal" width={400} height={300} className="w-full rounded-lg border-2 border-primary/30" unoptimized />
                        </div>
                      </div>
                      {gapData.gap != null && (
                        <div className="text-center p-4 bg-primary/10 rounded-xl border border-primary/20">
                          <p className="text-sm text-text-secondary">Gap to Goal</p>
                          <p className="text-3xl font-bold text-primary">{gapData.gap.toFixed(1)}% to go</p>
                          {gapData.scan_history.length >= 2 && (() => {
                            const prev = gapData.scan_history[gapData.scan_history.length - 2].bf;
                            const curr = gapData.current_bf!;
                            const weekDelta = prev - curr;
                            return weekDelta > 0 ? (
                              <p className="text-sm text-emerald-400 mt-1">-{weekDelta.toFixed(1)}% since last scan</p>
                            ) : null;
                          })()}
                        </div>
                      )}
                    </div>
                  )}

                  {/* CTA: Go to Journey (if no goal yet) */}
                  {!gapData?.goal_image_url && (
                    <div className="text-center pt-4">
                      <p className="text-sm text-text-secondary mb-3">Ready to see your goal physique?</p>
                      <Button variant="primary" onClick={() => updateLocationForTab('journey')}>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Start Your Transformation Journey
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </div>
                  )}

                  <div className="rounded-xl border border-emerald-200 bg-emerald-50/80 p-5 text-left">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-700">Next step</p>
                        <h3 className="text-lg font-semibold text-emerald-950">Lock this scan with a proof photo</h3>
                        <p className="text-sm text-emerald-800/80">
                          Your scan is the estimate. The proof photo is what you will compare against next week.
                        </p>
                      </div>
                      <Button
                        data-testid="scan-to-proof-cta"
                        variant="primary"
                        onClick={() => router.push('/progress?tab=photos&focus=upload&from=scan_result')}
                      >
                        Upload progress proof
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </div>
                  </div>

                  {/* New Scan button */}
                  <div className="text-center">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setScanImage(null);
                        setScanFile(null);
                        setScanResult({});
                        setPhotoConfirmed(false);
                        setScanQualityOk(null);
                        setError(null);
                      }}
                    >
                      New Scan
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ==================== TRANSFORMATION JOURNEY TAB ==================== */}
      {activeTab === 'journey' && (
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-text">Transformation Journey</h1>
            <p className="text-text-secondary mt-1">
              Set your goal, see the AI preview, and get a 10-step plan to get there
            </p>
          </div>

          <Card variant="elevated">
            <CardContent className="p-6">
              {!journeyImage ? (
                <div>
                  {validatingJourney ? (
                    <div className="flex flex-col items-center justify-center py-16">
                      <div className="w-16 h-16 rounded-full border-[3px] border-border border-t-primary animate-spin mb-6" />
                      <p className="text-base font-medium text-text">Checking framing and pose…</p>
                      <p className="text-sm text-text-light mt-2">This may take a moment</p>
                    </div>
                  ) : (
                    <>
                      <BodyScanPoseGuide variant="light" className="mb-4" />
                      <input ref={journeyFileInputRef} type="file" accept="image/*" onChange={handleJourneyFileSelect} className="hidden" />
                      <div
                        onClick={() => journeyFileInputRef.current?.click()}
                        className="border-2 border-dashed border-border rounded-xl p-12 text-center cursor-pointer hover:border-primary transition-colors"
                      >
                        <Sparkles className="h-16 w-16 text-text-light mx-auto mb-4" />
                        <p className="text-lg font-medium text-text mb-2">Upload your current body photo</p>
                        <p className="text-sm text-text-secondary">We&apos;ll generate your transformation journey</p>
                      </div>
                      <Button
                        type="button"
                        variant="secondary"
                        className="w-full mt-4"
                        onClick={() => setShowJourneyGuide(true)}
                      >
                        <Camera className="h-4 w-4 mr-2" />
                        Use camera with guide
                      </Button>
                    </>
                  )}
                </div>
              ) : !journeyResult ? (
                <div className="space-y-6">
                  {isGenerating ? (
                    <ProcessingOverlay active={isGenerating} steps={JOURNEY_STEPS} />
                  ) : (
                    <>
                      <Image src={journeyImage} alt="Current" width={800} height={600} className="w-full max-h-64 object-contain rounded-lg" unoptimized />
                      {validatingJourney && (
                        <p className="text-sm text-text-secondary">Checking framing and pose…</p>
                      )}

                      <form
                        key={JSON.stringify(formDefaults)}
                        onSubmit={(e) => {
                          e.preventDefault();
                          handleGenerateJourney(Object.fromEntries(new FormData(e.currentTarget)));
                        }}
                        className="space-y-6"
                      >
                        <div className="grid grid-cols-2 gap-4">
                          <Select name="gender" label="Gender" required defaultValue={formDefaults.gender}>
                            <option value="">Select...</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                          </Select>
                          <Input name="age" label="Age" type="number" placeholder="30" defaultValue={formDefaults.age} />
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                          <Input name="weight_kg" label="Weight (kg)" type="number" step="0.1" min="30" max="300" placeholder="75" defaultValue={formDefaults.weight_kg} />
                          <Input name="height_cm" label="Height (cm)" type="number" step="1" min="120" max="250" placeholder="175" defaultValue={formDefaults.height_cm} />
                          <Select name="activity_level" label="Activity" defaultValue={formDefaults.activity_level || 'moderate'}>
                            <option value="sedentary">Sedentary</option>
                            <option value="light">Light</option>
                            <option value="moderate">Moderate</option>
                            <option value="active">Active</option>
                            <option value="very_active">Very Active</option>
                          </Select>
                        </div>

                        {/* Goal Settings */}
                        <div className="p-4 bg-surfaceAlt rounded-xl border border-border space-y-4">
                          <h3 className="font-semibold text-text flex items-center gap-2">
                            <Dumbbell className="h-5 w-5 text-primary" />
                            Your Goal
                          </h3>
                          <Input
                            name="target_bf"
                            label="Target Body Fat %"
                            type="number"
                            step="0.5"
                            min="3"
                            max="45"
                            placeholder="12"
                            required
                          />

                          {/* Muscle Gain per Body Part */}
                          <div>
                            <p className="text-sm font-medium text-text mb-3">Muscle Gain by Area (kg)</p>
                            <div className="grid grid-cols-3 gap-3">
                              {Object.entries(muscleGains).map(([part, val]) => (
                                <div key={part}>
                                  <label className="text-xs text-text-secondary capitalize">{part}</label>
                                  <input
                                    type="number"
                                    step="0.5"
                                    min="0"
                                    max="10"
                                    value={val}
                                    onChange={(e) => setMuscleGains(prev => ({ ...prev, [part]: parseFloat(e.target.value) || 0 }))}
                                    className="w-full mt-1 px-3 py-2 bg-surface border border-border rounded-lg text-text text-sm"
                                  />
                                </div>
                              ))}
                            </div>
                            <p className="text-xs text-text-light mt-2">
                              Total: +{Object.values(muscleGains).reduce((a, b) => a + b, 0).toFixed(1)}kg muscle
                            </p>
                          </div>
                        </div>

                        <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                          <div className="flex items-start gap-3">
                            <input type="checkbox" id="journeyConfirm" checked={photoConfirmed} onChange={(e) => setPhotoConfirmed(e.target.checked)} className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer" />
                            <label htmlFor="journeyConfirm" className="text-xs text-amber-800 dark:text-amber-200 cursor-pointer">
                              I confirm this is my photo or I have permission to upload it. AI previews are visualizations, not predictions or guarantees.
                            </label>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          variant="primary"
                          size="lg"
                          disabled={!canJourney || !photoConfirmed || journeyQualityOk !== true || validatingJourney}
                          className="w-full"
                        >
                          <Sparkles className="h-5 w-5 mr-2" />
                          Generate My Journey ({journeyCost} credits)
                        </Button>

                        {!canJourney && (
                          <Button type="button" variant="secondary" onClick={() => router.push('/upgrade')} className="w-full">
                            <Coins className="h-5 w-5 mr-2" />
                            Get Credits
                          </Button>
                        )}
                      </form>
                    </>
                  )}
                </div>
              ) : (
                <JourneyResult
                  result={journeyResult}
                  originalImage={journeyImage}
                  journeyPrefill={{
                    weightKg: formDefaults.weight_kg,
                    age: formDefaults.age,
                    heightCm: formDefaults.height_cm,
                    activityLevel: formDefaults.activity_level || 'moderate',
                    gender: formDefaults.gender === 'male' || formDefaults.gender === 'female' ? formDefaults.gender : undefined,
                  }}
                  onReset={() => {
                    setJourneyImage(null);
                    setJourneyFile(null);
                    setJourneyResult(null);
                    setPhotoConfirmed(false);
                    setJourneyQualityOk(null);
                    setError(null);
                  }}
                />
              )}
            </CardContent>
          </Card>
        </div>
      )}

      <BodyCaptureGuide
        open={showScanGuide}
        onClose={() => setShowScanGuide(false)}
        onCapture={processScanFile}
        guideImageSrc={IDEAL_BODY_SCAN_POSE_IMAGE}
        validationMessage={showScanGuide ? error : null}
      />
      <BodyCaptureGuide
        open={showJourneyGuide}
        onClose={() => setShowJourneyGuide(false)}
        onCapture={processJourneyFile}
        guideImageSrc={IDEAL_BODY_SCAN_POSE_IMAGE}
        validationMessage={showJourneyGuide ? error : null}
      />
    </div>
  );
}

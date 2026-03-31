'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Timer, Play, Square, History, Flame, Clock, Trophy } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { useLanguage } from '@/contexts/LanguageContext';
import { fastingApi } from '@/lib/api/services';

interface FastingProtocol {
  id: string;
  name: string;
  fastHours: number;
  eatHours: number;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface ActiveSession {
  id: string;
  protocol: string;
  started_at: string;
  target_hours: number;
  elapsed_hours: number;
  remaining_hours: number;
  progress_percent: number;
  completed: boolean;
}

interface HistorySession {
  id: string;
  protocol: string;
  started_at: string;
  ended_at?: string;
  target_hours: number;
  actual_hours?: number;
  completed?: boolean;
}

const PROTOCOLS: FastingProtocol[] = [
  { id: '16:8', name: '16:8', fastHours: 16, eatHours: 8, description: 'Most popular. Skip breakfast, eat lunch to dinner.', difficulty: 'beginner' },
  { id: '18:6', name: '18:6', fastHours: 18, eatHours: 6, description: 'Extended fast. Eat within a 6-hour window.', difficulty: 'intermediate' },
  { id: '20:4', name: '20:4 (Warrior)', fastHours: 20, eatHours: 4, description: 'Warrior Diet. One large meal + snacks.', difficulty: 'advanced' },
  { id: '14:10', name: '14:10', fastHours: 14, eatHours: 10, description: 'Gentle start. Great for beginners.', difficulty: 'beginner' },
  { id: 'omad', name: 'OMAD (23:1)', fastHours: 23, eatHours: 1, description: 'One Meal A Day. Maximum autophagy benefits.', difficulty: 'advanced' },
  { id: 'custom', name: 'Custom', fastHours: 0, eatHours: 0, description: 'Set your own fasting duration.', difficulty: 'beginner' },
];

function formatDuration(ms: number): { hours: number; minutes: number; seconds: number } {
  const totalSec = Math.max(0, Math.floor(ms / 1000));
  return {
    hours: Math.floor(totalSec / 3600),
    minutes: Math.floor((totalSec % 3600) / 60),
    seconds: totalSec % 60,
  };
}

function ProgressRing({ progress, size = 200 }: { progress: number; size?: number }) {
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.min(Math.max(progress, 0), 1);
  const offset = circumference * (1 - clamped);

  const themeColor = typeof document !== 'undefined'
    ? getComputedStyle(document.documentElement).getPropertyValue('--color-primary-hex').trim() || '#06b6d4'
    : '#06b6d4';
  const color = clamped >= 1 ? '#22c55e' : clamped >= 0.75 ? '#f59e0b' : themeColor;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle cx={size / 2} cy={size / 2} r={radius}
        fill="none" stroke="var(--color-border)" strokeWidth={stroke} />
      <circle cx={size / 2} cy={size / 2} r={radius}
        fill="none" stroke={color} strokeWidth={stroke}
        strokeDasharray={circumference} strokeDashoffset={offset}
        strokeLinecap="round"
        className="transition-all duration-1000 ease-linear" />
    </svg>
  );
}

const PROTOCOL_KEY_MAP: Record<string, string> = {
  '16:8': '16_8', '18:6': '18_6', '20:4': '20_4',
  '14:10': '14_10', 'omad': 'OMAD', 'custom': 'Custom',
};

export default function FastingPage() {
  const { t } = useLanguage();
  const [activeFast, setActiveFast] = useState<ActiveSession | null>(null);
  const [fastHistory, setFastHistory] = useState<HistorySession[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const [showProtocols, setShowProtocols] = useState(false);
  const [customHours, setCustomHours] = useState(16);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [curRes, histRes] = await Promise.all([
        fastingApi.getCurrent(),
        fastingApi.getHistory(30),
      ]);
      if (curRes.data.active && curRes.data.session) {
        setActiveFast(curRes.data.session as ActiveSession);
      } else {
        setActiveFast(null);
      }
      setFastHistory((histRes.data.sessions || []) as HistorySession[]);
    } catch {
      toast.error('Failed to load fasting data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    if (!activeFast) return;
    const tick = () => {
      const now = Date.now();
      const start = new Date(activeFast.started_at).getTime();
      setElapsed(now - start);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [activeFast]);

  const startFast = useCallback(async (protocol: FastingProtocol) => {
    const hours = protocol.id === 'custom' ? customHours : protocol.fastHours;
    setActionLoading(true);
    try {
      await fastingApi.startFast(protocol.id, hours);
      setShowProtocols(false);
      toast.success(`Started ${protocol.name} fast`);
      await loadData();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to start fast');
    } finally {
      setActionLoading(false);
    }
  }, [customHours, loadData]);

  const endFast = useCallback(async () => {
    setActionLoading(true);
    try {
      const res = await fastingApi.endFast();
      toast.success(res.data.message || 'Fast ended');
      await loadData();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to end fast');
    } finally {
      setActionLoading(false);
    }
  }, [loadData]);

  const targetMs = activeFast ? activeFast.target_hours * 3600000 : 1;
  const progress = activeFast ? Math.min(elapsed / targetMs, 1) : 0;
  const { hours: elH, minutes: elM, seconds: elS } = formatDuration(elapsed);
  const remaining = activeFast ? Math.max(0, targetMs - elapsed) : 0;
  const { hours: remH, minutes: remM, seconds: remS } = formatDuration(remaining);

  const stats = useMemo(() => {
    const completed = fastHistory.filter(f => f.completed);
    const totalFasts = fastHistory.length;
    if (totalFasts === 0) return { totalFasts: 0, avgHours: 0, longestHours: 0, completedCount: 0 };

    const durations = fastHistory
      .filter(f => f.actual_hours != null)
      .map(f => f.actual_hours!);

    return {
      totalFasts,
      avgHours: durations.length ? Math.round((durations.reduce((a, b) => a + b, 0) / durations.length) * 10) / 10 : 0,
      longestHours: durations.length ? Math.round(Math.max(...durations) * 10) / 10 : 0,
      completedCount: completed.length,
    };
  }, [fastHistory]);

  if (loading) return <div className="max-w-4xl mx-auto py-16 text-center text-text-secondary text-sm">Loading…</div>;

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-text">{t('fasting.title')}</h1>
        <p className="text-text-secondary mt-1">{t('fasting.subtitle')}</p>
      </div>

      {activeFast ? (
        <Card variant="elevated" className="overflow-hidden">
          <div className="bg-gradient-to-br from-primary/10 to-secondary/10 p-8">
            <div className="flex flex-col items-center">
              <div className="relative">
                <ProgressRing progress={progress} size={220} />
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-xs text-text-secondary uppercase tracking-wider">
                    {progress >= 1 ? t('fasting.completed') : t('fasting.elapsed')}
                  </span>
                  <span className="text-4xl font-bold text-text tabular-nums">
                    {String(elH).padStart(2, '0')}:{String(elM).padStart(2, '0')}
                  </span>
                  <span className="text-lg text-text-secondary tabular-nums">
                    :{String(elS).padStart(2, '0')}
                  </span>
                </div>
              </div>

              <div className="mt-6 text-center">
                <Badge variant={progress >= 1 ? 'success' : 'warning'} className="text-sm px-4 py-1.5 mb-3">
                  {activeFast.protocol} &middot; {activeFast.target_hours}h {t('fasting.target')}
                </Badge>

                {progress < 1 && (
                  <p className="text-text-secondary text-sm">
                    {t('fasting.remainingTime', { hours: remH, minutes: remM, seconds: remS })}
                  </p>
                )}
                {progress >= 1 && (
                  <p className="text-green-500 font-semibold text-sm">
                    {t('fasting.reachedGoal')}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-3 gap-6 mt-6 w-full max-w-sm">
                <div className="text-center">
                  <p className="text-xs text-text-secondary">{t('fasting.started')}</p>
                  <p className="text-sm font-semibold text-text">
                    {new Date(activeFast.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-text-secondary">{t('fasting.progressLabel')}</p>
                  <p className="text-sm font-semibold text-text">
                    {Math.round(progress * 100)}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-text-secondary">{t('fasting.goalLabel')}</p>
                  <p className="text-sm font-semibold text-text">
                    {new Date(new Date(activeFast.started_at).getTime() + activeFast.target_hours * 3600000)
                      .toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>

              <Button
                variant="danger"
                className="mt-8"
                onClick={endFast}
                disabled={actionLoading}
                isLoading={actionLoading}
              >
                <Square className="h-4 w-4 mr-2" />
                {t('fasting.endFast')}
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        <Card variant="elevated">
          <CardContent className="p-8 text-center">
            {!showProtocols ? (
              <div className="space-y-6">
                <div className="mx-auto w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                  <Timer className="h-10 w-10 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-text">{t('fasting.readyToFast')}</h2>
                  <p className="text-text-secondary mt-2">{t('fasting.chooseProtocol')}</p>
                </div>
                <Button variant="primary" size="lg" onClick={() => setShowProtocols(true)}>
                  <Play className="h-5 w-5 mr-2" />
                  {t('fasting.startAFast')}
                </Button>
              </div>
            ) : (
              <div className="space-y-4 text-left">
                <h3 className="text-lg font-bold text-text text-center">{t('fasting.chooseProtocolTitle')}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {PROTOCOLS.map(p => (
                    <button
                      key={p.id}
                      onClick={() => p.id !== 'custom' ? startFast(p) : undefined}
                      disabled={actionLoading}
                      className="p-4 rounded-xl border-2 border-border hover:border-primary transition-all text-left hover:shadow-md group disabled:opacity-50"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-text group-hover:text-primary transition-colors">
                          {t(`fasting.protocol${PROTOCOL_KEY_MAP[p.id]}`)}
                        </span>
                        <Badge variant={
                          p.difficulty === 'beginner' ? 'success' :
                          p.difficulty === 'intermediate' ? 'warning' : 'error'
                        } className="text-xs">
                          {p.difficulty}
                        </Badge>
                      </div>
                      <p className="text-xs text-text-secondary">{t(`fasting.protocol${PROTOCOL_KEY_MAP[p.id]}Desc`)}</p>
                      {p.id === 'custom' && (
                        <div className="mt-2 flex items-center gap-2" onClick={e => e.stopPropagation()}>
                          <input
                            type="number"
                            min={1}
                            max={72}
                            value={customHours}
                            onChange={e => setCustomHours(Math.max(1, Math.min(72, parseInt(e.target.value) || 1)))}
                            className="w-20 px-2 py-1 rounded border border-border bg-surface text-text text-sm"
                          />
                          <span className="text-xs text-text-secondary">{t('fasting.hours')}</span>
                          <Button size="sm" variant="primary" onClick={() => startFast(p)} className="ml-auto" disabled={actionLoading}>
                            {t('fasting.go')}
                          </Button>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
                <div className="text-center pt-2">
                  <Button variant="outline" size="sm" onClick={() => setShowProtocols(false)}>
                    {t('common.cancel')}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Trophy className="h-5 w-5 text-primary mx-auto mb-1" />
            <p className="text-2xl font-bold text-text">{stats.totalFasts}</p>
            <p className="text-xs text-text-secondary">{t('fasting.totalFasts')}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="h-5 w-5 text-blue-500 mx-auto mb-1" />
            <p className="text-2xl font-bold text-text">{stats.avgHours}h</p>
            <p className="text-xs text-text-secondary">{t('fasting.avgDuration')}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <Flame className="h-5 w-5 text-orange-500 mx-auto mb-1" />
            <p className="text-2xl font-bold text-text">{stats.longestHours}h</p>
            <p className="text-xs text-text-secondary">{t('fasting.longestFast')}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <Timer className="h-5 w-5 text-green-500 mx-auto mb-1" />
            <p className="text-2xl font-bold text-text">{stats.completedCount}</p>
            <p className="text-xs text-text-secondary">{t('fasting.completedCount')}</p>
          </CardContent>
        </Card>
      </div>

      {/* History */}
      {fastHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              {t('fasting.fastingHistory')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {fastHistory.slice(0, 10).map(session => {
                const start = new Date(session.started_at);
                const durationH = session.actual_hours != null
                  ? Math.round(session.actual_hours * 10) / 10
                  : session.ended_at
                    ? Math.round((new Date(session.ended_at).getTime() - start.getTime()) / 3600000 * 10) / 10
                    : 0;
                const hitGoal = session.completed || durationH >= session.target_hours;

                return (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-surfaceAlt transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${hitGoal ? 'bg-green-500' : 'bg-orange-500'}`} />
                      <div>
                        <p className="text-sm font-semibold text-text">{session.protocol}</p>
                        <p className="text-xs text-text-secondary">
                          {start.toLocaleDateString()} &middot; {start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-text">{durationH}h</p>
                      <p className="text-xs text-text-secondary">/ {session.target_hours}h {t('fasting.ofGoal')}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

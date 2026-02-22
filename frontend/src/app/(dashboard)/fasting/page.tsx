'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Timer, Play, Square, History, TrendingUp, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { fastingApi } from '@/lib/api/services';
import toast from 'react-hot-toast';

interface FastingSession {
  id: string;
  protocol: string;
  target_hours: number;
  started_at: string;
  ended_at: string | null;
  actual_hours: number | null;
  completed: boolean;
  notes: string | null;
  elapsed_hours?: number;
  remaining_hours?: number;
  progress_percent?: number;
}

interface CurrentFastResponse {
  active: boolean;
  session: FastingSession | null;
}

interface HistoryResponse {
  sessions: FastingSession[];
  total: number;
  completed: number;
  completion_rate: number;
}

type Presets = Record<string, { fast_hours: number; eat_hours: number; description?: string }>;

const PROTOCOL_META: Record<string, { label: string; description: string; color: string }> = {
  '16:8': { label: '16:8', description: '16h fast, 8h eating window', color: 'from-violet-500 to-purple-600' },
  '18:6': { label: '18:6', description: '18h fast, 6h eating window', color: 'from-blue-500 to-indigo-600' },
  '20:4': { label: '20:4', description: '20h fast, 4h eating window', color: 'from-emerald-500 to-teal-600' },
  '14:10': { label: '14:10', description: '14h fast, 10h eating window', color: 'from-amber-500 to-orange-600' },
  'omad': { label: 'OMAD', description: 'One meal a day (23h fast)', color: 'from-rose-500 to-pink-600' },
};

function formatDuration(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = Math.floor(totalSeconds % 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function formatRelativeDate(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const days = Math.floor(diff / 86400000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  return d.toLocaleDateString();
}

export default function FastingPage() {
  const [currentFast, setCurrentFast] = useState<CurrentFastResponse | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [presets, setPresets] = useState<Presets | null>(null);
  const [selectedProtocol, setSelectedProtocol] = useState('16:8');
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [ending, setEnding] = useState(false);
  const [liveElapsed, setLiveElapsed] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [currentRes, historyRes, presetsRes] = await Promise.all([
        fastingApi.getCurrent(),
        fastingApi.getHistory(30),
        fastingApi.getPresets(),
      ]);
      setCurrentFast(currentRes.data);
      setHistory(historyRes.data);
      setPresets(presetsRes.data);
    } catch {
      toast.error('Failed to load fasting data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (currentFast?.active && currentFast.session) {
      const started = new Date(currentFast.session.started_at).getTime();
      const tick = () => {
        setLiveElapsed((Date.now() - started) / 1000);
      };
      tick();
      intervalRef.current = setInterval(tick, 1000);
      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    } else {
      setLiveElapsed(0);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentFast?.active, currentFast?.session?.started_at]);

  const handleStart = async () => {
    setStarting(true);
    try {
      const preset = presets?.[selectedProtocol];
      await fastingApi.startFast(selectedProtocol, preset?.fast_hours);
      toast.success(`Started ${selectedProtocol} fast!`);
      await fetchData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start fast';
      toast.error(msg);
    } finally {
      setStarting(false);
    }
  };

  const handleEnd = async () => {
    setEnding(true);
    try {
      const res = await fastingApi.endFast();
      toast.success(res.data.message || 'Fast ended');
      await fetchData();
    } catch {
      toast.error('Failed to end fast');
    } finally {
      setEnding(false);
    }
  };

  const targetSeconds = (currentFast?.session?.target_hours ?? 16) * 3600;
  const progress = Math.min((liveElapsed / targetSeconds) * 100, 100);
  const circumference = 2 * Math.PI * 80;
  const strokeOffset = circumference * (1 - progress / 100);
  const isCompleted = liveElapsed >= targetSeconds;

  const avgDuration =
    history && history.sessions.length > 0
      ? history.sessions
          .filter((s) => s.actual_hours != null)
          .reduce((sum, s) => sum + (s.actual_hours ?? 0), 0) /
        (history.sessions.filter((s) => s.actual_hours != null).length || 1)
      : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-violet-100 dark:bg-violet-900/30">
          <Timer className="h-6 w-6 text-violet-600 dark:text-violet-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Intermittent Fasting</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Track your fasting windows</p>
        </div>
      </div>

      {/* Active Fast Card */}
      {currentFast?.active && currentFast.session ? (
        <div
          data-tour="fasting-timer"
          className="relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-6 md:p-8 shadow-lg"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-violet-500/10 to-transparent rounded-bl-full pointer-events-none" />

          <div className="flex flex-col items-center gap-6">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500" />
              </span>
              {isCompleted ? 'Goal Reached!' : 'Fasting'}
            </span>

            {/* Progress Ring */}
            <div className="relative">
              <svg className="w-48 h-48 transform -rotate-90">
                <circle
                  cx="96" cy="96" r="80"
                  stroke="currentColor"
                  className="text-gray-200 dark:text-gray-700"
                  strokeWidth="8" fill="none"
                />
                <circle
                  cx="96" cy="96" r="80"
                  stroke="url(#gradient)"
                  strokeWidth="8" fill="none"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeOffset}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#6d28d9" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-mono font-bold text-gray-900 dark:text-white">
                  {formatDuration(liveElapsed)}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  of {currentFast.session.target_hours}h goal
                </span>
              </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-4 w-full max-w-sm text-center">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Protocol</p>
                <p className="font-semibold text-gray-900 dark:text-white">{currentFast.session.protocol.toUpperCase()}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Progress</p>
                <p className="font-semibold text-violet-600 dark:text-violet-400">{progress.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Remaining</p>
                <p className="font-semibold text-gray-900 dark:text-white">
                  {isCompleted ? 'Done!' : formatDuration(Math.max(0, targetSeconds - liveElapsed))}
                </p>
              </div>
            </div>

            <button
              onClick={handleEnd}
              disabled={ending}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-red-500 hover:bg-red-600 text-white font-semibold transition-colors disabled:opacity-50"
            >
              <Square className="h-4 w-4" />
              {ending ? 'Ending...' : 'End Fast'}
            </button>
          </div>
        </div>
      ) : (
        /* Protocol Selector */
        <div data-tour="fasting-timer" className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Choose a Protocol</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(PROTOCOL_META).map(([key, meta]) => (
              <button
                key={key}
                onClick={() => setSelectedProtocol(key)}
                className={`relative p-5 rounded-2xl border-2 transition-all text-left ${
                  selectedProtocol === key
                    ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 shadow-md'
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className={`inline-flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br ${meta.color} mb-3`}>
                  <Clock className="h-5 w-5 text-white" />
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white">{meta.label}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{meta.description}</p>
                {selectedProtocol === key && (
                  <div className="absolute top-3 right-3">
                    <CheckCircle2 className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                  </div>
                )}
              </button>
            ))}
          </div>

          <button
            onClick={handleStart}
            disabled={starting}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-semibold transition-all shadow-lg shadow-violet-500/25 disabled:opacity-50"
          >
            <Play className="h-5 w-5" />
            {starting ? 'Starting...' : `Start ${PROTOCOL_META[selectedProtocol]?.label ?? selectedProtocol} Fast`}
          </button>
        </div>
      )}

      {/* Stats */}
      {history && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Fasts', value: history.total, icon: History, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-100 dark:bg-blue-900/30' },
            { label: 'Completed', value: history.completed, icon: CheckCircle2, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-100 dark:bg-emerald-900/30' },
            { label: 'Completion Rate', value: `${history.completion_rate}%`, icon: TrendingUp, color: 'text-violet-600 dark:text-violet-400', bg: 'bg-violet-100 dark:bg-violet-900/30' },
            { label: 'Avg Duration', value: `${avgDuration.toFixed(1)}h`, icon: Clock, color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-100 dark:bg-amber-900/30' },
          ].map((stat) => (
            <div key={stat.label} className="rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-4">
              <div className={`inline-flex items-center justify-center w-9 h-9 rounded-lg ${stat.bg} mb-2`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* History */}
      {history && history.sessions.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <History className="h-5 w-5 text-gray-400" />
            Recent Sessions
          </h2>
          <div className="space-y-2">
            {history.sessions.slice(0, 10).map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center gap-3">
                  {session.completed ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
                  ) : session.ended_at ? (
                    <XCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                  ) : (
                    <Clock className="h-5 w-5 text-violet-500 animate-pulse flex-shrink-0" />
                  )}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {session.protocol.toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatRelativeDate(session.started_at)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {session.actual_hours != null
                      ? `${session.actual_hours.toFixed(1)}h`
                      : 'In progress'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    / {session.target_hours}h target
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

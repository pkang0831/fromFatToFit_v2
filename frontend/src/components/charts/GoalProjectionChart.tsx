'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart
} from 'recharts';
import { weightApi } from '@/lib/api/services';
import type { GoalProjectionResponse } from '@/types/api';
import { useThemeColors } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';

const GOAL_PROJECTION_CACHE_TTL_MS = 5 * 60 * 1000;

type GoalProjectionCacheEntry = {
  storedAt: number;
  projection: GoalProjectionResponse;
};

interface GoalProjectionChartProps {
  daysHistory?: number;
}

const GoalProjectionChart: React.FC<GoalProjectionChartProps> = ({
  daysHistory = 30
}) => {
  const [projection, setProjection] = useState<GoalProjectionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [targetDeficit, setTargetDeficit] = useState<number | undefined>(undefined);
  const [deficitInput, setDeficitInput] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const initialLoadDone = useRef(false);
  const skipNextTargetFetch = useRef(false);
  const { primary, secondary } = useThemeColors();
  const { user } = useAuth();

  const getCacheKey = (deficit?: number) =>
    `devenira.goalProjection.v1.${user?.id ?? 'anon'}.${daysHistory}.${deficit == null ? 'auto' : deficit}`;

  const readCachedProjection = (deficit?: number) => {
    if (typeof window === 'undefined') return null;
    try {
      const raw = window.sessionStorage.getItem(getCacheKey(deficit));
      if (!raw) return null;
      const parsed = JSON.parse(raw) as GoalProjectionCacheEntry;
      if (!parsed?.storedAt || !parsed?.projection) return null;
      if (Date.now() - parsed.storedAt > GOAL_PROJECTION_CACHE_TTL_MS) return null;
      return parsed.projection;
    } catch {
      return null;
    }
  };

  const writeCachedProjection = (projectionData: GoalProjectionResponse, deficit?: number) => {
    if (typeof window === 'undefined') return;
    try {
      const payload: GoalProjectionCacheEntry = {
        storedAt: Date.now(),
        projection: projectionData,
      };
      window.sessionStorage.setItem(getCacheKey(deficit), JSON.stringify(payload));
    } catch {
      // Cache is best-effort only.
    }
  };

  const getSaneStartingDeficit = (value?: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) return 500;
    if (value >= 300 && value <= 700) return Math.round(value / 50) * 50;
    return 500;
  };

  useEffect(() => {
    const cached = readCachedProjection();
    if (cached) {
      setProjection(cached);
      setLoading(false);

      const initial = getSaneStartingDeficit(cached.target_deficit ?? cached.avg_daily_deficit);
      setDeficitInput(String(initial));
      setTargetDeficit(initial);
      skipNextTargetFetch.current = true;
      initialLoadDone.current = true;
      return;
    }

    fetchProjection();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [daysHistory, user?.id]);

  // Debounced re-fetch when targetDeficit changes (skip initial)
  useEffect(() => {
    if (!initialLoadDone.current) return;
    if (skipNextTargetFetch.current) {
      skipNextTargetFetch.current = false;
      return;
    }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchProjection(targetDeficit);
    }, 500);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetDeficit]);

  const fetchProjection = async (deficit?: number) => {
    try {
      if (initialLoadDone.current) {
        setIsRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      
      const response = await weightApi.getProjection(daysHistory, deficit);
      
      setProjection(response.data);
      writeCachedProjection(response.data, deficit);

      if (!initialLoadDone.current) {
        const initial = getSaneStartingDeficit(response.data.avg_daily_deficit);
        setDeficitInput(String(initial));
        setTargetDeficit(initial);
        skipNextTargetFetch.current = true;
        initialLoadDone.current = true;
      }
    } catch (err: unknown) {
      console.error('Error fetching goal projection:', err);
      setError(err instanceof Error ? err.message : 'Failed to load projection');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleDeficitChange = (value: string) => {
    setDeficitInput(value);
    const num = parseInt(value, 10);
    if (!isNaN(num) && num >= 200 && num <= 1200) {
      setTargetDeficit(num);
    }
  };

  const adjustDeficit = (delta: number) => {
    const current = targetDeficit ?? 500;
    const next = Math.max(200, Math.min(1200, current + delta));
    setDeficitInput(String(next));
    setTargetDeficit(next);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error/[0.06] border border-error/20 rounded-2xl p-6">
        <p className="text-error">{error}</p>
        <button
          onClick={() => fetchProjection()}
          className="mt-4 px-4 py-2 bg-error text-white rounded-xl hover:bg-error/80 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!projection || (projection.historical_data.length === 0 && projection.projection_data.length === 0)) {
    return (
      <div className="bg-white/[0.02] border border-border rounded-2xl p-8 text-center">
        <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-text mb-2">No Weight Data Yet</h3>
        <p className="text-text-secondary text-sm">
          Start logging your weight to see trends and goal projections here.
        </p>
      </div>
    );
  }

  // Build a date-keyed map so both projection lines share the same data points
  const dateMap = new Map<string, {
    actual: number | null;
    movingAvg: number | null;
    projected: number | null;
    actualProjected: number | null;
  }>();

  for (const point of projection.historical_data) {
    dateMap.set(point.date, {
      actual: point.weight_kg,
      movingAvg: point.moving_avg_weight,
      projected: null,
      actualProjected: null,
    });
  }

  // Connect the last historical point to both projection lines
  const lastHistDate = projection.historical_data.length > 0
    ? projection.historical_data[projection.historical_data.length - 1].date
    : null;

  if (lastHistDate && dateMap.has(lastHistDate)) {
    const entry = dateMap.get(lastHistDate)!;
    if (projection.projection_data.length > 0) entry.projected = projection.moving_avg_weight;
    if (projection.actual_projection_data.length > 0) entry.actualProjected = projection.moving_avg_weight;
  }

  for (const point of projection.projection_data) {
    const existing = dateMap.get(point.date);
    if (existing) {
      existing.projected = point.projected_weight;
    } else {
      dateMap.set(point.date, { actual: null, movingAvg: null, projected: point.projected_weight, actualProjected: null });
    }
  }

  for (const point of projection.actual_projection_data) {
    const existing = dateMap.get(point.date);
    if (existing) {
      existing.actualProjected = point.projected_weight;
    } else {
      dateMap.set(point.date, { actual: null, movingAvg: null, projected: null, actualProjected: point.projected_weight });
    }
  }

  const chartData = Array.from(dateMap.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, values]) => ({ date, ...values }));

  const hasActualProjection = projection.actual_projection_data.length > 0;
  const actualPaceLooksNoisy = Math.abs(projection.avg_daily_deficit) > 1200;
  const selectedDeficit = targetDeficit ?? getSaneStartingDeficit(projection.target_deficit ?? projection.avg_daily_deficit);

  const formatDate = (dateStr: string) => {
    // Parse date in local timezone to avoid timezone conversion issues
    const [year, month, day] = dateStr.split('-').map(Number);
    return `${month}/${day}`;
  };

  const formatLongDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const targetWeight = projection.target_weight;
  const goalDateLabel = projection.estimated_goal_date ? formatLongDate(projection.estimated_goal_date) : null;
  const summaryHeadline = projection.estimated_goal_date && targetWeight
    ? `At ${selectedDeficit} kcal/day, you could reach ${targetWeight} kg around ${goalDateLabel}.`
    : projection.message;
  const summarySupport = actualPaceLooksNoisy
    ? 'Recent logging pace looks unusually aggressive or noisy, so use this chart as direction only.'
    : hasActualProjection
      ? `Your recent pace from logged data is about ${projection.avg_daily_deficit.toFixed(0)} kcal/day.`
      : 'This is a directional forecast, not a precise prescription.';
  const chartMin = Math.min(
    ...chartData.flatMap(point => [point.actual, point.movingAvg, point.projected, point.actualProjected].filter((v): v is number => typeof v === 'number'))
  );
  const chartMax = Math.max(
    ...chartData.flatMap(point => [point.actual, point.movingAvg, point.projected, point.actualProjected].filter((v): v is number => typeof v === 'number'))
  );

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-blue-300/80">Today</p>
          <p className="mt-3 text-sm text-text-secondary">Current weight</p>
          <p className="mt-1 text-3xl font-semibold text-blue-300">
            {projection.current_weight} kg
          </p>
          {projection.moving_avg_weight && (
            <p className="mt-2 text-sm text-text-secondary">
              3-day trend: {projection.moving_avg_weight} kg
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300/80">Goal</p>
          <p className="mt-3 text-sm text-text-secondary">Target weight</p>
          <p className="mt-1 text-3xl font-semibold text-emerald-300">
            {targetWeight ? `${targetWeight} kg` : 'Not set'}
          </p>
          {targetWeight && (
            <p className="mt-2 text-sm text-text-secondary">
              {Math.abs(projection.current_weight - targetWeight).toFixed(1)} kg remaining
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-violet-300/80">Pace</p>
          <p className="mt-3 text-sm text-text-secondary">Planned daily deficit</p>
          <div className="mt-2 flex items-center gap-2">
            <button
              onClick={() => adjustDeficit(-100)}
              className="h-8 w-8 rounded-lg border border-white/10 bg-white/5 text-violet-200 transition-colors hover:bg-white/10"
            >
              -
            </button>
            <input
              type="number"
              value={deficitInput}
              onChange={(e) => handleDeficitChange(e.target.value)}
              className="w-24 rounded-lg border border-white/10 bg-surface px-2 py-1 text-center text-xl font-semibold text-violet-200 focus:outline-none focus:ring-2 focus:ring-violet-400/40 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              min={200}
              max={1200}
              step={50}
            />
            <button
              onClick={() => adjustDeficit(100)}
              className="h-8 w-8 rounded-lg border border-white/10 bg-white/5 text-violet-200 transition-colors hover:bg-white/10"
            >
              +
            </button>
            <span className="text-xs text-violet-300/70">kcal/day</span>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {[300, 500, 700].map((preset) => (
              <button
                key={preset}
                onClick={() => {
                  setDeficitInput(String(preset));
                  setTargetDeficit(preset);
                }}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                  targetDeficit === preset
                    ? 'bg-violet-500 text-white'
                    : 'bg-white/5 text-violet-200 hover:bg-white/10'
                }`}
              >
                {preset} kcal
              </button>
            ))}
          </div>
          {isRefreshing && (
            <p className="mt-2 text-xs text-violet-300/80 animate-pulse">Updating projection…</p>
          )}
          <p className="mt-2 text-sm text-text-secondary">
            Your recent pace: {actualPaceLooksNoisy ? 'unusually aggressive / noisy' : `${projection.avg_daily_deficit.toFixed(0)} kcal/day`}
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-orange-300/80">Estimate</p>
          <p className="mt-3 text-sm text-text-secondary">Goal date</p>
          {projection.estimated_days_to_goal ? (
            <>
              <p className="mt-1 text-3xl font-semibold text-orange-300">
                {projection.estimated_days_to_goal} days
              </p>
              {projection.estimated_goal_date && (
                <p className="mt-2 text-sm text-text-secondary">
                  {goalDateLabel}
                </p>
              )}
            </>
          ) : (
            <p className="mt-1 text-sm text-text-secondary">Set a target weight to estimate a goal date</p>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-text-secondary">Read this first</p>
        <h3 className="mt-3 text-2xl font-semibold text-text">
          {summaryHeadline}
        </h3>
        <p className="mt-3 text-sm text-text-secondary">
          {projection.message}
        </p>
        <p className="mt-2 text-sm text-text-secondary">
          {summarySupport}
        </p>
      </div>

      {/* Chart */}
      <div className="bg-surface rounded-2xl p-6 border border-border">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-text">
              Daily weight path to goal
            </h3>
            <p className="mt-1 text-sm text-text-secondary">
              Blue is your logged weight, gray is your 3-day trend, gold is your plan, red is your recent pace, and green is your target.
            </p>
          </div>
          <div className="flex flex-wrap gap-3 text-xs text-text-secondary">
            <span className="inline-flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-blue-500" />
              Logged weight
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="h-0.5 w-5 bg-[var(--color-secondary)]" />
              3-day trend
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="h-0.5 w-5 border-t-2 border-dashed border-amber-400" />
              Your plan
            </span>
            {hasActualProjection && (
              <span className="inline-flex items-center gap-2">
                <span className="h-0.5 w-5 border-t-2 border-dashed border-rose-400" />
                Your recent pace
              </span>
            )}
          </div>
        </div>
        
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              stroke="rgba(255,255,255,0.3)"
              style={{ fontSize: '12px' }}
              axisLine={false}
              tickLine={false}
              minTickGap={28}
            />
            <YAxis
              stroke="rgba(255,255,255,0.3)"
              style={{ fontSize: '12px' }}
              axisLine={false}
              tickLine={false}
              domain={[Math.floor(chartMin - 2), Math.ceil(chartMax + 2)]}
              label={{ value: 'Weight (kg)', angle: -90, position: 'insideLeft', fill: 'rgba(255,255,255,0.3)' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--color-surface, white)',
                border: '1px solid var(--color-border-light, #e5e7eb)',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                color: 'var(--color-text, #1f2937)'
              }}
              formatter={(value: any, name: string) => {
                const labelMap: Record<string, string> = {
                  actual: 'Logged weight',
                  movingAvg: '3-day trend',
                  projected: `Your plan (${deficitInput} kcal/day)`,
                  actualProjected: actualPaceLooksNoisy ? 'Your recent pace (noisy)' : `Your recent pace (${projection.avg_daily_deficit.toFixed(0)} kcal/day)`,
                };
                const label = labelMap[name] || name;
                return [typeof value === 'number' ? `${value.toFixed(1)} kg` : value, label];
              }}
              labelFormatter={(label: string) => {
                // Parse date in local timezone to avoid timezone conversion
                const [year, month, day] = label.split('-').map(Number);
                const date = new Date(year, month - 1, day);
                return date.toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric'
                });
              }}
            />
            
            {/* Target weight reference line */}
            {targetWeight && (
              <ReferenceLine
                y={targetWeight}
                stroke="#10b981"
                strokeDasharray="5 5"
                label={{
                  value: `Target: ${targetWeight}kg`,
                  position: 'right',
                  fill: '#10b981',
                  fontSize: 12
                }}
              />
            )}
            
            {/* Historical actual weight */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#3b82f6"
              strokeWidth={2.5}
              dot={{ fill: '#3b82f6', r: 2 }}
              activeDot={{ r: 4 }}
              name="Logged weight"
              connectNulls
            />
            
            {/* Historical moving average */}
            <Line
              type="monotone"
              dataKey="movingAvg"
              stroke={secondary}
              strokeWidth={2.5}
              dot={false}
              name="3-day trend"
              connectNulls
            />
            
            {/* Projected weight (target deficit) */}
            <Line
              type="monotone"
              dataKey="projected"
              stroke="#f59e0b"
              strokeWidth={2.5}
              strokeDasharray="5 5"
              dot={false}
              activeDot={{ r: 4, fill: '#f59e0b' }}
              name={`Your plan (${deficitInput} kcal/day)`}
              connectNulls
            />
            
            {/* Projected weight (actual deficit) */}
            {hasActualProjection && (
              <Line
                type="monotone"
                dataKey="actualProjected"
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={false}
                activeDot={{ r: 4, fill: '#ef4444' }}
                name={actualPaceLooksNoisy ? 'Your recent pace (noisy)' : `Your recent pace (${projection.avg_daily_deficit.toFixed(0)} kcal/day)`}
                connectNulls
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Body Fat (if available) */}
      {projection.current_body_fat && (
        <div className="bg-surface rounded-2xl p-6 border border-border">
          <h3 className="text-lg font-semibold text-text mb-4">Body Fat %</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-text-secondary">Current</p>
              <p className="text-2xl font-bold text-primary font-number">
                {projection.current_body_fat}%
              </p>
            </div>
            {projection.target_body_fat && (
              <div>
                <p className="text-sm text-text-secondary">Target</p>
                <p className="text-2xl font-bold text-emerald-400 font-number">
                  {projection.target_body_fat}%
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GoalProjectionChart;

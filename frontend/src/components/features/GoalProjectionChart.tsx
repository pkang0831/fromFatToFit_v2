'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart
} from 'recharts';
import { weightApi } from '@/lib/api/services';
import type { GoalProjectionResponse } from '@/types/api';

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

  useEffect(() => {
    fetchProjection();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [daysHistory]);

  // Debounced re-fetch when targetDeficit changes (skip initial)
  useEffect(() => {
    if (!initialLoadDone.current) return;
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

      if (!initialLoadDone.current) {
        const initial = response.data.avg_daily_deficit > 0
          ? Math.round(response.data.avg_daily_deficit)
          : 500;
        setDeficitInput(String(initial));
        setTargetDeficit(initial);
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
    if (!isNaN(num) && num >= 0 && num <= 5000) {
      setTargetDeficit(num);
    }
  };

  const adjustDeficit = (delta: number) => {
    const current = targetDeficit ?? 500;
    const next = Math.max(0, Math.min(5000, current + delta));
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
      <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <p className="text-red-600 dark:text-red-400">{error}</p>
        <button
          onClick={() => fetchProjection()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!projection || (projection.historical_data.length === 0 && projection.projection_data.length === 0)) {
    return (
      <div className="bg-gray-100 dark:bg-gray-700 border border-gray-100 dark:border-gray-700 rounded-xl p-8 text-center">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Weight Data Yet</h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm">
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

  const formatDate = (dateStr: string) => {
    // Parse date in local timezone to avoid timezone conversion issues
    const [year, month, day] = dateStr.split('-').map(Number);
    return `${month}/${day}`;
  };

  const targetWeight = projection.target_weight;

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/30 dark:to-blue-900/20 rounded-lg p-4">
          <p className="text-sm text-blue-600 dark:text-blue-400 font-medium mb-1">Current Weight</p>
          <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
            {projection.current_weight} kg
          </p>
          {projection.moving_avg_weight && (
            <p className="text-xs text-blue-500 mt-1">
              3-Day Avg: {projection.moving_avg_weight} kg
            </p>
          )}
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950/30 dark:to-emerald-900/20 rounded-lg p-4">
          <p className="text-sm text-emerald-600 dark:text-emerald-400 font-medium mb-1">Target Weight</p>
          <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">
            {targetWeight ? `${targetWeight} kg` : 'Not set'}
          </p>
          {targetWeight && (
            <p className="text-xs text-emerald-500 mt-1">
              Remaining: {Math.abs(projection.current_weight - targetWeight).toFixed(1)} kg
            </p>
          )}
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/30 dark:to-purple-900/20 rounded-lg p-4">
          <p className="text-sm text-purple-600 dark:text-purple-400 font-medium mb-1">Target Deficit</p>
          <div className="flex items-center gap-1 mt-1">
            <button
              onClick={() => adjustDeficit(-100)}
              className="w-7 h-7 rounded-md bg-purple-200 hover:bg-purple-300 text-purple-700 font-bold text-sm flex items-center justify-center transition-colors"
            >
              -
            </button>
            <input
              type="number"
              value={deficitInput}
              onChange={(e) => handleDeficitChange(e.target.value)}
              className="w-20 text-center text-lg font-bold text-purple-700 dark:text-purple-300 bg-white/70 dark:bg-gray-800/70 border border-purple-200 dark:border-purple-700 rounded-md px-1 py-0.5 focus:outline-none focus:ring-2 focus:ring-purple-400 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              min={0}
              max={5000}
              step={50}
            />
            <button
              onClick={() => adjustDeficit(100)}
              className="w-7 h-7 rounded-md bg-purple-200 hover:bg-purple-300 text-purple-700 font-bold text-sm flex items-center justify-center transition-colors"
            >
              +
            </button>
            <span className="text-xs text-purple-500 ml-0.5">kcal/day</span>
          </div>
          {isRefreshing && (
            <p className="text-xs text-purple-400 mt-1 animate-pulse">Updating projection...</p>
          )}
          <p className="text-xs text-purple-500 mt-1">
            Actual: {projection.avg_daily_deficit.toFixed(0)} kcal/day
          </p>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/30 dark:to-orange-900/20 rounded-lg p-4">
          <p className="text-sm text-orange-600 dark:text-orange-400 font-medium mb-1">Est. Goal Date</p>
          {projection.estimated_days_to_goal ? (
            <>
              <p className="text-2xl font-bold text-orange-700">
                {projection.estimated_days_to_goal} days
              </p>
              {projection.estimated_goal_date && (
                <p className="text-xs text-orange-500 mt-1">
                  {(() => {
                    const [year, month, day] = projection.estimated_goal_date.split('-').map(Number);
                    const date = new Date(year, month - 1, day);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                  })()}
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-orange-600">Set a target weight to see your goal date</p>
          )}
        </div>
      </div>

      {/* Status Message */}
      <div
        className={`rounded-lg p-4 ${
          projection.on_track
            ? 'bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800'
            : 'bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800'
        }`}
      >
        <p
          className={`font-medium ${
            projection.on_track ? 'text-emerald-700 dark:text-emerald-400' : 'text-amber-700 dark:text-amber-400'
          }`}
        >
          {projection.on_track ? '✓ ' : '⚠ '}
          {projection.message}
        </p>
      </div>

      {/* Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
          Weight Trend & Goal Projection
        </h3>
        
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              label={{ value: 'Weight (kg)', angle: -90, position: 'insideLeft' }}
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
                  actual: 'Actual Weight',
                  movingAvg: '3-Day Avg',
                  projected: `Target Deficit (${deficitInput} kcal)`,
                  actualProjected: `Current Pace (${projection.avg_daily_deficit.toFixed(0)} kcal)`,
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
            <Legend />
            
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
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 3 }}
              name="Actual Weight"
              connectNulls
            />
            
            {/* Historical moving average */}
            <Line
              type="monotone"
              dataKey="movingAvg"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={false}
              name="3-Day Avg"
              connectNulls
            />
            
            {/* Projected weight (target deficit) */}
            <Line
              type="monotone"
              dataKey="projected"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: '#f59e0b', r: 3 }}
              name={`Target Deficit (${deficitInput} kcal)`}
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
                dot={{ fill: '#ef4444', r: 2 }}
                name={`Current Pace (${projection.avg_daily_deficit.toFixed(0)} kcal)`}
                connectNulls
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Body Fat (if available) */}
      {projection.current_body_fat && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Body Fat %</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Current</p>
              <p className="text-2xl font-bold text-blue-600">
                {projection.current_body_fat}%
              </p>
            </div>
            {projection.target_body_fat && (
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Target</p>
                <p className="text-2xl font-bold text-emerald-600">
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

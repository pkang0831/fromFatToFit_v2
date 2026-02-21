'use client';

import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    fetchProjection();
  }, [daysHistory]);

  const fetchProjection = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Add cache busting parameter
      const cacheBuster = Date.now();
      const response = await weightApi.getProjection(daysHistory);
      
      console.log('RAW API Response (cache buster:', cacheBuster, '):', response.data);
      console.log('Historical data from API:', response.data.historical_data);
      
      setProjection(response.data);
    } catch (err: any) {
      console.error('Error fetching goal projection:', err);
      setError(err.message || 'Failed to load projection');
    } finally {
      setLoading(false);
    }
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
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchProjection}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!projection) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">No projection data available</p>
      </div>
    );
  }

  // Combine historical and projection data for the chart
  const historicalData = projection.historical_data.map((point, index) => ({
    date: point.date,
    actual: point.weight_kg,
    movingAvg: point.moving_avg_weight,
    projected: null as number | null,
    type: 'historical' as const
  }));
  
  // For the last historical point, also add projected value to connect lines
  if (historicalData.length > 0 && projection.projection_data.length > 0) {
    historicalData[historicalData.length - 1].projected = projection.moving_avg_weight;
  }
  
  const projectionData = projection.projection_data.map(point => ({
    date: point.date,
    actual: null as number | null,
    movingAvg: null as number | null,
    projected: point.projected_weight,
    type: 'projection' as const
  }));
  
  const chartData = [...historicalData, ...projectionData];
  
  console.log('Chart data:', {
    historicalCount: projection.historical_data.length,
    projectionCount: projection.projection_data.length,
    chartDataCount: chartData.length,
    lastHistorical: chartData[projection.historical_data.length - 1],
    firstProjection: chartData[projection.historical_data.length],
    allHistoricalDates: historicalData.map(d => ({ date: d.date, actual: d.actual })),
    allChartData: chartData.map(d => ({ date: d.date, actual: d.actual, movingAvg: d.movingAvg, projected: d.projected }))
  });

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
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
          <p className="text-sm text-blue-600 font-medium mb-1">Current Weight</p>
          <p className="text-2xl font-bold text-blue-700">
            {projection.current_weight} kg
          </p>
          {projection.moving_avg_weight && (
            <p className="text-xs text-blue-500 mt-1">
              3-Day Avg: {projection.moving_avg_weight} kg
            </p>
          )}
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-4">
          <p className="text-sm text-emerald-600 font-medium mb-1">Target Weight</p>
          <p className="text-2xl font-bold text-emerald-700">
            {targetWeight ? `${targetWeight} kg` : 'Not set'}
          </p>
          {targetWeight && (
            <p className="text-xs text-emerald-500 mt-1">
              Remaining: {Math.abs(projection.current_weight - targetWeight).toFixed(1)} kg
            </p>
          )}
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
          <p className="text-sm text-purple-600 font-medium mb-1">Daily Change</p>
          <p className="text-2xl font-bold text-purple-700">
            {projection.daily_weight_change > 0 ? '+' : ''}
            {projection.daily_weight_change.toFixed(2)} kg/day
          </p>
          {Math.abs(projection.daily_weight_change) > 0.3 && (
            <p className="text-xs text-red-500 mt-1 font-semibold">
              ⚠️ Unrealistic rate
            </p>
          )}
          <p className="text-xs text-purple-500 mt-1">
            Avg Deficit: {projection.avg_daily_deficit.toFixed(0)} kcal/day
          </p>
          {projection.avg_daily_deficit === 0 && (
            <p className="text-xs text-amber-600 mt-1">
              📝 Log your meals and workouts
            </p>
          )}
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
          <p className="text-sm text-orange-600 font-medium mb-1">Est. Goal Date</p>
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
            <p className="text-sm text-orange-600">Calculating...</p>
          )}
        </div>
      </div>

      {/* Status Message */}
      <div
        className={`rounded-lg p-4 ${
          projection.on_track
            ? 'bg-emerald-50 border border-emerald-200'
            : 'bg-amber-50 border border-amber-200'
        }`}
      >
        <p
          className={`font-medium ${
            projection.on_track ? 'text-emerald-700' : 'text-amber-700'
          }`}
        >
          {projection.on_track ? '✓ ' : '⚠ '}
          {projection.message}
        </p>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
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
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
              formatter={(value: any, name: string) => {
                const label = {
                  actual: 'Actual Weight',
                  movingAvg: '3-Day Avg',
                  projected: 'Projected Weight'
                }[name] || name;
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
            
            {/* Projected weight */}
            <Line
              type="monotone"
              dataKey="projected"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: '#f59e0b', r: 3 }}
              name="Projected Weight"
              connectNulls
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Body Fat (if available) */}
      {projection.current_body_fat && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Body Fat %</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Current</p>
              <p className="text-2xl font-bold text-blue-600">
                {projection.current_body_fat}%
              </p>
            </div>
            {projection.target_body_fat && (
              <div>
                <p className="text-sm text-gray-600">Target</p>
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

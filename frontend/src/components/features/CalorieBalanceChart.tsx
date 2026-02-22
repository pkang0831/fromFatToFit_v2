'use client';

import { useState, useEffect } from 'react';
import { 
  AreaChart, 
  Area, 
  Line,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine 
} from 'recharts';
import { dashboardApi } from '@/lib/api/services';
import type { CalorieBalanceTrendPoint, CalorieBalanceTrendResponse } from '@/types/api';
import { Card, CardContent } from '@/components/ui';

interface Props {
  days: number;
}

export function CalorieBalanceChart({ days }: Props) {
  const [data, setData] = useState<CalorieBalanceTrendPoint[]>([]);
  const [summary, setSummary] = useState<CalorieBalanceTrendResponse['summary'] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [days]);

  const loadData = async () => {
    try {
      setLoading(true);
      const response = await dashboardApi.getCalorieBalanceTrend(days);
      setData(response.data.data);
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Failed to load calorie balance trend:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ value: number; name: string; color: string; payload: CalorieBalanceTrendPoint }> }) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const isDeficitPositive = data.deficit > 0;

    return (
      <div className="bg-white dark:bg-gray-800 p-4 shadow-2xl rounded-lg border-2 border-gray-200 dark:border-gray-700">
        <p className="font-bold text-gray-900 dark:text-white mb-3">{formatDate(data.date)}</p>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between gap-4">
            <span className="text-orange-600">🍽️ Intake:</span>
            <span className="font-semibold">{Math.round(data.consumed)} kcal</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-blue-600">🔥 Burned:</span>
            <span className="font-semibold">{Math.round(data.burned)} kcal</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-gray-700 dark:text-gray-300">📊 Net Cal:</span>
            <span className="font-semibold">{Math.round(data.net)} kcal</span>
          </div>
          <div className="border-t pt-2 mt-2">
            <div className="flex items-center justify-between gap-4">
              <span className={isDeficitPositive ? 'text-green-600' : 'text-red-600'}>
                💡 Deficit:
              </span>
              <span className={`font-bold ${isDeficitPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isDeficitPositive ? '+' : ''}{Math.round(data.deficit)} kcal {isDeficitPositive ? '✅' : '⚠️'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        <p>No data available</p>
      </div>
    );
  }

  const avgGoal = data.length > 0 ? data[0].goal : 2000;

  return (
    <div className="space-y-6">
      {/* Chart */}
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="consumedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F97316" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#F97316" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="burnedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '14px', paddingTop: '10px' }}
            formatter={(value) => {
              if (value === 'consumed') return '🍽️ Intake';
              if (value === 'burned') return '🔥 Burned';
              if (value === 'net') return '📊 Net Cal';
              return value;
            }}
          />
          
          {/* Reference line for goal */}
          <ReferenceLine 
            y={avgGoal} 
            stroke="#9CA3AF" 
            strokeDasharray="5 5"
            label={{ value: `Goal: ${avgGoal}`, position: 'right', fill: '#6B7280' }}
          />
          
          {/* Areas */}
          <Area 
            type="monotone" 
            dataKey="consumed" 
            stroke="#F97316" 
            fill="url(#consumedGradient)"
            strokeWidth={2}
          />
          <Area 
            type="monotone" 
            dataKey="burned" 
            stroke="#3B82F6" 
            fill="url(#burnedGradient)"
            strokeWidth={2}
          />
          
          {/* Net line */}
          <Line 
            type="monotone" 
            dataKey="net" 
            stroke="#10B981" 
            strokeWidth={3}
            dot={{ fill: '#10B981', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/30 dark:to-orange-900/20 border-orange-200 dark:border-orange-800">
            <CardContent className="p-4 text-center">
              <div className="text-sm text-orange-700 mb-1">Avg Intake</div>
              <div className="text-3xl font-bold text-orange-600">
                {Math.round(summary.avg_consumed)}
              </div>
              <div className="text-xs text-orange-600 mt-1">kcal/day</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/30 dark:to-blue-900/20 border-blue-200 dark:border-blue-800">
            <CardContent className="p-4 text-center">
              <div className="text-sm text-blue-700 mb-1">Avg Burned</div>
              <div className="text-3xl font-bold text-blue-600">
                {Math.round(summary.avg_burned)}
              </div>
              <div className="text-xs text-blue-600 mt-1">kcal/day</div>
            </CardContent>
          </Card>

          <Card className={`bg-gradient-to-br ${
            summary.avg_deficit > 0 
              ? 'from-green-50 to-green-100 dark:from-green-950/30 dark:to-green-900/20 border-green-200 dark:border-green-800' 
              : 'from-red-50 to-red-100 dark:from-red-950/30 dark:to-red-900/20 border-red-200 dark:border-red-800'
          }`}>
            <CardContent className="p-4 text-center">
              <div className={`text-sm mb-1 ${summary.avg_deficit > 0 ? 'text-green-700' : 'text-red-700'}`}>
                Avg Deficit
              </div>
              <div className={`text-3xl font-bold ${summary.avg_deficit > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {summary.avg_deficit > 0 ? '+' : ''}{Math.round(summary.avg_deficit)}
              </div>
              <div className={`text-xs mt-1 ${summary.avg_deficit > 0 ? 'text-green-600' : 'text-red-600'}`}>
                kcal/day {summary.avg_deficit > 0 ? '✅' : '⚠️'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

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
import type { CalorieBalanceTrendPoint } from '@/types/api';
import { Card, CardContent } from '@/components/ui';

interface Props {
  days: number;
}

export function CalorieBalanceChart({ days }: Props) {
  const [data, setData] = useState<CalorieBalanceTrendPoint[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
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

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const isDeficitPositive = data.deficit > 0;

    return (
      <div className="bg-surface p-4 shadow-2xl rounded-lg border-2 border-border">
        <p className="font-bold text-text mb-3">{formatDate(data.date)}</p>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between gap-4">
            <span className="text-orange-500">Intake:</span>
            <span className="font-semibold text-text">{Math.round(data.consumed)} kcal</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-blue-500">Burned:</span>
            <span className="font-semibold text-text">{Math.round(data.burned)} kcal</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-text-secondary">Net Cal:</span>
            <span className="font-semibold text-text">{Math.round(data.net)} kcal</span>
          </div>
          <div className="border-t border-border pt-2 mt-2">
            <div className="flex items-center justify-between gap-4">
              <span className={isDeficitPositive ? 'text-green-500' : 'text-red-500'}>
                Deficit:
              </span>
              <span className={`font-bold ${isDeficitPositive ? 'text-green-500' : 'text-red-500'}`}>
                {isDeficitPositive ? '+' : ''}{Math.round(data.deficit)} kcal
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
        <div className="h-80 bg-surfaceAlt rounded-lg"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-text-secondary">
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
          margin={{ top: 10, right: 60, left: 0, bottom: 0 }}
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
            label={{ value: `Goal`, position: 'right', fill: '#6B7280', fontSize: 12 }}
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
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/40 dark:to-orange-900/30 border-orange-200 dark:border-orange-800">
            <CardContent className="p-4 text-center">
              <div className="text-sm text-orange-700 dark:text-orange-400 mb-1">Avg Intake</div>
              <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                {Math.round(summary.avg_consumed)}
              </div>
              <div className="text-xs text-orange-600 dark:text-orange-500 mt-1">kcal/day</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/40 dark:to-blue-900/30 border-blue-200 dark:border-blue-800">
            <CardContent className="p-4 text-center">
              <div className="text-sm text-blue-700 dark:text-blue-400 mb-1">Avg Burned</div>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {Math.round(summary.avg_burned)}
              </div>
              <div className="text-xs text-blue-600 dark:text-blue-500 mt-1">kcal/day</div>
            </CardContent>
          </Card>

          <Card className={`bg-gradient-to-br ${
            summary.avg_deficit > 0 
              ? 'from-green-50 to-green-100 dark:from-green-950/40 dark:to-green-900/30 border-green-200 dark:border-green-800' 
              : 'from-red-50 to-red-100 dark:from-red-950/40 dark:to-red-900/30 border-red-200 dark:border-red-800'
          }`}>
            <CardContent className="p-4 text-center">
              <div className={`text-sm mb-1 ${summary.avg_deficit > 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}`}>
                Avg Deficit
              </div>
              <div className={`text-3xl font-bold ${summary.avg_deficit > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {summary.avg_deficit > 0 ? '+' : ''}{Math.round(summary.avg_deficit)}
              </div>
              <div className={`text-xs mt-1 ${summary.avg_deficit > 0 ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500'}`}>
                kcal/day
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

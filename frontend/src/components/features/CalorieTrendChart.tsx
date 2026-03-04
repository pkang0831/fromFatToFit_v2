'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatDateShort } from '@/lib/utils/date';

interface CalorieTrendChartProps {
  data: Array<{ date: string; calories: number; goal: number }>;
  averageCalories: number;
}

export default function CalorieTrendChart({ data, averageCalories }: CalorieTrendChartProps) {
  return (
    <>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EFEBE9" />
          <XAxis
            dataKey="date"
            tickFormatter={(date) => formatDateShort(date)}
            stroke="#6D4C41"
          />
          <YAxis stroke="#6D4C41" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #D7CCC8',
              borderRadius: '0.5rem',
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="calories" stroke="#8B4513" strokeWidth={2} name="Calories" />
          <Line type="monotone" dataKey="goal" stroke="#D2691E" strokeWidth={2} strokeDasharray="5 5" name="Goal" />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-center text-sm text-text-secondary mt-4">
        Average: {Math.round(averageCalories)} calories/day
      </p>
    </>
  );
}

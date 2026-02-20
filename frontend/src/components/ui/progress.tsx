import React from 'react';
import { cn } from '@/lib/utils/cn';

export interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  className,
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  // Auto-select color based on percentage
  let colorClass = 'bg-primary';
  if (percentage >= 90) {
    colorClass = 'bg-red-500';
  } else if (percentage >= 70) {
    colorClass = 'bg-yellow-500';
  } else {
    colorClass = 'bg-green-500';
  }

  return (
    <div className={cn('w-full h-3 bg-gray-200 rounded-full overflow-hidden', className)}>
      <div
        className={cn('h-full rounded-full transition-all duration-300', colorClass)}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

Progress.displayName = 'Progress';

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

  let colorClass = 'bg-primary';
  if (percentage >= 90) {
    colorClass = 'bg-error';
  } else if (percentage >= 70) {
    colorClass = 'bg-warning';
  } else {
    colorClass = 'bg-success';
  }

  return (
    <div className={cn('w-full h-3 bg-black/[0.06] dark:bg-white/[0.06] rounded-full overflow-hidden', className)}>
      <div
        className={cn('h-full rounded-full transition-all duration-500 ease-out', colorClass)}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

Progress.displayName = 'Progress';

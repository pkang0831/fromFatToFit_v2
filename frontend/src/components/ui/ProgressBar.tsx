import React from 'react';
import { cn } from '@/lib/utils/cn';

export interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  className,
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const variants = {
    default: 'bg-primary',
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
  };

  // Auto-select variant based on percentage
  let autoVariant = variant;
  if (variant === 'default') {
    if (percentage >= 90) {
      autoVariant = 'success';
    } else if (percentage >= 70) {
      autoVariant = 'warning';
    } else if (percentage < 50) {
      autoVariant = 'error';
    }
  }

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-text">{label}</span>
          <span className="text-sm text-text-secondary">
            {value} / {max}
          </span>
        </div>
      )}
      <div className={cn('w-full bg-border-light rounded-full overflow-hidden', sizes[size])}>
        <div
          className={cn('h-full rounded-full transition-all duration-300', variants[autoVariant])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

ProgressBar.displayName = 'ProgressBar';

import React from 'react';
import { cn } from '@/lib/utils/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    const variants = {
      primary:
        'bg-gradient-primary text-white hover:shadow-glow-cyan active:scale-[0.97] btn-glow',
      secondary:
        'bg-secondary text-white hover:bg-secondary-light active:scale-[0.97]',
      outline:
        'border-2 border-primary/30 text-primary bg-transparent hover:bg-primary/10 hover:border-primary/50',
      ghost:
        'text-primary hover:bg-primary/10',
      danger:
        'bg-error text-white hover:bg-red-500 active:scale-[0.97]',
    };

    const sizes = {
      sm: 'text-sm px-3.5 py-1.5 rounded-lg',
      md: 'text-sm px-5 py-2.5 rounded-xl',
      lg: 'text-base px-7 py-3 rounded-xl',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'relative font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100',
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <div className="flex items-center justify-center gap-2">
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading...</span>
          </div>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

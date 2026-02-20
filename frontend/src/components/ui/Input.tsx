import React from 'react';
import { cn } from '@/lib/utils/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, type, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text mb-1.5">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <input
          type={type}
          className={cn(
            'flex h-10 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-light focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-error focus:ring-error',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
        {helperText && !error && <p className="mt-1 text-sm text-text-secondary">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text mb-1.5">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <textarea
          className={cn(
            'flex min-h-[80px] w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-light focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-error focus:ring-error',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
        {helperText && !error && <p className="mt-1 text-sm text-text-secondary">{helperText}</p>}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, helperText, children, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text mb-1.5">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <select
          className={cn(
            'flex h-10 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-error focus:ring-error',
            className
          )}
          ref={ref}
          {...props}
        >
          {children}
        </select>
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
        {helperText && !error && <p className="mt-1 text-sm text-text-secondary">{helperText}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';

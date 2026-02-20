import React, { useEffect } from 'react';
import { cn } from '@/lib/utils/cn';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-text/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal content */}
      <div
        className={cn(
          'relative bg-surface rounded-xl shadow-xl w-full mx-4 max-h-[90vh] overflow-y-auto',
          sizes[size]
        )}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-6 border-b border-border-light">
            <h2 className="text-xl font-bold text-text">{title}</h2>
            <button
              onClick={onClose}
              className="text-text-secondary hover:text-text transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        )}

        {/* Body */}
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

Modal.displayName = 'Modal';

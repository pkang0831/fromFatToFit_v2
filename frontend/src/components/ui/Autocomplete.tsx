'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Search, Loader2 } from 'lucide-react';

export interface AutocompleteOption {
  id: string;
  label: string;
  subtitle?: string;
  group?: string;
  data?: Record<string, any>;
}

interface AutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (option: AutocompleteOption) => void;
  options: AutocompleteOption[];
  placeholder?: string;
  label?: string;
  loading?: boolean;
  emptyMessage?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}

export function Autocomplete({
  value,
  onChange,
  onSelect,
  options,
  placeholder = 'Search...',
  label,
  loading = false,
  emptyMessage = 'No results found. Try a different search.',
  error,
  required = false,
  disabled = false,
}: AutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setHighlightedIndex(0);
  }, [options]);

  const handleInputChange = (newValue: string) => {
    onChange(newValue);
    setIsOpen(true);
    setHighlightedIndex(0);
  };

  const handleSelectOption = (option: AutocompleteOption) => {
    onSelect(option);
    onChange(option.label);
    setIsOpen(false);
    inputRef.current?.blur();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && e.key !== 'Enter') {
      setIsOpen(true);
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => 
          prev < options.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (options.length > 0 && highlightedIndex >= 0) {
          handleSelectOption(options[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  const hasTypedEnough = value.length >= 2;
  const showDropdown = isOpen && hasTypedEnough;

  let lastGroup: string | undefined;

  return (
    <div ref={containerRef} className="relative">
      {label && (
        <label className="block text-sm font-medium text-text mb-1">
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={`
            w-full px-4 py-2 pr-10
            border rounded-xl
            bg-surface text-text
            placeholder:text-text-light
            focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all
            ${error ? 'border-error' : 'border-border hover:border-primary/40'}
          `}
        />
        
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          {loading ? (
            <Loader2 className="h-4 w-4 text-primary animate-spin" />
          ) : (
            <Search className="h-4 w-4 text-text-light" />
          )}
        </div>
      </div>

      {error && (
        <p className="mt-1 text-sm text-error">{error}</p>
      )}

      {showDropdown && (
        <div className="absolute z-50 w-full mt-1 bg-surface border border-border rounded-xl shadow-lg max-h-64 overflow-y-auto">
          {loading && options.length === 0 ? (
            <div className="px-4 py-3 text-sm text-text-secondary flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Searching...
            </div>
          ) : options.length === 0 ? (
            <div className="px-4 py-3">
              <p className="text-sm text-text-secondary">{emptyMessage}</p>
              <p className="text-xs text-text-light mt-1">
                You can type a food name and enter calories manually below.
              </p>
            </div>
          ) : (
            options.map((option, index) => {
              const showGroupHeader = option.group && option.group !== lastGroup;
              lastGroup = option.group;

              return (
                <div key={option.id}>
                  {showGroupHeader && (
                    <div className="px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-text-light bg-surfaceAlt border-t border-border">
                      {option.group}
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => handleSelectOption(option)}
                    className={`
                      w-full px-4 py-2.5 text-left
                      hover:bg-primary/10
                      transition-colors
                      ${index === highlightedIndex ? 'bg-primary/10' : ''}
                      ${!showGroupHeader && index !== 0 ? 'border-t border-border' : ''}
                    `}
                    onMouseEnter={() => setHighlightedIndex(index)}
                  >
                    <div className="font-medium text-sm text-text">{option.label}</div>
                    {option.subtitle && (
                      <div className="text-xs text-text-secondary mt-0.5">
                        {option.subtitle}
                      </div>
                    )}
                  </button>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}

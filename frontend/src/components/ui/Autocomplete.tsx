'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { ChevronDown, Search } from 'lucide-react';

export interface AutocompleteOption {
  id: string;
  label: string;
  subtitle?: string;
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
  error,
  required = false,
  disabled = false,
}: AutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset highlighted index when options change
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

  const showDropdown = isOpen && options.length > 0;

  return (
    <div ref={containerRef} className="relative">
      {label && (
        <label className="block text-sm font-medium text-gray-900 dark:text-white mb-1">
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
            border rounded-lg
            bg-white dark:bg-gray-800 text-gray-900 dark:text-white
            placeholder:text-gray-500 dark:text-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all
            ${error ? 'border-error' : 'border-gray-200 dark:border-gray-700 hover:border-primary'}
          `}
        />
        
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          {loading ? (
            <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
          ) : (
            <Search className="h-4 w-4 text-gray-500 dark:text-gray-500" />
          )}
        </div>
      </div>

      {error && (
        <p className="mt-1 text-sm text-error">{error}</p>
      )}

      {/* Dropdown */}
      {showDropdown && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {options.map((option, index) => (
            <button
              key={option.id}
              type="button"
              onClick={() => handleSelectOption(option)}
              className={`
                w-full px-4 py-3 text-left
                hover:bg-gray-100 dark:bg-gray-700
                transition-colors
                ${index === highlightedIndex ? 'bg-gray-100 dark:bg-gray-700' : ''}
                ${index !== 0 ? 'border-t border-gray-100 dark:border-gray-700' : ''}
              `}
              onMouseEnter={() => setHighlightedIndex(index)}
            >
              <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
              {option.subtitle && (
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                  {option.subtitle}
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

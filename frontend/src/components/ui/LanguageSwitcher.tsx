'use client';

import { useState, useRef, useEffect } from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { LANGUAGES, type Locale } from '@/lib/i18n';

interface LanguageSwitcherProps {
  variant?: 'default' | 'compact' | 'footer';
}

export function LanguageSwitcher({ variant = 'default' }: LanguageSwitcherProps) {
  const { locale, setLocale } = useLanguage();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const locales = Object.entries(LANGUAGES) as [Locale, typeof LANGUAGES[Locale]][];

  if (variant === 'compact') {
    return (
      <div ref={ref} className="relative">
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-1.5 px-2 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Change language"
          data-testid="lang-switcher"
        >
          <Globe className="h-4 w-4" />
          <span className="uppercase text-xs font-medium">{locale}</span>
        </button>
        {open && (
          <div className="absolute bottom-full mb-1 left-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1 z-50 min-w-[160px] max-h-[320px] overflow-y-auto">
            {locales.map(([code, lang]) => (
              <button
                key={code}
                onClick={() => { setLocale(code); setOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-between ${
                  code === locale ? 'text-primary font-medium' : 'text-gray-700 dark:text-gray-300'
                }`}
              >
                <span>{lang.nativeName}</span>
                {code === locale && <span className="text-primary">✓</span>}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (variant === 'footer') {
    return (
      <div ref={ref} className="relative inline-block">
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-2 px-3 py-2 text-sm text-white/50 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
          aria-label="Change language"
          data-testid="lang-switcher"
        >
          <Globe className="h-4 w-4" />
          <span>{LANGUAGES[locale].nativeName}</span>
        </button>
        {open && (
          <div className="absolute bottom-full mb-1 left-0 bg-gray-900 border border-gray-700 rounded-lg shadow-lg py-1 z-50 min-w-[160px] max-h-[320px] overflow-y-auto">
            {locales.map(([code, lang]) => (
              <button
                key={code}
                onClick={() => { setLocale(code); setOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-800 transition-colors flex items-center justify-between ${
                  code === locale ? 'text-primary font-medium' : 'text-gray-300'
                }`}
              >
                <span>{lang.nativeName}</span>
                {code === locale && <span className="text-primary">✓</span>}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary/30 transition-colors"
        aria-label="Change language"
        data-testid="lang-switcher"
      >
        <Globe className="h-4 w-4" />
        <span>{LANGUAGES[locale].nativeName}</span>
      </button>
      {open && (
        <div className="absolute top-full mt-1 right-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1 z-50 min-w-[180px] max-h-[400px] overflow-y-auto">
          {locales.map(([code, lang]) => (
            <button
              key={code}
              onClick={() => { setLocale(code); setOpen(false); }}
              className={`w-full text-left px-4 py-2.5 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-between ${
                code === locale ? 'text-primary font-medium bg-primary/5' : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              <span>{lang.nativeName}</span>
              <span className="text-xs text-gray-400 uppercase">{code}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

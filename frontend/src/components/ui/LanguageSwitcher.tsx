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
          className="flex items-center gap-1.5 px-2 py-1.5 text-sm text-text-secondary hover:text-text rounded-lg hover:bg-surfaceAlt transition-colors"
          aria-label="Change language"
          data-testid="lang-switcher"
        >
          <Globe className="h-4 w-4" />
          <span className="uppercase text-xs font-medium">{locale}</span>
        </button>
        {open && (
          <div className="absolute bottom-full mb-1 left-0 bg-surface border border-border rounded-xl shadow-lg py-1 z-50 min-w-[160px] max-h-[320px] overflow-y-auto">
            {locales.map(([code, lang]) => (
              <button
                key={code}
                onClick={() => { setLocale(code); setOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-surfaceAlt transition-colors flex items-center justify-between ${
                  code === locale ? 'text-primary font-medium' : 'text-text-secondary'
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
          <div className="absolute bottom-full mb-1 left-0 bg-[#12121a] border border-white/[0.08] rounded-xl shadow-lg py-1 z-50 min-w-[160px] max-h-[320px] overflow-y-auto">
            {locales.map(([code, lang]) => (
              <button
                key={code}
                onClick={() => { setLocale(code); setOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-white/[0.04] transition-colors flex items-center justify-between ${
                  code === locale ? 'text-primary font-medium' : 'text-white/60'
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
        className="flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text rounded-xl border border-border hover:border-primary/30 transition-colors"
        aria-label="Change language"
        data-testid="lang-switcher"
      >
        <Globe className="h-4 w-4" />
        <span>{LANGUAGES[locale].nativeName}</span>
      </button>
      {open && (
        <div className="absolute top-full mt-1 right-0 bg-surface border border-border rounded-xl shadow-lg py-1 z-50 min-w-[180px] max-h-[400px] overflow-y-auto">
          {locales.map(([code, lang]) => (
            <button
              key={code}
              onClick={() => { setLocale(code); setOpen(false); }}
              className={`w-full text-left px-4 py-2.5 text-sm hover:bg-surfaceAlt transition-colors flex items-center justify-between ${
                code === locale ? 'text-primary font-medium bg-primary/5' : 'text-text-secondary'
              }`}
            >
              <span>{lang.nativeName}</span>
              <span className="text-xs text-text-light uppercase">{code}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

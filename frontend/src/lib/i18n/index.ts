import en from './en.json';
import ko from './ko.json';
import ja from './ja.json';
import zh from './zh.json';
import es from './es.json';
import fr from './fr.json';
import de from './de.json';
import pt from './pt.json';
import hi from './hi.json';
import ar from './ar.json';

export const LANGUAGES = {
  en: { name: 'English', nativeName: 'English', dir: 'ltr' as const },
  ko: { name: 'Korean', nativeName: '한국어', dir: 'ltr' as const },
  ja: { name: 'Japanese', nativeName: '日本語', dir: 'ltr' as const },
  zh: { name: 'Chinese', nativeName: '中文', dir: 'ltr' as const },
  es: { name: 'Spanish', nativeName: 'Español', dir: 'ltr' as const },
  fr: { name: 'French', nativeName: 'Français', dir: 'ltr' as const },
  de: { name: 'German', nativeName: 'Deutsch', dir: 'ltr' as const },
  pt: { name: 'Portuguese', nativeName: 'Português', dir: 'ltr' as const },
  hi: { name: 'Hindi', nativeName: 'हिन्दी', dir: 'ltr' as const },
  ar: { name: 'Arabic', nativeName: 'العربية', dir: 'rtl' as const },
} as const;

export type Locale = keyof typeof LANGUAGES;
export const DEFAULT_LOCALE: Locale = 'en';
export const LOCALE_STORAGE_KEY = 'ftf-locale';

const translations: Record<Locale, typeof en> = { en, ko, ja, zh, es, fr, de, pt, hi, ar };

type NestedKeyOf<T, Prefix extends string = ''> = T extends object
  ? { [K in keyof T & string]: NestedKeyOf<T[K], Prefix extends '' ? K : `${Prefix}.${K}`> }[keyof T & string]
  : Prefix;

export type TranslationKey = NestedKeyOf<typeof en>;

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split('.');
  let current: unknown = obj;
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') return path;
    current = (current as Record<string, unknown>)[key];
  }
  return typeof current === 'string' ? current : path;
}

export function getTranslation(locale: Locale, key: string, params?: Record<string, string | number>): string {
  const dict = translations[locale] || translations[DEFAULT_LOCALE];
  let text = getNestedValue(dict as unknown as Record<string, unknown>, key);

  if (text === key) {
    text = getNestedValue(translations[DEFAULT_LOCALE] as unknown as Record<string, unknown>, key);
  }

  if (params) {
    for (const [param, value] of Object.entries(params)) {
      text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), String(value));
    }
  }

  return text;
}

export function detectBrowserLocale(): Locale {
  if (typeof window === 'undefined') return DEFAULT_LOCALE;

  const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
  if (stored && stored in LANGUAGES) return stored as Locale;

  const browserLang = navigator.language.split('-')[0];
  if (browserLang in LANGUAGES) return browserLang as Locale;

  return DEFAULT_LOCALE;
}

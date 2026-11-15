import { format, parseISO, formatDistance } from 'date-fns';

export function formatDate(date: string | Date, formatStr: string = 'yyyy-MM-dd'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr);
}

export function formatDateShort(date: string | Date): string {
  return formatDate(date, 'MMM d');
}

export function formatDateLong(date: string | Date): string {
  return formatDate(date, 'MMMM d, yyyy');
}

export function getTodayString(): string {
  return format(new Date(), 'yyyy-MM-dd');
}

/**
 * Parse a date string (yyyy-MM-dd) in local timezone
 * Avoids UTC conversion issues
 */
export function parseLocalDate(dateString: string): Date {
  const [year, month, day] = dateString.split('-').map(Number);
  return new Date(year, month - 1, day);
}

/**
 * Format a date string (yyyy-MM-dd) in English locale
 * Uses local timezone to avoid date shift issues
 */
export function formatLocalDate(dateString: string, options?: Intl.DateTimeFormatOptions): string {
  const date = parseLocalDate(dateString);
  return date.toLocaleDateString('en-US', options || {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/** Format date in local locale (alias for formatLocalDate for compatibility) */
export function formatLocalDateKR(dateString: string, options?: Intl.DateTimeFormatOptions): string {
  return formatLocalDate(dateString, options);
}

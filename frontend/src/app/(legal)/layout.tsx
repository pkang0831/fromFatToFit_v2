'use client';

import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary hover:opacity-80 transition-opacity">
            {t('common.appName')}
          </Link>
          <nav className="flex gap-6 text-sm items-center">
            <Link href="/terms" className="text-gray-600 dark:text-gray-400 hover:text-primary transition-colors">
              {t('legal.terms')}
            </Link>
            <Link href="/privacy" className="text-gray-600 dark:text-gray-400 hover:text-primary transition-colors">
              {t('legal.privacy')}
            </Link>
            <Link href="/disclaimer" className="text-gray-600 dark:text-gray-400 hover:text-primary transition-colors">
              {t('legal.disclaimer')}
            </Link>
            <LanguageSwitcher />
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {children}
      </main>

      <footer className="border-t border-gray-200 dark:border-gray-800 py-8 text-center">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          &copy; {new Date().getFullYear()} {t('common.appName')}. {t('legal.allRightsReserved')}
        </p>
      </footer>
    </div>
  );
}

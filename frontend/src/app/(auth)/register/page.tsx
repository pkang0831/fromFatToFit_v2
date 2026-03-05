'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent } from '@/components/ui';
import { SocialLoginButtons } from '@/components/features/SocialLoginButtons';

export default function RegisterPage() {
  const { t } = useLanguage();
  const [error] = useState<string | null>(null);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">{t('common.appName')}</h1>
          <p className="text-gray-600 dark:text-gray-400">{t('auth.createAccount')}</p>
        </div>

        <Card variant="elevated">
          <CardContent>
            <SocialLoginButtons googleTestId="register-google" />

            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600 dark:text-gray-400">{t('auth.hasAccount')} </span>
              <Link href="/login" className="text-primary hover:text-primary-dark font-medium">
                {t('auth.signInLink')}
              </Link>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-error/10 border border-error rounded-lg">
                <p className="text-sm text-error">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

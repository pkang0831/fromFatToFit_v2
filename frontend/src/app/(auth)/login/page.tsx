'use client';

import { useState, FormEvent } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, Button, Input } from '@/components/ui';
import { SocialLoginButtons } from '@/components/features/SocialLoginButtons';

const EMAIL_LOGIN_ENABLED = process.env.NEXT_PUBLIC_ENABLE_EMAIL_LOGIN === 'true';

export default function LoginPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, error, loading } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const displayError = localError || error;

  const handleEmailLogin = async (e: FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    try {
      const user = await login({ email: email.trim(), password });
      const requestedNext = searchParams.get('next');
      const nextPath = requestedNext && requestedNext.startsWith('/') ? requestedNext : '/home';
      router.push(user.onboarding_completed ? nextPath : `/onboarding?next=${encodeURIComponent(nextPath)}`);
    } catch {
      /* error set in context */
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">{t('common.appName')}</h1>
          <p className="text-gray-600 dark:text-gray-400">{t('auth.signInTitle')}</p>
        </div>

        <Card variant="elevated">
          <CardContent className="space-y-6 pt-6">
            <SocialLoginButtons googleTestId="login-google" />

            {EMAIL_LOGIN_ENABLED && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-surface px-2 text-text-secondary">
                      {t('auth.signInWithEmailPassword')}
                    </span>
                  </div>
                </div>

                <form onSubmit={handleEmailLogin} className="space-y-4" data-testid="email-login-form">
                  <div>
                    <label htmlFor="email-login-email" className="block text-sm font-medium text-text mb-1">
                      {t('auth.email')}
                    </label>
                    <Input
                      id="email-login-email"
                      data-testid="email-login-email"
                      type="email"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={loading}
                    />
                  </div>
                  <div>
                    <label htmlFor="email-login-password" className="block text-sm font-medium text-text mb-1">
                      {t('auth.password')}
                    </label>
                    <Input
                      id="email-login-password"
                      data-testid="email-login-password"
                      type="password"
                      autoComplete="current-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      minLength={6}
                      disabled={loading}
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={loading} data-testid="email-login-submit">
                    {loading ? '…' : t('auth.signInButton')}
                  </Button>
                </form>
              </>
            )}

            {displayError && (
              <div className="p-3 bg-error/10 border border-error rounded-lg">
                <p className="text-sm text-error">{displayError}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

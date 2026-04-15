'use client';

import { FormEvent, Suspense, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, Button, Input } from '@/components/ui';
import { SocialLoginButtons } from '@/components/features/SocialLoginButtons';
import { getRetentionSessionId } from '@/lib/analytics';

const EMAIL_LOGIN_ENABLED = process.env.NEXT_PUBLIC_ENABLE_EMAIL_LOGIN === 'true';

function RegisterPageContent() {
  const { t } = useLanguage();
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = searchParams ?? new URLSearchParams();
  const { register, error, loading } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [consent, setConsent] = useState({
    terms: false,
    privacy: false,
    sensitiveData: false,
    age: false,
  });
  const nextPath = params.get('next');
  const attributionSource = params.get('source') || params.get('ref') || undefined;
  const attributionToken = params.get('share_token') || params.get('share') || undefined;
  const attributionSessionId = params.get('session_id') || getRetentionSessionId() || undefined;
  const loginHref = nextPath && nextPath.startsWith('/')
    ? `/login?next=${encodeURIComponent(nextPath)}`
    : '/login';
  const safeNextPath = nextPath && nextPath.startsWith('/') ? nextPath : '/home';
  const displayError = localError || error;

  const handleEmailRegister = async (e: FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (password.length < 8) {
      setLocalError('Password must be at least 8 characters.');
      return;
    }

    if (password !== confirmPassword) {
      setLocalError('Passwords do not match.');
      return;
    }

    if (!consent.terms || !consent.privacy || !consent.sensitiveData || !consent.age) {
      setLocalError('You must accept all required agreements to create an account.');
      return;
    }

    try {
      await register({
        email: email.trim(),
        password,
        full_name: fullName.trim() || undefined,
        attribution_source: attributionSource,
        attribution_token: attributionToken,
        attribution_session_id: attributionSessionId,
        consent_terms: consent.terms,
        consent_privacy: consent.privacy,
        consent_sensitive_data: consent.sensitiveData,
        consent_age_verification: consent.age,
      });
      router.push(`/onboarding?next=${encodeURIComponent(safeNextPath)}`);
    } catch {
      /* error surfaced via context */
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">{t('common.appName')}</h1>
          <p className="text-gray-600 dark:text-gray-400">{t('auth.createAccount')}</p>
        </div>

        <Card variant="elevated">
          <CardContent className="space-y-6 pt-6">
            <SocialLoginButtons googleTestId="register-google" />

            {EMAIL_LOGIN_ENABLED && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-surface px-2 text-text-secondary">
                      Create an account with email
                    </span>
                  </div>
                </div>

                <form onSubmit={handleEmailRegister} className="space-y-4" data-testid="email-register-form">
                  <div>
                    <label htmlFor="register-full-name" className="block text-sm font-medium text-text mb-1">
                      Full Name
                    </label>
                    <Input
                      id="register-full-name"
                      data-testid="email-register-name"
                      type="text"
                      autoComplete="name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      disabled={loading}
                    />
                  </div>

                  <div>
                    <label htmlFor="register-email" className="block text-sm font-medium text-text mb-1">
                      {t('auth.email')}
                    </label>
                    <Input
                      id="register-email"
                      data-testid="email-register-email"
                      type="email"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={loading}
                    />
                  </div>

                  <div>
                    <label htmlFor="register-password" className="block text-sm font-medium text-text mb-1">
                      {t('auth.password')}
                    </label>
                    <Input
                      id="register-password"
                      data-testid="email-register-password"
                      type="password"
                      autoComplete="new-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      minLength={8}
                      disabled={loading}
                    />
                  </div>

                  <div>
                    <label htmlFor="register-confirm-password" className="block text-sm font-medium text-text mb-1">
                      Confirm Password
                    </label>
                    <Input
                      id="register-confirm-password"
                      data-testid="email-register-password-confirm"
                      type="password"
                      autoComplete="new-password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      minLength={8}
                      disabled={loading}
                    />
                  </div>

                  <div className="space-y-3 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-text-secondary">
                    <label className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={consent.terms && consent.privacy && consent.sensitiveData && consent.age}
                        onChange={(e) => {
                          const checked = e.target.checked;
                          setConsent({ terms: checked, privacy: checked, sensitiveData: checked, age: checked });
                        }}
                        className="mt-1 h-4 w-4 rounded border-border"
                      />
                      <span>Agree to all required terms</span>
                    </label>
                    <label className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={consent.terms}
                        onChange={(e) => setConsent((prev) => ({ ...prev, terms: e.target.checked }))}
                        className="mt-1 h-4 w-4 rounded border-border"
                      />
                      <span>I agree to the <Link href="/terms" target="_blank" className="text-primary hover:underline">Terms</Link> and <Link href="/disclaimer" target="_blank" className="text-primary hover:underline">Disclaimer</Link>.</span>
                    </label>
                    <label className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={consent.privacy}
                        onChange={(e) => setConsent((prev) => ({ ...prev, privacy: e.target.checked }))}
                        className="mt-1 h-4 w-4 rounded border-border"
                      />
                      <span>I agree to the <Link href="/privacy" target="_blank" className="text-primary hover:underline">Privacy Policy</Link>.</span>
                    </label>
                    <label className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={consent.sensitiveData}
                        onChange={(e) => setConsent((prev) => ({ ...prev, sensitiveData: e.target.checked }))}
                        className="mt-1 h-4 w-4 rounded border-border"
                      />
                      <span>I consent to processing sensitive body image data for analysis and progress tracking.</span>
                    </label>
                    <label className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={consent.age}
                        onChange={(e) => setConsent((prev) => ({ ...prev, age: e.target.checked }))}
                        className="mt-1 h-4 w-4 rounded border-border"
                      />
                      <span>I confirm that I am 18 or older.</span>
                    </label>
                  </div>

                  <Button type="submit" className="w-full" disabled={loading} data-testid="email-register-submit">
                    {loading ? '…' : 'Create account'}
                  </Button>
                </form>
              </>
            )}

            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600 dark:text-gray-400">{t('auth.hasAccount')} </span>
              <Link href={loginHref} className="text-primary hover:text-primary-dark font-medium">
                {t('auth.signInLink')}
              </Link>
            </div>

            {displayError && (
              <div className="mt-4 p-3 bg-error/10 border border-error rounded-lg">
                <p className="text-sm text-error">{displayError}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50 dark:bg-gray-950" />}>
      <RegisterPageContent />
    </Suspense>
  );
}

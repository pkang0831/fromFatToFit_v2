'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button, Input, Card, CardContent, Select } from '@/components/ui';
import { SocialLoginButtons } from '@/components/features/SocialLoginButtons';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const { t } = useLanguage();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Consent label fragments (keep <a> links, inject translated text around them)
  const termsLink = t('auth.consent.termsLink');
  const disclaimerLink = t('auth.consent.disclaimerLink');
  const termsFull = t('auth.consent.terms', { terms: termsLink, disclaimer: disclaimerLink });
  const termsParts = termsFull.split(termsLink);
  const termsBetween = termsParts[1]?.split(disclaimerLink) ?? ['', ''];
  const privacyLink = t('auth.consent.privacyLink');
  const privacyFull = t('auth.consent.privacy', { privacy: privacyLink });
  const privacyParts = privacyFull.split(privacyLink);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const confirmPassword = formData.get('confirmPassword') as string;
    const full_name = formData.get('full_name') as string;
    const ethnicity = formData.get('ethnicity') as string;
    const gender = formData.get('gender') as string;
    const age = formData.get('age') as string;
    const height_cm = formData.get('height_cm') as string;
    const weight_kg = formData.get('weight_kg') as string;
    const activity_level = formData.get('activity_level') as string;

    // Validation
    if (password.length < 8) {
      setError(t('auth.passwordMin'));
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError(t('auth.passwordMismatch'));
      setIsLoading(false);
      return;
    }

    const agreeTerms = formData.get('agreeTerms') === 'on';
    const agreePrivacy = formData.get('agreePrivacy') === 'on';
    const agreeSensitiveData = formData.get('agreeSensitiveData') === 'on';
    const agreeAge = formData.get('agreeAge') === 'on';

    if (!agreeTerms || !agreePrivacy || !agreeSensitiveData || !agreeAge) {
      setError('Please accept all required agreements to continue');
      setIsLoading(false);
      return;
    }

    if (age && Number(age) < 18) {
      setError('You must be at least 18 years old to use this service');
      setIsLoading(false);
      return;
    }

    try {
      await register({ 
        email, 
        password,
        full_name: full_name || undefined,
        ethnicity: ethnicity || undefined,
        gender: (gender as 'male' | 'female') || undefined,
        age: age ? Number(age) : undefined,
        height_cm: height_cm ? Number(height_cm) : undefined,
        weight_kg: weight_kg ? Number(weight_kg) : undefined,
        activity_level: activity_level || undefined,
        consent_terms: agreeTerms,
        consent_privacy: agreePrivacy,
        consent_sensitive_data: agreeSensitiveData,
        consent_age_verification: agreeAge,
      });
      // Use window.location to ensure cookies are sent with the next request
      window.location.href = '/home';
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      setIsLoading(false);
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
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                type="text"
                name="full_name"
                label={t('auth.fullName')}
                placeholder="John Doe"
                helperText={t('common.optional')}
                autoComplete="name"
              />

              <Input
                type="email"
                name="email"
                label={t('auth.email')}
                placeholder="you@example.com"
                required
                autoComplete="email"
                data-testid="register-email"
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select name="gender" label={t('auth.gender')} required>
                  <option value="">{t('auth.select')}</option>
                  <option value="male">{t('auth.male')}</option>
                  <option value="female">{t('auth.female')}</option>
                </Select>
                <Input
                  type="number"
                  name="age"
                  label={t('auth.age')}
                  placeholder="30"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="number"
                  name="height_cm"
                  label={t('auth.height')}
                  placeholder="170"
                  required
                />
                <Input
                  type="number"
                  name="weight_kg"
                  label={t('auth.weight')}
                  placeholder="70"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select name="ethnicity" label={t('auth.ethnicity')} required>
                  <option value="">{t('auth.select')}</option>
                  <option value="Asian">{t('auth.ethnicity_options.asian')}</option>
                  <option value="Caucasian">{t('auth.ethnicity_options.caucasian')}</option>
                  <option value="African">{t('auth.ethnicity_options.african')}</option>
                  <option value="Hispanic">{t('auth.ethnicity_options.hispanic')}</option>
                  <option value="Middle Eastern">{t('auth.ethnicity_options.middleEastern')}</option>
                  <option value="Pacific Islander">{t('auth.ethnicity_options.pacificIslander')}</option>
                  <option value="Mixed">{t('auth.ethnicity_options.mixed')}</option>
                  <option value="Other">{t('auth.ethnicity_options.other')}</option>
                </Select>
                <Select name="activity_level" label={t('auth.activityLevel')}>
                  <option value="sedentary">{t('auth.sedentary')}</option>
                  <option value="light">{t('auth.light')}</option>
                  <option value="moderate" selected>{t('auth.moderate')}</option>
                  <option value="active">{t('auth.active')}</option>
                  <option value="athlete">{t('auth.athlete')}</option>
                </Select>
              </div>

              <Input
                type="password"
                name="password"
                label={t('auth.password')}
                placeholder="••••••••"
                required
                helperText={t('auth.passwordMin')}
                autoComplete="new-password"
                data-testid="register-password"
              />

              <Input
                type="password"
                name="confirmPassword"
                label={t('auth.confirmPassword')}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />

              <div className="space-y-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">{t('auth.consent.title')}</p>

                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    name="agreeTerms"
                    id="agreeTerms"
                    required
                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                    data-testid="consent-terms"
                  />
                  <label htmlFor="agreeTerms" className="text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                    {termsParts[0]}
                    <a href="/terms" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-medium">{termsLink}</a>
                    {termsBetween[0]}
                    <a href="/disclaimer" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-medium">{disclaimerLink}</a>
                    {termsBetween[1]}
                  </label>
                </div>

                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    name="agreePrivacy"
                    id="agreePrivacy"
                    required
                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                    data-testid="consent-privacy"
                  />
                  <label htmlFor="agreePrivacy" className="text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                    {privacyParts[0]}
                    <a href="/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-medium">{privacyLink}</a>
                    {privacyParts[1]}
                  </label>
                </div>

                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    name="agreeSensitiveData"
                    id="agreeSensitiveData"
                    required
                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                    data-testid="consent-sensitive"
                  />
                  <label htmlFor="agreeSensitiveData" className="text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                    {t('auth.consent.sensitiveData')}
                  </label>
                </div>

                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    name="agreeAge"
                    id="agreeAge"
                    required
                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                    data-testid="consent-age"
                  />
                  <label htmlFor="agreeAge" className="text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                    {t('auth.consent.ageVerification')}
                  </label>
                </div>
              </div>

              {error && (
                <div className="p-3 bg-error/10 border border-error rounded-lg">
                  <p className="text-sm text-error">{error}</p>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                className="w-full"
                data-testid="register-submit"
              >
                {t('auth.createAccountButton')}
              </Button>

              <div className="text-center text-sm">
                <span className="text-gray-600 dark:text-gray-400">{t('auth.hasAccount')} </span>
                <Link href="/login" className="text-primary hover:text-primary-dark font-medium">
                  {t('auth.signInLink')}
                </Link>
              </div>
            </form>

            <SocialLoginButtons googleTestId="register-google" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

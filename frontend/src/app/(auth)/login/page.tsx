'use client';

import { useState, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Button, Input, Card, CardContent } from '@/components/ui';
import { SocialLoginButtons } from '@/components/features/SocialLoginButtons';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (window.location.search) {
      window.history.replaceState({}, '', '/login');
    }
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    try {
      await login({ email, password });
      // Use window.location to ensure cookies are sent with the next request
      window.location.href = '/home';
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">Health & Wellness</h1>
          <p className="text-gray-600 dark:text-gray-400">Sign in to your account</p>
        </div>

        <Card variant="elevated">
          <CardContent>
            <form method="post" action="" onSubmit={handleSubmit} className="space-y-6">
              <Input
                type="email"
                name="email"
                label="Email"
                placeholder="you@example.com"
                required
                autoComplete="email"
              />

              <Input
                type="password"
                name="password"
                label="Password"
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />

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
              >
                Sign In
              </Button>

              <div className="text-center text-sm">
                <span className="text-gray-600 dark:text-gray-400">Don&apos;t have an account? </span>
                <Link href="/register" className="text-primary hover:text-primary-dark font-medium">
                  Create one
                </Link>
              </div>
            </form>

            <SocialLoginButtons />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

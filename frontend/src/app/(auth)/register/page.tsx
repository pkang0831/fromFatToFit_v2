'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Button, Input, Card, CardContent, Select } from '@/components/ui';
import { SocialLoginButtons } from '@/components/features/SocialLoginButtons';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setError('Password must be at least 8 characters');
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
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
          <h1 className="text-4xl font-bold text-primary mb-2">FromFatToFit</h1>
          <p className="text-gray-600 dark:text-gray-400">Create your account</p>
        </div>

        <Card variant="elevated">
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                type="text"
                name="full_name"
                label="Full Name"
                placeholder="John Doe"
                helperText="Optional"
                autoComplete="name"
              />

              <Input
                type="email"
                name="email"
                label="Email"
                placeholder="you@example.com"
                required
                autoComplete="email"
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select name="gender" label="Gender" required>
                  <option value="">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </Select>
                <Input
                  type="number"
                  name="age"
                  label="Age"
                  placeholder="30"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="number"
                  name="height_cm"
                  label="Height (cm)"
                  placeholder="170"
                  required
                />
                <Input
                  type="number"
                  name="weight_kg"
                  label="Weight (kg)"
                  placeholder="70"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select name="ethnicity" label="Ethnicity" required>
                  <option value="">Select...</option>
                  <option value="Asian">Asian</option>
                  <option value="Caucasian">Caucasian</option>
                  <option value="African">African</option>
                  <option value="Hispanic">Hispanic</option>
                  <option value="Middle Eastern">Middle Eastern</option>
                  <option value="Pacific Islander">Pacific Islander</option>
                  <option value="Mixed">Mixed</option>
                  <option value="Other">Other</option>
                </Select>
                <Select name="activity_level" label="Activity Level">
                  <option value="sedentary">Sedentary</option>
                  <option value="light">Lightly Active</option>
                  <option value="moderate" selected>Moderately Active</option>
                  <option value="active">Very Active</option>
                  <option value="athlete">Athlete</option>
                </Select>
              </div>

              <Input
                type="password"
                name="password"
                label="Password"
                placeholder="••••••••"
                required
                helperText="Minimum 8 characters"
                autoComplete="new-password"
              />

              <Input
                type="password"
                name="confirmPassword"
                label="Confirm Password"
                placeholder="••••••••"
                required
                autoComplete="new-password"
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
                Create Account
              </Button>

              <div className="text-center text-sm">
                <span className="text-gray-600 dark:text-gray-400">Already have an account? </span>
                <Link href="/login" className="text-primary hover:text-primary-dark font-medium">
                  Sign in
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

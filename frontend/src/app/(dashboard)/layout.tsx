'use client';

import { useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Sidebar } from '@/components/layout/Sidebar';
import { MobileNav } from '@/components/layout/MobileNav';
import { FeatureTour } from '@/components/tour/FeatureTour';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, loading, user } = useAuth();
  const redirecting = useRef(false);

  useEffect(() => {
    if (!loading && !isAuthenticated && !redirecting.current) {
      redirecting.current = true;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      window.location.replace('/login');
    }
  }, [isAuthenticated, loading]);

  useEffect(() => {
    if (!loading && isAuthenticated && user && !user.onboarding_completed && !redirecting.current) {
      redirecting.current = true;
      window.location.replace('/onboarding');
    }
  }, [isAuthenticated, loading, user]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950 dark:bg-gray-950">
      <Sidebar />
      <FeatureTour />
      <main className="flex-1 overflow-x-hidden pb-20 lg:pb-0">
        <ErrorBoundary>
          <div className="container mx-auto px-4 py-8 max-w-7xl">
            {children}
          </div>
        </ErrorBoundary>
      </main>
      <MobileNav />
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Sidebar } from '@/components/layout/Sidebar';
import { MobileNav } from '@/components/layout/MobileNav';

const FeatureTour = dynamic(
  () => import('@/components/tour/FeatureTour').then((m) => ({ default: m.FeatureTour })),
  { ssr: false }
);

function readHasAccessToken(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    return Boolean(localStorage.getItem('access_token'));
  } catch {
    return false;
  }
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [likelySession] = useState(readHasAccessToken);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      const next = typeof window !== 'undefined' ? window.location.pathname : '';
      const loginUrl = next && next !== '/login' ? `/login?next=${encodeURIComponent(next)}` : '/login';
      router.replace(loginUrl);
    }
  }, [isAuthenticated, loading, router]);

  // Token in storage: show dashboard chrome immediately and load the main column while profile resolves.
  if (loading && likelySession) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 overflow-x-hidden pb-20 lg:pb-0">
          <div className="container mx-auto px-4 py-8 max-w-7xl flex min-h-[40vh] flex-col items-center justify-center">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent" />
            <p className="mt-4 text-sm text-text-secondary">Loading your workspace…</p>
          </div>
        </main>
        <MobileNav />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-text-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mx-auto" />
          <p className="mt-4 text-text-secondary">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-x-hidden pb-20 lg:pb-0">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {children}
        </div>
      </main>
      <MobileNav />
      <FeatureTour />
    </div>
  );
}

'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { paymentApi } from '@/lib/api/services';
import type { UsageLimitsResponse, UsageLimit } from '@/types/api';
import { useAuth } from './AuthContext';
import { AxiosError } from 'axios';

interface SubscriptionContextType {
  isPremium: boolean;
  usageLimits: UsageLimitsResponse | null;
  loading: boolean;
  error: string | null;
  refreshLimits: () => Promise<void>;
  checkFeatureAccess: (feature: keyof UsageLimitsResponse['limits']) => {
    hasAccess: boolean;
    remaining: number;
    limit: number;
  };
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

export function SubscriptionProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [usageLimits, setUsageLimits] = useState<UsageLimitsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLimits = async () => {
    if (!isAuthenticated) {
      setUsageLimits(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await paymentApi.getUsageLimits();
      setUsageLimits(response.data);
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      const message = error.response?.data?.detail || 'Failed to load usage limits';
      setError(message);
      console.error('Failed to fetch usage limits:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLimits();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const refreshLimits = async () => {
    await fetchLimits();
  };

  const checkFeatureAccess = (feature: keyof UsageLimitsResponse['limits']) => {
    if (!usageLimits) {
      return { hasAccess: false, remaining: 0, limit: 0 };
    }

    const limit = usageLimits.limits[feature];
    
    // Premium users have unlimited access
    if (usageLimits.is_premium || limit.is_premium) {
      return { hasAccess: true, remaining: -1, limit: -1 };
    }

    // Check if user has remaining usage
    const hasAccess = limit.remaining > 0;
    return {
      hasAccess,
      remaining: limit.remaining,
      limit: limit.limit,
    };
  };

  const value: SubscriptionContextType = {
    isPremium: usageLimits?.is_premium ?? false,
    usageLimits,
    loading,
    error,
    refreshLimits,
    checkFeatureAccess,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
}

export function useSubscription() {
  const context = useContext(SubscriptionContext);
  if (context === undefined) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
}

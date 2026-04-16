import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { paymentApi } from '../services/api';
import { useAuth } from './AuthContext';

interface UsageLimits {
  food_scan: { current_count: number; limit: number; remaining: number; is_premium: boolean };
  body_fat_scan: { current_count: number; limit: number; remaining: number; is_premium: boolean };
  percentile_scan: { current_count: number; limit: number; remaining: number; is_premium: boolean };
  form_check: { current_count: number; limit: number; remaining: number; is_premium: boolean };
  transformation: { current_count: number; limit: number; remaining: number; is_premium: boolean };
}

interface SubscriptionContextType {
  isPremium: boolean;
  usageLimits: UsageLimits | null;
  loading: boolean;
  error: string | null;
  refreshLimits: () => Promise<{ is_premium: boolean; limits: UsageLimits } | null>;
  checkFeatureAccess: (feature: keyof UsageLimits) => { allowed: boolean; remaining: number };
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

export const SubscriptionProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useAuth();
  const [isPremium, setIsPremium] = useState(false);
  const [usageLimits, setUsageLimits] = useState<UsageLimits | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      setIsPremium(user.premium_status || false);
      void loadUsageLimits();
    } else {
      setIsPremium(false);
      setUsageLimits(null);
      setError(null);
      setLoading(false);
    }
  }, [user]);

  const loadUsageLimits = async () => {
    setLoading(true);
    try {
      setError(null);
      const { data } = await paymentApi.getUsageLimits();
      setUsageLimits(data.limits);
      setIsPremium(data.is_premium);
      return data;
    } catch (error) {
      console.error('Error loading usage limits:', error);
      setError('Unable to load premium status. Pull to refresh or try again.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const refreshLimits = async () => {
    return loadUsageLimits();
  };

  const checkFeatureAccess = (feature: keyof UsageLimits) => {
    if (isPremium) {
      return { allowed: true, remaining: 999 };
    }

    if (loading) {
      return { allowed: true, remaining: 0 };
    }

    if (!usageLimits) {
      return { allowed: false, remaining: 0 };
    }

    const limit = usageLimits[feature];
    if (!limit) {
      return { allowed: false, remaining: 0 };
    }

    const allowed = limit.remaining > 0;
    return { allowed, remaining: limit.remaining };
  };

  return (
    <SubscriptionContext.Provider
      value={{
        isPremium,
        usageLimits,
        loading,
        error,
        refreshLimits,
        checkFeatureAccess,
      }}
    >
      {children}
    </SubscriptionContext.Provider>
  );
};

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (context === undefined) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

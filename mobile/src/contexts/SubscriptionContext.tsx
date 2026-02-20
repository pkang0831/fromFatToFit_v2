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
  refreshLimits: () => Promise<void>;
  checkFeatureAccess: (feature: keyof UsageLimits) => { allowed: boolean; remaining: number };
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

export const SubscriptionProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useAuth();
  const [isPremium, setIsPremium] = useState(false);
  const [usageLimits, setUsageLimits] = useState<UsageLimits | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setIsPremium(user.premium_status || false);
      loadUsageLimits();
    } else {
      setIsPremium(false);
      setUsageLimits(null);
      setLoading(false);
    }
  }, [user]);

  const loadUsageLimits = async () => {
    try {
      const { data } = await paymentApi.getUsageLimits();
      setUsageLimits(data.limits);
      setIsPremium(data.is_premium);
    } catch (error) {
      console.error('Error loading usage limits:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshLimits = async () => {
    await loadUsageLimits();
  };

  const checkFeatureAccess = (feature: keyof UsageLimits) => {
    if (!usageLimits) {
      return { allowed: false, remaining: 0 };
    }

    const limit = usageLimits[feature];
    if (!limit) {
      return { allowed: false, remaining: 0 };
    }

    if (limit.is_premium) {
      return { allowed: true, remaining: 999 };
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

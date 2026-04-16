import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { Session } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { supabase } from '../services/auth';
import { authApi } from '../services/api';

interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  height_cm?: number;
  weight_kg?: number;
  age?: number;
  gender?: string;
  ethnicity?: string;
  activity_level?: string;
  calorie_goal?: number;
  premium_status: boolean;
}

interface AuthContextType {
  user: UserProfile | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName?: string) => Promise<{ session: Session | null }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function buildFallbackProfile(session: Session): UserProfile {
  const metadata = (session.user.user_metadata || {}) as Record<string, string | undefined>;

  return {
    id: session.user.id,
    email: session.user.email || '',
    full_name: metadata.full_name || metadata.name || undefined,
    premium_status: false,
  };
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    supabase.auth
      .getSession()
      .then(({ data: { session } }) => {
        setSession(session);
        if (session) {
          void loadUserProfile(session);
        } else {
          setLoading(false);
        }
      })
      .catch((error) => {
        console.error('Error restoring session:', error);
        setUser(null);
        setSession(null);
        setLoading(false);
      });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        void loadUserProfile(session);
      } else {
        setUser(null);
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const loadUserProfile = async (sessionToUse: Session | null = session) => {
    try {
      if (!sessionToUse) {
        setUser(null);
        return null;
      }

      const { data } = await authApi.getProfile();
      setUser(data);
      return data;
    } catch (error) {
      console.error('Error loading user profile:', error);
      const status = (error as any)?.response?.status;

      if (status === 401 || status === 403) {
        setUser(null);
        return null;
      }

      if (sessionToUse) {
        const fallbackProfile = buildFallbackProfile(sessionToUse);
        setUser(fallbackProfile);
        return fallbackProfile;
      }

      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      // Store tokens
      if (data.session) {
        await AsyncStorage.setItem('access_token', data.session.access_token);
        await AsyncStorage.setItem('refresh_token', data.session.refresh_token);
      }

      setSession(data.session ?? null);
      await loadUserProfile(data.session ?? null);
      return;
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  const signUp = async (email: string, password: string, fullName?: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (error) throw error;

      // Store tokens
      if (data.session) {
        await AsyncStorage.setItem('access_token', data.session.access_token);
        await AsyncStorage.setItem('refresh_token', data.session.refresh_token);
      }

      setSession(data.session ?? null);
      if (data.session) {
        await loadUserProfile(data.session);
      } else {
        setUser(null);
        setLoading(false);
      }
      return { session: data.session ?? null };
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
      setUser(null);
      setSession(null);
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  const refreshProfile = async () => {
    await loadUserProfile(session);
  };

  const updateProfile = async (data: Partial<UserProfile>) => {
    try {
      await authApi.updateProfile(data);
      await loadUserProfile();
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        signIn,
        signUp,
        signOut,
        refreshProfile,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

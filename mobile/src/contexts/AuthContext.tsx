import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { Session } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { makeRedirectUri } from 'expo-auth-session';
import * as Linking from 'expo-linking';
import * as QueryParams from 'expo-auth-session/build/QueryParams';
import * as WebBrowser from 'expo-web-browser';
import { supabase } from '../services/auth';
import { authApi } from '../services/api';

WebBrowser.maybeCompleteAuthSession();

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
  signInWithGoogle: () => Promise<void>;
  signUp: (email: string, password: string, fullName?: string) => Promise<{ session: Session | null }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const OAUTH_REDIRECT_URL = makeRedirectUri({
  scheme: 'devenira',
  path: 'auth/callback',
});

function buildFallbackProfile(session: Session): UserProfile {
  const metadata = (session.user.user_metadata || {}) as Record<string, string | undefined>;

  return {
    id: session.user.id,
    email: session.user.email || '',
    full_name: metadata.full_name || metadata.name || undefined,
    premium_status: false,
  };
}

async function persistLegacyTokens(nextSession: Session | null) {
  if (!nextSession) {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
    return;
  }

  await AsyncStorage.setItem('access_token', nextSession.access_token);
  await AsyncStorage.setItem('refresh_token', nextSession.refresh_token);
}

async function createSessionFromUrl(url: string) {
  const { params, errorCode } = QueryParams.getQueryParams(url);

  if (errorCode) {
    throw new Error(errorCode);
  }

  const nestedUrl = typeof params.url === 'string' ? params.url : undefined;
  if (nestedUrl && nestedUrl !== url) {
    const decodedNestedUrl = decodeURIComponent(nestedUrl);
    return createSessionFromUrl(decodedNestedUrl);
  }

  const accessToken = typeof params.access_token === 'string' ? params.access_token : undefined;
  const refreshToken = typeof params.refresh_token === 'string' ? params.refresh_token : undefined;
  const authCode = typeof params.code === 'string' ? params.code : undefined;

  if (accessToken && refreshToken) {
    const { data, error } = await supabase.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken,
    });

    if (error) throw error;

    await persistLegacyTokens(data.session);
    return data.session;
  }

  if (authCode) {
    const { data, error } = await supabase.auth.exchangeCodeForSession(authCode);

    if (error) throw error;

    await persistLegacyTokens(data.session);
    return data.session;
  }

  return null;
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth
      .getSession()
      .then(({ data: { session } }) => {
        setSession(session);
        if (session) {
          void persistLegacyTokens(session);
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

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      void persistLegacyTokens(nextSession);

      if (nextSession) {
        void loadUserProfile(nextSession);
      } else {
        setUser(null);
        setLoading(false);
      }
    });

    const urlSubscription = Linking.addEventListener('url', ({ url }) => {
      void createSessionFromUrl(url).catch((error) => {
        console.error('OAuth deep link failed:', error);
      });
    });

    void Linking.getInitialURL().then((url) => {
      if (!url) return;
      return createSessionFromUrl(url).catch((error) => {
        console.error('Initial OAuth deep link failed:', error);
      });
    });

    return () => {
      subscription.unsubscribe();
      urlSubscription.remove();
    };
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

      if (data.session) {
        await persistLegacyTokens(data.session);
      }

      setSession(data.session ?? null);
      await loadUserProfile(data.session ?? null);
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  const signInWithGoogle = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: OAUTH_REDIRECT_URL,
          skipBrowserRedirect: true,
        },
      });

      if (error) throw error;
      if (!data?.url) throw new Error('Google sign-in could not be started.');

      const result = await WebBrowser.openAuthSessionAsync(data.url, OAUTH_REDIRECT_URL);

      if (result.type === 'success' && result.url) {
        await createSessionFromUrl(result.url);
        return;
      }

      if (result.type === 'cancel' || result.type === 'dismiss') {
        throw new Error('Google sign-in was canceled.');
      }

      throw new Error('Google sign-in could not be completed.');
    } catch (error) {
      console.error('Google sign in error:', error);
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

      if (data.session) {
        await persistLegacyTokens(data.session);
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
      await Promise.allSettled([authApi.logout(), supabase.auth.signOut()]);
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
        signInWithGoogle,
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

'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api/services';
import { supabase, type OAuthProvider } from '@/lib/supabase';
import { setAuthCookie, clearAuthCookie } from '@/lib/utils/cookie';
import type { User, UserLogin, UserRegister, AccountDeletionResponse } from '@/types/api';
import { AxiosError } from 'axios';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (data: UserLogin) => Promise<User>;
  loginWithOAuth: (provider: OAuthProvider, nextPath?: string) => Promise<void>;
  register: (data: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
  deleteAccount: () => Promise<AccountDeletionResponse>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function clearAllTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  clearAuthCookie('access_token');
  clearAuthCookie('refresh_token');
}

function redirectToLogin() {
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof window === 'undefined') return;
        const path = window.location.pathname.replace(/\/$/, '') || '/';
        const isAuthPage =
          path === '/login' ||
          path === '/register' ||
          window.location.pathname.startsWith('/auth/callback');

        if (isAuthPage) { setLoading(false); return; }

        const token = localStorage.getItem('access_token');
        if (!token) { clearAllTokens(); setLoading(false); return; }

        // Proactively refresh the Supabase session so the API call uses a valid JWT
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          const { data: refreshData } = await supabase.auth.refreshSession();
          if (refreshData.session) {
            localStorage.setItem('access_token', refreshData.session.access_token);
            localStorage.setItem('refresh_token', refreshData.session.refresh_token);
            setAuthCookie('access_token', refreshData.session.access_token);
            setAuthCookie('refresh_token', refreshData.session.refresh_token);
          }
        }

        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Auth check timeout')), 5000)
        );

        const response = await Promise.race([authApi.getProfile(), timeoutPromise]) as Awaited<ReturnType<typeof authApi.getProfile>>;
        setUser(response.data);

        const liveToken = localStorage.getItem('access_token');
        if (liveToken && !document.cookie.includes('access_token=')) {
          const refreshToken = localStorage.getItem('refresh_token');
          setAuthCookie('access_token', liveToken);
          if (refreshToken) setAuthCookie('refresh_token', refreshToken);
        }
      } catch (_: unknown) {
        clearAllTokens();
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  useEffect(() => {
    const handleSessionExpired = () => {
      setUser(null);
      clearAllTokens();
      redirectToLogin();
    };
    window.addEventListener('session-expired', handleSessionExpired);
    return () => window.removeEventListener('session-expired', handleSessionExpired);
  }, []);

  const login = async (data: UserLogin): Promise<User> => {
    try {
      setError(null);
      setLoading(true);
      const response = await authApi.login(data);
      const { access_token, refresh_token, user: userData } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setAuthCookie('access_token', access_token);
      setAuthCookie('refresh_token', refresh_token);
      setUser(userData);
      return userData;
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      const message = error.response?.data?.detail || 'Login failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const loginWithOAuth = async (provider: OAuthProvider, nextPath?: string) => {
    try {
      setError(null);
      const redirectToUrl = new URL('/auth/callback', window.location.origin);
      const currentNext = nextPath ?? new URLSearchParams(window.location.search).get('next') ?? undefined;
      if (currentNext && currentNext.startsWith('/')) {
        redirectToUrl.searchParams.set('next', currentNext);
      }
      const redirectTo = redirectToUrl.toString();
      const { error } = await supabase.auth.signInWithOAuth({ provider, options: { redirectTo } });
      if (error) throw error;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'OAuth login failed';
      setError(message);
      throw new Error(message);
    }
  };

  const register = async (data: UserRegister) => {
    try {
      setError(null);
      setLoading(true);
      const response = await authApi.register(data);
      const { access_token, refresh_token, user: userData } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setAuthCookie('access_token', access_token);
      setAuthCookie('refresh_token', refresh_token);
      setUser(userData);
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      const message = error.response?.data?.detail || 'Registration failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await Promise.allSettled([authApi.logout(), supabase.auth.signOut()]);
    } catch (_) {
      /* noop */
    }
    finally {
      clearAllTokens();
      setUser(null);
      redirectToLogin();
    }
  };

  const deleteAccount = async (): Promise<AccountDeletionResponse> => {
    try {
      setError(null);
      const response = await authApi.deleteAccount();
      await supabase.auth.signOut();
      clearAllTokens();
      setUser(null);
      redirectToLogin();
      return response.data;
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      const message = error.response?.data?.detail || 'Account deletion failed';
      setError(message);
      throw new Error(message);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      setError(null);
      const response = await authApi.updateProfile(data);
      setUser(response.data);
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      const message = error.response?.data?.detail || 'Update failed';
      setError(message);
      throw new Error(message);
    }
  };

  const refreshUser = async () => {
    try {
      const response = await authApi.getProfile();
      setUser(response.data);
    } catch (_) { /* noop */ }
  };

  const value: AuthContextType = {
    user, loading, error, isAuthenticated: !!user,
    login, loginWithOAuth, register, logout, deleteAccount, updateProfile, refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}

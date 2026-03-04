'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api/services';
import { supabase, type OAuthProvider } from '@/lib/supabase';
import { setAuthCookie, clearAuthCookie } from '@/lib/utils/cookie';
import type { User, UserLogin, UserRegister } from '@/types/api';
import { AxiosError } from 'axios';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (data: UserLogin) => Promise<void>;
  loginWithOAuth: (provider: OAuthProvider) => Promise<void>;
  register: (data: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
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
        const path = window.location.pathname;
        const isAuthPage = path === '/login' || path === '/register' ||
          path.startsWith('/auth/callback') || path.startsWith('/onboarding');

        if (isAuthPage) { setLoading(false); return; }

        const token = localStorage.getItem('access_token');
        if (!token) { clearAllTokens(); setLoading(false); return; }

        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Auth check timeout')), 5000)
        );

        const response = await Promise.race([authApi.getProfile(), timeoutPromise]) as Awaited<ReturnType<typeof authApi.getProfile>>;
        setUser(response.data);

        if (!document.cookie.includes('access_token=')) {
          const refreshToken = localStorage.getItem('refresh_token');
          setAuthCookie('access_token', token);
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

  const login = async (data: UserLogin) => {
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
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      const message = error.response?.data?.detail || 'Login failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const loginWithOAuth = async (provider: OAuthProvider) => {
    try {
      setError(null);
      const redirectTo = `${window.location.origin}/auth/callback`;
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
    try { await authApi.logout(); } catch (_) { /* noop */ }
    finally {
      clearAllTokens();
      setUser(null);
      redirectToLogin();
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
    login, loginWithOAuth, register, logout, updateProfile, refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}

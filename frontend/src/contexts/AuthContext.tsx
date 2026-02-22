'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api/services';
import { supabase, type OAuthProvider } from '@/lib/supabase';
import type { User, UserLogin, UserRegister } from '@/types/api';
import { AxiosError } from 'axios';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  sessionExpired: boolean;
  isAuthenticated: boolean;
  login: (data: UserLogin) => Promise<void>;
  loginWithOAuth: (provider: OAuthProvider) => Promise<void>;
  register: (data: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);

  // Check for existing auth token on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        // 🔧 Skip auth check on login/register pages to avoid infinite loading
        const isAuthPage = window.location.pathname === '/login' || 
                           window.location.pathname === '/register' ||
                           window.location.pathname.startsWith('/auth/callback') ||
                           window.location.pathname.startsWith('/onboarding');
        
        if (isAuthPage) {
          setLoading(false);
          return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
          document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          return;
        }

        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Auth check timeout')), 5000)
        );
        
        const response = await Promise.race([
          authApi.getProfile(),
          timeoutPromise
        ]) as any;
        
        setUser(response.data);
        setSessionExpired(false);
        
        const hasCookie = document.cookie.includes('access_token=');
        if (!hasCookie) {
          const refreshToken = localStorage.getItem('refresh_token');
          document.cookie = `access_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
          if (refreshToken) {
            document.cookie = `refresh_token=${refreshToken}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`;
          }
        }
      } catch (err: unknown) {
        console.error('Failed to load user:', err);
        
        if (err instanceof AxiosError && err.response?.status === 401) {
          setSessionExpired(true);
        }
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Global session expiry listener
  useEffect(() => {
    const handleSessionExpired = () => {
      setSessionExpired(true);
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
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

      // Store in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Also store in cookies for middleware access
      document.cookie = `access_token=${access_token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
      document.cookie = `refresh_token=${refresh_token}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`;
      
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
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: { redirectTo },
      });
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

      // Store in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Also store in cookies for middleware access
      document.cookie = `access_token=${access_token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
      document.cookie = `refresh_token=${refresh_token}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`;
      
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
      await authApi.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Clear cookies
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      
      setUser(null);
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
    } catch (err) {
      console.error('Failed to refresh user:', err);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    error,
    sessionExpired,
    isAuthenticated: !!user,
    login,
    loginWithOAuth,
    register,
    logout,
    updateProfile,
    refreshUser,
  };

  // Show session expired UI if session is expired
  if (sessionExpired && !loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px'
      }}>
        <div style={{
          maxWidth: '450px',
          width: '100%',
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
          padding: '40px',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '24px' }}>
            <div style={{
              margin: '0 auto 16px',
              width: '80px',
              height: '80px',
              background: '#fee2e2',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg style={{ width: '40px', height: '40px', color: '#dc2626' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: 'bold',
              color: '#1f2937',
              marginBottom: '12px'
            }}>
              Session Timed Out
            </h1>
            <p style={{
              fontSize: '16px',
              color: '#6b7280',
              marginBottom: '24px',
              lineHeight: '1.6'
            }}>
              Your session has expired for security reasons.<br />
              Please log in again to continue.
            </p>
          </div>
          
          <button
            onClick={() => {
              setSessionExpired(false);
              window.location.href = '/login';
            }}
            style={{
              width: '100%',
              background: '#2563eb',
              color: 'white',
              fontWeight: '600',
              fontSize: '16px',
              padding: '14px 24px',
              borderRadius: '10px',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#1d4ed8';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(37, 99, 235, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#2563eb';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 14px rgba(37, 99, 235, 0.4)';
            }}
          >
            Log In Again
          </button>
          
          <p style={{
            fontSize: '14px',
            color: '#9ca3af',
            marginTop: '16px'
          }}>
            Your data is safe and secure.
          </p>
        </div>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

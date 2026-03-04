'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { setAuthCookie } from '@/lib/utils/cookie';

export default function AuthCallbackPage() {
  const [status, setStatus] = useState<'loading' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    let timeout: NodeJS.Timeout;

    const tryGetSession = async (attempt: number): Promise<void> => {
      try {
        // Check hash tokens first (implicit flow)
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const hashAccess = hashParams.get('access_token');
        const hashRefresh = hashParams.get('refresh_token');

        if (hashAccess && hashRefresh) {
          const { error: setErr } = await supabase.auth.setSession({
            access_token: hashAccess,
            refresh_token: hashRefresh,
          });
          if (setErr) throw setErr;
          storeTokensAndRedirect(hashAccess, hashRefresh);
          return;
        }

        // Try code exchange (PKCE flow)
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        if (code) {
          const { data: exchangeData, error: exchangeErr } =
            await supabase.auth.exchangeCodeForSession(code);
          if (exchangeErr) throw exchangeErr;
          if (exchangeData.session) {
            storeTokensAndRedirect(
              exchangeData.session.access_token,
              exchangeData.session.refresh_token,
            );
            return;
          }
        }

        // Supabase may have auto-processed the hash — poll getSession
        const { data, error } = await supabase.auth.getSession();
        if (error) throw error;
        if (data.session) {
          storeTokensAndRedirect(data.session.access_token, data.session.refresh_token);
          return;
        }

        // Retry up to 5 times with increasing delay
        if (attempt < 5) {
          timeout = setTimeout(() => tryGetSession(attempt + 1), 800 * attempt);
          return;
        }

        throw new Error('No session found after OAuth callback');
      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setErrorMsg(err.message || 'Authentication failed');
        setStatus('error');
      }
    };

    // Also listen for auth state change as a fallback
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' && session) {
        storeTokensAndRedirect(session.access_token, session.refresh_token);
      }
    });

    tryGetSession(1);

    return () => {
      clearTimeout(timeout);
      subscription.unsubscribe();
    };
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="text-center">
        {status === 'loading' ? (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
            <p className="mt-4 text-gray-600 dark:text-gray-400">Completing sign in...</p>
          </>
        ) : (
          <div className="max-w-md">
            <div className="w-16 h-16 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Sign In Failed</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{errorMsg}</p>
            <a
              href="/login"
              className="inline-block px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark transition-colors"
            >
              Back to Login
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

function storeTokensAndRedirect(accessToken: string, refreshToken: string) {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  setAuthCookie('access_token', accessToken);
  setAuthCookie('refresh_token', refreshToken);
  window.location.href = '/onboarding';
}

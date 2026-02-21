'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function AuthCallbackPage() {
  const [status, setStatus] = useState<'loading' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const { data, error } = await supabase.auth.getSession();

        if (error) throw error;
        if (!data.session) {
          // Supabase PKCE flow: exchange the code from the URL hash
          const hashParams = new URLSearchParams(window.location.hash.substring(1));
          const accessToken = hashParams.get('access_token');
          const refreshToken = hashParams.get('refresh_token');

          if (accessToken && refreshToken) {
            const { error: setErr } = await supabase.auth.setSession({
              access_token: accessToken,
              refresh_token: refreshToken,
            });
            if (setErr) throw setErr;

            storeTokensAndRedirect(accessToken, refreshToken);
            return;
          }

          // Try code exchange (PKCE flow used by newer Supabase versions)
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

          throw new Error('No session found after OAuth callback');
        }

        storeTokensAndRedirect(data.session.access_token, data.session.refresh_token);
      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setErrorMsg(err.message || 'Authentication failed');
        setStatus('error');
      }
    };

    handleCallback();
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="text-center">
        {status === 'loading' ? (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
            <p className="mt-4 text-text-secondary">Completing sign in...</p>
          </>
        ) : (
          <div className="max-w-md">
            <div className="w-16 h-16 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-text mb-2">Sign In Failed</h2>
            <p className="text-text-secondary mb-6">{errorMsg}</p>
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
  document.cookie = `access_token=${accessToken}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
  document.cookie = `refresh_token=${refreshToken}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`;
  window.location.href = '/home';
}

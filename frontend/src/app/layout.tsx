import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import '@/styles/globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import { SubscriptionProvider } from '@/contexts/SubscriptionContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { LanguageProvider } from '@/contexts/LanguageContext';
import { ErrorBoundary } from '@/components/ErrorBoundary';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'FromFatToFit — AI-Powered Fitness Tracking',
    template: '%s | FromFatToFit',
  },
  description: 'Track calories with your camera, scan your body fat with AI, and visualize your transformation. All-in-one AI fitness app.',
  keywords: ['fitness tracker', 'calorie counter', 'body fat scanner', 'AI fitness', 'workout tracker', 'meal tracker', 'body transformation'],
  authors: [{ name: 'FromFatToFit' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://fromfattofit.com',
    siteName: 'FromFatToFit',
    title: 'FromFatToFit — AI-Powered Fitness Tracking',
    description: 'Track calories with your camera, scan your body fat with AI, and visualize your transformation.',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FromFatToFit — AI-Powered Fitness Tracking',
    description: 'Track calories with your camera, scan your body fat with AI, and visualize your transformation.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

const themeScript = `
(function() {
  try {
    var stored = localStorage.getItem('theme');
    var dark = stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (dark) document.documentElement.classList.add('dark');
    var lang = localStorage.getItem('ftf-locale');
    if (lang) document.documentElement.lang = lang;
    if (lang === 'ar') document.documentElement.dir = 'rtl';
  } catch(e) {}
})();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className={inter.className}>
        <ThemeProvider>
          <LanguageProvider>
            <ErrorBoundary>
              <AuthProvider>
                <SubscriptionProvider>
                  {children}
                  <Toaster position="top-center" />
                </SubscriptionProvider>
              </AuthProvider>
            </ErrorBoundary>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

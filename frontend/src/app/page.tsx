'use client';

import { useEffect } from 'react';
import { HeroSection } from '@/components/landing/HeroSection';
import { FounderStorySection } from '@/components/landing/FounderStorySection';
import { StartHereSection } from '@/components/landing/StartHereSection';
import { HowItWorksSection } from '@/components/landing/HowItWorksSection';
import { TrustSection } from '@/components/landing/TrustSection';
import { FAQSection } from '@/components/landing/FAQSection';
import { FinalCTASection } from '@/components/landing/FinalCTASection';
import { FooterSection } from '@/components/landing/FooterSection';

export default function LandingPage() {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (window.location.pathname !== '/') return;

    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    const urlParams = new URLSearchParams(window.location.search);
    const hasOAuthHash =
      hashParams.has('access_token') ||
      hashParams.has('refresh_token') ||
      hashParams.has('error') ||
      hashParams.has('error_description');
    const hasOAuthCode = urlParams.has('code');

    if (!hasOAuthHash && !hasOAuthCode) return;

    const callbackUrl = new URL('/auth/callback', window.location.origin);
    callbackUrl.search = window.location.search;
    callbackUrl.hash = window.location.hash;
    window.location.replace(callbackUrl.toString());
  }, []);

  return (
    <main className="overflow-hidden bg-[#0a0a0f] text-white">
      <HeroSection />
      <FounderStorySection />
      <StartHereSection />
      <HowItWorksSection />
      <TrustSection />
      <FAQSection />
      <FinalCTASection />
      <FooterSection />
    </main>
  );
}

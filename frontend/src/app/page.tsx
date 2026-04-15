'use client';

import { HeroSection } from '@/components/landing/HeroSection';
import { FounderStorySection } from '@/components/landing/FounderStorySection';
import { StartHereSection } from '@/components/landing/StartHereSection';
import { HowItWorksSection } from '@/components/landing/HowItWorksSection';
import { TrustSection } from '@/components/landing/TrustSection';
import { FinalCTASection } from '@/components/landing/FinalCTASection';
import { FooterSection } from '@/components/landing/FooterSection';

export default function LandingPage() {
  return (
    <main className="overflow-hidden bg-[#0a0a0f] text-white">
      <HeroSection />
      <FounderStorySection />
      <StartHereSection />
      <HowItWorksSection />
      <TrustSection />
      <FinalCTASection />
      <FooterSection />
    </main>
  );
}

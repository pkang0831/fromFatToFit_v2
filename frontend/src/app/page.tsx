'use client';

import { HeroSection } from '@/components/landing/HeroSection';
import { HowItWorksSection } from '@/components/landing/HowItWorksSection';
import { TransformationShowcaseSection } from '@/components/landing/TransformationShowcaseSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { WhyReturnSection } from '@/components/landing/WhyReturnSection';
import { TrustSection } from '@/components/landing/TrustSection';
import { FounderStorySection } from '@/components/landing/FounderStorySection';
import { TestimonialsSection } from '@/components/landing/TestimonialsSection';
import { PricingSection } from '@/components/landing/PricingSection';
import { FAQSection } from '@/components/landing/FAQSection';
import { FinalCTASection } from '@/components/landing/FinalCTASection';
import { FooterSection } from '@/components/landing/FooterSection';

export default function LandingPage() {
  return (
    <main className="overflow-hidden bg-[#0a0a0f] text-white">
      <HeroSection />
      <HowItWorksSection />
      <TransformationShowcaseSection />
      <div id="features"><FeaturesSection /></div>
      <WhyReturnSection />
      <TrustSection />
      <FounderStorySection />
      <div id="testimonials"><TestimonialsSection /></div>
      <div id="pricing"><PricingSection /></div>
      <div id="faq"><FAQSection /></div>
      <FinalCTASection />
      <FooterSection />
    </main>
  );
}

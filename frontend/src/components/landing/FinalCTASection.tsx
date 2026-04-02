'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

export function FinalCTASection() {
  const { t } = useLanguage();

  return (
    <section className="py-24 px-6 relative overflow-hidden" style={{ backgroundColor: '#080810' }}>
      <div
        className="absolute inset-0"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(201,169,110,0.06) 0%, transparent 60%)' }}
      />

      <motion.div
        className="max-w-2xl mx-auto text-center relative z-10"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-100px' }}
        transition={{ duration: 0.7 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-5">
          {t('landing.finalCtaTitle')}
        </h2>
        <p className="text-lg text-white/45 mb-10 leading-relaxed">
          {t('landing.finalCtaSubtitle')}
        </p>
        <Link
          href="/try"
          className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-gradient-primary text-white font-semibold text-lg shadow-glow-cyan hover:scale-105 transition-transform duration-200"
        >
          {t('landing.getStarted')}
          <ArrowRight className="w-5 h-5" />
        </Link>
      </motion.div>
    </section>
  );
}

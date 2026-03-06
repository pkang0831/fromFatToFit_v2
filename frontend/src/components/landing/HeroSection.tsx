'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';

export function HeroSection() {
  const { t } = useLanguage();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0a0a0f]">
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(6,182,212,0.15) 0%, transparent 70%)' }}
          animate={{ scale: [1, 1.3, 1], x: [0, 30, 0], y: [0, -20, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute -bottom-32 -left-32 w-[600px] h-[600px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)' }}
          animate={{ scale: [1.2, 1, 1.2], x: [0, -20, 0], y: [0, 30, 0] }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(6,182,212,0.05) 0%, transparent 60%)' }}
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        />
        {/* Grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/[0.06] border border-white/[0.08] text-primary text-sm font-medium rounded-full mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            {t('landing.badge')}
          </span>
        </motion.div>

        <motion.h1
          className="text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-[1.1] mb-6 tracking-tight"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.15 }}
        >
          {t('landing.heroTitle')}{' '}
          <span className="gradient-text">{t('landing.heroHighlight')}</span>
        </motion.h1>

        <motion.p
          className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-12 leading-relaxed"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          {t('landing.heroDescription')}
        </motion.p>

        <motion.div
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.45 }}
        >
          <Link
            href="/register"
            className="group relative px-8 py-4 bg-gradient-primary text-white font-semibold rounded-xl text-lg transition-all hover:shadow-glow-cyan hover:-translate-y-0.5 btn-glow"
            data-testid="hero-cta"
          >
            {t('landing.getStarted')}
          </Link>
          <Link
            href="/login"
            className="px-8 py-4 bg-white/[0.06] text-white font-semibold rounded-xl text-lg border border-white/[0.1] hover:bg-white/[0.1] hover:border-white/[0.2] transition-all hover:-translate-y-0.5 backdrop-blur-sm"
            data-testid="hero-signin"
          >
            {t('landing.signIn')}
          </Link>
        </motion.div>

        {/* Social proof + stats */}
        <motion.div
          className="mt-20 flex flex-col items-center gap-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.7 }}
        >
          {/* Avatar stack */}
          <div className="flex items-center gap-3">
            <div className="flex -space-x-3">
              {['A', 'S', 'J', 'M', 'K'].map((letter, i) => (
                <div
                  key={letter}
                  className="w-9 h-9 rounded-full border-2 border-[#0a0a0f] bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center text-white/80 text-xs font-bold"
                  style={{ zIndex: 5 - i }}
                >
                  {letter}
                </div>
              ))}
            </div>
            <span className="text-sm text-white/40">
              Join <span className="text-primary font-semibold font-number">10,000+</span> users
            </span>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-3 gap-8 md:gap-16">
            {[
              { value: '10K+', labelKey: 'landing.stats.users' },
              { value: '500K+', labelKey: 'landing.stats.meals' },
              { value: '5+', labelKey: 'landing.stats.aiModels' },
            ].map((stat) => (
              <div key={stat.labelKey} className="text-center">
                <div className="text-2xl md:text-3xl font-bold gradient-text font-number">{stat.value}</div>
                <div className="text-xs md:text-sm text-white/40 mt-1">{t(stat.labelKey)}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center p-1.5">
          <motion.div
            className="w-1.5 h-1.5 rounded-full bg-primary"
            animate={{ y: [0, 16, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>
      </motion.div>
    </section>
  );
}

'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { Shield, ArrowRight } from 'lucide-react';

export function HeroSection() {
  const { t } = useLanguage();

  return (
    <section className="relative overflow-hidden bg-[#0a0a0f] py-16 md:min-h-screen md:flex md:items-center md:justify-center">
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(201,169,110,0.15) 0%, transparent 70%)' }}
          animate={{ scale: [1, 1.3, 1], x: [0, 30, 0], y: [0, -20, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute -bottom-32 -left-32 h-[600px] w-[600px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(168,139,122,0.12) 0%, transparent 70%)' }}
          animate={{ scale: [1.2, 1, 1.2], x: [0, -20, 0], y: [0, 30, 0] }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        />
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      <div className="relative z-10 mx-auto max-w-6xl px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <span className="mb-8 inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.06] px-4 py-1.5 text-sm font-medium text-primary backdrop-blur-sm">
            <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            {t('landing.badge')}
          </span>
        </motion.div>

        <motion.h1
          className="mb-6 text-4xl font-bold leading-[1.05] tracking-tight text-white md:text-6xl lg:text-7xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.15 }}
        >
          {t('landing.heroTitle')}{' '}
          <br className="hidden md:block" />
          <span className="gradient-text">{t('landing.heroHighlight')}</span>
        </motion.h1>

        <motion.p
          className="mx-auto mb-4 max-w-3xl text-lg leading-relaxed text-white/72 md:text-xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          {t('landing.heroDescription')}
        </motion.p>

        <motion.p
          className="mb-4 text-sm font-medium text-primary/85"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          {t('landing.heroProof')}
        </motion.p>

        <motion.p
          className="mb-10 text-sm text-white/58"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.45 }}
        >
          {t('landing.heroFounder')}
        </motion.p>

        <motion.div
          className="flex flex-col items-center justify-center gap-4 sm:flex-row"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          <Link
            href="/try"
            className="group relative flex items-center gap-2 rounded-xl bg-gradient-primary px-8 py-4 text-lg font-semibold text-white transition-all hover:-translate-y-0.5 hover:shadow-glow-cyan btn-glow"
            data-testid="hero-cta"
          >
            {t('landing.getStarted')}
            <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
          </Link>
        </motion.div>

        <motion.div
          className="mx-auto mt-14 max-w-5xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.75 }}
        >
          <div className="grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
            <div className="rounded-3xl border border-white/[0.08] bg-white/[0.03] p-4 md:p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="text-left">
                  <p className="text-xs uppercase tracking-[0.24em] text-primary/80">{t('landing.heroStoryLabel')}</p>
                  <p className="mt-1 text-sm text-white/45">{t('landing.heroStoryCaption')}</p>
                </div>
                <div className="hidden items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1 text-xs text-white/50 md:flex">
                  <Shield className="h-3.5 w-3.5 text-primary/70" />
                  <span>{t('landing.heroStoryTrust')}</span>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-black/30">
                  <div className="relative aspect-[4/5]">
                    <Image
                      src="/founder/start.jpg"
                      alt="Founder before the transformation"
                      fill
                      className="object-cover"
                      sizes="(max-width: 640px) 100vw, 50vw"
                      priority
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
                    <div className="absolute inset-x-0 bottom-0 p-4 text-left">
                      <p className="text-xs uppercase tracking-[0.22em] text-primary/90">{t('landing.heroStartLabel')}</p>
                      <p className="mt-2 text-2xl font-bold text-white">{t('landing.heroStartStat')}</p>
                      <p className="mt-2 text-sm text-white/72">{t('landing.heroStartBody')}</p>
                    </div>
                  </div>
                </div>

                <div className="overflow-hidden rounded-2xl border border-primary/20 bg-black/30">
                  <div className="relative aspect-[4/5]">
                    <Image
                      src="/founder/final-body.jpg"
                      alt="Founder after the transformation"
                      fill
                      className="object-cover"
                      sizes="(max-width: 640px) 100vw, 50vw"
                      priority
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
                    <div className="absolute inset-x-0 bottom-0 p-4 text-left">
                      <p className="text-xs uppercase tracking-[0.22em] text-primary/90">{t('landing.heroFinalLabel')}</p>
                      <p className="mt-2 text-2xl font-bold text-white">{t('landing.heroFinalStat')}</p>
                      <p className="mt-2 text-sm text-white/72">{t('landing.heroFinalBody')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-primary/15 bg-primary/[0.04] p-4 text-left lg:hidden">
              <p className="text-xs uppercase tracking-[0.22em] text-primary/85">{t('landing.heroQuoteLabel')}</p>
              <p className="mt-2 text-lg font-semibold text-white">{t('landing.heroQuote')}</p>
              <p className="mt-3 text-sm leading-relaxed text-white/65">{t('landing.heroQuoteBody')}</p>
            </div>

            <div className="hidden rounded-3xl border border-white/[0.08] bg-white/[0.02] p-4 md:p-5 lg:block">
              <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-black/20">
                <div className="relative aspect-[4/5]">
                  <Image
                    src="/founder/final-portrait.jpg"
                    alt="Founder portrait after the transformation"
                    fill
                    className="object-cover"
                    sizes="(max-width: 1024px) 100vw, 30vw"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
                </div>
              </div>

              <div className="mt-4 rounded-2xl border border-primary/15 bg-primary/[0.04] p-4 text-left">
                <p className="text-xs uppercase tracking-[0.22em] text-primary/85">{t('landing.heroQuoteLabel')}</p>
                <p className="mt-2 text-lg font-semibold text-white">{t('landing.heroQuote')}</p>
                <p className="mt-3 text-sm leading-relaxed text-white/65">{t('landing.heroQuoteBody')}</p>
              </div>

              <div className="mt-4 flex items-center justify-center gap-2 text-xs text-white/35">
                <Shield className="h-3.5 w-3.5" />
                <span>{t('landing.heroStoryTrust')}</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-white/20 p-1.5">
          <motion.div
            className="h-1.5 w-1.5 rounded-full bg-primary"
            animate={{ y: [0, 16, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>
      </motion.div>
    </section>
  );
}

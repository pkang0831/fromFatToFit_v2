'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { ArrowRight, Camera, ScanFace, Sparkles, Target } from 'lucide-react';

import { EcosystemConstellationDemo } from '@/components/ui/ecosystem-constellation-demo';

export function HeroSection() {
  const { t } = useLanguage();

  return (
    <section className="relative overflow-hidden bg-[#06060b] py-16 md:min-h-screen md:flex md:items-center">
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-36 right-0 h-[560px] w-[560px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 72%)' }}
          animate={{ scale: [1, 1.2, 1], x: [0, 24, 0], y: [0, -24, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute -bottom-40 -left-28 h-[620px] w-[620px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)' }}
          animate={{ scale: [1.18, 1, 1.18], x: [0, -18, 0], y: [0, 26, 0] }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        />
        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '72px 72px',
          }}
        />
      </div>

      <div className="relative z-10 mx-auto grid max-w-7xl gap-12 px-6 lg:grid-cols-[0.92fr_1.08fr] lg:items-center">
        <div className="text-left">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.05] px-4 py-1.5 text-sm font-medium text-primary backdrop-blur-sm">
              <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
              {t('landing.badge')}
            </span>
          </motion.div>

          <motion.h1
            className="mt-8 text-4xl font-bold leading-[0.98] tracking-tight text-white md:text-6xl xl:text-7xl"
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
          >
            {t('landing.heroTitle')}
            <br className="hidden md:block" />
            <span className="gradient-text">{t('landing.heroHighlight')}</span>
          </motion.h1>

          <motion.p
            className="mt-6 max-w-2xl text-lg leading-relaxed text-white/68 md:text-xl"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            {t('landing.heroDescription')}
          </motion.p>

          <motion.div
            className="mt-8 flex flex-wrap gap-3"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            {[
              { label: 'Choose your goal', icon: Target },
              { label: 'Scan your baseline', icon: ScanFace },
              { label: 'Keep weekly proof', icon: Camera },
            ].map(({ label, icon: Icon }) => (
              <div
                key={label}
                className="inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.04] px-4 py-2 text-sm text-white/72"
              >
                <Icon className="h-4 w-4 text-primary" />
                <span>{label}</span>
              </div>
            ))}
          </motion.div>

          <motion.div
            className="mt-10 flex flex-col gap-4 sm:flex-row"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Link
              href="/goal-planner"
              className="group relative inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-violet-500 via-fuchsia-500 to-blue-500 px-8 py-4 text-lg font-semibold text-white transition-all hover:-translate-y-0.5 hover:shadow-[0_18px_60px_rgba(139,92,246,0.3)]"
              data-testid="hero-cta"
            >
              Start with your goal
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/try"
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/[0.1] bg-white/[0.04] px-8 py-4 text-lg font-semibold text-white/84 transition-all hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
            >
              Try the free scan
            </Link>
          </motion.div>

          <motion.div
            className="mt-10 grid gap-4 sm:grid-cols-3"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            <div className="rounded-3xl border border-white/[0.08] bg-white/[0.03] p-5">
              <p className="text-xs uppercase tracking-[0.22em] text-primary/75">Why it feels better</p>
              <p className="mt-3 text-base font-semibold text-white">One place to start</p>
              <p className="mt-2 text-sm leading-6 text-white/56">
                We stop throwing random features at new users on the first screen.
              </p>
            </div>
            <div className="rounded-3xl border border-white/[0.08] bg-white/[0.03] p-5">
              <p className="text-xs uppercase tracking-[0.22em] text-primary/75">What you measure</p>
              <p className="mt-3 text-base font-semibold text-white">Eyes first, numbers second</p>
              <p className="mt-2 text-sm leading-6 text-white/56">
                This product is for body-change proof, not for drowning in abstract stats.
              </p>
            </div>
            <div className="rounded-3xl border border-white/[0.08] bg-white/[0.03] p-5">
              <p className="text-xs uppercase tracking-[0.22em] text-primary/75">Real reason to return</p>
              <p className="mt-3 text-base font-semibold text-white">Weekly proof loop</p>
              <p className="mt-2 text-sm leading-6 text-white/56">
                Come back when motivation is shaky and let the visual record speak first.
              </p>
            </div>
          </motion.div>
        </div>

        <motion.div
          className="relative"
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.2 }}
        >
          <div className="absolute -inset-6 rounded-[36px] bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.18),transparent_68%)] blur-3xl" />
          <div className="relative overflow-hidden rounded-[32px] border border-white/[0.08] bg-white/[0.03] p-3 shadow-[0_36px_120px_rgba(0,0,0,0.34)]">
            <div className="pointer-events-none absolute left-8 top-8 z-10 rounded-full border border-white/[0.08] bg-black/40 px-3 py-1 text-xs uppercase tracking-[0.22em] text-white/68 backdrop-blur-md">
              Your body-change loop
            </div>

            <EcosystemConstellationDemo />

            <div className="absolute inset-x-6 bottom-6 z-10 grid gap-3 rounded-[28px] border border-white/[0.08] bg-black/42 p-4 backdrop-blur-xl md:grid-cols-3">
              <div className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-primary/80">Goal</p>
                <p className="mt-1 text-sm font-medium text-white">Pick cut, bulk, recomp, or maintain.</p>
              </div>
              <div className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-primary/80">Baseline</p>
                <p className="mt-1 text-sm font-medium text-white">Use one scan to anchor the starting point.</p>
              </div>
              <div className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-primary/80">Proof</p>
                <p className="mt-1 text-sm font-medium text-white">Return weekly so progress is visible.</p>
              </div>
            </div>
          </div>

          <div className="mt-4 flex items-center gap-2 text-sm text-white/45">
            <Sparkles className="h-4 w-4 text-primary/80" />
            <span>Designed to feel like one clear product again, not a pile of tools.</span>
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

'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export function FounderStorySection() {
  return (
    <section className="py-24 px-6 bg-[#0a0a0f] relative overflow-hidden">
      <div
        className="absolute inset-0 opacity-30"
        style={{ background: 'radial-gradient(ellipse at 30% 60%, rgba(168,139,122,0.08) 0%, transparent 60%)' }}
      />

      <div className="max-w-5xl mx-auto relative z-10">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/[0.06] border border-white/[0.08] text-primary text-xs font-semibold uppercase tracking-[0.2em] rounded-full mb-6">
            Why this exists
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Built by someone who{' '}
            <span className="gradient-text">lost 50kg.</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          {/* Before / After photos */}
          <motion.div
            className="flex gap-4"
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.7 }}
          >
            <div className="flex-1 rounded-2xl overflow-hidden border border-white/[0.08] bg-white/[0.02]">
              <div className="relative aspect-[3/4] w-full">
                <Image
                  src="/images/founder/before.jpg"
                  alt="Founder at 120kg"
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 45vw, 240px"
                  loading="lazy"
                  quality={60}
                />
              </div>
              <div className="px-4 py-3 text-center border-t border-white/[0.06]">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/40">120 kg</p>
                <p className="text-[11px] text-white/25 mt-0.5">The mirror showed the same person every day</p>
              </div>
            </div>

            <div className="flex-1 rounded-2xl overflow-hidden border border-primary/30 bg-primary/[0.02]">
              <div className="relative aspect-[3/4] w-full">
                <Image
                  src="/images/founder/after.jpg"
                  alt="Founder at 70kg"
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 45vw, 240px"
                  loading="lazy"
                  quality={60}
                />
              </div>
              <div className="px-4 py-3 text-center border-t border-primary/20">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary/80">70 kg</p>
                <p className="text-[11px] text-primary/40 mt-0.5">The change happened long before I could see it</p>
              </div>
            </div>
          </motion.div>

          {/* Story text */}
          <motion.div
            className="space-y-6"
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.7, delay: 0.15 }}
          >
            <blockquote className="text-2xl md:text-3xl font-bold text-white leading-snug">
              &ldquo;The hardest part of losing 50kg wasn&apos;t the diet.
              It was the months where the mirror showed nothing.&rdquo;
            </blockquote>

            <div className="space-y-4 text-white/50 leading-relaxed">
              <p>
                I lost 1kg. Couldn&apos;t see it. Lost 3kg. Still couldn&apos;t see it.
                Nobody said a word. That&apos;s when quitting felt rational — not weak, rational.
              </p>
              <p>
                The worst lie your brain tells you mid-cut is: <em className="text-white/70">&ldquo;Nothing is changing.&rdquo;</em>{' '}
                Your eyes adapt to the body they see every day. You literally cannot see your own progress.
              </p>
              <p>
                So I built the tool I wish I&apos;d had.
                Not another motivational app. A <span className="text-white font-semibold">weekly proof system</span> that
                shows you — in numbers and side-by-side photos — that the gap is closing, even when
                the mirror says otherwise.
              </p>
            </div>

            <div className="pt-4 border-t border-white/[0.06]">
              <p className="text-sm text-white/30 mb-4">
                If you&apos;re in a cut right now and fighting the urge to quit — this is for you.
              </p>
              <Link
                href="/try"
                className="group inline-flex items-center gap-2 px-6 py-3 bg-gradient-primary text-white font-semibold rounded-xl transition-all hover:shadow-glow-cyan hover:-translate-y-0.5 btn-glow"
              >
                Try your free scan
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

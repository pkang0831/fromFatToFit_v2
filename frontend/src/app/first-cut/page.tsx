'use client';

import Image from 'next/image';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Target, BarChart3, ImageIcon, Shield } from 'lucide-react';

export default function FirstCutLanding() {
  return (
    <main className="overflow-hidden bg-[#0a0a0f] text-white">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-6">
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(201,169,110,0.12) 0%, transparent 70%)' }}
          />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-red-500/10 border border-red-500/20 text-red-300 text-xs font-semibold uppercase tracking-[0.2em] rounded-full mb-6">
                First real cut
              </span>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-[1.1] mb-6 tracking-tight">
                Your first cut is when the{' '}
                <span className="gradient-text">mirror is cruelest.</span>
              </h1>
              <p className="text-lg text-white/50 mb-4 leading-relaxed">
                You&apos;re eating less, training harder, and the scale moved — but the mirror shows the same person.
                That&apos;s not failure. That&apos;s your eyes adapting to the body they see every day.
              </p>
              <p className="text-white/70 font-medium mb-8">
                This app exists because the founder went through 50kg of that silence and almost quit.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <Link
                  href="/try"
                  className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-primary text-white font-semibold rounded-xl text-lg transition-all hover:shadow-glow-cyan hover:-translate-y-0.5 btn-glow"
                >
                  Free body scan — no sign-up
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </motion.div>

            <motion.div
              className="flex gap-4"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <div className="flex-1 rounded-2xl overflow-hidden border border-white/[0.08]">
                <div className="relative aspect-[3/4]">
                  <Image src="/images/founder/before.jpg" alt="Before" fill className="object-cover" sizes="240px" />
                </div>
                <div className="px-3 py-2.5 text-center bg-white/[0.02] border-t border-white/[0.06]">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/35">Day 1</p>
                </div>
              </div>
              <div className="flex-1 rounded-2xl overflow-hidden border border-primary/30">
                <div className="relative aspect-[3/4]">
                  <Image src="/images/founder/after.jpg" alt="After" fill className="object-cover" sizes="240px" />
                </div>
                <div className="px-3 py-2.5 text-center bg-primary/[0.04] border-t border-primary/20">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-primary/70">Proof</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Problem */}
      <section className="py-20 px-6 bg-[#080810]">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-8">
              Week 2 is when most people quit their first cut.
            </h2>
            <div className="space-y-4 text-white/50 leading-relaxed text-lg">
              <p>
                Not because the diet is too hard. Because they look in the mirror and see <span className="text-white font-medium">nothing different</span>.
              </p>
              <p>
                The scale says -2kg. The mirror says &ldquo;same.&rdquo; Nobody at the gym notices.
                Your brain starts building the case: <em className="text-white/70">&ldquo;Maybe this isn&apos;t working.&rdquo;</em>
              </p>
              <p>
                It is working. You just can&apos;t see it. And that&apos;s exactly the problem this app solves.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
            Weekly proof that your cut is working.
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: Target, title: 'Set your target', desc: 'Upload a photo. See what you could look like at your goal body fat. That image becomes your benchmark — not a vague number.' },
              { icon: BarChart3, title: 'Scan every week', desc: 'Each scan updates your body fat estimate and shows the gap shrinking. Side-by-side with last week. Numbers that prove the mirror is lying.' },
              { icon: ImageIcon, title: 'Stack your proof', desc: 'Progress photos, weight trends, and gap charts build a timeline. By week 8, you have undeniable evidence that the cut worked.' },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                className="p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02]"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
              >
                <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-4">
                  <item.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-white/45 leading-relaxed text-sm">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-[#080810]">
        <motion.div
          className="max-w-2xl mx-auto text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Don&apos;t quit your cut because the mirror is slow.
          </h2>
          <p className="text-lg text-white/45 mb-8">
            Free first scan. No sign-up. See where you stand in 60 seconds.
          </p>
          <Link
            href="/try"
            className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-gradient-primary text-white font-semibold text-lg shadow-glow-cyan hover:scale-105 transition-transform"
          >
            Try Free Body Scan
            <ArrowRight className="w-5 h-5" />
          </Link>
          <div className="flex items-center justify-center gap-2 mt-6 text-white/25 text-xs">
            <Shield className="w-3.5 h-3.5" />
            <span>Photos encrypted & never shared</span>
          </div>
        </motion.div>
      </section>
    </main>
  );
}

'use client';

import Image from 'next/image';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, CalendarClock, BarChart3, ImageIcon, Shield } from 'lucide-react';

const deadlines = [
  { label: 'Summer body', weeks: '12 weeks', color: 'text-amber-300', bg: 'bg-amber-500/10 border-amber-500/20' },
  { label: 'Wedding prep', weeks: '16 weeks', color: 'text-rose-300', bg: 'bg-rose-500/10 border-rose-500/20' },
  { label: 'Photoshoot', weeks: '8 weeks', color: 'text-cyan-300', bg: 'bg-cyan-500/10 border-cyan-500/20' },
  { label: 'Reunion / trip', weeks: '10 weeks', color: 'text-emerald-300', bg: 'bg-emerald-500/10 border-emerald-500/20' },
];

export default function DeadlineLanding() {
  return (
    <main className="overflow-hidden bg-[#0a0a0f] text-white">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-6">
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="absolute -bottom-32 -left-32 w-[600px] h-[600px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(168,139,122,0.1) 0%, transparent 70%)' }}
          />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold uppercase tracking-[0.2em] rounded-full mb-6">
                <CalendarClock className="w-3.5 h-3.5" />
                Deadline approaching
              </span>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-[1.1] mb-6 tracking-tight">
                D-12 weeks.{' '}
                <span className="gradient-text">See the gap close every week.</span>
              </h1>
              <p className="text-lg text-white/50 mb-8 leading-relaxed">
                Summer, wedding, photoshoot, trip — you have a date and a body you want to show up in.
                This app shows you each week whether you&apos;re on track. Not hope. Proof.
              </p>

              <div className="flex flex-wrap gap-2 mb-8">
                {deadlines.map(d => (
                  <span key={d.label} className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${d.bg} ${d.color}`}>
                    {d.label} · {d.weeks}
                  </span>
                ))}
              </div>

              <Link
                href="/try"
                className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-primary text-white font-semibold rounded-xl text-lg transition-all hover:shadow-glow-cyan hover:-translate-y-0.5 btn-glow"
              >
                Start with a free scan
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
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
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/35">Week 0</p>
                </div>
              </div>
              <div className="flex-1 rounded-2xl overflow-hidden border border-primary/30">
                <div className="relative aspect-[3/4]">
                  <Image src="/images/founder/after.jpg" alt="After" fill className="object-cover" sizes="240px" />
                </div>
                <div className="px-3 py-2.5 text-center bg-primary/[0.04] border-t border-primary/20">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-primary/70">Deadline</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-20 px-6 bg-[#080810]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
            What 12 weeks of weekly proof looks like.
          </h2>

          <div className="space-y-6">
            {[
              { week: 'Week 1', title: 'Your baseline scan', desc: 'Body fat estimate, goal preview, starting point locked in. You know exactly where you stand.', accent: 'border-white/10' },
              { week: 'Week 4', title: 'First visible gap change', desc: 'BF trending down. Side-by-side photos show what the mirror won\'t. You\'re ahead of where you think.', accent: 'border-primary/30' },
              { week: 'Week 8', title: 'Undeniable proof', desc: 'Your progress timeline has 8 data points, 8 photos, and a gap chart going in one direction. No more doubt.', accent: 'border-primary/50' },
              { week: 'Week 12', title: 'Deadline ready', desc: 'You walk into that room, that beach, that studio knowing exactly how far you came — because you measured every week.', accent: 'border-emerald-500/50' },
            ].map((item, i) => (
              <motion.div
                key={item.week}
                className={`flex gap-6 p-6 rounded-2xl border bg-white/[0.02] ${item.accent}`}
                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="w-20 flex-shrink-0">
                  <span className="text-xs font-bold uppercase tracking-[0.2em] text-primary/70">{item.week}</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-1">{item.title}</h3>
                  <p className="text-white/45 text-sm leading-relaxed">{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <motion.div
          className="max-w-2xl mx-auto text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Your deadline won&apos;t move. Start your proof today.
          </h2>
          <p className="text-lg text-white/45 mb-8">
            Free first scan. No sign-up. See your starting point in 60 seconds.
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

'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Users, BarChart3, Bell, Shield, Camera, TrendingDown } from 'lucide-react';

export default function CoachesLanding() {
  return (
    <main className="overflow-hidden bg-[#0a0a0f] text-white">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-6">
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(201,169,110,0.1) 0%, transparent 70%)' }}
          />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold uppercase tracking-[0.2em] rounded-full mb-6">
              <Users className="w-3.5 h-3.5" />
              For online coaches & trainers
            </span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-[1.1] mb-6 tracking-tight">
              Your client quits at week 4 because{' '}
              <span className="gradient-text">they can&apos;t see the change.</span>
            </h1>
            <p className="text-lg text-white/50 max-w-2xl mx-auto mb-8 leading-relaxed">
              You know they&apos;re progressing. Their macros are dialed. But they look in the mirror, see nothing,
              and ghost you. Devenira gives them weekly visual proof so you stop losing clients to their own eyes.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/try"
                className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-primary text-white font-semibold rounded-xl text-lg transition-all hover:shadow-glow-cyan hover:-translate-y-0.5 btn-glow"
              >
                Try it yourself first
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="mailto:coaches@devenira.com"
                className="inline-flex items-center gap-2 px-6 py-3 border border-white/[0.1] text-white/70 rounded-xl hover:border-white/20 hover:text-white transition-all"
              >
                Contact for group plans
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pain points */}
      <section className="py-20 px-6 bg-[#080810]">
        <div className="max-w-5xl mx-auto">
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-white text-center mb-4"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            The three reasons clients ghost mid-program.
          </motion.h2>
          <p className="text-center text-white/40 mb-12 max-w-2xl mx-auto">
            You&apos;ve seen all three. Devenira fixes each one.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: Camera,
                problem: '"I don\'t look any different"',
                fix: 'Weekly AI body scans with side-by-side comparisons. Numbers + photos that show what the mirror hides.',
              },
              {
                icon: TrendingDown,
                problem: '"I don\'t know if this is working"',
                fix: 'Gap-to-goal tracking with body fat trends. A dashboard showing their target getting closer each week.',
              },
              {
                icon: Bell,
                problem: '"I forgot / I\'ll do it tomorrow"',
                fix: 'Automated weekly check-in reminders. One scan per week takes 60 seconds. Habit, not motivation.',
              },
            ].map((item, i) => (
              <motion.div
                key={item.problem}
                className="p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02]"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
              >
                <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
                  <item.icon className="w-6 h-6 text-rose-300" />
                </div>
                <p className="text-white font-semibold mb-3">{item.problem}</p>
                <p className="text-white/45 text-sm leading-relaxed">{item.fix}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How coaches use it */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
            How coaches use Devenira as a retention layer.
          </h2>

          <div className="space-y-6">
            {[
              { step: '01', title: 'Send your client a link', desc: 'They do their first scan in 60 seconds, no app download needed. Their baseline is set.' },
              { step: '02', title: 'They check in weekly', desc: 'Each Sunday they scan. The app sends reminders. You don\'t have to chase them for progress photos.' },
              { step: '03', title: 'You both see the proof', desc: 'Body fat trends, gap-to-goal charts, side-by-side photos. When they wobble at week 4, the data shows the truth.' },
              { step: '04', title: 'Retention goes up', desc: 'Clients who see weekly evidence stay longer. The app doesn\'t replace you — it makes your coaching stick.' },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                className="flex gap-6 p-6 rounded-2xl border border-white/[0.06] bg-white/[0.02]"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-lg font-bold text-emerald-300">{item.step}</span>
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

      {/* Stats */}
      <section className="py-16 px-6 bg-[#080810]">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            {[
              { stat: '50kg', label: 'Founder\'s own transformation', sub: '120kg → 70kg' },
              { stat: '60s', label: 'Per weekly check-in', sub: 'One photo, one scan' },
              { stat: 'Week 2→8', label: 'The danger zone this covers', sub: 'When clients quit most' },
            ].map((item, i) => (
              <motion.div
                key={item.stat}
                className="p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02]"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <p className="text-3xl font-bold text-white mb-1">{item.stat}</p>
                <p className="text-sm text-white/60 font-medium">{item.label}</p>
                <p className="text-xs text-white/30 mt-1">{item.sub}</p>
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
            Stop losing clients to their own mirror.
          </h2>
          <p className="text-lg text-white/45 mb-8">
            Try the scan yourself. Then send it to one client who&apos;s wobbling.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/try"
              className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-gradient-primary text-white font-semibold text-lg shadow-glow-cyan hover:scale-105 transition-transform"
            >
              Try Free Scan
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="mailto:coaches@devenira.com"
              className="inline-flex items-center gap-2 px-6 py-3 border border-white/[0.1] text-white/70 rounded-xl hover:border-white/20 hover:text-white transition-all"
            >
              Group pricing inquiry
            </a>
          </div>
          <div className="flex items-center justify-center gap-2 mt-6 text-white/25 text-xs">
            <Shield className="w-3.5 h-3.5" />
            <span>Client photos encrypted & never shared</span>
          </div>
        </motion.div>
      </section>
    </main>
  );
}

'use client';

import Link from 'next/link';
import { ArrowRight, Camera, Flame, Dumbbell, Sparkles } from 'lucide-react';

const START_OPTIONS = [
  {
    title: 'Cut body fat',
    body: 'Best if you want to get leaner, tighten up, or finally close the gap to a lower body-fat target.',
    href: '/goal-planner?intent=cut',
    icon: Flame,
    tone: 'from-rose-500/18 to-orange-500/10 border-rose-400/20',
  },
  {
    title: 'Build muscle',
    body: 'Use this if your priority is lean size, more strength, or a clean bulk instead of a deeper cut.',
    href: '/goal-planner?intent=lean_bulk',
    icon: Dumbbell,
    tone: 'from-sky-500/18 to-cyan-500/10 border-sky-400/20',
  },
  {
    title: 'Recomp slowly',
    body: 'For people who want to stay roughly the same weight while looking tighter, leaner, and more athletic.',
    href: '/goal-planner?intent=recomp',
    icon: Sparkles,
    tone: 'from-emerald-500/18 to-teal-500/10 border-emerald-400/20',
  },
];

export function StartHereSection() {
  return (
    <section className="bg-[#080810] px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-primary/80">Start Here</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-white md:text-5xl">
            Pick what you want first.
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-white/60">
            The current app throws too many features at you at once. We start simpler:
            choose your goal, then we guide the next step.
          </p>
        </div>

        <div className="mt-10 grid gap-5 lg:grid-cols-[1fr_1fr_1fr_0.9fr]">
          {START_OPTIONS.map(({ title, body, href, icon: Icon, tone }) => (
            <Link
              key={title}
              href={href}
              className={`group rounded-3xl border bg-gradient-to-br ${tone} p-6 transition-all duration-200 hover:-translate-y-1 hover:border-primary/40 hover:bg-white/[0.04]`}
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
                <Icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="mt-5 text-xl font-semibold text-white">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-white/60">{body}</p>
              <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary">
                Start with this goal
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </Link>
          ))}

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
              <Camera className="h-5 w-5 text-primary" />
            </div>
            <h3 className="mt-5 text-xl font-semibold text-white">Just scan me first</h3>
            <p className="mt-3 text-sm leading-6 text-white/60">
              If you do not know your goal yet, start with a free body scan and use that result as your baseline.
            </p>
            <Link
              href="/try"
              className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-white/85 transition-colors hover:text-primary"
            >
              Try the free scan
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

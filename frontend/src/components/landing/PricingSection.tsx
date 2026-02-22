'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    credits: '10 credits/month',
    highlight: false,
    features: [
      '10 credits per month',
      'Food camera analysis (1 credit)',
      'Body fat scan (5 credits)',
      'Basic progress charts',
      'Workout logging',
    ],
    cta: 'Start Free',
    href: '/register',
  },
  {
    name: 'Pro',
    price: '$9.99',
    period: '/month',
    credits: '100 credits/month',
    highlight: true,
    features: [
      '100 credits per month',
      'All AI features unlocked',
      'Transformation previews (10 credits)',
      'AI meal recommendations (2 credits)',
      'Priority support',
      'Advanced analytics',
    ],
    cta: 'Go Pro',
    href: '/register',
    badge: 'Most Popular',
  },
  {
    name: 'Credit Pack',
    price: '$4.99',
    period: 'one-time',
    credits: '50 credits',
    highlight: false,
    features: [
      '50 credits (never expire)',
      'Stack on top of any plan',
      'Use for any AI feature',
      'Buy as many as you need',
    ],
    cta: 'Buy Credits',
    href: '/register',
  },
];

export function PricingSection() {
  return (
    <section className="py-24 px-6 bg-white dark:bg-gray-800">
      <div className="max-w-6xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Simple, Credit-Based Pricing</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Pay only for what you use. Every AI feature has a clear credit cost.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              className={`relative rounded-2xl p-8 ${
                plan.highlight
                  ? 'bg-primary text-white shadow-xl scale-105 border-2 border-primary'
                  : 'bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-700 hover:border-primary/20'
              } transition-all`}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: i * 0.15 }}
            >
              {plan.badge && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-premium text-gray-900 dark:text-white text-sm font-semibold rounded-full">
                  {plan.badge}
                </span>
              )}

              <h3 className={`text-xl font-semibold mb-2 ${plan.highlight ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
                {plan.name}
              </h3>
              <div className="mb-1">
                <span className={`text-4xl font-bold ${plan.highlight ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
                  {plan.price}
                </span>
                <span className={`text-sm ml-1 ${plan.highlight ? 'text-white/70' : 'text-gray-600 dark:text-gray-400'}`}>
                  {plan.period}
                </span>
              </div>
              <p className={`text-sm mb-6 ${plan.highlight ? 'text-white/80' : 'text-primary font-medium'}`}>
                {plan.credits}
              </p>

              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <svg
                      className={`w-5 h-5 mt-0.5 flex-shrink-0 ${plan.highlight ? 'text-white/90' : 'text-success'}`}
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className={`text-sm ${plan.highlight ? 'text-white/90' : 'text-gray-600 dark:text-gray-400'}`}>
                      {f}
                    </span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.href}
                className={`block w-full py-3 text-center font-semibold rounded-xl transition-all ${
                  plan.highlight
                    ? 'bg-white text-primary hover:bg-white/90'
                    : 'bg-primary text-white hover:bg-primary-dark'
                }`}
              >
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

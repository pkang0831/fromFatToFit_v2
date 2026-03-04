'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';

const planDefs = [
  {
    nameKey: 'landing.planFree',
    price: '$0',
    periodKey: 'landing.planFreePeriod',
    creditsKey: 'landing.planFreeCredits',
    highlight: false,
    featureKeys: [
      'landing.planFreeFeature1', 'landing.planFreeFeature2', 'landing.planFreeFeature3',
      'landing.planFreeFeature4', 'landing.planFreeFeature5',
    ],
    ctaKey: 'landing.planFreeCta',
    href: '/register',
  },
  {
    nameKey: 'landing.planPro',
    price: '$9.99',
    periodKey: 'landing.planProPeriod',
    creditsKey: 'landing.planProCredits',
    highlight: true,
    featureKeys: [
      'landing.planProFeature1', 'landing.planProFeature2', 'landing.planProFeature3',
      'landing.planProFeature4', 'landing.planProFeature5', 'landing.planProFeature6',
    ],
    ctaKey: 'landing.planProCta',
    href: '/register',
    badgeKey: 'landing.planProBadge',
  },
  {
    nameKey: 'landing.planPack',
    price: '$4.99',
    periodKey: 'landing.planPackPeriod',
    creditsKey: 'landing.planPackCredits',
    highlight: false,
    featureKeys: [
      'landing.planPackFeature1', 'landing.planPackFeature2',
      'landing.planPackFeature3', 'landing.planPackFeature4',
    ],
    ctaKey: 'landing.planPackCta',
    href: '/register',
  },
];

export function PricingSection() {
  const { t } = useLanguage();

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
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">{t('landing.pricingTitle')}</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            {t('landing.pricingSubtitle')}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
          {planDefs.map((plan, i) => (
            <motion.div
              key={plan.nameKey}
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
              {plan.badgeKey && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-premium text-gray-900 dark:text-white text-sm font-semibold rounded-full">
                  {t(plan.badgeKey)}
                </span>
              )}

              <h3 className={`text-xl font-semibold mb-2 ${plan.highlight ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
                {t(plan.nameKey)}
              </h3>
              <div className="mb-1">
                <span className={`text-4xl font-bold ${plan.highlight ? 'text-white' : 'text-gray-900 dark:text-white'}`}>
                  {plan.price}
                </span>
                <span className={`text-sm ml-1 ${plan.highlight ? 'text-white/70' : 'text-gray-600 dark:text-gray-400'}`}>
                  {t(plan.periodKey)}
                </span>
              </div>
              <p className={`text-sm mb-6 ${plan.highlight ? 'text-white/80' : 'text-primary font-medium'}`}>
                {t(plan.creditsKey)}
              </p>

              <ul className="space-y-3 mb-8">
                {plan.featureKeys.map((fKey) => (
                  <li key={fKey} className="flex items-start gap-2">
                    <svg
                      className={`w-5 h-5 mt-0.5 flex-shrink-0 ${plan.highlight ? 'text-white/90' : 'text-success'}`}
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className={`text-sm ${plan.highlight ? 'text-white/90' : 'text-gray-600 dark:text-gray-400'}`}>
                      {t(fKey)}
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
                {t(plan.ctaKey)}
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

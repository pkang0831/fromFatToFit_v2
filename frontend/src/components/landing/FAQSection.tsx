'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/contexts/LanguageContext';

const faqKeys = [
  { qKey: 'faq.bodyfatAccuracy.q', aKey: 'faq.bodyfatAccuracy.a' },
  { qKey: 'faq.credits.q', aKey: 'faq.credits.a' },
  { qKey: 'faq.foodCamera.q', aKey: 'faq.foodCamera.a' },
  { qKey: 'faq.transformation.q', aKey: 'faq.transformation.a' },
  { qKey: 'faq.cancel.q', aKey: 'faq.cancel.a' },
  { qKey: 'faq.dataSecurity.q', aKey: 'faq.dataSecurity.a' },
];

export function FAQSection() {
  const { t } = useLanguage();
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section className="py-24 px-6 bg-white dark:bg-gray-800">
      <div className="max-w-3xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">{t('landing.faq')}</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">{t('landing.faqSubtitle')}</p>
        </motion.div>

        <div className="space-y-4">
          {faqKeys.map((faq, i) => (
            <motion.div
              key={i}
              className="border border-gray-100 dark:border-gray-700 rounded-xl overflow-hidden"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-30px' }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-5 text-left bg-gray-50 dark:bg-gray-950 hover:bg-gray-100 dark:bg-gray-700 transition-colors"
              >
                <span className="font-medium text-gray-900 dark:text-white pr-4">{t(faq.qKey)}</span>
                <motion.svg
                  className="w-5 h-5 text-gray-500 dark:text-gray-500 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  animate={{ rotate: openIndex === i ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </motion.svg>
              </button>
              <AnimatePresence>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 pb-5 text-gray-600 dark:text-gray-400 leading-relaxed">
                      {t(faq.aKey)}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

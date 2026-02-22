'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const faqs = [
  {
    q: 'How accurate is the body fat scan?',
    a: 'Our AI model is trained on thousands of labeled body images and achieves an accuracy comparable to skinfold caliper measurements (within 2-3% margin). For clinical precision, we still recommend DEXA scans.',
  },
  {
    q: 'How does the credit system work?',
    a: 'Every AI-powered feature costs a set number of credits. Free users get 10 credits per month. Pro subscribers get 100 credits per month. You can also purchase credit packs that never expire.',
  },
  {
    q: 'Is the food camera accurate?',
    a: 'The food camera uses advanced vision AI to identify foods and estimate portions. It works best with clearly visible, separated foods. You can always adjust the estimates manually for perfect accuracy.',
  },
  {
    q: 'What is the transformation preview?',
    a: 'It uses AI image editing to show you a realistic preview of what your body could look like at a different body fat percentage. It preserves your identity and produces natural-looking results.',
  },
  {
    q: 'Can I cancel my subscription anytime?',
    a: 'Yes, you can cancel your Pro subscription at any time. You will keep your credits until the end of the billing period. Purchased credit packs never expire regardless of subscription status.',
  },
  {
    q: 'Is my data secure?',
    a: 'Absolutely. All photos are processed securely and are never shared. Your health data is encrypted and stored following industry best practices. You can delete your data at any time.',
  },
];

export function FAQSection() {
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
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Frequently Asked Questions</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">Got questions? We have answers.</p>
        </motion.div>

        <div className="space-y-4">
          {faqs.map((faq, i) => (
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
                <span className="font-medium text-gray-900 dark:text-white pr-4">{faq.q}</span>
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
                      {faq.a}
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

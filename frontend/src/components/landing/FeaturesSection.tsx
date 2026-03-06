'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, BarChart3, Scan, Zap, TrendingUp, Brain } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

const features = [
  { icon: Camera, color: 'from-cyan-400 to-cyan-600' },
  { icon: BarChart3, color: 'from-violet-400 to-violet-600' },
  { icon: Scan, color: 'from-cyan-400 to-violet-500' },
  { icon: Zap, color: 'from-amber-400 to-orange-500' },
  { icon: TrendingUp, color: 'from-emerald-400 to-emerald-600' },
  { icon: Brain, color: 'from-pink-400 to-rose-600' },
];

const featureKeys = [
  { titleKey: 'landing.feature1Title', descKey: 'landing.feature1Desc' },
  { titleKey: 'landing.feature2Title', descKey: 'landing.feature2Desc' },
  { titleKey: 'landing.feature3Title', descKey: 'landing.feature3Desc' },
  { titleKey: 'landing.feature4Title', descKey: 'landing.feature4Desc' },
  { titleKey: 'landing.feature5Title', descKey: 'landing.feature5Desc' },
  { titleKey: 'landing.feature6Title', descKey: 'landing.feature6Desc' },
];

export function FeaturesSection() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState(0);

  return (
    <section className="py-24 px-6 bg-[#0a0a0f] relative overflow-hidden">
      {/* Subtle background gradient */}
      <div
        className="absolute inset-0 opacity-30"
        style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(6,182,212,0.08) 0%, transparent 60%)' }}
      />

      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {t('landing.featuresTitle')}{' '}
            <span className="gradient-text">{t('landing.featuresHighlight')}</span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            {t('landing.featuresSubtitle')}
          </p>
        </motion.div>

        {/* Tab navigation */}
        <motion.div
          className="flex flex-wrap justify-center gap-2 mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {featureKeys.map((feature, i) => {
            const Icon = features[i].icon;
            return (
              <button
                key={feature.titleKey}
                onClick={() => setActiveTab(i)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${
                  activeTab === i
                    ? 'bg-gradient-primary text-white shadow-glow-cyan'
                    : 'text-white/50 hover:text-white/80 hover:bg-white/[0.04]'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{t(feature.titleKey)}</span>
              </button>
            );
          })}
        </motion.div>

        {/* Active feature detail */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm p-8 md:p-12 mb-16"
          >
            <div className="flex flex-col md:flex-row items-center gap-8">
              <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${features[activeTab].color} flex items-center justify-center flex-shrink-0`}>
                {(() => {
                  const Icon = features[activeTab].icon;
                  return <Icon className="w-10 h-10 text-white" />;
                })()}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-3">{t(featureKeys[activeTab].titleKey)}</h3>
                <p className="text-white/50 leading-relaxed text-lg">{t(featureKeys[activeTab].descKey)}</p>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {featureKeys.map((feature, i) => {
            const Icon = features[i].icon;
            return (
              <motion.div
                key={feature.titleKey}
                className={`group p-6 rounded-2xl border transition-all duration-300 cursor-pointer ${
                  activeTab === i
                    ? 'border-primary/30 bg-primary/[0.04]'
                    : 'border-white/[0.06] bg-white/[0.02] hover:border-white/[0.12] hover:bg-white/[0.04]'
                }`}
                onClick={() => setActiveTab(i)}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${features[i].color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{t(feature.titleKey)}</h3>
                <p className="text-sm text-white/40 leading-relaxed">{t(feature.descKey)}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

const stages = [
  { key: 'start', bfLabel: '20%', week: null, color: 'from-blue-500/60 to-blue-600/60' },
  { key: 'early', bfLabel: '17%', week: 'Wk 8', color: 'from-emerald-500/60 to-emerald-600/60' },
  { key: 'mid', bfLabel: '14%', week: 'Wk 20', color: 'from-emerald-400/60 to-emerald-500/60' },
  { key: 'late', bfLabel: '12%', week: 'Wk 34', color: 'from-amber-500/60 to-amber-600/60' },
  { key: 'goal', bfLabel: '10%', week: 'Wk 48', color: 'from-primary/80 to-amber-700/80' },
];

export function TransformationShowcaseSection() {
  const { t } = useLanguage();

  return (
    <section className="py-24 px-6 bg-[#0a0a0f] relative overflow-hidden">
      <div
        className="absolute inset-0 opacity-20"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(201,169,110,0.1) 0%, transparent 70%)' }}
      />

      <div className="max-w-5xl mx-auto relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {t('landing.showcaseTitle')}{' '}
            <span className="gradient-text">{t('landing.showcaseHighlight')}</span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            {t('landing.showcaseSubtitle')}
          </p>
        </motion.div>

        {/* Timeline flow */}
        <div className="flex items-start gap-2 md:gap-4 overflow-x-auto pb-6 snap-x snap-mandatory">
          {stages.map((stage, i) => (
            <div key={stage.key} className="flex items-start gap-2 md:gap-4 snap-start">
              <motion.div
                className="shrink-0 w-[140px] md:w-[180px] rounded-2xl border border-white/[0.08] bg-white/[0.03] overflow-hidden"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className={`h-40 md:h-52 bg-gradient-to-br ${stage.color} flex items-center justify-center`}>
                  <div className="text-center">
                    <p className="text-3xl md:text-4xl font-bold text-white">{stage.bfLabel}</p>
                    <p className="text-xs text-white/60 mt-1">Body Fat</p>
                  </div>
                </div>
                <div className="p-3 space-y-1">
                  <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                    {t(`landing.showcase_${stage.key}`)}
                  </p>
                  {stage.week && (
                    <p className="text-[11px] text-white/40">{stage.week}</p>
                  )}
                  <p className="text-[11px] text-white/30 leading-snug">
                    {t(`landing.showcase_${stage.key}_desc`)}
                  </p>
                </div>
              </motion.div>

              {i < stages.length - 1 && (
                <div className="shrink-0 flex items-center h-40 md:h-52">
                  <ArrowRight className="w-4 h-4 text-white/20" />
                </div>
              )}
            </div>
          ))}
        </div>

        <motion.p
          className="text-center text-sm text-white/30 mt-6"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {t('landing.showcaseDisclaimer')}
        </motion.p>
      </div>
    </section>
  );
}

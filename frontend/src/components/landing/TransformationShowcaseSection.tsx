'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import { useLanguage } from '@/contexts/LanguageContext';

const stages = [
  { key: 'start', imageSrc: '/founder/start.jpg' },
  { key: 'proof', imageSrc: '/founder/final-body.jpg' },
  { key: 'final', imageSrc: '/founder/final-portrait.jpg' },
];

export function TransformationShowcaseSection() {
  const { t } = useLanguage();

  return (
    <section className="relative overflow-hidden bg-[#0a0a0f] px-6 py-24">
      <div
        className="absolute inset-0 opacity-20"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(201,169,110,0.1) 0%, transparent 70%)' }}
      />

      <div className="relative z-10 mx-auto max-w-6xl">
        <motion.div
          className="mb-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="mb-4 text-4xl font-bold text-white md:text-5xl">
            {t('landing.showcaseTitle')}{' '}
            <span className="gradient-text">{t('landing.showcaseHighlight')}</span>
          </h2>
          <p className="mx-auto max-w-3xl text-lg text-white/58">
            {t('landing.showcaseSubtitle')}
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3">
          {stages.map((stage, i) => (
            <motion.div
              key={stage.key}
              className="overflow-hidden rounded-3xl border border-white/[0.08] bg-white/[0.03]"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div className="relative aspect-[4/5]">
                <Image
                  src={stage.imageSrc}
                  alt={t(`landing.showcase_${stage.key}_alt`)}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 90vw, 320px"
                  loading="lazy"
                  quality={60}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/10 to-transparent" />
              </div>

              <div className="space-y-3 p-5 text-left">
                <div className="flex items-end justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-primary/85">
                      {t(`landing.showcase_${stage.key}`)}
                    </p>
                    <p className="mt-2 text-3xl font-bold text-white">{t(`landing.showcase_${stage.key}_stat`)}</p>
                  </div>
                  <span className="rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1 text-xs text-white/45">
                    {t(`landing.showcase_${stage.key}_tag`)}
                  </span>
                </div>

                <p className="text-sm leading-relaxed text-white/65">
                  {t(`landing.showcase_${stage.key}_desc`)}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.p
          className="mt-6 text-center text-sm text-white/36"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {t('landing.showcaseDisclaimer')}
        </motion.p>
      </div>
    </section>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Flame } from 'lucide-react';
import { streakApi } from '@/lib/api/services';

export function StreakBadge() {
  const [streak, setStreak] = useState(0);
  const [showFlame, setShowFlame] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await streakApi.getStreak();
        const days = res.data?.current_streak ?? res.data?.streak ?? 0;
        setStreak(days);
        if (days > 0) setShowFlame(true);
      } catch {
        setStreak(0);
      }
    };
    load();
  }, []);

  const getStreakColor = () => {
    if (streak >= 30) return 'from-violet-500 to-fuchsia-500';
    if (streak >= 14) return 'from-orange-500 to-red-500';
    if (streak >= 7) return 'from-amber-400 to-orange-500';
    return 'from-amber-300 to-amber-500';
  };

  return (
    <motion.div
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold ${
        streak > 0
          ? `bg-gradient-to-r ${getStreakColor()} text-white shadow-lg`
          : 'bg-white/[0.06] text-text-secondary border border-border'
      }`}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {showFlame ? (
        <motion.div
          animate={{ scale: [1, 1.2, 1], rotate: [0, -5, 5, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 2 }}
        >
          <Flame className="h-4 w-4" />
        </motion.div>
      ) : (
        <Flame className="h-4 w-4" />
      )}
      <span className="font-number">{streak}</span>
      <span className="text-xs opacity-80">day{streak !== 1 ? 's' : ''}</span>
    </motion.div>
  );
}

'use client';

import React, { useEffect, useState } from 'react';
import { Flame } from 'lucide-react';
import { streakApi } from '@/lib/api/services';
import toast from 'react-hot-toast';

export function StreakBadge() {
  const [streak, setStreak] = useState(0);
  const [longest, setLongest] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAndCheckIn();
  }, []);

  const loadAndCheckIn = async () => {
    try {
      const checkInRes = await streakApi.checkIn();
      const data = checkInRes.data;
      setStreak(data.streak);
      setLongest(data.longest || data.streak);
      
      if (data.milestone) {
        toast.success(data.message, { duration: 5000 });
      }
    } catch {
      try {
        const res = await streakApi.getStreak();
        setStreak(res.data.current_streak || 0);
        setLongest(res.data.longest_streak || 0);
      } catch {
        // Silently fail
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) return null;

  const getFlameColor = () => {
    if (streak >= 30) return 'text-red-500';
    if (streak >= 7) return 'text-orange-500';
    if (streak >= 3) return 'text-yellow-500';
    return 'text-gray-400';
  };

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950/30 dark:to-red-950/30 rounded-xl border border-orange-100 dark:border-orange-900/50">
      <Flame className={`w-5 h-5 ${getFlameColor()} ${streak >= 7 ? 'animate-pulse' : ''}`} />
      <div>
        <span className="text-lg font-bold text-gray-900 dark:text-white">{streak}</span>
        <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">day streak</span>
      </div>
      {longest > streak && (
        <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">
          Best: {longest}
        </span>
      )}
    </div>
  );
}

'use client';

import { Flame } from 'lucide-react';

export function StreakBadge() {
  return (
    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 text-sm font-medium">
      <Flame className="h-4 w-4" />
      <span>0 day streak</span>
    </div>
  );
}

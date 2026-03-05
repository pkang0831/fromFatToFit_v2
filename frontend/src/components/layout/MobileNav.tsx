'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import {
  Home,
  Utensils,
  Dumbbell,
  TrendingUp,
  MoreHorizontal,
  Camera,
  Timer,
  Scan,
  MessageCircle,
  User,
  X,
} from 'lucide-react';

const mainItems = [
  { href: '/home', label: 'Home', icon: Home },
  { href: '/calories', label: 'Calories', icon: Utensils },
  { href: '/workouts', label: 'Workouts', icon: Dumbbell },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
];

const moreItems = [
  { href: '/food-camera', label: 'Food Camera', icon: Camera },
  { href: '/fasting', label: 'Fasting', icon: Timer },
  { href: '/body-scan', label: 'Body Scan', icon: Scan },
  { href: '/chat', label: 'AI Coach', icon: MessageCircle },
  { href: '/profile', label: 'Profile', icon: User },
];

export function MobileNav() {
  const pathname = usePathname();
  const [showMore, setShowMore] = useState(false);

  const isMoreActive = moreItems.some((item) => pathname === item.href);

  return (
    <>
      {showMore && (
        <div className="lg:hidden fixed inset-0 bg-black/50 z-40" onClick={() => setShowMore(false)} />
      )}

      {showMore && (
        <div className="lg:hidden fixed bottom-[4.5rem] left-4 right-4 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 p-3">
          <div className="flex items-center justify-between mb-2 px-2">
            <span className="text-sm font-semibold text-gray-900 dark:text-white">More</span>
            <button onClick={() => setShowMore(false)} className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <X className="h-4 w-4 text-gray-500" />
            </button>
          </div>
          <div className="grid grid-cols-3 gap-1">
            {moreItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setShowMore(false)}
                  className={cn(
                    'flex flex-col items-center justify-center py-3 px-2 rounded-xl transition-colors',
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  )}
                >
                  <Icon className="h-6 w-6" />
                  <span className="text-xs mt-1.5 text-center leading-tight">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 z-50">
        <div className="flex items-center justify-around">
          {mainItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex flex-col items-center justify-center px-4 py-3 min-w-[4rem] transition-colors',
                  isActive
                    ? 'text-primary'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                )}
              >
                <Icon className={cn('h-6 w-6', isActive && 'text-primary')} />
                <span className="text-xs mt-1">{item.label}</span>
              </Link>
            );
          })}
          <button
            onClick={() => setShowMore(!showMore)}
            className={cn(
              'flex flex-col items-center justify-center px-4 py-3 min-w-[4rem] transition-colors',
              isMoreActive || showMore
                ? 'text-primary'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            <MoreHorizontal className={cn('h-6 w-6', (isMoreActive || showMore) && 'text-primary')} />
            <span className="text-xs mt-1">More</span>
          </button>
        </div>
      </nav>
    </>
  );
}

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Utensils,
  Dumbbell,
  MoreHorizontal,
  Camera,
  Timer,
  MessageCircle,
  X,
  Flame,
} from 'lucide-react';
import {
  CheckInIcon,
  DashboardIcon,
  GoalsIcon,
  ProfileIcon,
  ProgressIcon,
} from '@/components/ui/AppIcons';

const mainItems = [
  { href: '/home', labelKey: 'dashboardHome.navDashboard', icon: DashboardIcon },
  { href: '/body-scan', labelKey: 'dashboardHome.navCheckIn', icon: CheckInIcon },
  { href: '/progress', labelKey: 'dashboardHome.navProgress', icon: ProgressIcon },
  { href: '/goal-planner', labelKey: 'dashboardHome.navGoals', icon: GoalsIcon },
  { href: '/profile', labelKey: 'dashboardHome.navProfile', icon: ProfileIcon },
];

const moreItems = [
  { href: '/challenge', labelKey: 'nav.challengeSevenDay', icon: Flame },
  { href: '/chat', labelKey: 'nav.chat', icon: MessageCircle },
  { href: '/calories', labelKey: 'nav.calories', icon: Utensils },
  { href: '/food-camera', labelKey: 'nav.foodCamera', icon: Camera },
  { href: '/workouts', labelKey: 'nav.workouts', icon: Dumbbell },
  { href: '/fasting', labelKey: 'nav.fasting', icon: Timer },
];

function isRouteActive(pathname: string | null, href: string) {
  return pathname === href || pathname?.startsWith(`${href}/`) === true;
}

export function MobileNav() {
  const pathname = usePathname();
  const { t } = useLanguage();
  const [showMore, setShowMore] = useState(false);

  const isMoreActive = moreItems.some((item) => isRouteActive(pathname, item.href));

  return (
    <>
      {showMore && (
        <div className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={() => setShowMore(false)} />
      )}

      {showMore && (
        <div className="lg:hidden fixed bottom-[4.5rem] left-4 right-4 bg-surface border border-border rounded-2xl shadow-xl z-50 p-3">
          <div className="flex items-center justify-between mb-2 px-2">
            <span className="text-sm font-semibold text-text">{t('dashboardHome.navMore')}</span>
            <button onClick={() => setShowMore(false)} className="p-1 rounded-lg hover:bg-surfaceAlt">
              <X className="h-4 w-4 text-text-light" />
            </button>
          </div>
          <div className="grid grid-cols-3 gap-1">
            {moreItems.map((item) => {
              const isActive = isRouteActive(pathname, item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setShowMore(false)}
                  className={cn(
                    'flex flex-col items-center justify-center py-3 px-2 rounded-xl transition-all duration-200',
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-text-secondary hover:bg-surfaceAlt hover:text-text'
                  )}
                >
                  <Icon className="h-6 w-6" />
                  <span className="text-xs mt-1.5 text-center leading-tight">{t(item.labelKey)}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-surface/80 backdrop-blur-xl border-t border-border z-50">
        <div className="flex items-center justify-around">
          {mainItems.map((item) => {
            const isActive = isRouteActive(pathname, item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex flex-col items-center justify-center px-4 py-3 min-w-[4rem] transition-all duration-200',
                  isActive
                    ? 'text-primary'
                    : 'text-text-light hover:text-text'
                )}
              >
                <Icon className="h-[22px] w-[22px]" />
                <span className="text-xs mt-1">{t(item.labelKey)}</span>
              </Link>
            );
          })}
          <button
            onClick={() => setShowMore(!showMore)}
            className={cn(
              'flex flex-col items-center justify-center px-4 py-3 min-w-[4rem] transition-all duration-200',
              isMoreActive || showMore
                ? 'text-primary'
                : 'text-text-light hover:text-text'
            )}
          >
            <MoreHorizontal className="h-6 w-6" />
            <span className="text-xs mt-1">{t('dashboardHome.navMore')}</span>
          </button>
        </div>
      </nav>
    </>
  );
}

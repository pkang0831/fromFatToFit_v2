'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import { 
  Home, 
  Utensils, 
  Camera, 
  Dumbbell, 
  Scan, 
  User,
  Crown,
  TrendingUp,
  Zap,
  MessageCircle,
  Play,
  Moon,
  Sun,
  Timer,
} from 'lucide-react';
import { Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { paymentApi } from '@/lib/api/services';
import { TOUR_START_EVENT, resetAllTours } from '@/components/tour/FeatureTour';
import { useTheme } from '@/contexts/ThemeContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';

const navItems = [
  { href: '/home', labelKey: 'nav.home', icon: Home },
  { href: '/calories', labelKey: 'nav.calories', icon: Utensils },
  { href: '/food-camera', labelKey: 'nav.foodCamera', icon: Camera },
  { href: '/workouts', labelKey: 'nav.workouts', icon: Dumbbell },
  { href: '/fasting', labelKey: 'nav.fasting', icon: Timer },
  { href: '/progress', labelKey: 'nav.progress', icon: TrendingUp },
  { href: '/body-scan', labelKey: 'nav.bodyScan', icon: Scan },
  { href: '/chat', labelKey: 'nav.chat', icon: MessageCircle },
  { href: '/profile', labelKey: 'nav.profile', icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
  const { t } = useLanguage();
  const { isPremium } = useSubscription();
  const { theme, toggleTheme } = useTheme();
  const [credits, setCredits] = useState<number | null>(null);

  useEffect(() => {
    paymentApi.getCreditBalance()
      .then(res => setCredits(res.data.total_credits))
      .catch(() => {});
  }, [pathname]);

  const startTour = () => {
    resetAllTours();
    window.dispatchEvent(new Event(TOUR_START_EVENT));
  };

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-surface border-r border-border h-screen sticky top-0">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-primary">FromFatToFit</h1>
        <div className="flex items-center gap-2 mt-2">
          {isPremium && (
            <Badge variant="premium">
              <Crown className="h-3 w-3 mr-1" />
              Pro
            </Badge>
          )}
          {credits !== null && (
            <Link href="/upgrade" className="flex items-center gap-1 text-xs text-text-secondary hover:text-primary transition-colors">
              <Zap className="h-3 w-3" />
              {credits} credits
            </Link>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          const tourId = `nav-${item.href.slice(1)}`;

          return (
            <Link
              key={item.href}
              href={item.href}
              data-tour={tourId}
              className={cn(
                'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-white'
                  : 'text-text hover:bg-surfaceAlt'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{t(item.labelKey)}</span>
            </Link>
          );
        })}
      </nav>

      {/* Start Tour, Theme Toggle & Language Switcher */}
      <div className="px-4 pb-2 space-y-1">
        <div className="flex items-center justify-between px-4 py-2">
          <LanguageSwitcher variant="compact" />
        </div>
        <button
          onClick={toggleTheme}
          className="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-text-secondary hover:bg-surfaceAlt transition-colors w-full"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          <span className="text-sm font-medium">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
        <button
          onClick={startTour}
          className="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-text-secondary hover:bg-surfaceAlt hover:text-text w-full"
        >
          <Play className="h-5 w-5" />
          <span className="font-medium">Start Tour</span>
        </button>
      </div>

      {/* Upgrade CTA for free users */}
      {!isPremium && (
        <div className="p-4 border-t border-border">
          <Link
            href="/upgrade"
            className="flex items-center justify-center space-x-2 w-full px-4 py-3 bg-premium text-primary font-semibold rounded-lg hover:bg-premium-dark transition-colors"
          >
            <Crown className="h-5 w-5" />
            <span>{t('nav.upgrade')}</span>
          </Link>
        </div>
      )}
    </aside>
  );
}

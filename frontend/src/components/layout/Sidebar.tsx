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
  Sparkles,
  Shirt,
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
  { href: '/beauty-scan', labelKey: 'nav.beautyScan', icon: Sparkles },
  { href: '/fashion', labelKey: 'nav.fashion', icon: Shirt },
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
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold gradient-text">FromFatToFit</h1>
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
              <span className="font-number">{credits}</span> credits
            </Link>
          )}
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1">
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
                'flex items-center space-x-3 px-4 py-2.5 rounded-xl transition-all duration-200',
                isActive
                  ? 'bg-gradient-primary text-white shadow-glow-cyan'
                  : 'text-text-secondary hover:bg-surfaceAlt hover:text-text'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium text-sm">{t(item.labelKey)}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-3 pb-2 space-y-1">
        <div className="flex items-center justify-between px-4 py-2">
          <LanguageSwitcher variant="compact" />
        </div>
        <button
          onClick={toggleTheme}
          className="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-text-secondary hover:bg-surfaceAlt hover:text-text transition-all duration-200 w-full"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          <span className="text-sm font-medium">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
        <button
          onClick={startTour}
          className="flex items-center space-x-3 px-4 py-2.5 rounded-xl transition-all duration-200 text-text-secondary hover:bg-surfaceAlt hover:text-text w-full"
        >
          <Play className="h-5 w-5" />
          <span className="text-sm font-medium">Start Tour</span>
        </button>
      </div>

      {!isPremium && (
        <div className="p-3 border-t border-border">
          <Link
            href="/upgrade"
            className="flex items-center justify-center space-x-2 w-full px-4 py-3 bg-gradient-primary text-white font-semibold rounded-xl hover:shadow-glow-cyan transition-all duration-200"
          >
            <Crown className="h-5 w-5" />
            <span>{t('nav.upgrade')}</span>
          </Link>
        </div>
      )}
    </aside>
  );
}

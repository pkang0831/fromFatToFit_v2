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

const navItems = [
  { href: '/home', label: 'Home', icon: Home },
  { href: '/calories', label: 'Calories', icon: Utensils },
  { href: '/food-camera', label: 'Food Camera', icon: Camera },
  { href: '/workouts', label: 'Workouts', icon: Dumbbell },
  { href: '/fasting', label: 'Fasting', icon: Timer },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
  { href: '/body-scan', label: 'Body Scan', icon: Scan },
  { href: '/chat', label: 'AI Coach', icon: MessageCircle },
  { href: '/profile', label: 'Profile', icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
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
    <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-white dark:bg-gray-800 dark:bg-gray-900 border-r border-gray-100 dark:border-gray-700 dark:border-gray-800 h-screen sticky top-0">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-gray-100 dark:border-gray-700 dark:border-gray-800">
        <h1 className="text-2xl font-bold text-primary dark:text-white">FromFatToFit</h1>
        <div className="flex items-center gap-2 mt-2">
          {isPremium && (
            <Badge variant="premium">
              <Crown className="h-3 w-3 mr-1" />
              Pro
            </Badge>
          )}
          {credits !== null && (
            <Link href="/upgrade" className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400 dark:text-gray-400 hover:text-primary transition-colors">
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
                  ? 'bg-primary text-white dark:bg-primary/20 dark:text-white'
                  : 'text-gray-900 dark:text-white dark:text-gray-300 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Start Tour & Theme Toggle */}
      <div className="px-4 pb-2 space-y-1">
        <button
          onClick={toggleTheme}
          className="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors w-full"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          <span className="text-sm font-medium">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
        <button
          onClick={startTour}
          className="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-gray-600 dark:text-gray-400 dark:text-gray-400 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800 hover:text-gray-900 dark:text-white dark:hover:text-white w-full"
        >
          <Play className="h-5 w-5" />
          <span className="font-medium">Start Tour</span>
        </button>
      </div>

      {/* Upgrade CTA for free users */}
      {!isPremium && (
        <div className="p-4 border-t border-gray-100 dark:border-gray-700 dark:border-gray-800">
          <Link
            href="/upgrade"
            className="flex items-center justify-center space-x-2 w-full px-4 py-3 bg-premium text-primary font-semibold rounded-lg hover:bg-premium-dark transition-colors"
          >
            <Crown className="h-5 w-5" />
            <span>Upgrade to Premium</span>
          </Link>
        </div>
      )}
    </aside>
  );
}

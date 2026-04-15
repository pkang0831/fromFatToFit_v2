'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import { 
  Utensils, 
  Camera, 
  Dumbbell, 
  Crown,
  Zap,
  MessageCircle,
  Play,
  Moon,
  Sun,
  Timer,
  ChevronDown,
  Flame,
} from 'lucide-react';
import { Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { paymentApi } from '@/lib/api/services';
import { TOUR_START_EVENT, resetAllTours } from '@/components/tour/FeatureTour';
import { useTheme, COLOR_THEMES } from '@/contexts/ThemeContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { Check } from 'lucide-react';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import {
  CheckInIcon,
  DashboardIcon,
  GoalsIcon,
  ProfileIcon,
  ProgressIcon,
} from '@/components/ui/AppIcons';

const CREDIT_CACHE_KEY = 'sidebar_credit_balance';
const CREDIT_CACHE_TTL_MS = 60_000;

function readCachedCredits(): number | null {
  try {
    const raw = sessionStorage.getItem(CREDIT_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { total: number; ts: number };
    if (Date.now() - parsed.ts > CREDIT_CACHE_TTL_MS) return null;
    return parsed.total;
  } catch {
    return null;
  }
}

function writeCachedCredits(total: number) {
  try {
    sessionStorage.setItem(
      CREDIT_CACHE_KEY,
      JSON.stringify({ total, ts: Date.now() }),
    );
  } catch {
    /* noop */
  }
}

const coreItems = [
  { href: '/home', labelKey: 'dashboardHome.navDashboard', icon: DashboardIcon },
  { href: '/body-scan', labelKey: 'dashboardHome.navCheckIn', icon: CheckInIcon },
  { href: '/progress', labelKey: 'dashboardHome.navProgress', icon: ProgressIcon },
  { href: '/goal-planner', labelKey: 'dashboardHome.navGoals', icon: GoalsIcon },
  { href: '/profile', labelKey: 'dashboardHome.navProfile', icon: ProfileIcon },
];

const extraItems = [
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

export function Sidebar() {
  const pathname = usePathname();
  const { isPremium } = useSubscription();
  const { theme, colorTheme, toggleTheme, setColorTheme } = useTheme();
  const { t } = useLanguage();
  const [credits, setCredits] = useState<number | null>(null);
  const [extrasOpen, setExtrasOpen] = useState(() => {
    return extraItems.some((item) => isRouteActive(pathname, item.href));
  });

  useEffect(() => {
    const cachedCredits = readCachedCredits();
    if (cachedCredits != null) {
      setCredits(cachedCredits);
    }

    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    let idleId: number | undefined;

    const loadCredits = async () => {
      try {
        const res = await paymentApi.getCreditBalance();
        if (cancelled) return;
        setCredits(res.data.total_credits);
        writeCachedCredits(res.data.total_credits);
      } catch {
        /* noop */
      }
    };

    const deferFetch = pathname === '/home';
    if (deferFetch) {
      if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
        idleId = window.requestIdleCallback(() => {
          void loadCredits();
        }, { timeout: 2500 });
      } else {
        timeoutId = setTimeout(() => {
          void loadCredits();
        }, 1500);
      }
    } else if (cachedCredits == null) {
      void loadCredits();
    }

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
      if (idleId && typeof window !== 'undefined' && 'cancelIdleCallback' in window) {
        window.cancelIdleCallback(idleId);
      }
    };
  }, [pathname]);

  useEffect(() => {
    if (extraItems.some((item) => isRouteActive(pathname, item.href))) {
      setExtrasOpen(true);
    }
  }, [pathname]);

  const startTour = () => {
    resetAllTours();
    window.dispatchEvent(new Event(TOUR_START_EVENT));
  };

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-surface border-r border-border h-screen sticky top-0">
      <div className="p-6 border-b border-border">
        <h1 className="text-[1.65rem] font-semibold tracking-[-0.03em] text-text dark:text-white">Devenira</h1>
        <div className="mt-2 flex items-center gap-2">
          {isPremium && (
            <Badge variant="premium" className="rounded-full px-2.5 py-0.5 text-[11px] shadow-none">
              <Crown className="h-3 w-3 mr-1" />
              Pro
            </Badge>
          )}
          {credits !== null && (
            <Link href="/upgrade" className="flex items-center gap-1 text-xs text-text-secondary hover:text-primary transition-colors">
              <Zap className="h-3 w-3" />
              <span className="font-number">{credits}</span> {t('common.credits')}
            </Link>
          )}
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {coreItems.map((item) => {
          const isActive = isRouteActive(pathname, item.href);
          const Icon = item.icon;
          const tourId = `nav-${item.href.slice(1)}`;

          return (
            <Link
              key={item.href}
              href={item.href}
              data-tour={tourId}
              className={cn(
                'flex items-center space-x-3 rounded-xl px-4 py-2.5 transition-all duration-200',
                isActive
                  ? 'bg-background text-text dark:bg-white/[0.05] dark:text-white'
                  : 'text-text-secondary hover:bg-surfaceAlt hover:text-text'
              )}
            >
                  <Icon className="h-[18px] w-[18px]" />
                  <span className="font-medium text-sm">{t(item.labelKey)}</span>
                </Link>
              );
        })}

        {/* Extras collapsible */}
        <div className="pt-2">
          <button
            onClick={() => setExtrasOpen(!extrasOpen)}
            className="flex w-full items-center justify-between rounded-xl px-4 py-2 text-text-light transition-all duration-200 hover:bg-surfaceAlt hover:text-text-secondary"
          >
            <span className="text-xs font-semibold uppercase tracking-wider">{t('dashboardHome.navMore')}</span>
            <ChevronDown className={cn('h-4 w-4 transition-transform duration-200', extrasOpen && 'rotate-180')} />
          </button>

          <div className={cn(
            'space-y-0.5 overflow-hidden transition-all duration-200',
            extrasOpen ? 'max-h-96 opacity-100 mt-1' : 'max-h-0 opacity-0'
          )}>
            {extraItems.map((item) => {
              const isActive = isRouteActive(pathname, item.href);
              const Icon = item.icon;
              const tourId = `nav-${item.href.slice(1)}`;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  data-tour={tourId}
                  className={cn(
                    'flex items-center space-x-3 rounded-xl px-4 py-2 transition-all duration-200',
                    isActive
                      ? 'bg-background text-text dark:bg-white/[0.05] dark:text-white'
                      : 'text-text-light hover:bg-surfaceAlt hover:text-text-secondary'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="font-medium text-sm">{t(item.labelKey)}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      <div className="space-y-3 border-t border-border px-3 py-3">
        <div className="rounded-2xl border border-border/80 bg-surfaceAlt/40 px-4 py-3">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-light">
                {t('dashboardHome.accent')}
              </p>
              <p className="mt-1 text-xs text-text-secondary">
                {COLOR_THEMES.find((themeOption) => themeOption.id === colorTheme)?.label ?? 'Warm Gold'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {COLOR_THEMES.map((themeOption) => (
              <button
                key={themeOption.id}
                type="button"
                onClick={() => setColorTheme(themeOption.id)}
                title={themeOption.label}
                aria-label={`${t('dashboardHome.accent')}: ${themeOption.label}`}
                className={cn(
                  'relative h-7 w-7 flex-shrink-0 rounded-full transition-all duration-200',
                  'ring-1 ring-black/5 dark:ring-white/10 hover:scale-105',
                  colorTheme === themeOption.id && 'ring-2 ring-text/30 dark:ring-white/40'
                )}
                style={{ background: `linear-gradient(135deg, ${themeOption.primary}, ${themeOption.secondary})` }}
              >
                {colorTheme === themeOption.id ? (
                  <span className="absolute inset-0 flex items-center justify-center">
                    <Check className="h-3.5 w-3.5 text-white drop-shadow-md" strokeWidth={3} />
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        </div>

        <div className="px-4">
          <p className="text-[11px] font-medium text-text-light">
            {t('dashboardHome.preferences')}
          </p>
        </div>

        <div className="space-y-1 px-2">
          <div className="flex items-center justify-between px-2 py-1">
            <LanguageSwitcher variant="compact" />
          </div>

          <button
            onClick={toggleTheme}
            className="flex w-full items-center space-x-3 rounded-xl px-3 py-2 text-text-secondary transition-all duration-200 hover:bg-surfaceAlt hover:text-text"
          >
            {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            <span className="text-sm font-medium">{theme === 'dark' ? t('dashboardHome.lightMode') : 'Dark mode'}</span>
          </button>

          <button
            onClick={startTour}
            className="flex w-full items-center space-x-3 rounded-xl px-3 py-2 text-text-secondary transition-all duration-200 hover:bg-surfaceAlt hover:text-text"
          >
            <Play className="h-4 w-4" />
            <span className="text-sm font-medium">{t('dashboardHome.startTour')}</span>
          </button>
        </div>
      </div>

      {!isPremium && (
        <div className="border-t border-border p-3">
          <Link
            href="/upgrade"
            className="flex w-full items-center justify-center space-x-2 rounded-xl px-4 py-2 text-sm font-medium text-text-light transition-all duration-200 hover:text-text dark:hover:text-white"
          >
            <Crown className="h-4 w-4" />
            <span>Upgrade</span>
          </Link>
        </div>
      )}
    </aside>
  );
}

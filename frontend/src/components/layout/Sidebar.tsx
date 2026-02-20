'use client';

import React from 'react';
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
} from 'lucide-react';
import { Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';

const navItems = [
  { href: '/home', label: 'Home', icon: Home },
  { href: '/calories', label: 'Calories', icon: Utensils },
  { href: '/food-camera', label: 'Food Camera', icon: Camera },
  { href: '/workouts', label: 'Workouts', icon: Dumbbell },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
  { href: '/body-scan', label: 'Body Scan', icon: Scan },
  { href: '/profile', label: 'Profile', icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isPremium } = useSubscription();

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-surface border-r border-border-light h-screen sticky top-0">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-border-light">
        <h1 className="text-2xl font-bold text-primary">Health & Wellness</h1>
        {isPremium && (
          <Badge variant="premium" className="mt-2">
            <Crown className="h-3 w-3 mr-1" />
            Premium
          </Badge>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-text-onPrimary'
                  : 'text-text hover:bg-surfaceAlt'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Upgrade CTA for free users */}
      {!isPremium && (
        <div className="p-4 border-t border-border-light">
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

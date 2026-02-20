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
  User,
  TrendingUp,
} from 'lucide-react';

const navItems = [
  { href: '/home', label: 'Home', icon: Home },
  { href: '/calories', label: 'Calories', icon: Utensils },
  { href: '/workouts', label: 'Workouts', icon: Dumbbell },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
  { href: '/profile', label: 'Profile', icon: User },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-surface border-t border-border-light z-50">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
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
                  : 'text-text-secondary hover:text-text'
              )}
            >
              <Icon className={cn('h-6 w-6', isActive && 'text-primary')} />
              <span className="text-xs mt-1">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

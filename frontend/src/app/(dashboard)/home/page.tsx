'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Utensils, 
  Camera, 
  Dumbbell, 
  Scan, 
  TrendingUp,
  Flame,
  Crown,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { dashboardApi } from '@/lib/api/services';
import { Card, CardHeader, CardTitle, CardContent, Badge, Button } from '@/components/ui';
import dynamic from 'next/dynamic';
import { QuickStatsCard } from '@/components/features/QuickStatsCard';
import { StreakBadge } from '@/components/features/StreakBadge';
import type { QuickStatsResponse } from '@/types/api';
import { SkeletonStats, SkeletonChart, SkeletonCard } from '@/components/ui/Skeleton';

const CalorieBalanceChart = dynamic(
  () => import('@/components/features/CalorieBalanceChart').then(m => m.CalorieBalanceChart),
  { loading: () => <SkeletonChart />, ssr: false }
);

const featureCards = [
  {
    titleKey: 'dashboard.calorieTracker',
    descKey: 'dashboard.calorieTrackerDesc',
    icon: Utensils,
    href: '/calories',
    color: 'text-primary',
  },
  {
    titleKey: 'dashboard.aiFoodCamera',
    descKey: 'dashboard.aiFoodCameraDesc',
    icon: Camera,
    href: '/food-camera',
    color: 'text-secondary',
  },
  {
    titleKey: 'dashboard.workoutTracker',
    descKey: 'dashboard.workoutTrackerDesc',
    icon: Dumbbell,
    href: '/workouts',
    color: 'text-primary',
  },
  {
    titleKey: 'dashboard.bodyScanner',
    descKey: 'dashboard.bodyScannerDesc',
    icon: Scan,
    href: '/body-scan',
    color: 'text-secondary',
  },
];

export default function HomePage() {
  const router = useRouter();
  const { user } = useAuth();
  const { t } = useLanguage();
  const { isPremium } = useSubscription();
  const [stats, setStats] = useState<QuickStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [chartDays, setChartDays] = useState<7 | 30>(7);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await dashboardApi.getQuickStats();
        setStats(response.data);
      } catch (error: any) {
        console.error('Failed to load stats:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  const calorieProgress = stats 
    ? Math.min((stats.today_calories / stats.calorie_goal) * 100, 100)
    : 0;

  if (loading) return (
    <div className="space-y-6">
      <SkeletonStats count={4} />
      <SkeletonChart />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-text">
              {t('dashboard.hello', { name: user?.full_name || 'there' })}
            </h1>
            <p className="text-text-secondary mt-1">
              {t('dashboard.welcomeBack')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <StreakBadge />
            {isPremium && (
              <Badge variant="premium" className="text-base px-4 py-2">
                <Crown className="h-4 w-4 mr-2" />
                {t('dashboard.premiumMember')}
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      {stats ? (
        <div data-tour="home-stats" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <QuickStatsCard
            title={t('dashboard.todayCalories')}
            value={Math.round(stats.today_calories)}
            subtitle={t('dashboard.goalKcal', { value: stats.calorie_goal })}
            icon={Utensils}
            progress={{
              current: stats.today_calories,
              max: stats.calorie_goal,
            }}
          />
          <QuickStatsCard
            title={t('dashboard.todayProtein')}
            value={`${Math.round(stats.today_protein)}g`}
            subtitle={t('dashboard.keepItUp')}
            icon={TrendingUp}
          />
          <QuickStatsCard
            title={t('dashboard.todayBurned')}
            value={Math.round(stats.total_burned)}
            subtitle={t('dashboard.tdeeExercise', { tdee: Math.round(stats.tdee), exercise: Math.round(stats.workout_calories) })}
            icon={Flame}
          />
        </div>
      ) : null}

      {/* Calorie Balance Trend Chart */}
      <Card data-tour="home-chart" variant="elevated" className="bg-surface">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6" />
              {t('dashboard.calorieBalanceTrend')}
            </CardTitle>
            <div className="flex gap-2">
              <Button 
                size="sm" 
                variant={chartDays === 7 ? 'primary' : 'outline'}
                onClick={() => setChartDays(7)}
              >
                {t('dashboard.days7')}
              </Button>
              <Button 
                size="sm" 
                variant={chartDays === 30 ? 'primary' : 'outline'}
                onClick={() => setChartDays(30)}
              >
                {t('dashboard.days30')}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <CalorieBalanceChart days={chartDays} />
        </CardContent>
      </Card>

      {/* Feature Navigation Grid */}
      <div>
        <h2 className="text-2xl font-bold text-text mb-4">{t('dashboard.quickActions')}</h2>
        <div data-tour="home-actions" className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {featureCards.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link key={feature.href} href={feature.href}>
                <Card variant="outlined" className="hover:shadow-lg transition-all hover:-translate-y-1 h-full">
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className={`p-3 bg-primary/10 rounded-lg ${feature.color}`}>
                        <Icon className="h-8 w-8" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-text mb-2">
                          {t(feature.titleKey)}
                        </h3>
                        <p className="text-text-secondary">
                          {t(feature.descKey)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Premium Upgrade CTA (for free users) */}
      {!isPremium && (
        <Card variant="elevated" className="bg-gradient-to-r from-premium/10 to-secondary/10 border-2 border-premium/30">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-2xl font-bold text-text mb-2 flex items-center justify-center md:justify-start">
                  <Crown className="h-6 w-6 text-premium mr-2" />
                  {t('dashboard.upgradePremium')}
                </h3>
                <p className="text-text-secondary mb-4">
                  {t('dashboard.premiumCta')}
                </p>
                <ul className="text-sm text-text-secondary space-y-2 mb-4">
                  <li>&#10003; {t('dashboard.premiumBenefit1')}</li>
                  <li>&#10003; {t('dashboard.premiumBenefit2')}</li>
                  <li>&#10003; {t('dashboard.premiumBenefit3')}</li>
                  <li>&#10003; {t('dashboard.premiumBenefit4')}</li>
                </ul>
              </div>
              <div>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => router.push('/upgrade')}
                  className="bg-premium text-primary hover:bg-premium-dark"
                >
                  <Crown className="h-5 w-5 mr-2" />
                  {t('dashboard.getPremium')}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

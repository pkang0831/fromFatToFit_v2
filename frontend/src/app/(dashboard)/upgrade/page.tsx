'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Crown, Check, Sparkles, Zap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { useLanguage } from '@/contexts/LanguageContext';
import { paymentApi } from '@/lib/api/services';

type PricingPeriod = 'monthly' | 'yearly';

interface CreditBalance {
  monthly_credits: number;
  bonus_credits: number;
  total_credits: number;
  reset_date: string | null;
  credit_costs: Record<string, number>;
}

const creditCostLabelKeys: Record<string, string> = {
  food_scan: 'upgrade.foodCameraAnalysis',
  food_recommendation: 'upgrade.aiFoodRec',
  body_fat_scan: 'upgrade.bodyfatScan',
  percentile_scan: 'upgrade.percentileRanking',
  form_check: 'upgrade.workoutFormCheck',
  transformation: 'upgrade.transformationPreview',
  enhancement: 'upgrade.photoEnhancement',
};

const creditPacks = [
  { size: 50, price: 4.99 },
  { size: 100, price: 8.99 },
  { size: 200, price: 15.99 },
];

export default function UpgradePage() {
  const { isPremium } = useSubscription();
  const { t } = useLanguage();
  const [selectedPeriod, setSelectedPeriod] = useState<PricingPeriod>('yearly');
  const [isLoading, setIsLoading] = useState(false);
  const [packLoading, setPackLoading] = useState<number | null>(null);
  const [credits, setCredits] = useState<CreditBalance | null>(null);

  useEffect(() => {
    paymentApi.getCreditBalance()
      .then(res => setCredits(res.data))
      .catch(() => {});
  }, []);

  const pricing = {
    monthly: { price: 9.99, priceId: 'price_1T76GGCLiCRdyAkdUMiIPWdg', period: 'month' },
    yearly: { price: 89.99, priceId: 'price_1T76GGCLiCRdyAkdc6Y2Ehq0', period: 'year', savings: 'Save 25%' },
  };

  const handleSubscribe = async () => {
    setIsLoading(true);
    try {
      const plan = pricing[selectedPeriod];
      const response = await paymentApi.createCheckoutSession({
        price_id: plan.priceId,
        success_url: `${window.location.origin}/upgrade?success=true`,
        cancel_url: `${window.location.origin}/upgrade`,
      });
      window.location.href = response.data.checkout_url;
    } catch {
      toast.error(t('upgrade.checkoutFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleBuyPack = async (size: number) => {
    setPackLoading(size);
    try {
      const response = await paymentApi.buyCreditPack({
        pack_size: size,
        success_url: `${window.location.origin}/upgrade?credits=purchased`,
        cancel_url: `${window.location.origin}/upgrade`,
      });
      window.location.href = response.data.checkout_url;
    } catch {
      toast.error(t('upgrade.checkoutFailed'));
    } finally {
      setPackLoading(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-12">
      {/* Credit Balance Banner */}
      {credits && (
        <Card variant="elevated" className="bg-gradient-to-r from-primary/5 to-secondary/5">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                  <Zap className="h-7 w-7 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{t('upgrade.creditBalance')}</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">{t('upgrade.creditsLabel', { count: credits.total_credits })}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    {t('upgrade.monthlyBonus', { monthly: credits.monthly_credits, bonus: credits.bonus_credits })}
                  </p>
                </div>
              </div>
              {credits.reset_date && (
                <div className="text-sm text-gray-600 dark:text-gray-400 text-center sm:text-right">
                  {t('upgrade.monthlyReset')}<br />
                  <span className="font-medium text-gray-900 dark:text-white">
                    {new Date(credits.reset_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Header */}
      <div className="text-center">
        {isPremium ? (
          <>
            <Crown className="h-12 w-12 text-premium mx-auto mb-3" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">{t('upgrade.proMember')}</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">{t('upgrade.proDesc')}</p>
          </>
        ) : (
          <>
            <Badge variant="premium" className="text-base px-4 py-2 mb-4">
              <Sparkles className="h-4 w-4 mr-2" />
              {t('upgrade.title')}
            </Badge>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">{t('upgrade.subtitle')}</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              {t('upgrade.subtitleDesc')}
            </p>
          </>
        )}
      </div>

      {/* Credit Cost Table */}
      {credits && (
        <Card>
          <CardHeader>
            <CardTitle>{t('upgrade.creditCosts')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(credits.credit_costs).map(([key, cost]) => (
                <div key={key} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                  <span className="text-sm text-gray-900 dark:text-white">{creditCostLabelKeys[key] ? t(creditCostLabelKeys[key]) : key}</span>
                  <Badge variant={credits.total_credits >= cost ? 'default' : 'error'} className="text-xs">
                    {cost} {cost === 1 ? t('upgrade.credit') : t('upgrade.creditPlural')}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subscription Plans */}
      {!isPremium && (
        <>
          <div className="flex justify-center">
            <div className="inline-flex items-center gap-2 p-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <button
                onClick={() => setSelectedPeriod('monthly')}
                className={`px-6 py-3 rounded-lg font-medium transition-all ${
                  selectedPeriod === 'monthly'
                    ? 'bg-primary text-white shadow-md'
                    : 'text-gray-900 dark:text-white hover:bg-white dark:bg-gray-800'
                }`}
              >
                {t('upgrade.monthly')}
              </button>
              <button
                onClick={() => setSelectedPeriod('yearly')}
                className={`px-6 py-3 rounded-lg font-medium transition-all relative ${
                  selectedPeriod === 'yearly'
                    ? 'bg-primary text-white shadow-md'
                    : 'text-gray-900 dark:text-white hover:bg-white dark:bg-gray-800'
                }`}
              >
                {t('upgrade.yearly')}
                <Badge variant="premium" className="absolute -top-2 -right-2 text-xs">
                  {t('upgrade.save25')}
                </Badge>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            {/* Free Plan */}
            <Card variant="outlined">
              <CardContent className="p-8 text-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{t('upgrade.free')}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">$0</span>
                  <span className="text-gray-600 dark:text-gray-400 ml-1">{t('upgrade.freePriceForever')}</span>
                </div>
                <p className="text-primary font-medium text-sm mb-6">{t('upgrade.freeCredits')}</p>
                <ul className="space-y-3 text-left mb-8">
                  {[t('upgrade.freeCredits'), t('upgrade.freeFeature1'), t('upgrade.freeFeature2'), t('upgrade.freeFeature3'), t('upgrade.freeFeature4')].map(f => (
                    <li key={f} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-success flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">{f}</span>
                    </li>
                  ))}
                </ul>
                <Button variant="secondary" size="lg" className="w-full" disabled>
                  {t('upgrade.currentPlan')}
                </Button>
              </CardContent>
            </Card>

            {/* Pro Plan */}
            <Card variant="elevated" className="border-2 border-premium/30 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <Badge variant="premium" className="px-4 py-1">{t('upgrade.mostPopular')}</Badge>
              </div>
              <CardContent className="p-8 text-center">
                <Crown className="h-8 w-8 text-premium mx-auto mb-2" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{t('upgrade.pro')}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">
                    ${pricing[selectedPeriod].price}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400 ml-1">{t('upgrade.perPeriod', { period: pricing[selectedPeriod].period })}</span>
                </div>
                <p className="text-primary font-medium text-sm mb-6">{t('upgrade.proCredits')}</p>
                <ul className="space-y-3 text-left mb-8">
                  {[t('upgrade.proCredits'), t('upgrade.proFeature1'), t('upgrade.proFeature2'), t('upgrade.proFeature3'), t('upgrade.proFeature4'), t('upgrade.proFeature5')].map(f => (
                    <li key={f} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-success flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">{f}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleSubscribe}
                  isLoading={isLoading}
                  className="w-full bg-premium text-primary hover:bg-premium-dark"
                >
                  <Crown className="h-5 w-5 mr-2" />
                  {t('upgrade.goPro')}
                </Button>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Credit Packs */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-2">{t('upgrade.buyPacks')}</h2>
        <p className="text-gray-600 dark:text-gray-400 text-center mb-8">
          {t('upgrade.buyPacksDesc')}
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl mx-auto">
          {creditPacks.map(pack => (
            <Card key={pack.size} variant="outlined" className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <Zap className="h-8 w-8 text-primary mx-auto mb-3" />
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{pack.size}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{t('common.credits')}</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">${pack.price}</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mb-6">
                  {t('upgrade.perCredit', { price: (pack.price / pack.size * 100).toFixed(1) })}
                </p>
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  onClick={() => handleBuyPack(pack.size)}
                  isLoading={packLoading === pack.size}
                >
                  {t('upgrade.buyNow')}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

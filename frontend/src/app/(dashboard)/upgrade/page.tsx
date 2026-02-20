'use client';

import { useState } from 'react';
import { Crown, Check, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { paymentApi } from '@/lib/api/services';

type PricingPeriod = 'monthly' | 'yearly';

export default function UpgradePage() {
  const { isPremium } = useSubscription();
  const [selectedPeriod, setSelectedPeriod] = useState<PricingPeriod>('yearly');
  const [isLoading, setIsLoading] = useState(false);

  const pricing = {
    monthly: {
      price: 9.99,
      priceId: 'price_monthly_xxx', // Replace with actual Stripe price ID
      period: 'month',
    },
    yearly: {
      price: 79.99,
      priceId: 'price_yearly_xxx', // Replace with actual Stripe price ID
      period: 'year',
      savings: '33% savings',
    },
  };

  const premiumFeatures = [
    {
      title: 'Unlimited Food Photo Analysis',
      description: 'Scan as many meals as you want with AI-powered nutrition data',
      icon: '📸',
    },
    {
      title: 'Unlimited Body Scans',
      description: 'Track your body composition with unlimited scans and analysis',
      icon: '📊',
    },
    {
      title: 'Video Form Analysis',
      description: 'Get AI-powered feedback on your workout form from video uploads',
      icon: '🎥',
    },
    {
      title: 'Body Transformation Previews',
      description: 'See AI-generated previews of your transformation goals',
      icon: '✨',
    },
    {
      title: 'Advanced Analytics',
      description: 'Detailed insights and trends for nutrition and fitness progress',
      icon: '📈',
    },
    {
      title: 'Priority Support',
      description: 'Get help faster with priority customer support',
      icon: '🎯',
    },
  ];

  const handleSubscribe = async () => {
    setIsLoading(true);
    try {
      const plan = pricing[selectedPeriod];
      const response = await paymentApi.createCheckoutSession({
        price_id: plan.priceId,
        success_url: `${window.location.origin}/upgrade/success`,
        cancel_url: `${window.location.origin}/upgrade`,
      });

      // Redirect to Stripe Checkout
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      alert('Failed to start checkout. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isPremium) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <Crown className="h-16 w-16 text-premium mx-auto mb-4" />
          <h1 className="text-4xl font-bold text-text mb-4">You're a Premium Member!</h1>
          <p className="text-xl text-text-secondary">
            Thank you for your support. Enjoy unlimited access to all features!
          </p>
        </div>

        <Card variant="elevated" className="bg-gradient-to-r from-premium/10 to-secondary/10">
          <CardContent className="p-8">
            <h3 className="text-2xl font-bold text-text mb-6 text-center">
              Your Premium Benefits
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {premiumFeatures.map((feature, index) => (
                <div key={index} className="flex items-start gap-3">
                  <span className="text-2xl">{feature.icon}</span>
                  <div>
                    <h4 className="font-semibold text-text mb-1">{feature.title}</h4>
                    <p className="text-sm text-text-secondary">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-12">
      {/* Header */}
      <div className="text-center">
        <Badge variant="premium" className="text-base px-4 py-2 mb-4">
          <Sparkles className="h-4 w-4 mr-2" />
          Premium Membership
        </Badge>
        <h1 className="text-5xl font-bold text-text mb-4">
          Upgrade to Premium
        </h1>
        <p className="text-xl text-text-secondary max-w-2xl mx-auto">
          Unlock unlimited AI-powered features and take your health journey to the next level
        </p>
      </div>

      {/* Pricing Toggle */}
      <div className="flex justify-center">
        <div className="inline-flex items-center gap-2 p-1 bg-surfaceAlt rounded-lg">
          <button
            onClick={() => setSelectedPeriod('monthly')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              selectedPeriod === 'monthly'
                ? 'bg-primary text-text-onPrimary shadow-md'
                : 'text-text hover:bg-surface'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setSelectedPeriod('yearly')}
            className={`px-6 py-3 rounded-lg font-medium transition-all relative ${
              selectedPeriod === 'yearly'
                ? 'bg-primary text-text-onPrimary shadow-md'
                : 'text-text hover:bg-surface'
            }`}
          >
            Yearly
            <Badge
              variant="premium"
              className="absolute -top-2 -right-2 text-xs"
            >
              Save 33%
            </Badge>
          </button>
        </div>
      </div>

      {/* Pricing Card */}
      <div className="max-w-md mx-auto">
        <Card variant="elevated" className="border-2 border-premium/30">
          <CardContent className="p-8 text-center">
            <Crown className="h-12 w-12 text-premium mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-text mb-2">Premium Plan</h3>
            <div className="mb-6">
              <span className="text-5xl font-bold text-text">
                ${pricing[selectedPeriod].price}
              </span>
              <span className="text-text-secondary ml-2">
                / {pricing[selectedPeriod].period}
              </span>
              {selectedPeriod === 'yearly' && (
                <p className="text-sm text-premium font-medium mt-2">
                  {pricing.yearly.savings}
                </p>
              )}
            </div>

            <Button
              variant="primary"
              size="lg"
              onClick={handleSubscribe}
              isLoading={isLoading}
              className="w-full bg-premium text-primary hover:bg-premium-dark mb-4"
            >
              <Crown className="h-5 w-5 mr-2" />
              Subscribe Now
            </Button>

            <p className="text-xs text-text-secondary">
              7-day free trial • Cancel anytime
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-3xl font-bold text-text text-center mb-8">
          Everything You Get
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {premiumFeatures.map((feature, index) => (
            <Card key={index} variant="outlined" className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-text mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-text-secondary">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-center">Free vs Premium</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-light">
                  <th className="text-left py-4 px-4 text-text font-semibold">Feature</th>
                  <th className="text-center py-4 px-4 text-text font-semibold">Free</th>
                  <th className="text-center py-4 px-4 text-text font-semibold">
                    <Badge variant="premium">Premium</Badge>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border-light">
                  <td className="py-4 px-4 text-text">Manual Food Logging</td>
                  <td className="text-center py-4 px-4">
                    <Check className="h-5 w-5 text-success mx-auto" />
                  </td>
                  <td className="text-center py-4 px-4">
                    <Check className="h-5 w-5 text-success mx-auto" />
                  </td>
                </tr>
                <tr className="border-b border-border-light">
                  <td className="py-4 px-4 text-text">AI Food Photo Analysis</td>
                  <td className="text-center py-4 px-4 text-text-secondary">5 scans</td>
                  <td className="text-center py-4 px-4 text-premium font-semibold">Unlimited</td>
                </tr>
                <tr className="border-b border-border-light">
                  <td className="py-4 px-4 text-text">Body Fat Estimation</td>
                  <td className="text-center py-4 px-4 text-text-secondary">1 scan</td>
                  <td className="text-center py-4 px-4 text-premium font-semibold">Unlimited</td>
                </tr>
                <tr className="border-b border-border-light">
                  <td className="py-4 px-4 text-text">Percentile Ranking</td>
                  <td className="text-center py-4 px-4 text-text-secondary">1 scan</td>
                  <td className="text-center py-4 px-4 text-premium font-semibold">Unlimited</td>
                </tr>
                <tr className="border-b border-border-light">
                  <td className="py-4 px-4 text-text">Workout Form Analysis</td>
                  <td className="text-center py-4 px-4 text-error">✗</td>
                  <td className="text-center py-4 px-4">
                    <Check className="h-5 w-5 text-success mx-auto" />
                  </td>
                </tr>
                <tr>
                  <td className="py-4 px-4 text-text">Transformation Previews</td>
                  <td className="text-center py-4 px-4 text-error">✗</td>
                  <td className="text-center py-4 px-4">
                    <Check className="h-5 w-5 text-success mx-auto" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* CTA Section */}
      <Card variant="elevated" className="bg-gradient-to-r from-premium/10 to-secondary/10">
        <CardContent className="p-12 text-center">
          <h3 className="text-3xl font-bold text-text mb-4">
            Ready to Transform Your Health Journey?
          </h3>
          <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
            Join thousands of users who have unlocked their full potential with Premium
          </p>
          <Button
            variant="primary"
            size="lg"
            onClick={handleSubscribe}
            isLoading={isLoading}
            className="bg-premium text-primary hover:bg-premium-dark text-lg px-12 py-6"
          >
            <Crown className="h-6 w-6 mr-2" />
            Start Your 7-Day Free Trial
          </Button>
          <p className="text-sm text-text-secondary mt-4">
            No credit card required • Cancel anytime
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

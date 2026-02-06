'use client';

/**
 * Subscription Management Page - Phase 3
 *
 * Manages user subscription tiers:
 * - View current plan
 * - Compare plans
 * - Upgrade/downgrade
 * - Payment method management
 * - Billing history
 */

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import {
  useV3SubscriptionInfo,
  useV3SubscriptionPlans,
  useV3UpgradeTier,
} from '@/hooks/useV3';

const BILLING_CYCLES = {
  monthly: { label: 'Monthly', discount: 0 },
  yearly: { label: 'Yearly', discount: 0.17 }, // ~17% discount (2 months free)
};

export default function SubscriptionPage() {
  const [billingCycle, setBillingCycle] = useState<keyof typeof BILLING_CYCLES>('monthly');
  const [selectedTier, setSelectedTier] = useState<'PREMIUM' | 'PRO' | null>(null);

  const { data: subscription, isLoading: subLoading, error: subError } = useV3SubscriptionInfo();
  const { data: plans, isLoading: plansLoading, error: plansError } = useV3SubscriptionPlans();
  const upgradeTier = useV3UpgradeTier();

  // Debug logging
  useEffect(() => {
    console.log('Subscription page - subscription data:', subscription);
    console.log('Subscription page - plans data:', plans);
    console.log('Subscription page - subLoading:', subLoading);
    console.log('Subscription page - plansLoading:', plansLoading);
    if (subError) console.error('Subscription error:', subError);
    if (plansError) console.error('Plans error:', plansError);
  }, [subscription, plans, subLoading, plansLoading, subError, plansError]);

  const handleUpgrade = async (tier: 'PREMIUM' | 'PRO') => {
    console.log('Upgrade button clicked for tier:', tier);
    console.log('Current billing cycle:', billingCycle);

    try {
      console.log('Calling upgradeTier mutation...');
      const result = await upgradeTier.mutateAsync({
        newTier: tier,
        billingCycle,
      });

      console.log('Upgrade result:', result);

      // Update localStorage with new tier for immediate UI update
      localStorage.setItem('user_tier', result.new_tier);
      console.log('Updated localStorage with tier:', result.new_tier);

      setSelectedTier(null);

      // Show success message
      alert(`Successfully upgraded to ${tier}!`);

      // Refresh page data
      window.location.reload();
    } catch (error) {
      console.error('Upgrade failed:', error);
      alert(`Upgrade failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const getPrice = (basePrice: number) => {
    if (billingCycle === 'yearly') {
      const monthlyPrice = basePrice * (1 - BILLING_CYCLES.yearly.discount);
      return Math.round(monthlyPrice * 100) / 100;
    }
    return basePrice;
  };

  const getYearlyPrice = (basePrice: number) => {
    return basePrice * 12 * (1 - BILLING_CYCLES.yearly.discount);
  };

  if (subLoading || plansLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-[50vh]">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  // Show errors if any
  if (subError || plansError) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-[50vh]">
          <Card variant="elevated" className="max-w-md">
            <CardContent className="p-6">
              <div className="text-center">
                <div className="text-4xl mb-4">⚠️</div>
                <h3 className="text-xl font-bold text-text-primary mb-2">
                  Failed to load subscription data
                </h3>
                <p className="text-text-secondary mb-4">
                  {subError ? 'Subscription data error' : 'Plans data error'}
                </p>
                <Button
                  variant="primary"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageContainer>
    );
  }

  const currentTier = subscription?.current_tier || 'FREE';

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Subscription"
        description="Manage your subscription and access premium features"
      />

      {/* Current Plan */}
      {subscription && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="text-2xl">📋</span>
              Current Plan
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-2xl font-bold text-text-primary">
                    {subscription.tier_name}
                  </h3>
                  <Badge variant={currentTier === 'FREE' ? 'default' : 'success'}>
                    {subscription.subscription_status === 'active' ? 'Active' : subscription.subscription_status}
                  </Badge>
                </div>
                <p className="text-text-secondary">
                  {subscription.subscribed_at
                    ? `Subscribed on ${new Date(subscription.subscribed_at).toLocaleDateString()}`
                    : 'Free plan - no subscription required'}
                </p>
              </div>
              {currentTier !== 'FREE' && (
                <Button variant="outline">
                  Manage Subscription
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Billing Cycle Toggle */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex items-center bg-bg-elevated rounded-lg p-1">
          {Object.entries(BILLING_CYCLES).map(([key, value]) => (
            <button
              key={key}
              onClick={() => setBillingCycle(key as keyof typeof BILLING_CYCLES)}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                billingCycle === key
                  ? 'bg-accent-primary text-white shadow-lg'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              {value.label}
              {value.discount > 0 && (
                <span className="ml-2 text-xs opacity-75">
                  Save {Math.round(value.discount * 100)}%
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Pricing Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {plans?.map((plan) => {
          const isCurrentPlan = plan.tier === currentTier;
          const isPopular = plan.tier === 'PREMIUM';

          return (
            <Card
              key={plan.tier}
              className={`relative ${isPopular ? 'ring-2 ring-accent-primary shadow-lg' : ''} ${
                isCurrentPlan ? 'bg-accent-primary/5' : ''
              }`}
            >
              {isPopular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge variant="info" className="px-4 py-1">
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{plan.name}</span>
                  {isCurrentPlan && (
                    <Badge variant="success">Current</Badge>
                  )}
                </CardTitle>
                <div className="mt-4">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-text-primary">
                      ${getPrice(plan.price_monthly)}
                    </span>
                    <span className="text-text-secondary">/month</span>
                  </div>
                  {billingCycle === 'yearly' && (
                    <p className="text-sm text-text-secondary mt-1">
                      Billed ${getYearlyPrice(plan.price_yearly)} yearly
                    </p>
                  )}
                </div>
              </CardHeader>

              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <span className="text-accent-success text-lg">✓</span>
                      <span className="text-sm text-text-secondary">{feature}</span>
                    </li>
                  ))}
                </ul>

                {!isCurrentPlan && plan.tier !== 'FREE' && (
                  <Button
                    variant={isPopular ? 'primary' : 'outline'}
                    className="w-full"
                    onClick={() => {
                      console.log('Button clicked, plan tier:', plan.tier);
                      handleUpgrade(plan.tier as 'PREMIUM' | 'PRO');
                    }}
                    disabled={upgradeTier.isPending}
                  >
                    {upgradeTier.isPending ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin">⏳</span>
                        Processing...
                      </span>
                    ) : (
                      `Upgrade to ${plan.name}`
                    )}
                  </Button>
                )}

                {isCurrentPlan && (
                  <Button variant="outline" className="w-full" disabled>
                    Current Plan
                  </Button>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Features Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-default">
                  <th className="text-left py-3 px-4 font-semibold text-text-primary">Feature</th>
                  <th className="text-center py-3 px-4 font-semibold text-text-primary">Free</th>
                  <th className="text-center py-3 px-4 font-semibold text-text-primary">Premium</th>
                  <th className="text-center py-3 px-4 font-semibold text-text-primary">Pro</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { feature: 'Course Chapters', free: '1-3', premium: 'All', pro: 'All' },
                  { feature: 'Quiz Grading', free: 'Rule-based', premium: 'AI Enhanced', pro: 'AI Advanced' },
                  { feature: 'AI Mentor', free: '❌', premium: '✓', pro: '✓' },
                  { feature: 'Adaptive Learning', free: '❌', premium: '✓', pro: '✓' },
                  { feature: 'Streak Tracking', free: '3 days', premium: 'Unlimited', pro: 'Unlimited' },
                  { feature: 'Achievements', free: 'Basic', premium: 'All', pro: 'All' },
                  { feature: 'API Access', free: '❌', premium: '❌', pro: '✓' },
                  { feature: 'Priority Support', free: '❌', premium: 'Email', pro: '24h Response' },
                ].map((row, i) => (
                  <tr key={i} className="border-b border-border-default">
                    <td className="py-3 px-4 text-sm text-text-primary">{row.feature}</td>
                    <td className="py-3 px-4 text-sm text-center text-text-secondary">{row.free}</td>
                    <td className="py-3 px-4 text-sm text-center text-text-secondary">{row.premium}</td>
                    <td className="py-3 px-4 text-sm text-center text-text-secondary">{row.pro}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}

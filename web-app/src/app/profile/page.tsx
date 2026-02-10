'use client';

/**
 * User profile and settings page with subscription management.
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { GlassCard } from '@/components/ui/GlassCard';
import { useAuth } from '@/hooks';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import { tutorApi, CertificateItem, CertificateEligibility } from '@/lib/api-v3';
import { useV3SubscriptionInfo, useV3SubscriptionPlans, useV3UpgradeTier } from '@/hooks/useV3';
import Link from 'next/link';
import { User, Lock, Gem, Download, Check, X, Award, ExternalLink, ClipboardList, Loader, Sparkles } from 'lucide-react';

const BILLING_CYCLES = {
  monthly: { label: 'Monthly', discount: 0 },
  yearly: { label: 'Yearly', discount: 0.17 },
};

export default function ProfilePage() {
  const { data: user } = useAuth();
  const [userId] = useLocalStorage('user_id', '');
  const [certificates, setCertificates] = useState<CertificateItem[]>([]);
  const [eligibility, setEligibility] = useState<CertificateEligibility | null>(null);
  const [isLoadingCertificates, setIsLoadingCertificates] = useState(true);
  const [billingCycle, setBillingCycle] = useState<keyof typeof BILLING_CYCLES>('monthly');

  // Subscription hooks
  const { data: subscription, isLoading: subLoading, refetch: refetchSubscription } = useV3SubscriptionInfo();
  const { data: plans, isLoading: plansLoading } = useV3SubscriptionPlans();
  const upgradeTier = useV3UpgradeTier();

  const isFree = !user || user.tier === 'free';
  const currentTier = subscription?.current_tier || 'FREE';

  const fetchCertificates = async () => {
    try {
      const data = await tutorApi.getUserCertificates(userId);
      setCertificates(data.certificates);
    } catch (error) {
      // Ignore errors
    } finally {
      setIsLoadingCertificates(false);
    }
  };

  const fetchEligibility = async () => {
    try {
      const data = await tutorApi.checkCertificateEligibility(userId);
      setEligibility(data);
    } catch (error) {
      // Ignore errors
    }
  };

  useEffect(() => {
    if (userId) {
      fetchCertificates();
      fetchEligibility();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleGenerateCertificate = async () => {
    if (!userId) return;

    const studentName = prompt('Enter your full name for the certificate (min 2 characters):');
    if (!studentName || !studentName.trim()) {
      alert('Please enter your name to generate the certificate.');
      return;
    }

    const trimmedName = studentName.trim();
    if (trimmedName.length < 2) {
      alert('Name must be at least 2 characters long.');
      return;
    }

    if (trimmedName.length > 100) {
      alert('Name is too long. Please use a shorter version (max 100 characters).');
      return;
    }

    try {
      await tutorApi.generateCertificate({ user_id: userId, student_name: trimmedName });
      await fetchCertificates();
      await fetchEligibility();
      alert('Certificate generated successfully!');
    } catch (error: any) {
      alert(error.message || 'Failed to generate certificate. Please ensure you meet all requirements (100% completion, 70%+ quiz average).');
    }
  };

  const handleUpgrade = async (tier: 'PREMIUM' | 'PRO') => {
    try {
      const result = await upgradeTier.mutateAsync({
        newTier: tier,
        billingCycle,
      });

      localStorage.setItem('user_tier', result.new_tier);
      await refetchSubscription();

      alert(`Successfully upgraded to ${tier}!`);
      window.location.reload();
    } catch (error) {
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

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Profile & Settings"
        description="Manage your account, subscription, and preferences"
      />

      <div className="grid grid-cols-1 gap-6">
        {/* Account Information and Password - Side by Side */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Account Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <User className="w-5 h-5 text-cosmic-primary" />
                </div>
                Account Information
              </CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Email Address
                </label>
                <Input value={user?.email || 'Loading...'} disabled />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Member Since
                </label>
                <Input
                  value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Loading...'}
                  disabled
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  User ID
                </label>
                <Input
                  value={user?.id || 'Loading...'}
                  disabled
                />
              </div>
            </CardContent>
          </Card>

          {/* Change Password */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                  <Lock className="w-5 h-5 text-accent-warning" />
                </div>
                Change Password
              </CardTitle>
              <CardDescription>Update your password</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label htmlFor="current-password" className="block text-sm font-medium text-text-secondary mb-2">
                  Current Password
                </label>
                <Input id="current-password" type="password" placeholder="Enter current password" />
              </div>
              <div>
                <label htmlFor="new-password" className="block text-sm font-medium text-text-secondary mb-2">
                  New Password
                </label>
                <Input id="new-password" type="password" placeholder="Enter new password" />
              </div>
              <div>
                <label htmlFor="confirm-password" className="block text-sm font-medium text-text-secondary mb-2">
                  Confirm New Password
                </label>
                <Input id="confirm-password" type="password" placeholder="Confirm new password" />
              </div>
              <Button variant="primary">Update Password</Button>
            </CardContent>
          </Card>
        </div>

        {/* Subscription Plans (Always Visible) */}
        <Card className="bg-gradient-to-r from-accent-premium/5 to-accent-primary/5 border-accent-premium/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-premium to-accent-primary flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                Upgrade Your Plan
              </CardTitle>
              <CardDescription>Choose the plan that fits your learning goals</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Billing Cycle Toggle */}
              <div className="flex justify-center mb-6">
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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {plans?.map((plan) => {
                  const isCurrentPlan = plan.tier === currentTier;
                  const isPopular = plan.tier === 'PREMIUM';

                  return (
                    <Card
                      key={plan.tier}
                      className={`relative ${isPopular ? 'ring-2 ring-accent-primary' : ''} ${
                        isCurrentPlan ? 'bg-accent-primary/5' : ''
                      }`}
                    >
                      {isPopular && (
                        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                          <Badge variant="info" className="px-3 py-1">Most Popular</Badge>
                        </div>
                      )}

                      <CardHeader className="pb-3">
                        <CardTitle className="flex items-center justify-between text-base">
                          <span>{plan.name}</span>
                          {isCurrentPlan && <Badge variant="success">Current</Badge>}
                        </CardTitle>
                        <div className="mt-2">
                          <div className="flex items-baseline gap-2">
                            <span className="text-3xl font-bold text-text-primary">
                              ${getPrice(plan.price_monthly)}
                            </span>
                            <span className="text-text-secondary text-sm">/month</span>
                          </div>
                          {billingCycle === 'yearly' && (
                            <p className="text-xs text-text-secondary mt-1">
                              Billed ${getYearlyPrice(plan.price_yearly)} yearly
                            </p>
                          )}
                        </div>
                      </CardHeader>

                      <CardContent className="pt-0">
                        <ul className="space-y-2 mb-4">
                          {plan.features.map((feature, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <Check className="text-accent-success w-4 h-4 flex-shrink-0 mt-0.5" />
                              <span className="text-text-secondary">{feature}</span>
                            </li>
                          ))}
                        </ul>

                        {!isCurrentPlan && plan.tier !== 'FREE' && (
                          <Button
                            variant={isPopular ? 'primary' : 'outline'}
                            className="w-full"
                            onClick={() => handleUpgrade(plan.tier as 'PREMIUM' | 'PRO')}
                            disabled={upgradeTier.isPending}
                            size="sm"
                          >
                            {upgradeTier.isPending ? (
                              <span className="flex items-center gap-2">
                                <Loader className="w-4 h-4 animate-spin" />
                                Processing...
                              </span>
                            ) : (
                              <span>Upgrade to {plan.tier}</span>
                            )}
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
      </div>

      {/* All Certificates Section */}
      <GlassCard className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center">
              <Award className="w-5 h-5 text-white" />
            </div>
            All Certificates
          </CardTitle>
          <CardDescription>
            Course completion certificates (Requirements: 100% completion, 70%+ average score)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Eligibility Status */}
          {eligibility && (
            <div className={`p-4 rounded-lg border mb-4 ${
              eligibility.eligible
                ? 'bg-green-500/10 border-green-500/30'
                : 'bg-glass-hover border-glass-border'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {eligibility.eligible ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : (
                    <X className="w-5 h-5 text-orange-500" />
                  )}
                  <span className="font-semibold text-text-primary">
                    {eligibility.eligible ? 'Eligible for Certificate!' : 'Requirements Not Met'}
                  </span>
                </div>
              </div>
              {!eligibility.eligible && (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-text-secondary">Completion: </span>
                    <span className={`font-semibold ${eligibility.completion_percentage >= eligibility.min_completion_required ? 'text-green-500' : 'text-text-primary'}`}>
                      {eligibility.completion_percentage}% / {eligibility.min_completion_required}%
                    </span>
                  </div>
                  <div>
                    <span className="text-text-secondary">Average Score: </span>
                    <span className={`font-semibold ${eligibility.average_score >= eligibility.min_score_required ? 'text-green-500' : 'text-text-primary'}`}>
                      {eligibility.average_score}% / {eligibility.min_score_required}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Generate Certificate Button */}
          {eligibility && eligibility.eligible && (
            <Button variant="primary" onClick={handleGenerateCertificate} className="w-full mb-4">
              <Award className="w-4 h-4 mr-2" />
              Generate Certificate
            </Button>
          )}

          {/* Certificates List */}
          <div className="space-y-3">
            {isLoadingCertificates ? (
              <div className="text-center py-8 text-text-secondary">Loading certificates...</div>
            ) : certificates.length === 0 ? (
              <div className="text-center py-8 text-text-secondary">
                <Award className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No certificates yet. Complete all course requirements to earn one!</p>
              </div>
            ) : (
              certificates.map((cert) => (
                <div
                  key={cert.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-glass-hover border border-glass-border"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono font-bold text-cosmic-primary">{cert.certificate_id}</span>
                      <Badge variant="success">Verified</Badge>
                    </div>
                    <div className="text-sm text-text-secondary">
                      Issued to <span className="text-text-primary font-medium">{cert.student_name}</span>
                      {' '} on {new Date(cert.issued_at).toLocaleDateString()}
                    </div>
                    <div className="flex gap-4 mt-2 text-xs text-text-secondary">
                      <span>Completion: {cert.completion_percentage}%</span>
                      <span>Avg Score: {cert.average_quiz_score}%</span>
                      <span>Chapters: {cert.total_chapters_completed}</span>
                      <span>Streak: {cert.total_streak_days} days</span>
                    </div>
                  </div>
                  <Link
                    href={`/certificate/verify/${cert.certificate_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Button variant="outline" size="sm" className="gap-1">
                      <ExternalLink className="w-4 h-4" />
                      View
                    </Button>
                  </Link>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </GlassCard>

      {/* Danger Zone */}
      <Card className="mt-6 border-accent-danger/30">
        <CardHeader>
          <CardTitle className="text-accent-danger flex items-center gap-2">
            <X className="w-5 h-5" />
            Danger Zone
          </CardTitle>
          <CardDescription>Irreversible actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-text-secondary">
              Deleting your account will permanently remove all your data including progress, quiz results, and personal information. This action cannot be undone.
            </p>
            <Button variant="danger" className="w-full sm:w-auto">
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}

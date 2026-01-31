'use client';

/**
 * User profile and settings page with Professional/Modern SaaS theme.
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input, Textarea } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useAuth } from '@/hooks';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default function ProfilePage() {
  const { data: user } = useAuth();

  const isFree = !user || user.tier === 'free';

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Profile & Settings"
        description="Manage your account and preferences"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Account Info & Password */}
        <div className="lg:col-span-2 space-y-6">
          {/* Account Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-xl">👤</span>
                Account Information
              </CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Email Address
                </label>
                <Input value={user?.email || 'student@example.com'} disabled />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Member Since
                </label>
                <Input
                  value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'January 2026'}
                  disabled
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  User ID
                </label>
                <Input
                  value={user?.id || '82b8b862-059a-416a-9ef4-e582a4870efa'}
                  disabled
                />
              </div>
            </CardContent>
          </Card>

          {/* Change Password */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-xl">🔒</span>
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

        {/* Right Column - Subscription */}
        <div className="space-y-6">
          <Card variant={isFree ? 'default' : 'elevated'}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-xl">💎</span>
                Subscription
              </CardTitle>
              <CardDescription>Your current plan</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className={`p-4 rounded-lg border ${
                isFree
                  ? 'bg-bg-elevated/50 border-border-default'
                  : 'bg-accent-premium/10 border-accent-premium/30'
              }`}>
                <div className="text-sm font-medium text-text-secondary mb-1">
                  Current Tier
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-2xl font-bold capitalize">
                    {user?.tier || 'free'}
                  </div>
                  {isFree ? (
                    <Badge variant="default">Free</Badge>
                  ) : (
                    <Badge variant="premium">PRO</Badge>
                  )}
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold text-text-primary">
                  {isFree ? 'Free Plan Benefits' : 'Premium Benefits'}
                </h3>
                <ul className="text-sm text-text-secondary space-y-2">
                  {(isFree ? [
                    { benefit: 'First 3 chapters', included: true },
                    { benefit: 'Basic quizzes', included: true },
                    { benefit: 'Progress tracking', included: true },
                    { benefit: 'All 10 chapters', included: false },
                    { benefit: 'Advanced quizzes', included: false },
                    { benefit: 'AI Mentor (Phase 2)', included: false },
                  ] : [
                    { benefit: 'All 10 chapters', included: true },
                    { benefit: 'Advanced quizzes', included: true },
                    { benefit: 'AI-powered features', included: true },
                    { benefit: 'Progress tracking', included: true },
                    { benefit: 'Priority support', included: true },
                    { benefit: 'Certificates', included: true },
                  ]).map((item, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className={item.included ? 'text-accent-success' : 'text-text-muted'}>
                        {item.included ? '✓' : '✗'}
                      </span>
                      <span className={item.included ? 'text-text-primary' : 'text-text-muted'}>
                        {item.benefit}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              {isFree && (
                <Button variant="primary" className="w-full">
                  Upgrade to Premium - $9.99/mo
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Data Export */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-xl">📥</span>
            Data Export
          </CardTitle>
          <CardDescription>Download your learning data (GDPR compliance)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="secondary">Export All Data (JSON)</Button>
            <Button variant="outline">Export Progress (CSV)</Button>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="mt-6 border-accent-danger/30">
        <CardHeader>
          <CardTitle className="text-accent-danger flex items-center gap-2">
            <span>⚠️</span>
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

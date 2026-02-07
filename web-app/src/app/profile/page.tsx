'use client';

/**
 * User profile and settings page with Professional/Modern SaaS theme.
 */
import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input, Textarea } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { GlassCard } from '@/components/ui/GlassCard';
import { useAuth } from '@/hooks';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import { tutorApi, CertificateItem, CertificateEligibility } from '@/lib/api-v3';
import Link from 'next/link';
import { User, AlertTriangle, Lock, Gem, Download, Check, X, Award, ExternalLink } from 'lucide-react';

export default function ProfilePage() {
  const { data: user } = useAuth();
  const [userId] = useLocalStorage('user_id', '');
  const [certificates, setCertificates] = useState<CertificateItem[]>([]);
  const [eligibility, setEligibility] = useState<CertificateEligibility | null>(null);
  const [isLoadingCertificates, setIsLoadingCertificates] = useState(true);

  const isFree = !user || user.tier === 'free';

  useEffect(() => {
    if (userId) {
      fetchCertificates();
      fetchEligibility();
    }
  }, [userId]);

  const fetchCertificates = async () => {
    try {
      const data = await tutorApi.getUserCertificates(userId);
      setCertificates(data.certificates);
    } catch (error) {
      console.error('Failed to fetch certificates:', error);
    } finally {
      setIsLoadingCertificates(false);
    }
  };

  const fetchEligibility = async () => {
    try {
      const data = await tutorApi.checkCertificateEligibility(userId);
      setEligibility(data);
    } catch (error) {
      console.error('Failed to check eligibility:', error);
    }
  };

  const handleGenerateCertificate = async () => {
    if (!userId) return;

    const studentName = prompt('Enter your full name for the certificate:');
    if (!studentName || !studentName.trim()) return;

    try {
      await tutorApi.generateCertificate({ user_id: userId, student_name: studentName.trim() });
      await fetchCertificates();
      await fetchEligibility();
      alert('Certificate generated successfully!');
    } catch (error: any) {
      console.error('Failed to generate certificate:', error);
      alert(error.message || 'Failed to generate certificate. Please ensure you meet all requirements.');
    }
  };

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

        {/* Right Column - Subscription */}
        <div className="space-y-6">
          <Card variant={isFree ? 'default' : 'elevated'}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
                  <Gem className="w-5 h-5 text-accent-premium" />
                </div>
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
                        {item.included ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
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
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center">
              <Download className="w-5 h-5 text-accent-primary" />
            </div>
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

      {/* Certificates Section - Gamification Feature */}
      <GlassCard className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center">
              <Award className="w-5 h-5 text-white" />
            </div>
            Certificates
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
                    <AlertTriangle className="w-5 h-5 text-orange-500" />
                  )}
                  <span className="font-semibold text-text-primary">
                    {eligibility.eligible ? 'Eligible for Certificate!' : 'Not Yet Eligible'}
                  </span>
                </div>
                {eligibility.eligible && (
                  <Button variant="primary" onClick={handleGenerateCertificate}>
                    <Award className="w-4 h-4 mr-1" />
                    Generate Certificate
                  </Button>
                )}
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
            <AlertTriangle className="w-5 h-5" />
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

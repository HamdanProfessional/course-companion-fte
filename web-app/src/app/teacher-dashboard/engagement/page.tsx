'use client';

/**
 * Teacher Engagement Page
 *
 * Features:
 * - Student engagement metrics
 * - Activity tracking
 * - Communication tools
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Eye, Clock, TrendingUp, AlertCircle, Send, Users, Target } from 'lucide-react';
import { useTeacherEngagement, type AtRiskStudent, type RecentActivity } from '@/hooks';

export default function TeacherEngagementPage() {
  const router = useRouter();

  const {
    metrics,
    atRiskStudents = [],
    recentActivity = [],
    isLoading,
    error,
    refetch,
  } = useTeacherEngagement();

  useEffect(() => {
    const role = localStorage.getItem('user_role');
    if (role !== 'teacher') {
      router.push('/dashboard');
    }
  }, [router]);

  // Helper to format timestamp
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMinutes / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMinutes < 1) return 'Just now';
      if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      if (diffDays === 1) return '1 day ago';
      if (diffDays < 7) return `${diffDays} days ago`;
      return date.toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  // Helper to format last activity
  const formatLastActivity = (lastActivity: string): string => {
    try {
      const date = new Date(lastActivity);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return '1 day ago';
      if (diffDays < 7) return `${diffDays} days ago`;
      return `${diffDays} days ago`;
    } catch {
      return 'Unknown';
    }
  };

  // Helper to get risk badge variant
  const getRiskBadgeVariant = (riskLevel: string): 'danger' | 'warning' | 'info' => {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'info';
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <PageContainer>
        <div className="text-center py-12">
          <p className="text-accent-danger mb-4">Failed to load engagement data</p>
          <Button variant="primary" onClick={() => refetch()}>
            Try Again
          </Button>
        </div>
      </PageContainer>
    );
  }

  // Calculate weekly change from weekly_activity array if available
  const weeklyChange = metrics?.weekly_activity && metrics.weekly_activity.length >= 2
    ? ((metrics.weekly_activity[metrics.weekly_activity.length - 1] - metrics.weekly_activity[0]) / Math.abs(metrics.weekly_activity[0]) * 100).toFixed(0)
    : '+0';

  const displayWeeklyChange = weeklyChange.startsWith('-') ? weeklyChange : `+${weeklyChange}`;

  return (
    <PageContainer>
      <PageHeader
        title="Student Engagement"
        description="Track and improve student engagement"
      />

      {/* Engagement Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <Clock className="w-6 h-6 text-cosmic-primary" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-text-primary">{metrics?.average_session_time ?? 'N/A'}</h3>
            <p className="text-sm text-text-secondary">Avg. Session Time</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                <Users className="w-6 h-6 text-accent-success" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-text-primary">{metrics?.active_students ?? 0}</h3>
            <p className="text-sm text-text-secondary">Active This Week</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center">
                <Target className="w-6 h-6 text-accent-primary" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-text-primary">{metrics?.completion_rate ?? 0}%</h3>
            <p className="text-sm text-text-secondary">Completion Rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-accent-warning" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-accent-warning">{displayWeeklyChange}%</h3>
            <p className="text-sm text-text-secondary">Weekly Change</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* At-Risk Students */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-danger/20 to-accent-danger/10 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-accent-danger" />
              </div>
              At-Risk Students
            </CardTitle>
          </CardHeader>
          <CardContent>
            {atRiskStudents.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-text-muted">No at-risk students detected. Great job keeping everyone engaged!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {atRiskStudents.map((student) => (
                  <div
                    key={student.user_id}
                    className="p-4 rounded-lg border border-accent-danger/30 bg-accent-danger/5"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-text-primary">{student.name}</h4>
                        <p className="text-sm text-text-secondary">{student.email}</p>
                      </div>
                      <Badge
                        variant={getRiskBadgeVariant(student.risk_level)}
                        className="capitalize"
                      >
                        {student.risk_level} Risk
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-text-secondary mb-2">
                      <Clock className="w-4 h-4" />
                      Last activity: {formatLastActivity(student.last_activity)}
                    </div>
                    {student.risk_factors && student.risk_factors.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {student.risk_factors.slice(0, 2).map((factor, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {factor}
                          </Badge>
                        ))}
                      </div>
                    )}
                    <Button variant="outline" size="sm" className="w-full">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Send Nudge
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity Feed */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
                <Eye className="w-6 h-6 text-accent-info" />
              </div>
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentActivity.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-text-muted">No recent activity yet. Activity will appear here as students engage with the course.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.activity_id} className="flex items-start gap-3 pb-4 border-b border-border-default last:border-0 last:pb-0">
                    <div className="w-8 h-8 rounded-full bg-cosmic-primary/20 flex items-center justify-center flex-shrink-0">
                      <Users className="w-4 h-4 text-cosmic-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-text-primary">
                        <span className="font-semibold">{activity.student_name}</span> {activity.description}
                      </p>
                      <p className="text-xs text-text-muted mt-1">{formatTimestamp(activity.timestamp)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Communication Tools */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
              <Send className="w-6 h-6 text-cosmic-primary" />
            </div>
            Bulk Communication
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-bg-elevated border border-border-default">
              <h4 className="font-semibold text-text-primary mb-2">Send Announcement</h4>
              <p className="text-sm text-text-secondary mb-4">
                Send a message to all students or specific groups
              </p>
              <div className="flex gap-3">
                <Button variant="primary">
                  <Send className="w-4 h-4 mr-2" />
                  Compose Message
                </Button>
                <Button variant="outline">
                  Schedule for Later
                </Button>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-bg-elevated border border-border-default">
              <h4 className="font-semibold text-text-primary mb-2">Automated Nudges</h4>
              <p className="text-sm text-text-secondary mb-4">
                Automatically remind inactive students to continue learning
              </p>
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Status: Active</span>
                <Badge variant="success">Enabled</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}

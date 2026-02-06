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

export default function TeacherEngagementPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  // Mock engagement data
  const engagementMetrics = {
    averageSessionTime: '24 min',
    activeStudents: 89,
    completionRate: 68,
    weeklyActivity: '+12%',
  };

  const atRiskStudents = [
    { id: 1, name: 'John Smith', email: 'john@example.com', lastActivity: '5 days ago', risk: 'high' },
    { id: 2, name: 'Sarah Johnson', email: 'sarah@example.com', lastActivity: '3 days ago', risk: 'medium' },
    { id: 3, name: 'Mike Brown', email: 'mike@example.com', lastActivity: '7 days ago', risk: 'high' },
  ];

  const recentActivity = [
    { student: 'Emily Davis', action: 'Completed Chapter 3', time: '2 minutes ago' },
    { student: 'Tom Wilson', action: 'Started Quiz 2', time: '15 minutes ago' },
    { student: 'Lisa Anderson', action: 'Achieved 7-day streak', time: '1 hour ago' },
    { student: 'James Lee', action: 'Asked a question in AI Mentor', time: '2 hours ago' },
  ];

  useEffect(() => {
    const role = localStorage.getItem('user_role');
    if (role !== 'teacher') {
      router.push('/dashboard');
      return;
    }
    setIsLoading(false);
  }, [router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

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
            <h3 className="text-2xl font-bold text-text-primary">{engagementMetrics.averageSessionTime}</h3>
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
            <h3 className="text-2xl font-bold text-text-primary">{engagementMetrics.activeStudents}</h3>
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
            <h3 className="text-2xl font-bold text-text-primary">{engagementMetrics.completionRate}%</h3>
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
            <h3 className="text-2xl font-bold text-accent-warning">{engagementMetrics.weeklyActivity}</h3>
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
            <div className="space-y-3">
              {atRiskStudents.map((student) => (
                <div
                  key={student.id}
                  className="p-4 rounded-lg border border-accent-danger/30 bg-accent-danger/5"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-text-primary">{student.name}</h4>
                      <p className="text-sm text-text-secondary">{student.email}</p>
                    </div>
                    <Badge
                      variant={student.risk === 'high' ? 'danger' : 'warning'}
                      className="capitalize"
                    >
                      {student.risk} Risk
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-text-secondary mb-3">
                    <Clock className="w-4 h-4" />
                    Last activity: {student.lastActivity}
                  </div>
                  <Button variant="outline" size="sm" className="w-full">
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Send Nudge
                  </Button>
                </div>
              ))}
            </div>
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
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 pb-4 border-b border-border-default last:border-0 last:pb-0">
                  <div className="w-8 h-8 rounded-full bg-cosmic-primary/20 flex items-center justify-center flex-shrink-0">
                    <Users className="w-4 h-4 text-cosmic-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-text-primary">
                      <span className="font-semibold">{activity.student}</span> {activity.action}
                    </p>
                    <p className="text-xs text-text-muted mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
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

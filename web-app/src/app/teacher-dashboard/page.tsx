'use client';

/**
 * Teacher Dashboard - Professional/Modern SaaS theme
 *
 * Features:
 * - Overview stats (students, engagement, performance)
 * - Student progress monitoring
 * - Quiz performance analytics
 * - Course content management
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { Users, TrendingUp, Award, BookOpen, MessageSquare, CheckCircle, BarChart3, FileEdit, GraduationCap, Target, Flame, AlertTriangle, Trophy } from 'lucide-react';
import Link from 'next/link';
import { useTeacherAnalytics, useTeacherStudents } from '@/hooks';

// StatCard component for teacher metrics
function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'default',
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon?: React.ReactNode;
  trend?: { value: number; isPositive: boolean };
  variant?: 'default' | 'success' | 'warning' | 'info' | 'danger';
}) {
  const variantStyles = {
    default: 'text-accent-primary',
    success: 'text-accent-success',
    warning: 'text-accent-warning',
    info: 'text-accent-primary',
    danger: 'text-accent-danger',
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-text-secondary mb-1">{title}</p>
            <div className="flex items-baseline gap-2">
              <h3 className={`text-3xl font-bold ${variantStyles[variant]}`}>
                {value}
              </h3>
              {trend && (
                <span
                  className={`text-sm font-medium ${
                    trend.isPositive ? 'text-accent-success' : 'text-accent-danger'
                  }`}
                >
                  {trend.isPositive ? '↑' : '↓'} {trend.value}%
                </span>
              )}
            </div>
            <p className="text-sm text-text-muted mt-1">{subtitle}</p>
          </div>
          {icon && (
            <div className="w-12 h-12 rounded-xl bg-bg-elevated flex items-center justify-center text-2xl">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Quick Action Card
function QuickActionCard({
  title,
  description,
  icon,
  href,
  badge,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  badge?: string;
}) {
  return (
    <Link href={href} className="block group">
      <Card className="group-hover:border-accent-primary group-hover:shadow-lg transition-all h-full">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-accent-primary/10 flex items-center justify-center text-2xl group-hover:bg-accent-primary/20 transition-all">
              {icon}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-text-primary group-hover:text-accent-primary transition-colors">
                  {title}
                </h3>
                {badge && (
                  <Badge variant="info" className="text-xs">
                    {badge}
                  </Badge>
                )}
              </div>
              <p className="text-sm text-text-muted">{description}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

// Student Progress Row
function StudentProgressRow({
  name,
  email,
  progress,
  streak,
  lastActivity,
  tier,
}: {
  name: string;
  email: string;
  progress: number;
  streak: number;
  lastActivity: string;
  tier: string;
}) {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg border border-border-default hover:border-accent-primary hover:bg-bg-elevated transition-all">
      <div className="flex-1">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-accent-primary/10 flex items-center justify-center text-accent-primary font-semibold">
            {name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h4 className="font-medium text-text-primary">{name}</h4>
            <p className="text-sm text-text-muted">{email}</p>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-center">
          <p className="text-xs text-text-muted mb-1">Progress</p>
          <Badge variant={progress >= 75 ? 'success' : progress >= 50 ? 'intermediate' : 'beginner'}>
            {progress}%
          </Badge>
        </div>
        <div className="text-center">
          <p className="text-xs text-text-muted mb-1">Streak</p>
          <p className="text-sm font-medium text-text-primary flex items-center justify-center gap-1">
            <Flame className="w-4 h-4" />
            {streak}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-text-muted mb-1">Tier</p>
          <Badge variant={tier === 'PRO' ? 'premium' : tier === 'PREMIUM' ? 'intermediate' : 'beginner'}>
            {tier}
          </Badge>
        </div>
        <div className="text-center w-24">
          <p className="text-xs text-text-muted mb-1">Last Active</p>
          <p className="text-sm text-text-primary">{lastActivity}</p>
        </div>
        <Link href={`/teacher-dashboard/students/${email}`}>
          <Button variant="outline" size="sm">
            View Details
          </Button>
        </Link>
      </div>
    </div>
  );
}

export default function TeacherDashboardPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { data: stats, isLoading: statsLoading, error: statsError } = useTeacherAnalytics();
  const { data: students, isLoading: studentsLoading, error: studentsError } = useTeacherStudents();

  useEffect(() => {
    // Get user info from localStorage
    const id = localStorage.getItem('user_id');
    const role = localStorage.getItem('user_role');

    if (!id) {
      router.push('/login');
      return;
    }

    // Check if user is a teacher
    if (role !== 'teacher') {
      router.push('/dashboard');
      return;
    }

    setUserId(id);
    setUserRole(role);
    setIsLoading(false);
  }, [router]);

  if (isLoading || statsLoading || studentsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (statsError || studentsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-text-muted mb-4">Failed to load teacher dashboard data</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  // Transform student data for display
  const displayStudents = students?.slice(0, 4).map(student => ({
    name: student.name,
    email: student.email,
    progress: student.progress,
    streak: student.streak,
    lastActivity: student.last_activity,
    tier: student.tier,
  })) || [];

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Teacher Dashboard"
        description="Monitor student progress and manage course content"
      />

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <QuickActionCard
          title="Manage Students"
          description="View and manage student enrollments"
          icon={<Users className="w-6 h-6" />}
          href="/teacher-dashboard/students"
        />
        <QuickActionCard
          title="Quiz Analytics"
          description="View quiz performance and insights"
          icon={<BarChart3 className="w-6 h-6" />}
          href="/teacher-dashboard/analytics"
        />
        <QuickActionCard
          title="Course Content"
          description="Edit chapters and quizzes"
          icon={<BookOpen className="w-6 h-6" />}
          href="/teacher-dashboard/content"
        />
        <QuickActionCard
          title="Engagement"
          description="Track student engagement metrics"
          icon={<MessageSquare className="w-6 h-6" />}
          href="/teacher-dashboard/engagement"
        />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Students"
          value={stats?.total_students || 0}
          subtitle="Enrolled in course"
          icon={<Users className="w-6 h-6 text-accent-primary" />}
          variant="default"
        />
        <StatCard
          title="Active Students"
          value={stats?.active_students || 0}
          subtitle="Active in last 7 days"
          icon={<TrendingUp className="w-6 h-6 text-accent-success" />}
          variant="success"
        />
        <StatCard
          title="Avg. Quiz Score"
          value={`${Math.round(stats?.average_score || 0)}%`}
          subtitle="Across all quizzes"
          icon={<Award className="w-6 h-6 text-accent-primary" />}
          variant="info"
        />
        <StatCard
          title="Completion Rate"
          value={`${Math.round(stats?.completion_rate || 0)}%`}
          subtitle="Students completed course"
          icon={<CheckCircle className="w-6 h-6 text-accent-warning" />}
          variant="warning"
        />
      </div>

      {/* Recent Student Activity */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <FileEdit className="w-6 h-6 text-cosmic-primary" />
              </div>
              Recent Student Activity
            </CardTitle>
            <Link href="/teacher-dashboard/students">
              <Button variant="outline" size="sm">
                View All Students →
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {displayStudents.length > 0 ? (
              displayStudents.map((student, index) => (
                <StudentProgressRow key={index} {...student} />
              ))
            ) : (
              <p className="text-center text-text-muted py-8">No students enrolled yet</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Performance Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
                <Trophy className="w-6 h-6 text-accent-premium" />
              </div>
              Top Performers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {displayStudents.slice(0, 3).map((student, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-accent-success/10 flex items-center justify-center text-accent-success font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{student.name}</p>
                      <p className="text-sm text-text-muted">{student.progress}% complete</p>
                    </div>
                  </div>
                  <Badge variant="success" className="gap-1">
                    <Flame className="w-3 h-3" />
                    {student.streak} day streak
                  </Badge>
                </div>
              ))}
              {displayStudents.length === 0 && (
                <p className="text-center text-text-muted py-4">No students yet</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Needs Attention */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-accent-warning" />
              </div>
              Needs Attention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">Students at risk</p>
                  <p className="text-sm text-text-muted">Not active in 7+ days</p>
                </div>
                <Badge variant="danger">{stats?.students_at_risk || 0} students</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">Failing quizzes</p>
                  <p className="text-sm text-text-muted">Score below 60%</p>
                </div>
                <Badge variant="warning">{stats?.students_failing_quizzes || 0} students</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">Stale streaks</p>
                  <p className="text-sm text-text-muted">Lost 3+ day streak</p>
                </div>
                <Badge variant="intermediate">{stats?.students_with_stale_streaks || 0} students</Badge>
              </div>
              <Link href="/teacher-dashboard/students?filter=at-risk">
                <Button variant="outline" className="w-full">
                  View At-Risk Students →
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}

'use client';

/**
 * Dashboard page with Professional/Modern SaaS theme.
 * Clean, content-focused interface optimized for educational platforms.
 */
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress, CircularProgress } from '@/components/ui/Progress';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useProgress, useStreak, useChapters } from '@/hooks';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// StatCard component for dashboard metrics
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
  variant?: 'default' | 'success' | 'warning' | 'info';
}) {
  const variantStyles = {
    default: 'text-accent-primary',
    success: 'text-accent-success',
    warning: 'text-accent-warning',
    info: 'text-accent-primary',
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

export default function DashboardPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    // Get the logged-in user's ID from localStorage
    const storedUserId = localStorage.getItem('user_id');
    const userRole = localStorage.getItem('user_role');

    if (!storedUserId) {
      // Not logged in, redirect to login
      router.push('/login');
      return;
    }

    // If user is a teacher, redirect to teacher dashboard
    if (userRole === 'teacher') {
      router.push('/teacher-dashboard');
      return;
    }

    setUserId(storedUserId);
  }, [router]);

  const { data: progress, isLoading: progressLoading } = useProgress(userId || '');
  const { data: streak, isLoading: streakLoading } = useStreak(userId || '');
  const { data: chapters, isLoading: chaptersLoading } = useChapters();

  if (!userId || progressLoading || streakLoading || chaptersLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const completionPercentage = progress?.completion_percentage || 0;
  const currentStreak = streak?.current_streak || 0;
  const completedCount = progress?.completed_chapters?.length || 0;
  const totalChapters = chapters?.length || 0;
  const completedChapters = new Set(progress?.completed_chapters || []);

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate' },
      advanced: { variant: 'advanced' as const, label: 'Advanced' },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Welcome back!"
        description="Continue your learning journey through AI Agent Development"
      />

      {/* Quick Links - AI Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <Link href="/adaptive-learning" className="group">
          <Card className="group-hover:border-accent-secondary group-hover:shadow-lg transition-all">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-accent-secondary/10 flex items-center justify-center text-2xl group-hover:bg-accent-secondary/20 transition-all">
                  🧠
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-text-primary group-hover:text-accent-secondary transition-colors">
                    Adaptive Learning
                  </h3>
                  <p className="text-sm text-text-muted mt-1">
                    AI-powered personalized recommendations
                  </p>
                </div>
                <span className="px-2 py-1 rounded text-xs font-bold bg-accent-secondary text-white">
                  AI
                </span>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/ai-mentor" className="group">
          <Card className="group-hover:border-accent-secondary group-hover:shadow-lg transition-all">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-accent-secondary/10 flex items-center justify-center text-2xl group-hover:bg-accent-secondary/20 transition-all">
                  🤖
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-text-primary group-hover:text-accent-secondary transition-colors">
                    AI Mentor
                  </h3>
                  <p className="text-sm text-text-muted mt-1">
                    24/7 interactive tutoring and Q&A
                  </p>
                </div>
                <span className="px-2 py-1 rounded text-xs font-bold bg-accent-secondary text-white">
                  AI
                </span>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Course Progress"
          value={`${completionPercentage.toFixed(0)}%`}
          subtitle={`${completedCount} of ${totalChapters} chapters`}
          icon="📊"
          variant="info"
        />
        <StatCard
          title="Current Streak"
          value={currentStreak}
          subtitle={currentStreak === 1 ? 'day in a row' : 'days in a row'}
          icon="🔥"
          variant="warning"
        />
        <StatCard
          title="Completed"
          value={completedCount}
          subtitle={`of ${totalChapters} chapters`}
          icon="✅"
          variant="success"
        />
        <StatCard
          title="Remaining"
          value={totalChapters - completedCount}
          subtitle="chapters to complete"
          icon="📚"
          variant="default"
        />
      </div>

      {/* Course Outline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <span className="text-2xl">📖</span>
            Course Outline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {chapters?.map((chapter, index) => {
              const isCompleted = completedChapters.has(chapter.id);
              const difficultyBadge = getDifficultyBadge(chapter.difficulty_level);

              return (
                <Link
                  key={chapter.id}
                  href={`/chapters/${chapter.id}`}
                  className="block group"
                >
                  <div className="flex items-center justify-between p-4 rounded-lg border border-border-default hover:border-accent-primary hover:bg-bg-elevated transition-all">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-lg bg-bg-elevated flex items-center justify-center text-lg font-bold text-text-secondary group-hover:text-accent-primary group-hover:bg-accent-primary/10 transition-all">
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="font-semibold text-text-primary group-hover:text-accent-primary transition-colors">
                          {chapter.title}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant={difficultyBadge.variant}>
                            {difficultyBadge.label}
                          </Badge>
                          <span className="text-sm text-text-muted">
                            ⏱️ {chapter.estimated_time} min
                          </span>
                        </div>
                      </div>
                    </div>
                    <div>
                      {isCompleted ? (
                        <Badge variant="success">✓ Completed</Badge>
                      ) : (
                        <span className="text-text-secondary text-sm font-medium group-hover:text-accent-primary transition-colors">
                          Start →
                        </span>
                      )}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        <Link href="/chapters">
          <Button variant="primary" className="w-full" size="lg">
            📚 Browse Chapters
          </Button>
        </Link>
        <Link href="/quizzes">
          <Button variant="secondary" className="w-full" size="lg">
            🎯 Take a Quiz
          </Button>
        </Link>
        <Link href="/progress">
          <Button variant="outline" className="w-full" size="lg">
            📊 View Progress
          </Button>
        </Link>
      </div>
    </PageContainer>
  );
}

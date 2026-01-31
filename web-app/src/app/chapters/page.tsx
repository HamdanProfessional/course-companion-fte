'use client';

/**
 * Chapters list page with Professional/Modern SaaS theme.
 * Grid layout with filters and clean card design.
 */
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Progress } from '@/components/ui/Progress';
import { Badge } from '@/components/ui/Badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useChapters, useProgress, useUserTier } from '@/hooks';
import Link from 'next/link';
import * as React from 'react';

export const dynamic = 'force-dynamic';

type FilterType = 'all' | 'completed' | 'in-progress' | 'locked';

export default function ChaptersPage() {
  const { data: chapters, isLoading } = useChapters();
  const { data: progress } = useProgress();
  const { data: tier } = useUserTier();
  const [filter, setFilter] = React.useState<FilterType>('all');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const completedChapters = new Set(progress?.completed_chapters || []);

  // Calculate completion percentage
  const completionPercent = chapters ? Math.round((completedChapters.size / chapters.length) * 100) : 0;

  // Filter chapters
  const filteredChapters = chapters?.filter((chapter, index) => {
    const isCompleted = completedChapters.has(chapter.id);
    const isLocked = tier === 'FREE' && index >= 3;

    switch (filter) {
      case 'completed':
        return isCompleted;
      case 'in-progress':
        return !isCompleted && !isLocked;
      case 'locked':
        return isLocked;
      default:
        return true;
    }
  }) || [];

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner', icon: '🌱' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate', icon: '🚀' },
      advanced: { variant: 'advanced' as const, label: 'Advanced', icon: '🏆' },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Course Chapters"
        description="Master AI Agent Development step by step"
      />

      {/* Progress Overview */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-text-secondary">Your Progress</span>
            <span className="text-sm font-bold text-text-primary">
              {completedChapters.size}/{chapters?.length} Complete
            </span>
          </div>
          <Progress value={completionPercent} size="md" className="mb-2" />
          <p className="text-xs text-text-muted">{completionPercent}% of course completed</p>
        </CardContent>
      </Card>

      {/* Filter Tabs */}
      <Tabs value={filter} onValueChange={(value) => setFilter(value as FilterType)} className="mb-6">
        <TabsList>
          <TabsTrigger value="all">All Chapters</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="in-progress">In Progress</TabsTrigger>
          <TabsTrigger value="locked">Locked</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Chapters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredChapters.map((chapter, index) => {
          const isCompleted = completedChapters.has(chapter.id);
          const isLocked = tier === 'FREE' && index >= 3;
          const difficultyBadge = getDifficultyBadge(chapter.difficulty_level);

          return (
            <Card
              key={chapter.id}
              variant={isCompleted ? 'elevated' : 'default'}
              className="group transition-all duration-300 hover:shadow-lg"
            >
              <CardHeader>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-bold text-text-secondary bg-bg-elevated px-2 py-1 rounded-md">
                        #{index + 1}
                      </span>
                      {isCompleted && (
                        <Badge variant="success">✓ Completed</Badge>
                      )}
                    </div>
                    <CardTitle className="text-xl group-hover:text-accent-primary transition-colors">
                      {chapter.title}
                    </CardTitle>
                  </div>
                  <div className="text-3xl transform group-hover:scale-110 transition-transform">
                    {isLocked ? '🔒' : isCompleted ? '🎉' : '📖'}
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant={difficultyBadge.variant}>
                    {difficultyBadge.icon} {difficultyBadge.label}
                  </Badge>
                  <span className="inline-flex items-center text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded-md">
                    ⏱️ {chapter.estimated_time} min
                  </span>
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-3">
                  {isLocked ? (
                    <div className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-4 text-center">
                      <p className="text-sm text-accent-warning font-medium mb-1">
                        🔒 Premium Content
                      </p>
                      <p className="text-xs text-text-muted">
                        Upgrade to PRO to unlock this chapter
                      </p>
                      <Link href="/profile">
                        <Button variant="outline" size="sm" className="mt-3">
                          Upgrade Now
                        </Button>
                      </Link>
                    </div>
                  ) : (
                    <>
                      <Link href={`/chapters/${chapter.id}`}>
                        <Button
                          variant={isCompleted ? 'outline' : 'primary'}
                          className="w-full"
                        >
                          {isCompleted ? '📚 Review Chapter' : '🚀 Start Chapter'}
                        </Button>
                      </Link>

                      {chapter.quiz_id && (
                        <Link href={`/quizzes/${chapter.quiz_id}`}>
                          <Button
                            variant="secondary"
                            className="w-full"
                          >
                            🎯 Take Quiz →
                          </Button>
                        </Link>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Motivational footer */}
      {chapters && completedChapters.size < chapters.length ? (
        <div className="text-center py-8 mt-8 border-t border-border-default">
          <p className="text-text-secondary text-sm">
            Keep learning! You're making great progress. 🌟
          </p>
        </div>
      ) : chapters && completedChapters.size === chapters.length ? (
        <div className="text-center py-8 mt-8 border-t border-border-default">
          <p className="text-accent-success font-semibold">
            🎉 Congratulations! You've completed the course!
          </p>
        </div>
      ) : null}
    </PageContainer>
  );
}

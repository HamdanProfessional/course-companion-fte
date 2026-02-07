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
import { EmptyStates } from '@/components/ui/EmptyState';
import { useChapters, useProgress, useUserTier } from '@/hooks';
import Link from 'next/link';
import * as React from 'react';
import { Sprout, Rocket, Trophy, Lock, BookOpen, CheckCircle, Play, Target, Star, Search, Clock, Check } from 'lucide-react';

type FilterType = 'all' | 'completed' | 'in-progress' | 'locked';

export default function ChaptersPage() {
  const { data: chapters, isLoading } = useChapters();
  const { data: progress } = useProgress();
  const { data: tier } = useUserTier();
  const [filter, setFilter] = React.useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = React.useState('');

  if (isLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  // Handle case when chapters array is empty or null
  if (!chapters || chapters.length === 0) {
    return (
      <PageContainer>
        <PageHeader
          title="Course Chapters"
          description="Master AI Agent Development step by step"
        />
        <EmptyStates.NoChapters
          title="No chapters available yet"
          description="Course content is being prepared. Check back soon!"
          size="lg"
        />
      </PageContainer>
    );
  }

  const completedChapters = new Set(progress?.completed_chapters || []);

  // Calculate completion percentage
  const completionPercent = chapters ? Math.round((completedChapters.size / chapters.length) * 100) : 0;

  // Filter chapters
  const filteredChapters = chapters?.filter((chapter, index) => {
    const isCompleted = completedChapters.has(chapter.id);
    const isLocked = tier === 'FREE' && index >= 3;
    const matchesSearch = searchQuery === '' ||
      chapter.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chapter.description?.toLowerCase().includes(searchQuery.toLowerCase());

    // Apply filter and search
    switch (filter) {
      case 'completed':
        return isCompleted && matchesSearch;
      case 'in-progress':
        return !isCompleted && !isLocked && matchesSearch;
      case 'locked':
        return isLocked && matchesSearch;
      default:
        return matchesSearch;
    }
  }) || [];

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner', icon: Sprout },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate', icon: Rocket },
      advanced: { variant: 'advanced' as const, label: 'Advanced', icon: Trophy },
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

      {/* Search Bar and Filters - Same Row */}
      <div className="mb-6 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        {/* Search Bar */}
        <div className="relative w-full md:w-[845px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
          <input
            type="text"
            placeholder="Search chapters..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-bg-elevated border border-border-default rounded-xl text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-cosmic-primary focus:border-transparent transition-all"
          />
        </div>

        {/* Filter Tabs */}
        <Tabs value={filter} onValueChange={(value) => setFilter(value as FilterType)} className="flex-shrink-0">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="in-progress">In Progress</TabsTrigger>
            <TabsTrigger value="locked">Locked</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

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

      {/* Chapters Grid */}
      {filteredChapters.length === 0 ? (
        <EmptyStates.NoChapters
          title={`No ${filter === 'all' ? '' : filter.replace('-', ' ')} chapters`}
          description={
            filter === 'completed'
              ? "You haven't completed any chapters yet. Start learning!"
              : filter === 'in-progress'
              ? "All chapters are either completed or locked."
              : filter === 'locked'
              ? tier === 'FREE'
              ? 'Upgrade to PRO to unlock more chapters!'
              : 'No locked chapters. Enjoy full access!'
              : 'Check back later for new course content.'
          }
          actionLabel={filter === 'completed' ? 'Browse Chapters' : undefined}
          actionHref={filter === 'completed' ? '/chapters' : undefined}
        />
      ) : (
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
                        <Badge variant="success" className="gap-1">
                          <Check className="w-3 h-3" />
                          Completed
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-xl group-hover:text-accent-primary transition-colors">
                      {chapter.title}
                    </CardTitle>
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center transform group-hover:scale-110 transition-transform">
                    {isLocked ? <Lock className="w-6 h-6 text-text-muted" /> : isCompleted ? <CheckCircle className="w-6 h-6 text-accent-success" /> : <BookOpen className="w-6 h-6 text-cosmic-primary" />}
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant={difficultyBadge.variant} className="gap-1">
                    <difficultyBadge.icon className="w-3 h-3" />
                    {difficultyBadge.label}
                  </Badge>
                  <span className="inline-flex items-center gap-1 text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded-md">
                    <Clock className="w-3 h-3" /> {chapter.estimated_time} min
                  </span>
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-3">
                  {isLocked ? (
                    <div className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-4 text-center">
                      <p className="text-sm text-accent-warning font-medium mb-1 flex items-center justify-center gap-2">
                        <Lock className="w-4 h-4" />
                        Premium Content
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
                          className="w-full gap-2"
                        >
                          {isCompleted ? <><BookOpen className="w-4 h-4" /> Review Chapter</> : <><Play className="w-4 h-4" /> Start Chapter</>}
                        </Button>
                      </Link>

                      {chapter.quiz_id && (
                        <Link href={`/quizzes/${chapter.quiz_id}`}>
                          <Button
                            variant="secondary"
                            className="w-full gap-2"
                          >
                            <Target className="w-4 h-4" />
                            Take Quiz →
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
      )}

      {/* Motivational footer */}
      {chapters && completedChapters.size < chapters.length ? (
        <div className="text-center py-8 mt-8 border-t border-border-default">
          <p className="text-text-secondary text-sm flex items-center justify-center gap-2">
            Keep learning! You're making great progress. <Star className="w-4 h-4 text-accent-warning fill-accent-warning" />
          </p>
        </div>
      ) : chapters && completedChapters.size === chapters.length ? (
        <div className="text-center py-8 mt-8 border-t border-border-default">
          <p className="text-accent-success font-semibold flex items-center justify-center gap-2">
            <Trophy className="w-5 h-5" />
            Congratulations! You've completed the course!
          </p>
        </div>
      ) : null}
    </PageContainer>
  );
}

'use client';

/**
 * Chapters listing page - Professional/Modern SaaS theme.
 * Grid layout similar to quizzes page with filtering.
 * Premium features: Unlock mechanism, detailed analytics, upgrade prompts
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { EmptyStates } from '@/components/ui/EmptyState';
import { DifficultyBadge } from '@/components/ui/DifficultyBadge';
import { useChapters, useProgress, useUserTier } from '@/hooks';
import Link from 'next/link';
import * as React from 'react';
import { FileEdit, Rocket, BookOpen, BarChart3, Flame, Lock, CheckCircle, Play, Target, Clock, Check, Trophy, Search, AlertCircle, Star, Zap, Crown, Lightbulb, TrendingUp, Award } from 'lucide-react';

type FilterType = 'all' | 'completed' | 'in-progress' | 'locked';

// Chapter access limits by tier
const CHAPTER_ACCESS_LIMITS = {
  FREE: 3,        // Free users get first 3 chapters
  PREMIUM: 10,    // Premium users get first 10 chapters
  PRO: Infinity    // Pro users get all chapters
};

// Get current user ID from localStorage
const getCurrentUserId = (): string | undefined => {
  if (typeof window === 'undefined') return undefined;
  return localStorage.getItem('user_id') || undefined;
};

// Helper to get difficulty badge configuration
const getDifficultyBadge = (level: string) => {
  const badges = {
    beginner: {
      variant: 'beginner' as const,
      label: 'Beginner',
      color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-emerald-500/10',
      icon: <Target className="w-3.5 h-3.5" />
    },
    intermediate: {
      variant: 'intermediate' as const,
      label: 'Intermediate',
      color: 'bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-amber-500/10',
      icon: <Flame className="w-3.5 h-3.5" />
    },
    advanced: {
      variant: 'advanced' as const,
      label: 'Advanced',
      color: 'bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-rose-500/10',
      icon: <Zap className="w-3.5 h-3.5" />
    },
  };
  return badges[level as keyof typeof badges] || badges.beginner;
};

export default function ChaptersPage() {
  const { data: chapters, isLoading: chaptersLoading } = useChapters();
  const { data: progress } = useProgress();
  const { data: tier } = useUserTier();
  const [filter, setFilter] = React.useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = React.useState('');

  // Get access limit (number of chapters available) for current user tier
  const getAccessLimit = React.useCallback((): number => {
    const tierValue = tier || 'FREE';
    return CHAPTER_ACCESS_LIMITS[tierValue as keyof typeof CHAPTER_ACCESS_LIMITS] || 3;
  }, [tier]);

  const completedChapters = new Set(progress?.completed_chapters || []);

  // Calculate completion percentage
  const completionPercent = chapters ? Math.round((completedChapters.size / chapters.length) * 100) : 0;

  // Filter chapters
  const filteredChapters = React.useMemo(() => {
    if (!chapters) return [];

    return chapters.filter((chapter, index) => {
      const isCompleted = completedChapters.has(chapter.id);
      const accessLimit = getAccessLimit();
      const isLocked = (tier === 'FREE' || !tier) && index >= accessLimit;
      const matchesSearch = searchQuery === '' ||
        chapter.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        chapter.description?.toLowerCase().includes(searchQuery.toLowerCase());

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
    });
  }, [chapters, tier, filter, searchQuery, completedChapters, getAccessLimit]);

  // Calculate chapter stats
  const totalChapters = chapters?.length || 0;
  const completedCount = completedChapters.size || 0;
  const inProgressCount = React.useMemo(() => {
    return chapters?.filter((ch, index) => {
      const isCompleted = completedChapters.has(ch.id);
      const accessLimit = getAccessLimit();
      const isLocked = (tier === 'FREE' || !tier) && index >= accessLimit;
      return !isCompleted && !isLocked;
    }).length || 0;
  }, [chapters, completedChapters, getAccessLimit]);

  if (chaptersLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

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

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Course Chapters"
        description="Master AI Agent Development step by step"
      />

      {/* Premium Banner for FREE users */}
      {tier === 'FREE' && (
        <Card className="mb-6 bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 border-accent-primary/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                  <Crown className="w-5 h-5 text-accent-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">Upgrade to Premium</h3>
                  <p className="text-sm text-text-secondary">Unlock full course access, advanced chapters, and more</p>
                </div>
              </div>
              <Link href="/profile">
                <Button variant="primary" size="sm">Upgrade Now</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search Bar and Filters */}
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

      {/* Progress Overview with Premium Analytics */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-text-secondary">Course Progress</span>
            <span className="text-sm font-bold text-text-primary">
              {completedCount}/{totalChapters} Completed
            </span>
          </div>
          <Progress value={completionPercent} size="md" className="mb-2" />
          <p className="text-xs text-text-muted mb-4">{completionPercent}% of course completed</p>

          {/* Premium Analytics: Progress Stats */}
          {(tier === 'PREMIUM' || tier === 'PRO') && (
            <div className="border-t border-border-default pt-4 mt-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-accent-primary">{completionPercent}%</p>
                  <p className="text-xs text-text-muted">Completion</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-accent-success">{completedCount}</p>
                  <p className="text-xs text-text-muted">Completed</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-accent-warning">{inProgressCount}</p>
                  <p className="text-xs text-text-muted">In Progress</p>
                </div>
              </div>
            </div>
          )}

          {/* Free Tier: Limited Stats */}
          {tier === 'FREE' && (
            <div className="flex items-center justify-center gap-2 text-xs text-text-muted border-t border-border-default pt-3 mt-3">
              <Lock className="w-3 h-3" />
              <span>Upgrade to Premium for detailed analytics and insights</span>
            </div>
          )}
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
              ? 'Upgrade to Premium to unlock more chapters!'
              : 'No locked chapters. Enjoy full access!'
              : 'Check back later for new course content.'
          }
          actionLabel={filter === 'completed' ? 'Browse Chapters' : undefined}
          actionHref={filter === 'completed' ? '/chapters' : undefined}
          size="lg"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredChapters.map((chapter, index) => {
            const isCompleted = completedChapters.has(chapter.id);
            const accessLimit = getAccessLimit();
            const isLocked = (tier === 'FREE' || !tier) && index >= accessLimit;
            const difficultyBadge = getDifficultyBadge(chapter.difficulty_level || 'beginner');

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
                        {/* Premium Badge for completions */}
                        {(tier === 'PREMIUM' || tier === 'PRO') && isCompleted && (
                          <Badge variant="advanced" className="gap-1 bg-amber-500/10 text-amber-400 border-amber-500/20">
                            <Star className="w-3 h-3" />
                            Mastered!
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-lg group-hover:text-accent-primary transition-colors line-clamp-2">
                        {chapter.title}
                      </CardTitle>
                      <p className="text-sm text-text-muted mt-1 line-clamp-2">
                        {chapter.description}
                      </p>
                    </div>
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center transform group-hover:scale-110 transition-transform">
                      {isLocked ? <Lock className="w-6 h-6 text-text-muted" /> : isCompleted ? <Trophy className="w-6 h-6 text-accent-warning" /> : <BookOpen className="w-6 h-6 text-cosmic-primary" />}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={difficultyBadge.variant} className={`gap-1 ${difficultyBadge.color}`}>
                      {difficultyBadge.icon}
                      {difficultyBadge.label}
                    </Badge>
                    <span className="inline-flex items-center gap-1 text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded-md">
                      <Clock className="w-3 h-3" /> {chapter.estimated_time} min
                    </span>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="flex flex-col gap-3">
                    {isLocked ? (
                      <div className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-4 text-center">
                        <p className="text-sm text-accent-warning font-medium mb-1 flex items-center justify-center gap-2">
                          <Lock className="w-4 h-4" />
                          Premium Content
                        </p>
                        <p className="text-xs text-text-muted mb-3">
                          Upgrade to {tier === 'FREE' ? 'Premium' : 'Pro'} to unlock this chapter
                        </p>
                        <Link href="/profile" className="inline-block">
                          <Button
                            variant="outline"
                            size="sm"
                            className="w-full"
                          >
                            Upgrade Now
                          </Button>
                        </Link>
                      </div>
                    ) : (
                      <>
                        {/* Chapter Progress for completed chapters */}
                        {isCompleted && (
                          <div className="bg-bg-elevated/50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs text-text-muted">Status</span>
                              <span className="text-sm font-bold text-accent-success flex items-center gap-1">
                                <CheckCircle className="w-3 h-3" /> Completed
                              </span>
                            </div>
                            <Progress value={100} size="sm" />

                            {/* Premium: Completion feedback */}
                            {(tier === 'PREMIUM' || tier === 'PRO') && (
                              <div className="mt-2 pt-2 border-t border-border-default/50">
                                <p className="text-xs text-accent-success flex items-center gap-1">
                                  <Award className="w-3 h-3" /> Great job mastering this chapter!
                                </p>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Chapter Start/Review Button */}
                        <Link href={`/chapters/${chapter.id}`} className="block">
                          <Button
                            variant={isCompleted ? 'outline' : 'primary'}
                            size="sm"
                            className="w-full gap-2"
                          >
                            {isCompleted ? (
                              <>
                                <BookOpen className="w-4 h-4" /> Review Chapter
                              </>
                            ) : (
                              <>
                                <Play className="w-4 h-4" /> Start Chapter
                              </>
                            )}
                          </Button>
                        </Link>

                        {/* Quiz Link */}
                        {chapter.quiz_id && (
                          <Link href={`/quizzes/${chapter.quiz_id}`} className="block">
                            <Button
                              variant="secondary"
                              size="sm"
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

      {/* Premium Features Upsell Card */}
      {tier === 'FREE' && (
        <Card className="mt-6 bg-gradient-to-br from-accent-secondary/20 to-accent-primary/20 border-accent-secondary/30">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-secondary/30 to-accent-primary/30 flex items-center justify-center flex-shrink-0">
                <Crown className="w-6 h-6 text-accent-secondary" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-text-primary mb-2">Unlock Premium Course Features</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-accent-success" />
                    <span className="text-sm text-text-secondary">Access all chapters</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-accent-primary" />
                    <span className="text-sm text-text-secondary">Detailed analytics</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-accent-warning" />
                    <span className="text-sm text-text-secondary">Achievement badges</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 text-amber-400" />
                    <span className="text-sm text-text-secondary">Performance insights</span>
                  </div>
                </div>
                <Link href="/profile" className="inline-block">
                  <Button variant="primary" className="gap-2">
                    <Crown className="w-4 h-4" /> Upgrade to Premium
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
        <Link href="/quizzes" className="block">
          <Card className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-cosmic-primary">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center flex-shrink-0">
                  <FileEdit className="w-6 h-6 text-cosmic-primary" />
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">Take Quizzes</h4>
                  <p className="text-sm text-text-secondary">Test your knowledge</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/progress" className="block">
          <Card className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-accent-success">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-6 h-6 text-accent-success" />
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">View Progress</h4>
                  <p className="text-sm text-text-secondary">Track your learning journey</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Motivational footer */}
      {chapters && completedCount < totalChapters ? (
        <div className="text-center py-8 mt-8 border-t border-border-default">
          <p className="text-text-secondary text-sm flex items-center justify-center gap-2">
            Keep learning! You're making great progress. <Star className="w-4 h-4 text-accent-warning fill-accent-warning" />
          </p>
        </div>
      ) : chapters && completedCount === totalChapters ? (
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

'use client';

/**
 * Quizzes listing page - Professional/Modern SaaS theme.
 * Grid layout similar to chapters page with filtering.
 * Bug fixes applied: Progress tracking, quiz attempts, authentication handling
 * Premium features: Retry limits, unlock mechanism, detailed analytics, upgrade prompts
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
import { useQuizzes, useChapters, useProgress, useQuizAttempts, useUserTier } from '@/hooks';
import Link from 'next/link';
import * as React from 'react';
import { FileEdit, Rocket, BookOpen, BarChart3, Flame, Lock, CheckCircle, Play, Target, Clock, Check, Trophy, Search, AlertCircle, Star, Zap, Crown, Lightbulb } from 'lucide-react';

type FilterType = 'all' | 'completed' | 'in-progress' | 'locked';

// Quiz retry limits by tier
const QUIZ_RETRY_LIMITS = {
  FREE: 2,       // Free users can retry 2 times
  PREMIUM: 5,    // Premium users can retry 5 times
  PRO: Infinity    // Pro users have unlimited retries
};

// Quiz access limits by tier
const QUIZ_ACCESS_LIMITS = {
  FREE: 3,        // Free users get first 3 chapter quizzes
  PREMIUM: 10,    // Premium users get first 10 chapter quizzes
  PRO: Infinity    // Pro users get all quizzes
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

export default function QuizzesPage() {
  const { data: quizzes, isLoading: quizzesLoading } = useQuizzes();
  const { data: chapters, isLoading: chaptersLoading } = useChapters();
  const { data: progress } = useProgress();
  // BUG FIX #1: Pass userId to useQuizAttempts hook
  const userId = getCurrentUserId();
  const { data: quizAttempts = [], isLoading: quizAttemptsLoading, error: quizAttemptsError } = useQuizAttempts(userId);
  const { data: tier } = useUserTier();
  const [filter, setFilter] = React.useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = React.useState('');

  // BUG FIX: React hooks must be called before early returns
  // Get retry limit for current user tier
  const getRetryLimit = React.useCallback((quizId: string): number => {
    const tierValue = tier || 'FREE';
    return QUIZ_RETRY_LIMITS[tierValue as keyof typeof QUIZ_RETRY_LIMITS] || 2;
  }, [tier]);

  // Get access limit (number of quizzes available) for current user tier
  const getAccessLimit = React.useCallback((): number => {
    const tierValue = tier || 'FREE';
    return QUIZ_ACCESS_LIMITS[tierValue as keyof typeof QUIZ_ACCESS_LIMITS] || 3;
  }, [tier]);

  // Calculate number of attempts for a specific quiz
  const getQuizAttemptCount = React.useCallback((quizId: string): number => {
    if (!quizAttempts) return 0;
    return quizAttempts.filter((a: any) => String(a.quiz_id) === String(quizId)).length;
  }, [quizAttempts]);

  // Check if user has reached retry limit for a quiz
  const hasReachedRetryLimit = React.useCallback((quizId: string): boolean => {
    const attemptCount = getQuizAttemptCount(quizId);
    const retryLimit = getRetryLimit(quizId);
    // Allow at least one attempt (initial + retries)
    return attemptCount > retryLimit;
  }, [getRetryLimit, getQuizAttemptCount]);

  // Get attempts remaining for a quiz
  const getAttemptsRemaining = React.useCallback((quizId: string): number => {
    const attemptCount = getQuizAttemptCount(quizId);
    const retryLimit = getRetryLimit(quizId);
    return Math.max(0, retryLimit - attemptCount + 1);
  }, [getRetryLimit, getQuizAttemptCount]);

  // Calculate average score across all attempts (must be before early returns)
  const averageScore = React.useMemo(() => {
    if (!quizAttempts || quizAttempts.length === 0) return 0;
    const totalScore = quizAttempts.reduce((sum: number, a: any) => sum + (a.score || 0), 0);
    return Math.round(totalScore / quizAttempts.length);
  }, [quizAttempts]);

  // Get best score for each quiz (score >= 70 is considered completed)
  const getQuizScore = React.useCallback((quizId: string): number | null => {
    if (!quizAttempts || quizAttempts.length === 0) return null;
    const attempt = quizAttempts.find((a: any) => String(a.quiz_id) === String(quizId));
    return attempt?.score ?? null;
  }, [quizAttempts]);

  // Check if quiz is completed (attempt exists with score >= 70)
  const isQuizCompleted = React.useCallback((quizId: string): boolean => {
    if (!quizAttempts || quizAttempts.length === 0) return false;
    const attempt = quizAttempts.find((a: any) => String(a.quiz_id) === String(quizId));
    return attempt?.score !== undefined && attempt.score >= 70;
  }, [quizAttempts]);


  // Filter quizzes
  const filteredQuizzes = React.useMemo(() => {
    if (!quizzes) return [];

    return quizzes.filter((quiz) => {
      const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
      const chapterIndex = chapter ? chapters.indexOf(chapter) : -1;
      const isCompleted = isQuizCompleted(quiz.id);
      // BUG FIX #5: Handle undefined tier and check access limit
      const accessLimit = getAccessLimit();
      const isLocked = (tier === 'FREE' || !tier) && chapterIndex >= accessLimit;
      const matchesSearch = searchQuery === '' ||
        quiz.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        chapter?.title.toLowerCase().includes(searchQuery.toLowerCase());

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
  }, [quizzes, chapters, tier, filter, searchQuery, isQuizCompleted, getAccessLimit]);

  // Calculate quiz stats (completed = quiz_taken with score >= 70)
  const totalQuizzes = quizzes?.length || 0;
  const completedCount = React.useMemo(() => {
    return quizzes?.filter((quiz) => isQuizCompleted(quiz.id)).length || 0;
  }, [quizzes, isQuizCompleted]);
  const completionPercent = totalQuizzes > 0 ? Math.round((completedCount / totalQuizzes) * 100) : 0;

  if (quizzesLoading || chaptersLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  if (!quizzes || quizzes.length === 0) {
    return (
      <PageContainer>
        <PageHeader
          title="Quizzes"
          description="Test your knowledge with interactive assessments"
        />
        <EmptyStates.NoQuizzes
          title="No quizzes available yet"
          description="Quizzes will be added as you complete chapters."
          size="lg"
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Quizzes"
        description="Test your knowledge with interactive assessments"
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
                  <p className="text-sm text-text-secondary">Unlock unlimited quiz retries, detailed analytics, and more</p>
                </div>
              </div>
              <Link href="/profile">
                <Button variant="primary" size="sm">Upgrade Now</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* BUG FIX #2: Error handling for quiz attempts */}
      {quizAttemptsError && (
        <Card variant="warning" className="mb-6">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-accent-warning" />
              <p className="text-sm text-accent-warning">
                Unable to load quiz progress. Please refresh the page or log in to track your progress.
              </p>
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
            placeholder="Search quizzes..."
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
            <span className="text-sm font-medium text-text-secondary">Quiz Progress</span>
            <span className="text-sm font-bold text-text-primary">
              {completedCount}/{totalQuizzes} Completed
            </span>
          </div>
          <Progress value={completionPercent} size="md" className="mb-2" />
          <p className="text-xs text-text-muted mb-4">{completionPercent}% of quizzes completed</p>

          {/* Premium Analytics: Average Score */}
          {(tier === 'PREMIUM' || tier === 'PRO') && quizAttempts.length > 0 && (
            <div className="border-t border-border-default pt-4 mt-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-accent-primary">{averageScore}%</p>
                  <p className="text-xs text-text-muted">Average Score</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-accent-success">{completedCount}</p>
                  <p className="text-xs text-text-muted">Quizzes Passed</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-accent-warning">{getAccessLimit() - totalQuizzes}</p>
                  <p className="text-xs text-text-muted">Remaining</p>
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

      {/* Quizzes Grid */}
      {filteredQuizzes.length === 0 ? (
        <EmptyStates.NoQuizzes
          title={`No ${filter === 'all' ? '' : filter.replace('-', ' ')} quizzes`}
          description="No matching quizzes found."
          size="lg"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredQuizzes.map((quiz) => {
            const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
            const chapterIndex = chapter ? chapters.indexOf(chapter) : -1;
            const accessLimit = getAccessLimit();
            const isLocked = (tier === 'FREE' || !tier) && chapterIndex >= accessLimit;
            const isCompleted = isQuizCompleted(quiz.id);
            const bestScore = getQuizScore(quiz.id);
            const difficultyBadge = getDifficultyBadge(quiz.difficulty);
            const attemptCount = getQuizAttemptCount(quiz.id);
            const attemptsRemaining = getAttemptsRemaining(quiz.id);
            const hasReachedLimit = hasReachedRetryLimit(quiz.id);
            const difficultyLevel = quiz.difficulty || 'beginner';

            return (
              <Card
                key={quiz.id}
                variant={isQuizCompleted(quiz.id) ? 'elevated' : 'default'}
                className="group transition-all duration-300 hover:shadow-lg"
              >
                <CardHeader>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-bold text-text-secondary bg-bg-elevated px-2 py-1 rounded-md">
                          #{chapterIndex + 1}
                        </span>
                        {isQuizCompleted(quiz.id) && (
                          <Badge variant="success" className="gap-1">
                            <Check className="w-3 h-3" />
                            Completed
                          </Badge>
                        )}
                        {/* Premium Badge for high scorers */}
                        {(tier === 'PREMIUM' || tier === 'PRO') && bestScore !== null && bestScore >= 90 && (
                          <Badge variant="advanced" className="gap-1 bg-amber-500/10 text-amber-400 border-amber-500/20">
                            <Star className="w-3 h-3" />
                            Excellent!
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-lg group-hover:text-accent-primary transition-colors line-clamp-2">
                        {quiz.title}
                      </CardTitle>
                      {chapter && (
                        <p className="text-sm text-text-muted mt-1 line-clamp-1">
                          {chapter.title}
                        </p>
                      )}
                    </div>
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center transform group-hover:scale-110 transition-transform">
                      {isLocked ? <Lock className="w-6 h-6 text-text-muted" /> : isQuizCompleted(quiz.id) ? <Trophy className="w-6 h-6 text-accent-warning" /> : <FileEdit className="w-6 h-6 text-cosmic-primary" />}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={difficultyBadge.variant} className={`gap-1 ${difficultyBadge.color}`}>
                      <difficultyBadge.icon className="w-3 h-3" />
                      {difficultyBadge.label}
                    </Badge>
                    <span className="inline-flex items-center gap-1 text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded-md">
                      <Search className="w-3 h-3" /> {quiz.questions?.length || 0} questions
                    </span>
                    <span className="inline-flex items-center gap-1 text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded-md">
                      <Clock className="w-3 h-3" /> {chapter?.estimated_time || 15} min
                    </span>
                    {/* Premium: Attempt Counter */}
                    {(tier === 'PREMIUM' || tier === 'PRO') && attemptCount > 0 && (
                      <span className="inline-flex items-center gap-1 text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded-md">
                        <Target className="w-3 h-3" /> {attemptCount} attempt{attemptCount !== 1 ? 's' : ''}
                      </span>
                    )}
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
                          Upgrade to {tier === 'FREE' ? 'Premium' : 'Pro'} to unlock this quiz
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
                        {/* Previous Score Display */}
                        {bestScore !== null && (
                          <div className="bg-bg-elevated/50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs text-text-muted">Best Score</span>
                              <span className={`text-sm font-bold ${bestScore >= 70 ? 'text-accent-success' : 'text-accent-warning'}`}>
                                {bestScore}%
                              </span>
                            </div>
                            <Progress value={bestScore} size="sm" />

                            {/* Premium: Score feedback */}
                            {(tier === 'PREMIUM' || tier === 'PRO') && (
                              <div className="mt-2 pt-2 border-t border-border-default/50">
                                {bestScore >= 90 ? (
                                  <p className="text-xs text-accent-success flex items-center gap-1">
                                    <Star className="w-3 h-3" /> Excellent work!
                                  </p>
                                ) : bestScore >= 70 ? (
                                  <p className="text-xs text-accent-success flex items-center gap-1">
                                    <Check className="w-3 h-3" /> Well done!
                                  </p>
                                ) : (
                                  <p className="text-xs text-accent-warning flex items-center gap-1">
                                    <Target className="w-3 h-3" /> Keep practicing!
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Retry Limit Warning for Free Users */}
                        {tier === 'FREE' && hasReachedLimit && !isCompleted && (
                          <div className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-3 text-center">
                            <p className="text-sm text-accent-warning font-medium mb-1 flex items-center justify-center gap-2">
                              <AlertCircle className="w-4 h-4" />
                              Retry Limit Reached
                            </p>
                            <p className="text-xs text-text-muted mb-3">
                              You've used all {QUIZ_RETRY_LIMITS.FREE} attempts for this quiz. Upgrade to Premium for unlimited retries.
                            </p>
                            <Link href="/profile" className="inline-block">
                              <Button variant="outline" size="sm" className="w-full">
                                Upgrade for Unlimited Retries
                              </Button>
                            </Link>
                          </div>
                        )}

                        {/* Premium: Attempts Remaining */}
                        {(tier === 'PREMIUM' || tier === 'PRO') && attemptCount > 0 && attemptsRemaining < 5 && (
                          <div className="bg-accent-primary/10 border border-accent-primary/30 rounded-lg p-3">
                            <p className="text-xs text-text-primary">
                              {attemptsRemaining} attempts remaining out of {getRetryLimit(quiz.id)} total
                            </p>
                          </div>
                        )}

                        {/* Quiz Start/Retake Button */}
                        <Link href={`/quizzes/${quiz.id}`} className="block">
                          <Button
                            variant={isQuizCompleted(quiz.id) ? 'outline' : 'primary'}
                            size="sm"
                            className="w-full gap-2"
                            disabled={tier === 'FREE' && hasReachedLimit && !isCompleted}
                          >
                            {isQuizCompleted(quiz.id) ? (
                              <>
                                <Trophy className="w-4 h-4" /> Retake Quiz
                                {(tier === 'PREMIUM' || tier === 'PRO') && attemptsRemaining > 0 && (
                                  <span className="text-xs text-text-muted">({attemptsRemaining} left)</span>
                                )}
                              </>
                            ) : (
                              <>
                                <Play className="w-4 h-4" /> Start Quiz
                                {tier === 'FREE' && attemptsRemaining < QUIZ_RETRY_LIMITS.FREE && (
                                  <span className="text-xs text-text-muted">({attemptsRemaining} attempts left)</span>
                                )}
                              </>
                            )}
                          </Button>
                        </Link>
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
                <h3 className="font-bold text-text-primary mb-2">Unlock Premium Quiz Features</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-accent-success" />
                    <span className="text-sm text-text-secondary">Unlimited quiz retries</span>
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
        <Link href="/chapters" className="block">
          <Card className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-cosmic-primary">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-6 h-6 text-cosmic-primary" />
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">Browse Chapters</h4>
                  <p className="text-sm text-text-secondary">Review content before quizzes</p>
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
    </PageContainer>
  );
}

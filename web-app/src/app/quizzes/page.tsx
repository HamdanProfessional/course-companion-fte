'use client';

/**
 * Quizzes listing page - Professional/Modern SaaS theme.
 * Grid layout similar to chapters page with filtering.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { EmptyStates } from '@/components/ui/EmptyState';
import { useQuizzes, useChapters, useProgress, useUserTier } from '@/hooks';
import Link from 'next/link';
import * as React from 'react';
import { FileEdit, Sprout, Rocket, BookOpen, BarChart3, Flame, Lock, CheckCircle, Play, Target, Clock, Check, Trophy, Search, TrendingUp } from 'lucide-react';

type FilterType = 'all' | 'completed' | 'in-progress' | 'locked';

export default function QuizzesPage() {
  const { data: quizzes, isLoading: quizzesLoading } = useQuizzes();
  const { data: chapters, isLoading: chaptersLoading } = useChapters();
  const { data: progress } = useProgress();
  const { data: tier } = useUserTier();
  const [filter, setFilter] = React.useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = React.useState('');

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

  const completedChapters = new Set(progress?.completed_chapters || []);
  const completedQuizzes = new Set(progress?.completed_quizzes || []);

  // Get best score for each quiz
  const getQuizScore = (quizId: string) => {
    const attempt = progress?.quiz_attempts?.find((a: any) => a.quiz_id === quizId);
    return attempt?.best_score || null;
  };

  // Filter quizzes
  const filteredQuizzes = quizzes?.filter((quiz) => {
    const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
    const isCompleted = completedQuizzes.has(quiz.id);
    const isLocked = tier === 'FREE' && chapter && chapters.indexOf(chapter) >= 3;
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
  }) || [];

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner', icon: Sprout, color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate', icon: TrendingUp, color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
      advanced: { variant: 'advanced' as const, label: 'Advanced', icon: Rocket, color: 'bg-rose-500/10 text-rose-400 border-rose-500/20' },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  // Calculate quiz stats
  const totalQuizzes = quizzes?.length || 0;
  const completedCount = completedQuizzes.size;
  const completionPercent = totalQuizzes > 0 ? Math.round((completedCount / totalQuizzes) * 100) : 0;

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Quizzes"
        description="Test your knowledge with interactive assessments"
      />

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

      {/* Progress Overview */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-text-secondary">Quiz Progress</span>
            <span className="text-sm font-bold text-text-primary">
              {completedCount}/{totalQuizzes} Completed
            </span>
          </div>
          <Progress value={completionPercent} size="md" className="mb-2" />
          <p className="text-xs text-text-muted">{completionPercent}% of quizzes completed</p>
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
            const isLocked = tier === 'FREE' && chapterIndex >= 3;
            const isCompleted = completedQuizzes.has(quiz.id);
            const bestScore = getQuizScore(quiz.id);
            const difficultyBadge = getDifficultyBadge(quiz.difficulty);

            return (
              <Card
                key={quiz.id}
                variant={isCompleted ? 'elevated' : 'default'}
                className="group transition-all duration-300 hover:shadow-lg"
              >
                <CardHeader>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-bold text-text-secondary bg-bg-elevated px-2 py-1 rounded-md">
                          #{chapterIndex + 1}
                        </span>
                        {isCompleted && (
                          <Badge variant="success" className="gap-1">
                            <Check className="w-3 h-3" />
                            Completed
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
                      {isLocked ? <Lock className="w-6 h-6 text-text-muted" /> : isCompleted ? <Trophy className="w-6 h-6 text-accent-warning" /> : <FileEdit className="w-6 h-6 text-cosmic-primary" />}
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
                        <p className="text-xs text-text-muted mb-3">
                          Upgrade to PRO to unlock this quiz
                        </p>
                        <Link href="/profile" className="block">
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
                        {bestScore !== null && (
                          <div className="bg-bg-elevated/50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs text-text-muted">Best Score</span>
                              <span className={`text-sm font-bold ${bestScore >= 70 ? 'text-accent-success' : 'text-accent-warning'}`}>
                                {bestScore}%
                              </span>
                            </div>
                            <Progress value={bestScore} size="sm" />
                          </div>
                        )}
                        <Link href={`/quizzes/${quiz.id}`} className="block">
                          <Button
                            variant={isCompleted ? 'outline' : 'primary'}
                            className="w-full gap-2"
                          >
                            {isCompleted ? <><Trophy className="w-4 h-4" /> Retake Quiz</> : <><Play className="w-4 h-4" /> Start Quiz</>}
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

'use client';

/**
 * Quizzes listing page - Professional/Modern SaaS theme.
 * Shows all available quizzes with filtering and completion status.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { QuizCard } from '@/components/ui/QuizCard';
import { EmptyStates } from '@/components/ui/EmptyState';
import { useQuizzes, useChapters, useProgress } from '@/hooks';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { FileEdit, Sprout, Rocket, BookOpen, BarChart3, TrendingUp, Flame } from 'lucide-react';

export default function QuizzesPage() {
  const { data: quizzes, isLoading: quizzesLoading } = useQuizzes();
  const { data: chapters, isLoading: chaptersLoading } = useChapters();
  const { data: progress } = useProgress();

  if (quizzesLoading || chaptersLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  // Handle case when quizzes array is empty or null
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

  // Group quizzes by difficulty
  const beginnerQuizzes = quizzes?.filter((q) => q.difficulty === 'beginner') || [];
  const intermediateQuizzes = quizzes?.filter((q) => q.difficulty === 'intermediate') || [];
  const advancedQuizzes = quizzes?.filter((q) => q.difficulty === 'advanced') || [];

  // Get completion data
  const completedChapters = new Set(progress?.completed_chapters || []);

  const allQuizCards = quizzes?.map((quiz) => {
    const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
    const isChapterCompleted = completedChapters.has(quiz.chapter_id);
    return (
      <QuizCard
        key={quiz.id}
        id={quiz.id}
        title={quiz.title}
        difficulty={quiz.difficulty}
        chapterId={quiz.chapter_id}
        chapterTitle={chapter?.title}
        questionCount={quiz.questions?.length}
      />
    );
  }) || [];

  return (
    <PageContainer>
      <PageHeader
        title="Quizzes"
        description="Test your knowledge with interactive assessments"
      />

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Total Quizzes</p>
                <p className="text-3xl font-bold text-accent-primary mt-1">
                  {quizzes?.length || 0}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center">
                <FileEdit className="w-6 h-6 text-accent-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Beginner</p>
                <p className="text-3xl font-bold text-accent-success mt-1">
                  {beginnerQuizzes.length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                <Sprout className="w-6 h-6 text-accent-success" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Intermediate</p>
                <p className="text-3xl font-bold text-accent-info mt-1">
                  {intermediateQuizzes.length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-accent-info" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Advanced</p>
                <p className="text-3xl font-bold text-accent-warning mt-1">
                  {advancedQuizzes.length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                <Rocket className="w-6 h-6 text-accent-warning" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quizzes by Difficulty */}
      <Tabs defaultValue="all" className="space-y-6">
        <TabsList>
          <TabsTrigger value="all">All Quizzes</TabsTrigger>
          <TabsTrigger value="beginner">Beginner</TabsTrigger>
          <TabsTrigger value="intermediate">Intermediate</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-3">
          {allQuizCards.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center">
                  <FileEdit className="w-8 h-8 text-accent-primary" />
                </div>
                <p className="text-text-secondary">No quizzes available yet.</p>
              </CardContent>
            </Card>
          ) : (
            allQuizCards
          )}
        </TabsContent>

        <TabsContent value="beginner" className="space-y-3">
          {beginnerQuizzes.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                  <Sprout className="w-8 h-8 text-accent-success" />
                </div>
                <p className="text-text-secondary">No beginner quizzes yet.</p>
              </CardContent>
            </Card>
          ) : (
            beginnerQuizzes.map((quiz) => {
              const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
              return (
                <QuizCard
                  key={quiz.id}
                  id={quiz.id}
                  title={quiz.title}
                  difficulty={quiz.difficulty}
                  chapterId={quiz.chapter_id}
                  chapterTitle={chapter?.title}
                  questionCount={quiz.questions?.length}
                />
              );
            })
          )}
        </TabsContent>

        <TabsContent value="intermediate" className="space-y-3">
          {intermediateQuizzes.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
                  <TrendingUp className="w-8 h-8 text-accent-info" />
                </div>
                <p className="text-text-secondary">No intermediate quizzes yet.</p>
              </CardContent>
            </Card>
          ) : (
            intermediateQuizzes.map((quiz) => {
              const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
              return (
                <QuizCard
                  key={quiz.id}
                  id={quiz.id}
                  title={quiz.title}
                  difficulty={quiz.difficulty}
                  chapterId={quiz.chapter_id}
                  chapterTitle={chapter?.title}
                  questionCount={quiz.questions?.length}
                />
              );
            })
          )}
        </TabsContent>

        <TabsContent value="advanced" className="space-y-3">
          {advancedQuizzes.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                  <Rocket className="w-8 h-8 text-accent-warning" />
                </div>
                <p className="text-text-secondary">No advanced quizzes yet.</p>
              </CardContent>
            </Card>
          ) : (
            advancedQuizzes.map((quiz) => {
              const chapter = chapters?.find((ch) => ch.id === quiz.chapter_id);
              return (
                <QuizCard
                  key={quiz.id}
                  id={quiz.id}
                  title={quiz.title}
                  difficulty={quiz.difficulty}
                  chapterId={quiz.chapter_id}
                  chapterTitle={chapter?.title}
                  questionCount={quiz.questions?.length}
                />
              );
            })
          )}
        </TabsContent>
      </Tabs>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
        <a href="/dashboard" className="block">
          <Card className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-accent-primary">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-6 h-6 text-accent-primary" />
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">Browse Chapters</h4>
                  <p className="text-sm text-text-secondary">Review content before quizzes</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </a>

        <a href="/progress" className="block">
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
        </a>
      </div>
    </PageContainer>
  );
}

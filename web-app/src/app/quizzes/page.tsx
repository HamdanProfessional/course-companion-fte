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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Total Quizzes</p>
                <p className="text-3xl font-bold text-accent-primary mt-1">
                  {quizzes?.length || 0}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-bg-elevated flex items-center justify-center text-2xl">
                📝
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
              <div className="w-12 h-12 rounded-xl bg-bg-elevated flex items-center justify-center text-2xl">
                🌱
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
                  {intermediateQuizzes.length + advancedQuizzes.length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-bg-elevated flex items-center justify-center text-2xl">
                🚀
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
                <div className="text-4xl mb-3">📝</div>
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
                <div className="text-4xl mb-3">🌱</div>
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
                <div className="text-4xl mb-3">📈</div>
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
                <div className="text-4xl mb-3">🚀</div>
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
                <div className="text-3xl">📚</div>
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
                <div className="text-3xl">📊</div>
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

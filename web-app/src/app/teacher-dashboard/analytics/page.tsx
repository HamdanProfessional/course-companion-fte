'use client';

/**
 * Teacher Analytics Page
 *
 * Features:
 * - Quiz performance metrics
 * - Class-wide statistics
 * - Individual question analysis
 * - Performance trends
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useTeacherQuizAnalytics, type QuizPerformance, type QuestionAnalysis } from '@/hooks';
import Link from 'next/link';

export default function TeacherAnalyticsPage() {
  const router = useRouter();

  const {
    quizStats,
    quizPerformance = [],
    questionAnalysis = [],
    isLoading,
    error,
    refetch,
  } = useTeacherQuizAnalytics();

  useEffect(() => {
    const role = localStorage.getItem('user_role');
    if (role !== 'teacher') {
      router.push('/dashboard');
    }
  }, [router]);

  // Helper to get difficulty badge variant
  const getDifficultyVariant = (difficulty: string): 'beginner' | 'intermediate' | 'success' | 'premium' | 'danger' | 'warning' | 'info' => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
      case 'easy':
        return 'beginner';
      case 'intermediate':
      case 'medium':
        return 'intermediate';
      case 'advanced':
      case 'hard':
        return 'danger';
      default:
        return 'beginner';
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <PageContainer>
        <div className="text-center py-12">
          <p className="text-accent-danger mb-4">Failed to load quiz analytics</p>
          <Button variant="primary" onClick={() => refetch()}>
            Try Again
          </Button>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Quiz Analytics"
        description="Detailed quiz performance and insights"
      />

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Total Attempts</p>
            <h3 className="text-3xl font-bold text-accent-primary">
              {quizStats?.total_attempts ?? 0}
            </h3>
            <p className="text-xs text-text-muted mt-2">All quizzes combined</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Average Score</p>
            <h3 className="text-3xl font-bold text-accent-success">
              {quizStats?.average_score ?? 0}%
            </h3>
            <p className="text-xs text-accent-success mt-2">Class performance</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Pass Rate</p>
            <h3 className="text-3xl font-bold text-accent-info">
              {quizStats?.pass_rate ?? 0}%
            </h3>
            <p className="text-xs text-text-muted mt-2">Scored ≥60%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Completion Rate</p>
            <h3 className="text-3xl font-bold text-accent-warning">
              {quizStats?.completion_rate ?? 0}%
            </h3>
            <p className="text-xs text-text-muted mt-2">Students who attempted</p>
          </CardContent>
        </Card>
      </div>

      {/* Quiz Performance Breakdown */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <span className="text-2xl">📊</span>
            Quiz Performance Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          {quizPerformance.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-text-muted">No quiz performance data yet. Quizzes will appear here once students attempt them.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border-default">
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Quiz</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Attempts</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Avg Score</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Pass Rate</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Range</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {quizPerformance.map((quiz) => (
                    <tr key={quiz.quiz_id} className="border-b border-border-subtle hover:bg-bg-elevated">
                      <td className="p-4">
                        <p className="font-medium text-text-primary">{quiz.quiz_title}</p>
                        <p className="text-sm text-text-muted">ID: {quiz.quiz_id.slice(0, 8)}...</p>
                      </td>
                      <td className="p-4">
                        <span className="text-text-primary">{quiz.total_attempts}</span>
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={
                            quiz.average_score >= 80
                              ? 'success'
                              : quiz.average_score >= 70
                              ? 'intermediate'
                              : 'beginner'
                          }
                        >
                          {quiz.average_score}%
                        </Badge>
                      </td>
                      <td className="p-4">
                        <Badge variant={quiz.pass_rate >= 85 ? 'success' : 'intermediate'}>
                          {quiz.pass_rate}%
                        </Badge>
                      </td>
                      <td className="p-4">
                        <span className="text-sm text-text-muted">
                          {quiz.lowest_score}% - {quiz.highest_score}%
                        </span>
                      </td>
                      <td className="p-4">
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Question Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="text-2xl">📝</span>
              Question Analysis
            </CardTitle>
            <p className="text-sm text-text-muted">
              Most challenging questions identified
            </p>
          </CardHeader>
          <CardContent>
            {questionAnalysis.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-text-muted">No question data yet. Analysis will appear once students attempt quizzes.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {questionAnalysis.map((q) => (
                  <div key={q.question_id} className="p-4 rounded-lg bg-bg-elevated border border-border-subtle">
                    <div className="flex items-start justify-between mb-2">
                      <p className="text-sm font-medium text-text-primary flex-1 pr-4">
                        {q.question_text}
                      </p>
                      <Badge
                        variant={
                          q.correct_rate >= 75
                            ? 'success'
                            : q.correct_rate >= 60
                            ? 'intermediate'
                            : 'beginner'
                        }
                      >
                        {q.correct_rate}% correct
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-text-muted">
                      <span>⏱️ {q.average_time}s avg time</span>
                      <span>📊 {q.total_attempts} attempts</span>
                      <Badge variant={getDifficultyVariant(q.difficulty)} className="capitalize">
                        {q.difficulty}
                      </Badge>
                    </div>
                    {q.correct_rate < 70 && (
                      <div className="mt-2 pt-2 border-t border-border-subtle">
                        <p className="text-xs text-accent-warning">
                          ⚠️ Below target - consider reviewing this topic
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Performance Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="text-2xl">📈</span>
              Performance Insights
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-accent-success/10 border border-accent-success/30">
              <div className="flex items-start gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <p className="font-medium text-text-primary mb-1">Strong Performance</p>
                  <p className="text-sm text-text-secondary">
                    {quizPerformance.length > 0
                      ? `${quizPerformance.filter((q) => q.average_score >= 80).length} of ${quizPerformance.length} quizzes show strong comprehension. Students are excelling in foundational concepts.`
                      : 'Quiz performance data will appear here once students complete quizzes.'}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-accent-warning/10 border border-accent-warning/30">
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="font-medium text-text-primary mb-1">Needs Attention</p>
                  <p className="text-sm text-text-secondary">
                    {quizPerformance.filter((q) => q.average_score < 70).length > 0
                      ? `${quizPerformance.filter((q) => q.average_score < 70).length} quiz(es) below 70%. Consider reviewing content and adding more examples.`
                      : 'No quizzes need immediate attention.'}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-accent-info/10 border border-accent-info/30">
              <div className="flex items-start gap-3">
                <span className="text-2xl">💡</span>
                <div>
                  <p className="font-medium text-text-primary mb-1">Recommendation</p>
                  <p className="text-sm text-text-secondary">
                    {questionAnalysis.filter((q) => q.correct_rate < 60).length > 0
                      ? `${questionAnalysis.filter((q) => q.correct_rate < 60).length} question(s) have below 60% correct rate. Consider adding dedicated lessons on these topics.`
                      : 'Question-level data will help identify specific knowledge gaps.'}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-accent-primary/10 border border-accent-primary/30">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🎯</span>
                <div>
                  <p className="font-medium text-text-primary mb-1">Next Steps</p>
                  <p className="text-sm text-text-secondary">
                    Review question-level analytics to identify specific knowledge gaps. Create targeted practice problems for weak areas.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-4">
            <Link href="/teacher-dashboard/content">
              <Button variant="primary">
                📝 Edit Quiz Content
              </Button>
            </Link>
            <Button variant="outline">
              📥 Export Analytics Report
            </Button>
            <Button variant="outline">
              📧 Email Students
            </Button>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}

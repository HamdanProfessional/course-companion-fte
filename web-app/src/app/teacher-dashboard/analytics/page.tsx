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
import Link from 'next/link';

export default function TeacherAnalyticsPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const role = localStorage.getItem('user_role');
    if (role !== 'teacher') {
      router.push('/dashboard');
      return;
    }
    setIsLoading(false);
  }, [router]);

  // Mock quiz data
  const quizStats = {
    totalAttempts: 342,
    averageScore: 78,
    passRate: 85,
    completionRate: 72,
  };

  const quizPerformance = [
    {
      id: '1',
      title: 'Introduction to AI Agents',
      chapter: 'Chapter 1',
      attempts: 89,
      avgScore: 82,
      passRate: 92,
      difficulty: 'beginner',
    },
    {
      id: '2',
      title: 'Understanding MCP',
      chapter: 'Chapter 2',
      attempts: 76,
      avgScore: 75,
      passRate: 88,
      difficulty: 'beginner',
    },
    {
      id: '3',
      title: 'Creating Your First Agent',
      chapter: 'Chapter 3',
      attempts: 65,
      avgScore: 68,
      passRate: 78,
      difficulty: 'intermediate',
    },
    {
      id: '4',
      title: 'Building Reusable Skills',
      chapter: 'Chapter 4',
      attempts: 52,
      avgScore: 71,
      passRate: 82,
      difficulty: 'intermediate',
    },
    {
      id: '5',
      title: 'Agent Architectures',
      chapter: 'Chapter 5',
      attempts: 60,
      avgScore: 79,
      passRate: 86,
      difficulty: 'intermediate',
    },
  ];

  const questionAnalysis = [
    {
      question: 'What is the primary purpose of MCP?',
      correctRate: 85,
      avgTime: 45,
      attempts: 89,
    },
    {
      question: 'Which component handles agent perception?',
      correctRate: 72,
      avgTime: 62,
      attempts: 89,
    },
    {
      question: 'How do you create an MCP server?',
      correctRate: 68,
      avgTime: 120,
      attempts: 76,
    },
    {
      question: 'What is agent state management?',
      correctRate: 58,
      avgTime: 95,
      attempts: 65,
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
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
            <h3 className="text-3xl font-bold text-accent-primary">{quizStats.totalAttempts}</h3>
            <p className="text-xs text-text-muted mt-2">All quizzes combined</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Average Score</p>
            <h3 className="text-3xl font-bold text-accent-success">{quizStats.averageScore}%</h3>
            <p className="text-xs text-accent-success mt-2">↑ 5% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Pass Rate</p>
            <h3 className="text-3xl font-bold text-accent-info">{quizStats.passRate}%</h3>
            <p className="text-xs text-text-muted mt-2">Scored ≥60%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Completion Rate</p>
            <h3 className="text-3xl font-bold text-accent-warning">{quizStats.completionRate}%</h3>
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
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-default">
                  <th className="text-left p-4 text-sm font-medium text-text-secondary">Quiz</th>
                  <th className="text-left p-4 text-sm font-medium text-text-secondary">Attempts</th>
                  <th className="text-left p-4 text-sm font-medium text-text-secondary">Avg Score</th>
                  <th className="text-left p-4 text-sm font-medium text-text-secondary">Pass Rate</th>
                  <th className="text-left p-4 text-sm font-medium text-text-secondary">Difficulty</th>
                  <th className="text-left p-4 text-sm font-medium text-text-secondary">Actions</th>
                </tr>
              </thead>
              <tbody>
                {quizPerformance.map((quiz) => (
                  <tr key={quiz.id} className="border-b border-border-subtle hover:bg-bg-elevated">
                    <td className="p-4">
                      <p className="font-medium text-text-primary">{quiz.title}</p>
                      <p className="text-sm text-text-muted">{quiz.chapter}</p>
                    </td>
                    <td className="p-4">
                      <span className="text-text-primary">{quiz.attempts}</span>
                    </td>
                    <td className="p-4">
                      <Badge
                        variant={
                          quiz.avgScore >= 80
                            ? 'success'
                            : quiz.avgScore >= 70
                            ? 'intermediate'
                            : 'beginner'
                        }
                      >
                        {quiz.avgScore}%
                      </Badge>
                    </td>
                    <td className="p-4">
                      <Badge variant={quiz.passRate >= 85 ? 'success' : 'intermediate'}>
                        {quiz.passRate}%
                      </Badge>
                    </td>
                    <td className="p-4">
                      <Badge variant={quiz.difficulty === 'beginner' ? 'beginner' : 'intermediate'}>
                        {quiz.difficulty}
                      </Badge>
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
            <div className="space-y-4">
              {questionAnalysis.map((q, index) => (
                <div key={index} className="p-4 rounded-lg bg-bg-elevated border border-border-subtle">
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm font-medium text-text-primary flex-1 pr-4">
                      {q.question}
                    </p>
                    <Badge
                      variant={
                        q.correctRate >= 75
                          ? 'success'
                          : q.correctRate >= 60
                          ? 'intermediate'
                          : 'beginner'
                      }
                    >
                      {q.correctRate}% correct
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-text-muted">
                    <span>⏱️ {q.avgTime}s avg time</span>
                    <span>📊 {q.attempts} attempts</span>
                  </div>
                  {q.correctRate < 70 && (
                    <div className="mt-2 pt-2 border-t border-border-subtle">
                      <p className="text-xs text-accent-warning">
                        ⚠️ Below target - consider reviewing this topic
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Performance Trends */}
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
                    Chapter 1 & 2 quizzes show strong comprehension. Students are excelling in foundational concepts.
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
                    Chapter 3 quiz scores dropped. Consider reviewing "Creating Your First Agent" content and adding more examples.
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
                    State management questions have the lowest correct rate (58%). Consider adding a dedicated lesson on this topic.
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

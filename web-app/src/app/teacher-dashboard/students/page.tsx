'use client';

/**
 * Teacher Student Management Page
 *
 * Features:
 * - View all students with progress
 * - Filter by performance tier
 * - Search students by name/email
 * - View individual student details
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useTeacherStudents, type TeacherStudent } from '@/hooks';
import Link from 'next/link';

type FilterType = 'all' | 'at-risk' | 'excelling' | 'average';

export default function TeacherStudentsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<FilterType>('all');

  const { data: students = [], isLoading, error, refetch } = useTeacherStudents();

  useEffect(() => {
    const role = localStorage.getItem('user_role');
    if (role !== 'teacher') {
      router.push('/dashboard');
    }
  }, [router]);

  // Helper to check if student is at-risk
  const isAtRisk = (student: TeacherStudent): boolean => {
    return student.progress < 30;
  };

  // Helper to format last activity
  const formatLastActivity = (lastActivity: string): string => {
    try {
      const date = new Date(lastActivity);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffHours / 24);

      if (diffHours < 1) return 'Just now';
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      if (diffDays === 1) return '1 day ago';
      if (diffDays < 7) return `${diffDays} days ago`;
      return `${diffDays} days ago`;
    } catch {
      return 'Unknown';
    }
  };

  // Calculate average quiz score
  const avgScore = (scores: number[] = []): number => {
    if (!scores || scores.length === 0) return 0;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  };

  // Filter and search students
  const filteredStudents = students.filter((student) => {
    const matchesSearch =
      student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.email.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter =
      filter === 'all' ||
      (filter === 'at-risk' && isAtRisk(student)) ||
      (filter === 'excelling' && student.progress >= 80) ||
      (filter === 'average' && student.progress >= 40 && student.progress < 80);

    return matchesSearch && matchesFilter;
  });

  // Calculate stats
  const totalStudents = students.length;
  const activeThisWeek = students.filter((s) => {
    const lastActivity = new Date(s.last_activity);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return lastActivity > weekAgo;
  }).length;
  const atRiskCount = students.filter((s) => isAtRisk(s)).length;
  const excellingCount = students.filter((s) => s.progress >= 80).length;

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
          <p className="text-accent-danger mb-4">Failed to load student data</p>
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
        title="Student Management"
        description="View and manage all student progress"
      />

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Total Students</p>
            <h3 className="text-3xl font-bold text-accent-primary">{totalStudents}</h3>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Active This Week</p>
            <h3 className="text-3xl font-bold text-accent-success">{activeThisWeek}</h3>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">At Risk</p>
            <h3 className="text-3xl font-bold text-accent-danger">{atRiskCount}</h3>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Excelling</p>
            <h3 className="text-3xl font-bold text-accent-success">{excellingCount}</h3>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-[250px]">
              <Input
                type="text"
                placeholder="Search by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All Students
              </Button>
              <Button
                variant={filter === 'at-risk' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('at-risk')}
              >
                At Risk
              </Button>
              <Button
                variant={filter === 'average' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('average')}
              >
                Average
              </Button>
              <Button
                variant={filter === 'excelling' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('excelling')}
              >
                Excelling
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Students List */}
      <Card>
        <CardHeader>
          <CardTitle>
            Students ({filteredStudents.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {students.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-text-muted">No students yet. Students will appear here when they enroll.</p>
            </div>
          ) : filteredStudents.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-text-muted">No students found matching your criteria</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border-default">
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Student</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Progress</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Avg Score</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Streak</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Tier</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Last Active</th>
                    <th className="text-left p-4 text-sm font-medium text-text-secondary">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((student) => (
                    <tr key={student.user_id} className="border-b border-border-subtle hover:bg-bg-elevated">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-accent-primary/10 flex items-center justify-center text-accent-primary font-semibold">
                            {student.name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-text-primary">{student.name}</p>
                            <p className="text-sm text-text-muted">{student.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-bg-elevated rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                student.progress >= 75
                                  ? 'bg-accent-success'
                                  : student.progress >= 50
                                  ? 'bg-accent-warning'
                                  : 'bg-accent-danger'
                              }`}
                              style={{ width: `${student.progress}%` }}
                            />
                          </div>
                          <span className="text-sm text-text-primary">{student.progress}%</span>
                        </div>
                        <p className="text-xs text-text-muted mt-1">
                          {student.completed_chapters ?? 0} of {student.total_chapters ?? 0} chapters
                        </p>
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={
                            avgScore(student.quiz_scores) >= 80
                              ? 'success'
                              : avgScore(student.quiz_scores) >= 60
                              ? 'intermediate'
                              : 'beginner'
                          }
                        >
                          {avgScore(student.quiz_scores)}%
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-1">
                          <span>🔥</span>
                          <span className="text-sm text-text-primary">{student.streak} days</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={
                            student.tier === 'PRO'
                              ? 'premium'
                              : student.tier === 'PREMIUM'
                              ? 'intermediate'
                              : 'beginner'
                          }
                        >
                          {student.tier}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <span className="text-sm text-text-primary">{formatLastActivity(student.last_activity)}</span>
                      </td>
                      <td className="p-4">
                        <Link href={`/teacher-dashboard/students/${student.user_id}`}>
                          <Button variant="outline" size="sm">
                            View Details
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </PageContainer>
  );
}

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
import Link from 'next/link';

type FilterType = 'all' | 'at-risk' | 'excelling' | 'average';

export default function TeacherStudentsPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<FilterType>('all');

  useEffect(() => {
    const id = localStorage.getItem('user_id');
    const role = localStorage.getItem('user_role');

    if (!id || role !== 'teacher') {
      router.push('/dashboard');
      return;
    }

    setUserId(id);
    setUserRole(role);
    setIsLoading(false);
  }, [router]);

  // Mock student data
  const allStudents = [
    {
      id: '1',
      name: 'John Smith',
      email: 'john@example.com',
      progress: 75,
      streak: 12,
      lastActivity: '2 hours ago',
      tier: 'PREMIUM',
      quizScores: [85, 90, 78, 92],
      completedChapters: 6,
      totalChapters: 8,
      joinedDate: '2024-01-15',
    },
    {
      id: '2',
      name: 'Sarah Johnson',
      email: 'sarah@example.com',
      progress: 45,
      streak: 5,
      lastActivity: '1 day ago',
      tier: 'FREE',
      quizScores: [65, 70, 55, 60],
      completedChapters: 3,
      totalChapters: 8,
      joinedDate: '2024-01-20',
    },
    {
      id: '3',
      name: 'Mike Brown',
      email: 'mike@example.com',
      progress: 90,
      streak: 20,
      lastActivity: '1 hour ago',
      tier: 'PRO',
      quizScores: [95, 98, 92, 96],
      completedChapters: 7,
      totalChapters: 8,
      joinedDate: '2024-01-10',
    },
    {
      id: '4',
      name: 'Emily Davis',
      email: 'emily@example.com',
      progress: 30,
      streak: 3,
      lastActivity: '3 days ago',
      tier: 'FREE',
      quizScores: [45, 50, 40, 48],
      completedChapters: 2,
      totalChapters: 8,
      joinedDate: '2024-01-25',
    },
    {
      id: '5',
      name: 'David Wilson',
      email: 'david@example.com',
      progress: 60,
      streak: 8,
      lastActivity: '5 hours ago',
      tier: 'PREMIUM',
      quizScores: [75, 80, 72, 78],
      completedChapters: 5,
      totalChapters: 8,
      joinedDate: '2024-01-18',
    },
    {
      id: '6',
      name: 'Lisa Anderson',
      email: 'lisa@example.com',
      progress: 25,
      streak: 1,
      lastActivity: '5 days ago',
      tier: 'FREE',
      quizScores: [40, 35, 42, 38],
      completedChapters: 2,
      totalChapters: 8,
      joinedDate: '2024-01-28',
    },
  ];

  // Filter and search students
  const filteredStudents = allStudents.filter((student) => {
    const matchesSearch =
      student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.email.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter =
      filter === 'all' ||
      (filter === 'at-risk' && student.progress < 40) ||
      (filter === 'excelling' && student.progress >= 80) ||
      (filter === 'average' && student.progress >= 40 && student.progress < 80);

    return matchesSearch && matchesFilter;
  });

  // Calculate stats
  const avgScore = (scores: number[]) => Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);

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
        title="Student Management"
        description="View and manage all student progress"
      />

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Total Students</p>
            <h3 className="text-3xl font-bold text-accent-primary">{allStudents.length}</h3>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Active This Week</p>
            <h3 className="text-3xl font-bold text-accent-success">
              {allStudents.filter((s) => s.lastActivity.includes('hour') || s.lastActivity.includes('day')).length}
            </h3>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">At Risk</p>
            <h3 className="text-3xl font-bold text-accent-danger">
              {allStudents.filter((s) => s.progress < 40).length}
            </h3>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-text-secondary mb-1">Excelling</p>
            <h3 className="text-3xl font-bold text-accent-success">
              {allStudents.filter((s) => s.progress >= 80).length}
            </h3>
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
          {filteredStudents.length === 0 ? (
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
                    <tr key={student.id} className="border-b border-border-subtle hover:bg-bg-elevated">
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
                          {student.completedChapters} of {student.totalChapters} chapters
                        </p>
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={
                            avgScore(student.quizScores) >= 80
                              ? 'success'
                              : avgScore(student.quizScores) >= 60
                              ? 'intermediate'
                              : 'beginner'
                          }
                        >
                          {avgScore(student.quizScores)}%
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
                        <span className="text-sm text-text-primary">{student.lastActivity}</span>
                      </td>
                      <td className="p-4">
                        <Link href={`/teacher-dashboard/students/${student.id}`}>
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

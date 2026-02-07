'use client';

/**
 * Teacher Content Management Page
 *
 * Features:
 * - Manage chapters
 * - Edit quizzes
 * - Upload content
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { BookOpen, RotateCcw, BarChart3, Upload, FileEdit } from 'lucide-react';
import Link from 'next/link';
import { useChapters, useQuizzes } from '@/hooks';

export default function TeacherContentPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const { data: chapters, isLoading: chaptersLoading } = useChapters();
  const { data: quizzes, isLoading: quizzesLoading } = useQuizzes();

  useEffect(() => {
    const role = localStorage.getItem('user_role');
    if (role !== 'teacher') {
      router.push('/dashboard');
      return;
    }
    setIsLoading(false);
  }, [router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Content Management"
        description="Manage course chapters and quizzes"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Chapters Management */}
        <Card className="border-l-4 border-l-accent-primary">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-cosmic-primary" />
              </div>
              Chapters
            </CardTitle>
            <p className="text-sm text-text-muted">Manage course content</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-bg-elevated">
              <div>
                <p className="font-medium text-text-primary">Total Chapters</p>
                <p className="text-sm text-text-muted">{chapters?.length || 0} published chapters</p>
              </div>
              <span className="text-2xl font-bold text-accent-primary">{chapters?.length || 0}</span>
            </div>
            <Button variant="primary" className="w-full">
              + Add New Chapter
            </Button>
            <Link href="/chapters">
              <Button variant="outline" className="w-full">
                View All Chapters →
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Quizzes Management */}
        <Card className="border-l-4 border-l-accent-secondary">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-secondary/20 to-accent-secondary/10 flex items-center justify-center">
                <FileEdit className="w-6 h-6 text-accent-secondary" />
              </div>
              Quizzes
            </CardTitle>
            <p className="text-sm text-text-muted">Manage quiz content</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-bg-elevated">
              <div>
                <p className="font-medium text-text-primary">Total Quizzes</p>
                <p className="text-sm text-text-muted">{quizzes?.length || 0} active quizzes</p>
              </div>
              <span className="text-2xl font-bold text-accent-secondary">{quizzes?.length || 0}</span>
            </div>
            <Button variant="primary" className="w-full">
              + Create New Quiz
            </Button>
            <Link href="/quizzes">
              <Button variant="outline" className="w-full">
                View All Quizzes →
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex-col">
              <Upload className="w-8 h-8 mb-2 text-cosmic-primary" />
              <span>Import Content</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <BarChart3 className="w-8 h-8 mb-2 text-cosmic-primary" />
              <span>Export Content</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <RotateCcw className="w-8 h-8 mb-2 text-cosmic-primary" />
              <span>Sync with Backend</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8 p-6 rounded-lg bg-accent-info/10 border border-accent-info/30">
        <p className="text-sm text-text-primary">
          <strong>Coming Soon:</strong> Full content editor with WYSIWYG markdown editor, quiz builder,
          and bulk import functionality.
        </p>
      </div>
    </PageContainer>
  );
}

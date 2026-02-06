'use client';

/**
 * Teacher Engagement Page
 *
 * Features:
 * - Student engagement metrics
 * - Activity tracking
 * - Communication tools
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';

export default function TeacherEngagementPage() {
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
        title="Student Engagement"
        description="Track and improve student engagement"
      />

      <div className="mt-8 p-6 rounded-lg bg-accent-info/10 border border-accent-info/30">
        <p className="text-sm text-text-primary">
          <strong>Coming Soon:</strong> Engagement analytics, activity tracking, communication tools,
          and automated nudges for at-risk students.
        </p>
      </div>
    </PageContainer>
  );
}

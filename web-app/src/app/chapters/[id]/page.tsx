/**
 * Individual chapter page with Professional/Modern SaaS theme.
 */
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer } from '@/components/layout/PageContainer';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { useChapter, useProgress, backendApi } from '@/hooks';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ChapterPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: chapter, isLoading } = useChapter(params.id);
  const { data: progress } = useProgress();

  const isCompleted = progress?.completed_chapters?.includes(params.id);

  const markCompleteMutation = useMutation({
    mutationFn: () => backendApi.updateProgress('00000000-0000-0000-0000-000000000001', params.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!chapter) {
    return (
      <PageContainer>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📖</div>
          <h1 className="text-2xl font-bold text-text-primary">Chapter not found</h1>
          <p className="text-text-secondary mt-2">The chapter you're looking for doesn't exist.</p>
          <Link href="/chapters">
            <Button variant="outline" className="mt-6">
              ← Back to Chapters
            </Button>
          </Link>
        </div>
      </PageContainer>
    );
  }

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate' },
      advanced: { variant: 'advanced' as const, label: 'Advanced' },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  const difficultyBadge = getDifficultyBadge(chapter.difficulty_level);

  return (
    <PageContainer>
      <Breadcrumbs />

      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Link href="/chapters">
          <Button variant="ghost" size="sm" className="mb-4">
            ← Back to Chapters
          </Button>
        </Link>

        {/* Chapter Header */}
        <div className="mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-bold text-text-secondary bg-bg-elevated px-2 py-1 rounded-md">
                  Chapter {chapter.order}
                </span>
                <Badge variant={difficultyBadge.variant}>
                  {difficultyBadge.label}
                </Badge>
                {isCompleted && (
                  <Badge variant="success">✓ Completed</Badge>
                )}
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-text-primary mb-3">
                {chapter.title}
              </h1>
              <div className="flex items-center gap-4 text-sm text-text-secondary">
                <span className="flex items-center gap-1">
                  ⏱️ {chapter.estimated_time} min read
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Chapter Content */}
        <Card variant="default" className="mb-6">
          <CardContent className="prose prose-invert prose-lg max-w-none p-8">
            <div className="text-text-primary leading-relaxed whitespace-pre-wrap">
              {chapter.content}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap gap-3">
                <Button
                  variant={isCompleted ? 'secondary' : 'primary'}
                  size="lg"
                  onClick={() => markCompleteMutation.mutate()}
                  disabled={isCompleted || markCompleteMutation.isPending}
                  isLoading={markCompleteMutation.isPending}
                >
                  {isCompleted ? '✓ Chapter Complete' : 'Mark as Complete'}
                </Button>

                {chapter.quiz_id && (
                  <Link href={`/quizzes/${chapter.quiz_id}`}>
                    <Button variant="outline" size="lg">
                      Take Chapter Quiz →
                    </Button>
                  </Link>
                )}
              </div>

              <div className="text-sm text-text-muted">
                Chapter {chapter.order} of 10
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}

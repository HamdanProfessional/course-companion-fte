/**
 * Individual chapter page.
 */
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
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
      alert('Chapter marked as complete! 🎉');
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loading size="lg" />
      </div>
    );
  }

  if (!chapter) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900">Chapter not found</h1>
        <Link href="/chapters">
          <Button variant="outline" className="mt-4">
            ← Back to Chapters
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Link href="/chapters">
          <Button variant="ghost" className="mb-4">
            ← Back to Chapters
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{chapter.title}</h1>
        <div className="flex items-center space-x-4 mt-2">
          <span className="text-sm font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-700">
            {chapter.difficulty_level}
          </span>
          <span className="text-sm text-gray-500">
            {chapter.estimated_time} min read
          </span>
          {isCompleted && (
            <span className="text-sm font-medium text-green-600">✅ Completed</span>
          )}
        </div>
      </div>

      {/* Content */}
      <Card>
        <CardContent className="prose prose-lg max-w-none pt-6">
          <div className="whitespace-pre-wrap">{chapter.content}</div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-3">
          <Button
            variant="primary"
            onClick={() => markCompleteMutation.mutate()}
            disabled={isCompleted || markCompleteMutation.isPending}
          >
            {isCompleted ? 'Chapter Complete ✓' : 'Mark as Complete'}
          </Button>
          {chapter.quiz_id && (
            <Link href={`/quizzes/${chapter.quiz_id}`}>
              <Button variant="outline">
                Take Chapter Quiz →
              </Button>
            </Link>
          )}
        </div>
        <div className="text-sm text-gray-500">
          Chapter {chapter.order} of {chapter.order}
        </div>
      </div>
    </div>
  );
}

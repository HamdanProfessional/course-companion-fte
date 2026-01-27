/**
 * Chapters list page.
 */
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { useChapters, useProgress } from '@/hooks';
import Link from 'next/link';

export default function ChaptersPage() {
  const { data: chapters, isLoading } = useChapters();
  const { data: progress } = useProgress();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loading size="lg" />
      </div>
    );
  }

  const completedChapters = new Set(progress?.completed_chapters || []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Course Chapters</h1>
        <p className="text-gray-600 mt-2">
          Master AI Agent Development step by step
        </p>
      </div>

      {/* Chapters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {chapters?.map((chapter, index) => {
          const isCompleted = completedChapters.has(chapter.id);
          const isLocked = index >= 3 && progress?.tier === 'free';

          return (
            <Card
              key={chapter.id}
              className={`hover:shadow-lg transition-shadow ${
                isCompleted ? 'border-green-200 bg-green-50' : ''
              }`}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{chapter.title}</CardTitle>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                        {chapter.difficulty_level}
                      </span>
                      <span className="text-xs text-gray-500">
                        {chapter.estimated_time} min
                      </span>
                    </div>
                  </div>
                  <span className="text-2xl">
                    {isLocked ? '🔒' : isCompleted ? '✅' : '📖'}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {isLocked && (
                    <p className="text-sm text-amber-600">
                      Premium content - Upgrade to unlock
                    </p>
                  )}
                  <Link href={isLocked ? '#' : `/chapters/${chapter.id}`}>
                    <Button
                      variant={isCompleted ? 'outline' : 'primary'}
                      className="w-full"
                      disabled={isLocked}
                    >
                      {isCompleted ? 'Review Chapter' : 'Start Chapter'}
                    </Button>
                  </Link>
                  {chapter.quiz_id && !isLocked && (
                    <Link href={`/quizzes/${chapter.quiz_id}`}>
                      <Button variant="ghost" className="w-full text-sm">
                        Take Quiz →
                      </Button>
                    </Link>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

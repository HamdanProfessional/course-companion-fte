/**
 * Dashboard page with progress visualization and quick actions.
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { useProgress, useStreak, useChapters } from '@/hooks';
import Link from 'next/link';

export default function DashboardPage() {
  const { data: progress, isLoading: progressLoading } = useProgress();
  const { data: streak, isLoading: streakLoading } = useStreak();
  const { data: chapters, isLoading: chaptersLoading } = useChapters();

  if (progressLoading || streakLoading || chaptersLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loading size="lg" />
      </div>
    );
  }

  const completionPercentage = progress?.completion_percentage || 0;
  const currentStreak = streak?.current_streak || 0;
  const completedCount = progress?.completed_chapters?.length || 0;
  const totalChapters = chapters?.length || 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, Student! 👋
        </h1>
        <p className="text-gray-600 mt-2">
          Continue your journey to mastering AI Agent Development
        </p>
      </div>

      {/* Progress Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Progress Card */}
        <Card>
          <CardHeader>
            <CardTitle>Course Progress</CardTitle>
            <CardDescription>Your learning journey</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary-600">
                  {completionPercentage.toFixed(0)}%
                </div>
                <p className="text-sm text-gray-500 mt-1">Complete</p>
              </div>
              <Progress value={completionPercentage} />
              <div className="text-sm text-gray-600 text-center">
                {completedCount} of {totalChapters} chapters completed
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Streak Card */}
        <Card>
          <CardHeader>
            <CardTitle>Current Streak</CardTitle>
            <CardDescription>Keep up the momentum!</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center">
                {currentStreak > 0 ? (
                  <span className="text-6xl">🔥</span>
                ) : (
                  <span className="text-6xl">💪</span>
                )}
              </div>
              <div>
                <div className="text-4xl font-bold text-primary-600">
                  {currentStreak}
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {currentStreak === 1 ? 'day' : 'days'} in a row
                </p>
              </div>
              {currentStreak >= 7 && (
                <p className="text-sm font-semibold text-primary-600">
                  🎉 Amazing! A week streak!
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Jump back into learning</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/chapters">
              <Button className="w-full" variant="primary">
                Continue Learning →
              </Button>
            </Link>
            <Link href="/chapters">
              <Button className="w-full" variant="outline">
                Take a Quiz
              </Button>
            </Link>
            <Link href="/progress">
              <Button className="w-full" variant="ghost">
                View Progress
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Course Outline */}
      <Card>
        <CardHeader>
          <CardTitle>Course Outline</CardTitle>
          <CardDescription>AI Agent Development - {totalChapters} Chapters</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {chapters?.slice(0, 5).map((chapter) => {
              const isCompleted = progress?.completed_chapters?.includes(chapter.id);
              return (
                <Link
                  key={chapter.id}
                  href={`/chapters/${chapter.id}`}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">
                      {isCompleted ? '✅' : '📖'}
                    </span>
                    <div>
                      <h3 className="font-semibold text-gray-900">{chapter.title}</h3>
                      <p className="text-sm text-gray-500">
                        {chapter.difficulty_level} • {chapter.estimated_time} min
                      </p>
                    </div>
                  </div>
                  <span className="text-primary-600">→</span>
                </Link>
              );
            })}
            {totalChapters > 5 && (
              <Link href="/chapters">
                <Button variant="outline" className="w-full">
                  View All {totalChapters} Chapters
                </Button>
              </Link>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

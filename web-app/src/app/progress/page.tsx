/**
 * Progress visualization page.
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { Loading } from '@/components/ui/Loading';
import { useProgress, useStreak, useChapters } from '@/hooks';

export default function ProgressPage() {
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
  const longestStreak = streak?.longest_streak || 0;
  const completedChapters = progress?.completed_chapters || [];
  const totalChapters = chapters?.length || 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Your Progress</h1>
        <p className="text-gray-600 mt-2">
          Track your learning journey and achievements
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Completion
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {completionPercentage.toFixed(0)}%
            </div>
            <Progress value={completionPercentage} className="mt-3" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Chapters Done
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {completedChapters.length}/{totalChapters}
            </div>
            <p className="text-sm text-gray-500 mt-2">chapters completed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Current Streak
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <span className="text-3xl">🔥</span>
              <div className="text-3xl font-bold text-primary-600">
                {currentStreak}
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">days in a row</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Best Streak
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {longestStreak}
            </div>
            <p className="text-sm text-gray-500 mt-2">longest streak</p>
          </CardContent>
        </Card>
      </div>

      {/* Milestones */}
      <Card>
        <CardHeader>
          <CardTitle>Milestones</CardTitle>
          <CardDescription>Learning achievements</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { milestone: 'Started Learning', completed: true, icon: '🚀' },
              { milestone: 'First Chapter Complete', completed: completedChapters.length >= 1, icon: '📖' },
              { milestone: '3-Day Streak', completed: longestStreak >= 3, icon: '🔥' },
              { milestone: 'Week Streak', completed: longestStreak >= 7, icon: '⭐' },
              { milestone: 'Halfway There', completed: completedChapters.length >= totalChapters / 2, icon: '🎯' },
              { milestone: 'Course Complete', completed: completedChapters.length >= totalChapters, icon: '🎓' },
            ].map((item) => (
              <div
                key={item.milestone}
                className={`flex items-center space-x-3 p-3 rounded-lg ${
                  item.completed ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <span className="text-2xl">{item.icon}</span>
                <div className={`flex-1 ${item.completed ? 'text-green-900' : 'text-gray-500'}`}>
                  {item.milestone}
                </div>
                {item.completed && (
                  <span className="text-green-600 font-semibold">✓</span>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Completed Chapters List */}
      <Card>
        <CardHeader>
          <CardTitle>Completed Chapters</CardTitle>
          <CardDescription>Your learning history</CardDescription>
        </CardHeader>
        <CardContent>
          {completedChapters.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No chapters completed yet. Start learning to track your progress!
            </p>
          ) : (
            <div className="space-y-2">
              {chapters
                ?.filter((ch) => completedChapters.includes(ch.id))
                .map((chapter) => (
                  <div
                    key={chapter.id}
                    className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-green-600">✓</span>
                      <span className="font-medium text-green-900">{chapter.title}</span>
                    </div>
                    <span className="text-sm text-green-600">
                      {chapter.difficulty_level}
                    </span>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

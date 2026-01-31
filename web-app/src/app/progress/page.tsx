'use client';

/**
 * Progress visualization page with Professional/Modern SaaS theme.
 * Stats grid, milestones timeline, and completion history.
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress, CircularProgress } from '@/components/ui/Progress';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useProgress, useStreak, useChapters } from '@/hooks';

export const dynamic = 'force-dynamic';

export default function ProgressPage() {
  const { data: progress, isLoading: progressLoading } = useProgress();
  const { data: streak, isLoading: streakLoading } = useStreak();
  const { data: chapters, isLoading: chaptersLoading } = useChapters();

  if (progressLoading || streakLoading || chaptersLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const completionPercentage = progress?.completion_percentage || 0;
  const currentStreak = streak?.current_streak || 0;
  const longestStreak = streak?.longest_streak || 0;
  const completedChapters = progress?.completed_chapters || [];
  const totalChapters = chapters?.length || 0;

  const milestones = [
    { milestone: 'Started Learning', completed: true, icon: '🚀', description: 'Began your journey' },
    { milestone: 'First Chapter', completed: completedChapters.length >= 1, icon: '📖', description: 'Completed first chapter' },
    { milestone: '3-Day Streak', completed: longestStreak >= 3, icon: '🔥', description: '3 consecutive days' },
    { milestone: 'Week Streak', completed: longestStreak >= 7, icon: '⭐', description: '7 consecutive days' },
    { milestone: 'Halfway There', completed: completedChapters.length >= totalChapters / 2, icon: '🎯', description: '50% complete' },
    { milestone: 'Course Complete', completed: completedChapters.length >= totalChapters, icon: '🎓', description: '100% complete' },
  ];

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Your Progress"
        description="Track your learning journey and achievements"
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Completion */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-text-secondary">Completion</p>
                <p className="text-3xl font-bold text-accent-primary mt-1">
                  {completionPercentage.toFixed(0)}%
                </p>
              </div>
              <CircularProgress value={completionPercentage} size={80} strokeWidth={8} />
            </div>
            <Progress value={completionPercentage} size="sm" />
          </CardContent>
        </Card>

        {/* Chapters Done */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Chapters Done</p>
                <p className="text-3xl font-bold text-accent-success mt-1">
                  {completedChapters.length}/{totalChapters}
                </p>
                <p className="text-sm text-text-muted mt-2">chapters completed</p>
              </div>
              <div className="w-16 h-16 rounded-xl bg-bg-elevated flex items-center justify-center text-3xl">
                ✅
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Current Streak */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Current Streak</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-3xl font-bold text-accent-warning">{currentStreak}</span>
                  <span className="text-sm text-text-muted">days</span>
                </div>
                <p className="text-sm text-text-muted mt-2">keep it up!</p>
              </div>
              <div className="w-16 h-16 rounded-xl bg-bg-elevated flex items-center justify-center text-3xl">
                🔥
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Best Streak */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Best Streak</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-3xl font-bold text-accent-premium">{longestStreak}</span>
                  <span className="text-sm text-text-muted">days</span>
                </div>
                <p className="text-sm text-text-muted mt-2">personal best</p>
              </div>
              <div className="w-16 h-16 rounded-xl bg-bg-elevated flex items-center justify-center text-3xl">
                🏆
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Milestones Timeline */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-xl">🎯</span>
            Milestones
          </CardTitle>
          <CardDescription>Your learning achievements</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {milestones.map((item, index) => (
              <div
                key={item.milestone}
                className={`flex items-center gap-4 p-4 rounded-lg border transition-all ${
                  item.completed
                    ? 'bg-accent-success/10 border-accent-success/30'
                    : 'bg-bg-elevated/30 border-border-default opacity-60'
                }`}
              >
                <div className="relative">
                  {/* Timeline line */}
                  {index < milestones.length - 1 && (
                    <div className="absolute top-8 left-4 w-0.5 h-12 bg-border-default -z-10" />
                  )}
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                    item.completed ? 'bg-accent-success/20' : 'bg-bg-elevated'
                  }`}>
                    {item.icon}
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className={`font-semibold ${item.completed ? 'text-accent-success' : 'text-text-muted'}`}>
                    {item.milestone}
                  </h4>
                  <p className="text-sm text-text-secondary">{item.description}</p>
                </div>
                {item.completed && (
                  <div className="w-8 h-8 rounded-full bg-accent-success/20 flex items-center justify-center">
                    <span className="text-accent-success">✓</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Completed Chapters List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-xl">📚</span>
            Completed Chapters
          </CardTitle>
          <CardDescription>Your learning history</CardDescription>
        </CardHeader>
        <CardContent>
          {completedChapters.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">📖</div>
              <p className="text-text-secondary">
                No chapters completed yet. Start learning to track your progress!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {chapters
                ?.filter((ch) => completedChapters.includes(ch.id))
                .map((chapter) => (
                  <div
                    key={chapter.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-accent-success/30 bg-accent-success/5"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-accent-success/20 flex items-center justify-center">
                        <span className="text-accent-success">✓</span>
                      </div>
                      <div>
                        <h4 className="font-medium text-text-primary">{chapter.title}</h4>
                        <p className="text-sm text-text-muted">{chapter.difficulty_level}</p>
                      </div>
                    </div>
                    <Badge variant="success">Completed</Badge>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>
    </PageContainer>
  );
}

'use client';

/**
 * Complete Progress visualization page with Professional/Modern SaaS theme.
 * Features:
 * - Stats grid with overall progress
 * - Streak calendar visualization
 * - Quiz score history chart
 * - Achievements section
 * - Chapter-by-chapter progress breakdown
 * - Milestones timeline
 */
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress, CircularProgress } from '@/components/ui/Progress';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { EmptyStates } from '@/components/ui/EmptyState';
import {
  useV3ProgressSummary,
  useV3ChaptersProgress,
  useV3StreakCalendar,
  useV3ScoreHistory,
  useV3Achievements,
  useV3DailyCheckin,
  useV3Chapters,
} from '@/hooks/useV3';
import type { AchievementItem, ChapterProgress, ScoreHistoryItem } from '@/lib/api-v3';
import { BookOpen, Flame, Star, Target, GraduationCap, Trophy, FileEdit, CheckCircle, BarChart3, Rocket, Calendar, Clock } from 'lucide-react';

export default function ProgressPage() {
  const router = useRouter();
  const [selectedMonth, setSelectedMonth] = useState(new Date());

  // Fetch all progress data
  const { data: progressSummary, isLoading: progressLoading, refetch: refetchProgress } = useV3ProgressSummary();
  const { data: chaptersProgress, isLoading: chaptersLoading } = useV3ChaptersProgress();
  const { data: streakCalendar, isLoading: streakLoading } = useV3StreakCalendar(
    selectedMonth.getFullYear(),
    selectedMonth.getMonth() + 1
  );
  const { data: scoreHistory, isLoading: scoreLoading } = useV3ScoreHistory(30);
  const { data: achievements, isLoading: achievementsLoading } = useV3Achievements();
  const { data: chapters, isLoading: chaptersListLoading } = useV3Chapters();
  const checkinMutation = useV3DailyCheckin();

  // Loading state
  if (progressLoading || chaptersLoading || streakLoading || achievementsLoading || scoreLoading || chaptersListLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  // Handle case when there's no data
  if (!progressSummary && !chaptersProgress) {
    return (
      <PageContainer>
        <PageHeader
          title="Your Progress"
          description="Track your learning journey and achievements"
        />
        <EmptyStates.NoProgress size="lg" />
      </PageContainer>
    );
  }

  const completionPercentage = progressSummary?.completion_percentage || 0;
  const currentStreak = progressSummary?.current_streak || 0;
  const longestStreak = progressSummary?.longest_streak || 0;
  const totalChapters = progressSummary?.total_chapters || chapters?.length || 0;
  const completedChapters = progressSummary?.completed_chapters || [];
  const totalQuizzes = progressSummary?.total_quizzes_taken || 0;
  const averageScore = progressSummary?.average_score || 0;
  const unlockedAchievements = achievements?.filter(a => a.unlocked_at) || [];
  const totalAchievementsCount = achievements?.length || 0;

  const milestones = [
    { milestone: 'Started Learning', completed: true, icon: '🚀', Icon: Rocket, description: 'Began your journey' },
    { milestone: 'First Chapter', completed: completedChapters.length >= 1, icon: '📖', Icon: BookOpen, description: 'Completed first chapter' },
    { milestone: '3-Day Streak', completed: longestStreak >= 3, icon: '🔥', Icon: Flame, description: '3 consecutive days' },
    { milestone: 'Week Streak', completed: longestStreak >= 7, icon: '⭐', Icon: Star, description: '7 consecutive days' },
    { milestone: 'Halfway There', completed: completedChapters.length >= totalChapters / 2, icon: '🎯', Icon: Target, description: '50% complete' },
    { milestone: 'Course Complete', completed: completedChapters.length >= totalChapters, icon: '🎓', Icon: GraduationCap, description: '100% complete' },
  ];

  const handleCheckin = async () => {
    try {
      await checkinMutation.mutateAsync();
      refetchProgress();
    } catch (error) {
      console.error('Check-in failed:', error);
    }
  };

  const handlePreviousMonth = () => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1));
  };

  const handleNextMonth = () => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1));
  };

  const unlockedCount = unlockedAchievements.length;
  const achievementProgress = totalAchievementsCount > 0 ? (unlockedCount / totalAchievementsCount) * 100 : 0;

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Your Progress"
        description="Track your learning journey and achievements"
      />

      {/* Time Machine CTA */}
      <Card className="mb-8 bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 border-cosmic-primary/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-text-primary mb-2 flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center">
                  <Clock className="w-7 h-7 text-white" />
                </div>
                Time Machine: See How You've Grown
              </h3>
              <p className="text-text-secondary">
                View the evolution of your questions and understanding throughout the semester
              </p>
            </div>
            <Button
              variant="primary"
              size="lg"
              onClick={() => router.push('/time-machine')}
              className="gap-2"
            >
              <Clock className="w-5 h-5" />
              View Time Machine
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
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
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-accent-success" />
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
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                <Flame className="w-8 h-8 text-accent-warning" />
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
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
                <Trophy className="w-8 h-8 text-accent-premium" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quizzes Taken */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-secondary">Quizzes Taken</p>
                <p className="text-3xl font-bold text-accent-secondary mt-1">
                  {totalQuizzes}
                </p>
                <p className="text-sm text-text-muted mt-2">avg: {averageScore.toFixed(1)}%</p>
              </div>
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent-secondary/20 to-accent-secondary/10 flex items-center justify-center">
                <FileEdit className="w-8 h-8 text-accent-secondary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Streak Calendar */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-cosmic-primary" />
                </div>
                Streak Calendar
              </CardTitle>
              <CardDescription>Your learning activity this month</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={handlePreviousMonth}>
                ←
              </Button>
              <span className="text-sm font-medium min-w-[120px] text-center">
                {selectedMonth.toLocaleString('default', { month: 'long', year: 'numeric' })}
              </span>
              <Button variant="outline" size="sm" onClick={handleNextMonth} disabled={
                selectedMonth.getFullYear() === new Date().getFullYear() &&
                selectedMonth.getMonth() === new Date().getMonth()
              }>
                →
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {streakCalendar && streakCalendar.days.length > 0 ? (
            <div className="grid grid-cols-7 gap-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="text-center text-sm font-medium text-text-muted py-2">
                  {day}
                </div>
              ))}
              {streakCalendar.days.map((day, index) => {
                const dayDate = new Date(day.date);
                // Add empty cells for alignment
                if (index === 0) {
                  const firstDayOfWeek = dayDate.getDay();
                  return (
                    <>
                      {Array.from({ length: firstDayOfWeek }).map((_, i) => (
                        <div key={`empty-${i}`} className="aspect-square" />
                      ))}
                      <StreakDayCell day={day} />
                    </>
                  );
                }
                return <StreakDayCell key={day.date.toString()} day={day} />;
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-text-muted">
              No activity data for this month
            </div>
          )}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-text-muted">
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-bg-elevated" />
                <span>No activity</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-accent-success/30" />
                <span>Active day</span>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={handleCheckin} disabled={checkinMutation.isPending}>
              {checkinMutation.isPending ? 'Recording...' : (
                <span className="flex items-center gap-1">
                  <FileEdit className="w-4 h-4" />
                  Daily Check-in
                </span>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Quiz Score History */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-accent-info" />
            </div>
            Quiz Performance
          </CardTitle>
          <CardDescription>Your recent quiz scores</CardDescription>
        </CardHeader>
        <CardContent>
          {scoreHistory && scoreHistory.length > 0 ? (
            <div className="space-y-3">
              {scoreHistory.map((item, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div className="w-24 text-sm text-text-muted">
                    {new Date(item.date).toLocaleDateString()}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-text-primary">{item.quiz_title}</span>
                      <Badge variant={item.passed ? 'success' : 'warning'}>
                        {item.score}%
                      </Badge>
                    </div>
                    <Progress value={item.score} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
                <BarChart3 className="w-8 h-8 text-accent-info" />
              </div>
              <p className="text-text-secondary">No quiz history yet. Take a quiz to see your performance!</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Achievements */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-accent-premium" />
            </div>
            Achievements
          </CardTitle>
          <CardDescription>
            {unlockedCount} of {totalAchievementsCount} unlocked ({achievementProgress.toFixed(0)}%)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {achievements && achievements.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {achievements.map((achievement) => (
                <AchievementCard key={achievement.id} achievement={achievement} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
                <Trophy className="w-8 h-8 text-accent-premium" />
              </div>
              <p className="text-text-secondary">No achievements available yet.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chapter-by-Chapter Progress */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-cosmic-primary" />
            </div>
            Chapter Progress
          </CardTitle>
          <CardDescription>Detailed progress for each chapter</CardDescription>
        </CardHeader>
        <CardContent>
          {chaptersProgress && chaptersProgress.length > 0 ? (
            <div className="space-y-3">
              {chaptersProgress.map((chapter) => (
                <ChapterProgressRow key={chapter.chapter_id} chapter={chapter} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <BookOpen className="w-8 h-8 text-cosmic-primary" />
              </div>
              <p className="text-text-secondary">No chapter progress data available.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Milestones Timeline */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-accent-primary" />
            </div>
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
                  {index < milestones.length - 1 && (
                    <div className="absolute top-8 left-4 w-0.5 h-12 bg-border-default -z-10" />
                  )}
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    item.completed ? 'bg-accent-success/20' : 'bg-bg-elevated'
                  }`}>
                    {item.Icon ? <item.Icon className={`w-6 h-6 ${item.completed ? 'text-accent-success' : 'text-text-muted'}`} /> : <span className="text-2xl">{item.icon}</span>}
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
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-accent-success" />
            </div>
            Completed Chapters
          </CardTitle>
          <CardDescription>Your learning history</CardDescription>
        </CardHeader>
        <CardContent>
          {completedChapters.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <BookOpen className="w-8 h-8 text-cosmic-primary" />
              </div>
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

// Helper Components

function StreakDayCell({ day }: { day: { date: Date | string; active: boolean; streak_day?: number | null } }) {
  const date = typeof day.date === 'string' ? new Date(day.date) : day.date;
  const isToday = date.toDateString() === new Date().toDateString();

  return (
    <div
      className={`aspect-square rounded-lg flex items-center justify-center text-sm font-medium transition-all ${
        day.active
          ? 'bg-accent-success/30 text-accent-success'
          : isToday
          ? 'bg-accent-primary/20 text-accent-primary border border-accent-primary/30'
          : 'bg-bg-elevated/50 text-text-muted'
      }`}
    >
      {date.getDate()}
      {day.streak_day && day.streak_day > 0 && (
        <span className="absolute bottom-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-accent-warning" />
      )}
    </div>
  );
}

function AchievementCard({ achievement }: { achievement: AchievementItem }) {
  const isUnlocked = !!achievement.unlocked_at;

  return (
    <div
      className={`p-4 rounded-lg border transition-all ${
        isUnlocked
          ? `bg-accent-success/10 border-accent-success/30`
          : 'bg-bg-elevated/30 border-border-default opacity-60'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`text-3xl ${isUnlocked ? '' : 'grayscale opacity-50'}`}>
          {achievement.icon}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className={`font-semibold ${isUnlocked ? 'text-text-primary' : 'text-text-muted'}`}>
              {achievement.name}
            </h4>
            <Badge
              variant={achievement.rarity === 'legendary' ? 'premium' : achievement.rarity === 'epic' ? 'secondary' : 'outline'}
              className="text-xs"
            >
              {achievement.rarity}
            </Badge>
          </div>
          <p className="text-sm text-text-secondary">{achievement.description}</p>
          {!isUnlocked && achievement.progress > 0 && (
            <div className="mt-2">
              <Progress value={achievement.progress} size="sm" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ChapterProgressRow({ chapter }: { chapter: ChapterProgress }) {
  return (
    <div
      className={`flex items-center justify-between p-4 rounded-lg border transition-all ${
        chapter.completed
          ? 'bg-accent-success/10 border-accent-success/30'
          : 'bg-bg-elevated/30 border-border-default'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
          chapter.completed ? 'bg-accent-success/20 text-accent-success' : 'bg-bg-elevated text-text-muted'
        }`}>
          {chapter.chapter_order}
        </div>
        <div>
          <h4 className={`font-medium ${chapter.completed ? 'text-accent-success' : 'text-text-primary'}`}>
            {chapter.chapter_title}
          </h4>
          <p className="text-sm text-text-muted">Chapter {chapter.chapter_order}</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        {chapter.best_quiz_score !== null && (
          <div className="text-right">
            <p className="text-sm text-text-muted">Best Score</p>
            <p className={`font-semibold ${chapter.best_quiz_score >= 70 ? 'text-accent-success' : 'text-accent-warning'}`}>
              {chapter.best_quiz_score}%
            </p>
          </div>
        )}
        {chapter.completed && (
          <Badge variant="success">Completed</Badge>
        )}
        {chapter.quiz_taken && !chapter.completed && (
          <Badge variant="warning">In Progress</Badge>
        )}
      </div>
    </div>
  );
}

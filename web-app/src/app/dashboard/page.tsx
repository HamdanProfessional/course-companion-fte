'use client';

/**
 * Dashboard page with Nebula/Cosmic theme.
 * Immersive space-themed interface with animated components.
 */
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress, CircularProgress } from '@/components/ui/Progress';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { StatCard } from '@/components/ui/StatCard';
import { GlassCard } from '@/components/ui/GlassCard';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useProgress, useStreak, useChapters } from '@/hooks';
import { pageVariants, staggerContainer } from '@/lib/animations';
import { getMistakeStats } from '@/lib/mistakeBank';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Trophy, TrendingUp, Zap, FileText, Target, BarChart3, Brain, Bot, Clock, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [mistakeStats, setMistakeStats] = useState(getMistakeStats());

  useEffect(() => {
    // Get the logged-in user's ID from localStorage
    const storedUserId = localStorage.getItem('user_id');
    const userRole = localStorage.getItem('user_role');

    if (!storedUserId) {
      // Not logged in, redirect to login
      router.push('/login');
      return;
    }

    // If user is a teacher, redirect to teacher dashboard
    if (userRole === 'teacher') {
      router.push('/teacher-dashboard');
      return;
    }

    setUserId(storedUserId);
  }, [router]);

  const { data: progress, isLoading: progressLoading } = useProgress(userId || '');
  const { data: streak, isLoading: streakLoading } = useStreak(userId || '');
  const { data: chapters, isLoading: chaptersLoading } = useChapters();

  // Refresh mistake stats when page loads
  useEffect(() => {
    setMistakeStats(getMistakeStats());
  }, [progress, streak]);

  if (!userId || progressLoading || streakLoading || chaptersLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const completionPercentage = progress?.completion_percentage || 0;
  const currentStreak = streak?.current_streak || 0;
  const completedCount = progress?.completed_chapters?.length || 0;
  const totalChapters = chapters?.length || 0;
  const completedChapters = new Set(progress?.completed_chapters || []);

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate' },
      advanced: { variant: 'advanced' as const, label: 'Advanced' },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  return (
    <PageContainer>
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
      >
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <PageHeader
            title="Welcome back!"
            description="Continue your learning journey through AI Agent Development"
          />
        </motion.div>

        {/* Quick Links - AI Features */}
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
        >
          <Link href="/adaptive-learning" className="group">
            <GlassCard hover glow>
              <div className="flex items-center gap-4">
                <motion.div
                  whileHover={{ scale: 1.2 }}
                  transition={{ duration: 0.6 }}
                  className="w-12 h-12 rounded-xl bg-cosmic-primary/20 flex items-center justify-center group-hover:bg-cosmic-primary/30 transition-all"
                >
                  <Brain className="w-6 h-6 text-cosmic-primary" />
                </motion.div>
                <div className="flex-1">
                  <h3 className="font-semibold text-text-primary group-hover:text-cosmic-primary transition-colors">
                    Adaptive Learning
                  </h3>
                  <p className="text-sm text-text-secondary mt-1">
                    AI-powered personalized recommendations
                  </p>
                </div>
                <motion.span
                  whileHover={{ scale: 1.1 }}
                  className="px-2 py-1 rounded text-xs font-bold bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white"
                >
                  AI
                </motion.span>
              </div>
            </GlassCard>
          </Link>

          <Link href="/ai-mentor" className="group">
            <GlassCard hover glow>
              <div className="flex items-center gap-4">
                <motion.div
                  whileHover={{ scale: 1.2 }}
                  transition={{ duration: 0.6 }}
                  className="w-12 h-12 rounded-xl bg-cosmic-primary/20 flex items-center justify-center group-hover:bg-cosmic-primary/30 transition-all"
                >
                  <Bot className="w-6 h-6 text-cosmic-primary" />
                </motion.div>
                <div className="flex-1">
                  <h3 className="font-semibold text-text-primary group-hover:text-cosmic-primary transition-colors">
                    AI Mentor
                  </h3>
                  <p className="text-sm text-text-secondary mt-1">
                    24/7 interactive tutoring and Q&A
                  </p>
                </div>
                <motion.span
                  whileHover={{ scale: 1.1 }}
                  className="px-2 py-1 rounded text-xs font-bold bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white"
                >
                  AI
                </motion.span>
              </div>
            </GlassCard>
          </Link>
        </motion.div>

        {/* Stats Grid with Nebula Theme */}
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8"
        >
          <StatCard
            title="Course Progress"
            value={`${completionPercentage.toFixed(0)}%`}
            change={completionPercentage * 0.1}
            icon={<TrendingUp className="h-6 w-6" />}
            trend={completionPercentage > 50 ? 'up' : 'neutral'}
            variant="nebula"
          />
          <StatCard
            title="Current Streak"
            value={currentStreak}
            change={currentStreak > 0 ? Math.min(currentStreak, streak?.longest_streak || currentStreak) : 0}
            icon={<Zap className="h-6 w-6" />}
            trend={currentStreak > 0 ? 'up' : 'neutral'}
            variant="stellar"
          />
          <StatCard
            title="Completed"
            value={completedCount}
            icon={<Trophy className="h-6 w-6" />}
            variant="success"
          />
          <StatCard
            title="Mistakes"
            value={mistakeStats.remaining}
            change={mistakeStats.total > 0 ? Math.round((mistakeStats.mastered / mistakeStats.total) * 100) : 0}
            icon={<AlertCircle className="h-6 w-6" />}
            trend={mistakeStats.remaining === 0 ? 'up' : 'neutral'}
            variant="warning"
          />
          <StatCard
            title="Remaining"
            value={totalChapters - completedCount}
            icon={<BookOpen className="h-6 w-6" />}
            variant="cosmic"
          />
        </motion.div>

        {/* Course Outline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <GlassCard>
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-white">
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                  className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center"
                >
                  <BookOpen className="w-5 h-5 text-cosmic-primary" />
                </motion.div>
                Course Outline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {chapters?.map((chapter, index) => {
                  const isCompleted = completedChapters.has(chapter.id);
                  const difficultyBadge = getDifficultyBadge(chapter.difficulty_level);

                  return (
                    <motion.div
                      key={chapter.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Link href={`/chapters/${chapter.id}`} className="block group">
                        <div className="flex items-center justify-between p-4 rounded-xl border border-glass-border hover:border-cosmic-primary hover:bg-glass-hover transition-all backdrop-blur-sm">
                          <div className="flex items-center gap-4">
                            <motion.div
                              whileHover={{ scale: 1.1, rotate: 5 }}
                              className="w-12 h-12 rounded-lg bg-cosmic-secondary flex items-center justify-center text-lg font-bold text-text-secondary group-hover:text-cosmic-primary group-hover:bg-cosmic-primary/20 transition-all"
                            >
                              {index + 1}
                            </motion.div>
                            <div>
                              <h3 className="font-semibold text-text-primary group-hover:text-cosmic-primary transition-colors">
                                {chapter.title}
                              </h3>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge variant={difficultyBadge.variant}>
                                  {difficultyBadge.label}
                                </Badge>
                                <span className="text-sm text-text-secondary flex items-center gap-1">
                                  <Clock className="w-3.5 h-3.5" />
                                  {chapter.estimated_time} min
                                </span>
                              </div>
                            </div>
                          </div>
                          <div>
                            {isCompleted ? (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: 'spring', stiffness: 200 }}
                              >
                                <Badge variant="success">✓ Completed</Badge>
                              </motion.div>
                            ) : (
                              <span className="text-text-secondary text-sm font-medium group-hover:text-cosmic-primary transition-colors">
                                Start →
                              </span>
                            )}
                          </div>
                        </div>
                      </Link>
                    </motion.div>
                  );
                })}
              </div>
            </CardContent>
          </GlassCard>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8"
        >
          <Link href="/chapters">
            <Button variant="primary" className="w-full gap-2" size="lg">
              <FileText className="w-5 h-5" />
              Browse Chapters
            </Button>
          </Link>
          <Link href="/quizzes">
            <Button variant="secondary" className="w-full gap-2" size="lg">
              <Target className="w-5 h-5" />
              Take a Quiz
            </Button>
          </Link>
          <Link href="/progress">
            <Button variant="outline" className="w-full gap-2" size="lg">
              <BarChart3 className="w-5 h-5" />
              View Progress
            </Button>
          </Link>
        </motion.div>
      </motion.div>
    </PageContainer>
  );
}

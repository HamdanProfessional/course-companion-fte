'use client';

/**
 * Leaderboard Page - Global leaderboard with privacy controls
 * XP Formula: total_quiz_score + (10 × completed_chapters) + (5 × streak_days)
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Trophy, Medal, Star, TrendingUp, Eye, EyeOff, Crown, Award } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { tutorApi, LeaderboardData, LeaderboardOptInStatus } from '@/lib/api-v3';
import { pageVariants, staggerContainer } from '@/lib/animations';
import { useLocalStorage } from '@/hooks/useLocalStorage';

export default function LeaderboardPage() {
  const router = useRouter();
  const [userId] = useLocalStorage('user_id', '');
  const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null);
  const [optInStatus, setOptInStatus] = useState<LeaderboardOptInStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showOptInForm, setShowOptInForm] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [showRank, setShowRank] = useState(true);
  const [showScore, setShowScore] = useState(true);
  const [showStreak, setShowStreak] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!userId) {
      router.push('/login');
      return;
    }
    fetchLeaderboard();
    fetchOptInStatus();
  }, [userId, router]);

  const fetchLeaderboard = async () => {
    try {
      setIsLoading(true);
      const data = await tutorApi.getLeaderboard({
        limit: 10,
        user_id: userId || undefined,
      });
      setLeaderboard(data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchOptInStatus = async () => {
    try {
      const status = await tutorApi.getLeaderboardOptInStatus(userId);
      setOptInStatus(status);
      if (status) {
        setDisplayName(status.display_name);
        setShowRank(status.show_rank);
        setShowScore(status.show_score);
        setShowStreak(status.show_streak);
      }
    } catch (error) {
      console.error('Failed to fetch opt-in status:', error);
    }
  };

  const handleOptIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) return;

    try {
      setIsSubmitting(true);
      await tutorApi.optInToLeaderboard({
        user_id: userId,
        display_name: displayName,
        show_rank: showRank,
        show_score: showScore,
        show_streak: showStreak,
      });
      await fetchOptInStatus();
      await fetchLeaderboard();
      setShowOptInForm(false);
    } catch (error) {
      console.error('Failed to opt in:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOptOut = async () => {
    if (!userId) return;
    if (!confirm('Are you sure you want to opt out of the leaderboard?')) return;

    try {
      await tutorApi.optOutFromLeaderboard(userId);
      await fetchOptInStatus();
      await fetchLeaderboard();
    } catch (error) {
      console.error('Failed to opt out:', error);
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-gray-400" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-amber-700" />;
    return <span className="w-5 h-5 flex items-center justify-center text-sm font-bold text-text-secondary">#{rank}</span>;
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return <span className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-500 text-xs font-bold">CHAMPION</span>;
    if (rank === 2) return <span className="px-2 py-1 rounded bg-gray-400/20 text-gray-400 text-xs font-bold">2ND</span>;
    if (rank === 3) return <span className="px-2 py-1 rounded bg-amber-700/20 text-amber-700 text-xs font-bold">3RD</span>;
    return null;
  };

  if (!userId) {
    return null;
  }

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
            title="Global Leaderboard"
            description="Compete with students worldwide. XP = Quiz Score + (10 × Chapters) + (5 × Streak)"
          />
        </motion.div>

        {/* User Status Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <GlassCard>
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary mb-1">Your Status</h3>
                  {optInStatus?.is_opted_in ? (
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-cosmic-primary" />
                        <span className="text-text-primary font-bold">
                          Rank: #{leaderboard?.user_rank || 'N/A'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Star className="w-5 h-5 text-cosmic-purple" />
                        <span className="text-text-primary font-bold">
                          {leaderboard?.user_xp || 0} XP
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-text-secondary">Opt in to see your rank and XP on the leaderboard</p>
                  )}
                </div>

                {optInStatus?.is_opted_in ? (
                  <div className="flex items-center gap-3">
                    <Badge variant="success" className="gap-1">
                      <Eye className="w-3 h-3" />
                      Visible on Leaderboard
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleOptOut}
                    >
                      <EyeOff className="w-4 h-4 mr-1" />
                      Opt Out
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    onClick={() => setShowOptInForm(!showOptInForm)}
                  >
                    <Trophy className="w-4 h-4 mr-1" />
                    Join Leaderboard
                  </Button>
                )}
              </div>

              {/* Opt-In Form */}
              {showOptInForm && !optInStatus?.is_opted_in && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-6 pt-6 border-t border-glass-border"
                >
                  <form onSubmit={handleOptIn} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-text-primary mb-2">
                        Display Name (Anonymous)
                      </label>
                      <Input
                        type="text"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        placeholder="e.g., AgentMaster99"
                        required
                        maxLength={50}
                        className="w-full"
                      />
                      <p className="text-xs text-text-secondary mt-1">
                        This name will be displayed on the leaderboard instead of your email
                      </p>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-text-primary">Privacy Settings</label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={showRank}
                          onChange={(e) => setShowRank(e.target.checked)}
                          className="w-4 h-4 rounded"
                        />
                        <span className="text-sm text-text-secondary">Show my rank</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={showScore}
                          onChange={(e) => setShowScore(e.target.checked)}
                          className="w-4 h-4 rounded"
                        />
                        <span className="text-sm text-text-secondary">Show my average score</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={showStreak}
                          onChange={(e) => setShowStreak(e.target.checked)}
                          className="w-4 h-4 rounded"
                        />
                        <span className="text-sm text-text-secondary">Show my streak</span>
                      </label>
                    </div>

                    <Button
                      type="submit"
                      variant="primary"
                      disabled={isSubmitting || !displayName.trim()}
                    >
                      {isSubmitting ? 'Joining...' : 'Join Leaderboard'}
                    </Button>
                  </form>
                </motion.div>
              )}
            </div>
          </GlassCard>
        </motion.div>

        {/* Leaderboard Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <GlassCard>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-text-primary">Top Students</h2>
                <Badge variant="cosmic">
                  {leaderboard?.total_entries || 0} Participants
                </Badge>
              </div>

              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cosmic-primary" />
                </div>
              ) : (
                <div className="space-y-3">
                  {leaderboard?.leaderboard.map((entry) => (
                    <motion.div
                      key={entry.user_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`flex items-center gap-4 p-4 rounded-xl border ${
                        entry.user_id === userId
                          ? 'border-cosmic-primary bg-cosmic-primary/10'
                          : 'border-glass-border bg-glass-hover'
                      } transition-all`}
                    >
                      {/* Rank */}
                      <div className="flex-shrink-0 w-12 flex justify-center">
                        {getRankIcon(entry.rank)}
                      </div>

                      {/* Display Name */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-text-primary truncate">
                            {entry.display_name}
                          </h3>
                          {entry.user_id === userId && (
                            <Badge variant="success" className="text-xs">You</Badge>
                          )}
                          {getRankBadge(entry.rank)}
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-xs text-text-secondary">XP</div>
                          <div className="font-bold text-cosmic-primary">{entry.xp}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-text-secondary">Score</div>
                          <div className="font-bold text-text-primary">{entry.average_score.toFixed(1)}%</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-text-secondary">Streak</div>
                          <div className="font-bold text-cosmic-purple">{entry.current_streak} days</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-text-secondary">Chapters</div>
                          <div className="font-bold text-text-primary">{entry.completed_chapters}</div>
                        </div>
                      </div>
                    </motion.div>
                  ))}

                  {leaderboard?.leaderboard.length === 0 && (
                    <div className="text-center py-12 text-text-secondary">
                      <Trophy className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No students on the leaderboard yet.</p>
                      <p className="text-sm mt-1">Be the first to join!</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </GlassCard>
        </motion.div>
      </motion.div>
    </PageContainer>
  );
}

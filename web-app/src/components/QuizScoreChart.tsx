'use client';

/**
 * QuizScoreChart Component - Phase 3 Gamification
 *
 * Visual chart showing quiz score history and performance trends.
 * Helps students track their improvement over time.
 */

import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { LoadingSpinner } from './ui/Loading';
import { Badge } from './uiBadge';
import { useV3ScoreHistory } from '@/hooks/useV3';
import { useMemo } from 'react';

interface QuizScoreChartProps {
  limit?: number;
  className?: string;
}

export function QuizScoreChart({ limit = 30, className }: QuizScoreChartProps) {
  const { data: scoreHistory, isLoading } = useV3ScoreHistory(limit);

  // Calculate statistics
  const stats = useMemo(() => {
    if (!scoreHistory || scoreHistory.length === 0) return null;

    const scores = scoreHistory.map(h => h.score);
    const average = scores.reduce((a, b) => a + b, 0) / scores.length;
    const best = Math.max(...scores);
    const worst = Math.min(...scores);
    const passed = scoreHistory.filter(h => h.passed).length;

    // Calculate trend (compare recent vs older attempts)
    const midpoint = Math.floor(scores.length / 2);
    const recentAvg = scores.slice(0, midpoint).reduce((a, b) => a + b, 0) / midpoint;
    const olderAvg = scores.slice(midpoint).reduce((a, b) => a + b, 0) / (scores.length - midpoint);
    const trend = recentAvg - olderAvg;

    return { average, best, worst, passed, total: scores.length, trend };
  }, [scoreHistory]);

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="md" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!scoreHistory || scoreHistory.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <span className="text-2xl">📊</span>
            Quiz Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-text-secondary">
            <div className="text-5xl mb-4">📝</div>
            <p>No quiz attempts yet.</p>
            <p className="text-sm mt-2">Take your first quiz to see your progress!</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Find min/max for chart scaling
  const maxScore = Math.max(...scoreHistory.map(h => h.score));

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-2xl">📊</span>
          Quiz Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        {stats && (
          <div className="space-y-6">
            {/* Statistics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center p-3 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-primary">
                  {stats.average.toFixed(1)}
                </div>
                <div className="text-xs text-text-muted">Average Score</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-success">
                  {stats.best}%
                </div>
                <div className="text-xs text-text-muted">Best Score</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-warning">
                  {stats.worst}%
                </div>
                <div className="text-xs text-text-muted">Lowest Score</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-info">
                  {stats.passed}/{stats.total}
                </div>
                <div className="text-xs text-text-muted">Passed</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-bg-elevated col-span-2 md:col-span-1">
                <div className={`text-2xl font-bold ${
                  stats.trend > 0 ? 'text-accent-success' : stats.trend < 0 ? 'text-accent-danger' : 'text-text-secondary'
                }`}>
                  {stats.trend > 0 ? '+' : ''}{stats.trend.toFixed(1)}%
                </div>
                <div className="text-xs text-text-muted">Trend</div>
              </div>
            </div>

            {/* Chart */}
            <div className="p-4 rounded-lg bg-bg-secondary">
              <div className="flex items-end justify-between gap-1 h-48">
                {scoreHistory.map((item, index) => {
                  const heightPercentage = (item.score / 100) * 100;
                  const isRecent = index < 3;

                  return (
                    <div
                      key={index}
                      className="flex-1 flex flex-col items-center group relative"
                      title={`${item.quiz_title}: ${item.score}%`}
                    >
                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-2 hidden group-hover:block z-10 bg-bg-primary border border-border-default rounded-lg p-3 shadow-lg min-w-[150px]">
                        <div className="text-sm font-medium text-text-primary mb-1">
                          {item.quiz_title}
                        </div>
                        <div className="text-xs text-text-secondary">
                          {new Date(item.date).toLocaleDateString()}
                        </div>
                        <div className="text-lg font-bold text-accent-primary mt-1">
                          {item.score}%
                        </div>
                      </div>

                      {/* Bar */}
                      <div
                        className={`w-full rounded-t transition-all ${
                          item.passed
                            ? 'bg-gradient-to-t from-accent-primary to-accent-secondary'
                            : 'bg-gradient-to-t from-accent-danger to-accent-warning'
                        } ${isRecent ? 'ring-2 ring-accent-primary ring-offset-2 ring-offset-bg-secondary' : ''}`}
                        style={{ height: `${heightPercentage}%` }}
                      />

                      {/* Score label for recent attempts */}
                      {isRecent && (
                        <div className="text-xs font-semibold text-text-primary mt-1">
                          {item.score}%
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* X-axis labels */}
              <div className="flex justify-between mt-2 text-xs text-text-muted px-1">
                <span>{scoreHistory[scoreHistory.length - 1]?.date && new Date(scoreHistory[scoreHistory.length - 1].date).toLocaleDateString()}</span>
                <span>Most Recent</span>
              </div>
            </div>

            {/* Recent Attempts */}
            <div>
              <h4 className="font-semibold text-text-primary mb-3 text-sm">Recent Attempts</h4>
              <div className="space-y-2">
                {scoreHistory.slice(0, 5).map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg bg-bg-elevated hover:bg-bg-hover transition-colors"
                  >
                    <div className="flex-1">
                      <div className="text-sm font-medium text-text-primary">
                        {item.quiz_title}
                      </div>
                      <div className="text-xs text-text-muted">
                        {new Date(item.date).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={item.passed ? 'success' : 'warning'}>
                        {item.passed ? 'Passed' : 'Failed'}
                      </Badge>
                      <div className="text-lg font-bold text-accent-primary w-12 text-right">
                        {item.score}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

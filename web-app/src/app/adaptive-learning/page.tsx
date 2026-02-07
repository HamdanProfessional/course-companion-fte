'use client';

/**
 * Adaptive Learning Page - Phase 3
 *
 * AI-powered personalized learning features:
 * - Knowledge gap analysis
 * - Personalized chapter recommendations
 * - Learning path generation
 * - Smart study suggestions
 */

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import {
  useV3KnowledgeAnalysis,
  useV3Recommendations,
  useV3AIStatus,
} from '@/hooks/useV3';
import { useUserTier } from '@/hooks';
import { Target, Armchair, RotateCcw, Compass, Clock, Map, BookOpen, Zap, Sparkles, Check, TrendingDown, AlertCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

// Learning goals for path generation
const LEARNING_GOALS = [
  'Master MCP integration',
  'Build reusable skills',
  'Understand agent development',
  'Learn API design patterns',
  'Implement state management',
];

export default function AdaptiveLearningPage() {
  const [showPathForm, setShowPathForm] = useState(false);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  // Get user tier and fetch AI features
  const { data: tier } = useUserTier();
  const { data: aiStatus, isLoading: statusLoading } = useV3AIStatus();
  const { data: analysis, isLoading: analysisLoading, error: analysisError } = useV3KnowledgeAnalysis();
  const { data: recommendation, isLoading: recLoading } = useV3Recommendations();

  // Check if user can access AI features (PREMIUM or PRO tier)
  const canAccessAI = tier && (tier === 'PREMIUM' || tier === 'PRO');

  // Debug logging
  useEffect(() => {
    console.log('Adaptive Learning - User tier:', tier);
    console.log('Adaptive Learning - Can access AI:', canAccessAI);
  }, [tier, canAccessAI]);

  const toggleGoal = (goal: string) => {
    setSelectedGoals(prev =>
      prev.includes(goal)
        ? prev.filter(g => g !== goal)
        : [...prev, goal]
    );
  };

  if (statusLoading || analysisLoading || recLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-[50vh]">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="Adaptive Learning"
        description="AI-powered personalized learning experience tailored to your progress and goals"
      />

      {!canAccessAI ? (
        /* Upgrade Prompt */
        <Card className="mb-8">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-accent-premium" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Premium Feature</h2>
            <p className="text-text-secondary mb-6 max-w-md mx-auto">
              Unlock AI-powered adaptive learning with personalized recommendations and knowledge gap analysis.
            </p>
            <div className="flex justify-center gap-4">
              <Link href="/subscription">
                <Button variant="primary">Upgrade to Premium</Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline">Back to Dashboard</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Knowledge Gap Analysis */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Target className="w-6 h-6 text-cosmic-primary" />
                </div>
                Knowledge Gap Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analysis ? (
                <div className="space-y-6">
                  {/* Weak Topics - Enhanced Visual Design */}
                  {analysis.weak_topics && analysis.weak_topics.length > 0 && (
                    <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 rounded-xl p-5 border border-red-500/30">
                      <h4 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center">
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        </div>
                        Areas That Need Attention
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {analysis.weak_topics.map((topic, i) => (
                          <div
                            key={i}
                            className="flex items-center gap-3 p-3 rounded-lg bg-bg-elevated border border-red-500/20 hover:border-red-500/40 transition-all"
                          >
                            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                            <span className="text-sm font-medium text-text-primary">{topic}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Strong Topics - Enhanced Visual Design */}
                  {analysis.strong_topics && analysis.strong_topics.length > 0 && (
                    <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-xl p-5 border border-emerald-500/30">
                      <h4 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                          <Zap className="w-4 h-4 text-emerald-500" />
                        </div>
                        Your Strengths
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {analysis.strong_topics.map((topic, i) => (
                          <div
                            key={i}
                            className="flex items-center gap-3 p-3 rounded-lg bg-bg-elevated border border-emerald-500/20 hover:border-emerald-500/40 transition-all"
                          >
                            <div className="w-2 h-2 rounded-full bg-emerald-500" />
                            <span className="text-sm font-medium text-text-primary">{topic}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommended Review - Enhanced Visual Design */}
                  {analysis.recommended_review && analysis.recommended_review.length > 0 && (
                    <div className="bg-gradient-to-r from-amber-500/10 to-yellow-500/10 rounded-xl p-5 border border-amber-500/30">
                      <h4 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center">
                          <RotateCcw className="w-4 h-4 text-amber-500" />
                        </div>
                        Recommended Chapters to Review
                      </h4>
                      <div className="space-y-2">
                        {analysis.recommended_review.map((chapterId, i) => (
                          <Link key={i} href={`/chapters/${chapterId}`}>
                            <div className="flex items-center justify-between p-4 rounded-lg bg-bg-elevated border border-amber-500/20 hover:border-amber-500/50 hover:bg-amber-500/5 transition-all cursor-pointer group">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center">
                                  <BookOpen className="w-4 h-4 text-amber-500" />
                                </div>
                                <div>
                                  <span className="text-sm font-medium text-text-primary group-hover:text-amber-500 transition-colors">
                                    Chapter {chapterId}
                                  </span>
                                  <p className="text-xs text-text-muted mt-1">Review recommended based on your quiz performance</p>
                                </div>
                              </div>
                              <div className="w-6 h-6 rounded-full bg-amber-500/20 flex items-center justify-center group-hover:bg-amber-500/30 transition-colors">
                                <ArrowRight className="w-3 h-3 text-amber-500" />
                              </div>
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Explanation - Enhanced Visual Design */}
                  {analysis.explanation && (
                    <div className="bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 rounded-xl p-5 border border-cosmic-primary/30">
                      <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-cosmic-primary/20 flex items-center justify-center">
                          <AlertCircle className="w-4 h-4 text-cosmic-primary" />
                        </div>
                        AI Analysis
                      </h4>
                      <p className="text-sm text-text-secondary leading-relaxed">{analysis.explanation}</p>
                      {analysis.confidence_score !== undefined && (
                        <div className="mt-4 flex items-center gap-2">
                          <div className="flex-1 h-2 bg-bg-elevated rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-cosmic-primary to-cosmic-purple rounded-full transition-all duration-500"
                              style={{ width: `${analysis.confidence_score * 100}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-text-primary">
                            {Math.round(analysis.confidence_score * 100)}% confidence
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                    <Target className="w-8 h-8 text-cosmic-primary" />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary mb-2">Start Your Analysis</h3>
                  <p className="text-text-secondary max-w-md mx-auto mb-6">
                    Take more quizzes to unlock personalized knowledge gap analysis and learning recommendations.
                  </p>
                  <Link href="/quizzes">
                    <Button variant="primary">Take a Quiz</Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Personalized Recommendation */}
          {recommendation && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                    <Compass className="w-6 h-6 text-cosmic-primary" />
                  </div>
                  Recommended Next Chapter
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 rounded-lg p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-text-primary mb-2">
                        {recommendation.next_chapter_title}
                      </h3>
                      <p className="text-text-secondary mb-4">{recommendation.reason}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-text-muted flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {recommendation.estimated_completion_minutes} min
                        </span>
                        <Badge variant="info">{recommendation.difficulty_match}</Badge>
                      </div>
                    </div>
                    <Link href={`/chapters/${recommendation.next_chapter_id}`}>
                      <Button variant="primary" size="lg">
                        Start Learning →
                      </Button>
                    </Link>
                  </div>

                  {/* Alternative Paths */}
                  {recommendation.alternative_paths && recommendation.alternative_paths.length > 0 && (
                    <div className="mt-6 pt-6 border-t border-border-default">
                      <h4 className="text-sm font-semibold text-text-secondary mb-3">
                        Alternative Learning Paths
                      </h4>
                      <div className="space-y-2">
                        {recommendation.alternative_paths.map((alt: any, i: number) => (
                          <Link key={i} href={`/chapters/${alt.chapter_id}`}>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-bg-elevated hover:bg-bg-hover transition-colors cursor-pointer">
                              <span className="text-sm font-medium">{alt.title}</span>
                              <span className="text-xs text-text-muted">{alt.reason}</span>
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Generate Learning Path */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Map className="w-6 h-6 text-cosmic-primary" />
                </div>
                Personalized Learning Path
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!showPathForm ? (
                <div>
                  <p className="text-text-secondary mb-6">
                    Create a customized learning path based on your goals and available time.
                  </p>
                  <Button
                    variant="primary"
                    onClick={() => setShowPathForm(true)}
                  >
                    Generate My Path
                  </Button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Select Goals */}
                  <div>
                    <h4 className="font-semibold text-text-primary mb-3">
                      Select Your Learning Goals
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {LEARNING_GOALS.map(goal => (
                        <button
                          key={goal}
                          onClick={() => toggleGoal(goal)}
                          className={`p-4 rounded-lg border-2 text-left transition-all ${
                            selectedGoals.includes(goal)
                              ? 'border-accent-primary bg-accent-primary/10'
                              : 'border-border-default bg-bg-elevated hover:border-accent-secondary'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                              selectedGoals.includes(goal)
                                ? 'border-accent-primary bg-accent-primary'
                                : 'border-border-default'
                            }`}>
                              {selectedGoals.includes(goal) && (
                                <Check className="w-3 h-3 text-white" />
                              )}
                            </div>
                            <span className="font-medium">{goal}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Time Selection */}
                  <div>
                    <h4 className="font-semibold text-text-primary mb-3">
                      Available Time per Week
                    </h4>
                    <div className="grid grid-cols-4 gap-3">
                      {[2, 5, 10, 20].map(hours => (
                        <button
                          key={hours}
                          className="p-3 rounded-lg border-2 border-border-default bg-bg-elevated hover:border-accent-secondary transition-all"
                        >
                          <div className="text-center">
                            <div className="text-2xl font-bold text-accent-primary">{hours}h</div>
                            <div className="text-xs text-text-muted">/week</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
                    <Button
                      variant="outline"
                      onClick={() => setShowPathForm(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      disabled={selectedGoals.length === 0}
                    >
                      Generate Path
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </PageContainer>
  );
}

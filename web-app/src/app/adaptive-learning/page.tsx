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
import { motion } from 'framer-motion';
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
import { Target, Armchair, RotateCcw, Compass, Clock, Map, BookOpen, Zap, Sparkles, Check, TrendingUp, AlertCircle, ArrowRight, Flame } from 'lucide-react';
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

  const toggleGoal = (goal: string) => {
    setSelectedGoals(prev =>
      prev.includes(goal)
        ? prev.filter(g => g !== goal)
        : [...prev, goal]
    );
  };

  // Show initial loading only for tier check
  if (!tier) {
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
                {analysisLoading && <span className="ml-auto text-sm text-text-muted">Analyzing...</span>}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analysisLoading ? (
                <div className="text-center py-8">
                  <LoadingSpinner size="md" />
                  <p className="text-text-muted mt-3">AI is analyzing your quiz performance...</p>
                </div>
              ) : analysis ? (
                <div className="space-y-6">
                  {/* Weak Topics - Nebula Theme with Animations */}
                  {analysis.weak_topics && analysis.weak_topics.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5 }}
                      className="bg-gradient-to-br from-cosmic-purple/10 via-cosmic-pink/10 to-cosmic-rose/10 rounded-xl p-5 border border-cosmic-purple/30 hover:border-cosmic-purple/50 transition-all duration-300 hover:shadow-lg hover:shadow-cosmic-purple/20"
                    >
                      <h4 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
                        <motion.div
                          className="w-8 h-8 rounded-lg bg-cosmic-purple/20 flex items-center justify-center"
                          whileHover={{ scale: 1.1, rotate: 5 }}
                          transition={{ type: "spring", stiffness: 300 }}
                        >
                          <TrendingUp className="w-4 h-4 text-cosmic-purple" />
                        </motion.div>
                        Areas That Need Attention
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {analysis.weak_topics.map((topic, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            whileHover={{ scale: 1.02, x: 5 }}
                            className="flex items-center gap-3 p-3 rounded-lg bg-bg-elevated border border-cosmic-purple/20 hover:border-cosmic-purple/50 hover:bg-cosmic-purple/5 transition-all cursor-pointer"
                          >
                            <motion.div
                              className="w-2 h-2 rounded-full bg-cosmic-purple"
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                            />
                            <span className="text-sm font-medium text-text-primary">{topic}</span>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Strong Topics - Nebula Theme with Animations */}
                  {analysis.strong_topics && analysis.strong_topics.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                      className="bg-gradient-to-br from-emerald-500/10 via-teal-500/10 to-cosmic-cyan/10 rounded-xl p-5 border border-emerald-500/30 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/20"
                    >
                      <h4 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
                        <motion.div
                          className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center"
                          whileHover={{ scale: 1.1, rotate: -5 }}
                          transition={{ type: "spring", stiffness: 300 }}
                        >
                          <Zap className="w-4 h-4 text-emerald-500" />
                        </motion.div>
                        Your Strengths
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {analysis.strong_topics.map((topic, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 + 0.2 }}
                            whileHover={{ scale: 1.02, x: 5 }}
                            className="flex items-center gap-3 p-3 rounded-lg bg-bg-elevated border border-emerald-500/20 hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all cursor-pointer"
                          >
                            <motion.div
                              className="w-2 h-2 rounded-full bg-emerald-500"
                              animate={{ opacity: [1, 0.5, 1] }}
                              transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                            />
                            <span className="text-sm font-medium text-text-primary">{topic}</span>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Recommended Review - Nebula Theme with Animations */}
                  {analysis.recommended_review && analysis.recommended_review.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.2 }}
                      className="bg-gradient-to-br from-cosmic-blue/10 via-cosmic-cyan/10 to-cosmic-primary/10 rounded-xl p-5 border border-cosmic-blue/30 hover:border-cosmic-blue/50 transition-all duration-300 hover:shadow-lg hover:shadow-cosmic-blue/20"
                    >
                      <h4 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
                        <motion.div
                          className="w-8 h-8 rounded-lg bg-cosmic-blue/20 flex items-center justify-center"
                          whileHover={{ rotate: 180 }}
                          transition={{ type: "spring", stiffness: 200 }}
                        >
                          <RotateCcw className="w-4 h-4 text-cosmic-blue" />
                        </motion.div>
                        Recommended Chapters to Review
                      </h4>
                      <div className="space-y-2">
                        {analysis.recommended_review.map((chapterId, i) => (
                          <Link key={i} href={`/chapters/${chapterId}`}>
                            <motion.div
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: i * 0.1 + 0.3 }}
                              whileHover={{ scale: 1.02, x: 5 }}
                              className="flex items-center justify-between p-4 rounded-lg bg-bg-elevated border border-cosmic-blue/20 hover:border-cosmic-blue/50 hover:bg-cosmic-blue/5 transition-all cursor-pointer group"
                            >
                              <div className="flex items-center gap-3">
                                <motion.div
                                  className="w-8 h-8 rounded-lg bg-cosmic-blue/20 flex items-center justify-center"
                                  whileHover={{ rotate: 360 }}
                                  transition={{ duration: 0.6 }}
                                >
                                  <BookOpen className="w-4 h-4 text-cosmic-blue" />
                                </motion.div>
                                <div>
                                  <span className="text-sm font-medium text-text-primary group-hover:text-cosmic-blue transition-colors">
                                    Chapter {chapterId}
                                  </span>
                                  <p className="text-xs text-text-muted mt-1">Review recommended based on your quiz performance</p>
                                </div>
                              </div>
                              <motion.div
                                className="w-6 h-6 rounded-full bg-cosmic-blue/20 flex items-center justify-center group-hover:bg-cosmic-blue/30 transition-colors"
                                whileHover={{ x: 3 }}
                              >
                                <ArrowRight className="w-3 h-3 text-cosmic-blue" />
                              </motion.div>
                            </motion.div>
                          </Link>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Explanation - Nebula Theme with Animations */}
                  {analysis.explanation && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.3 }}
                      className="bg-gradient-to-br from-cosmic-primary/10 via-cosmic-purple/10 to-cosmic-pink/10 rounded-xl p-5 border border-cosmic-primary/30 hover:border-cosmic-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-cosmic-primary/20"
                    >
                      <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                        <motion.div
                          className="w-8 h-8 rounded-lg bg-cosmic-primary/20 flex items-center justify-center"
                          whileHover={{ scale: 1.1, rotate: 5 }}
                          transition={{ type: "spring", stiffness: 300 }}
                        >
                          <AlertCircle className="w-4 h-4 text-cosmic-primary" />
                        </motion.div>
                        AI Analysis
                      </h4>
                      <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="text-sm text-text-secondary leading-relaxed"
                      >
                        {analysis.explanation}
                      </motion.p>
                      {analysis.confidence_score !== undefined && (
                        <div className="mt-4 flex items-center gap-2">
                          <div className="flex-1 h-2 bg-bg-elevated rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-cosmic-primary via-cosmic-purple to-cosmic-pink rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${analysis.confidence_score * 100}%` }}
                              transition={{ duration: 1, delay: 0.6 }}
                            />
                          </div>
                          <motion.span
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.8 }}
                            className="text-xs font-medium text-text-primary"
                          >
                            {Math.round(analysis.confidence_score * 100)}% confidence
                          </motion.span>
                        </div>
                      )}
                    </motion.div>
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
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Compass className="w-6 h-6 text-cosmic-primary" />
                </div>
                Recommended Next Chapter
                {recLoading && <span className="ml-auto text-sm text-text-muted">Finding best chapter...</span>}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recLoading ? (
                <div className="text-center py-8">
                  <LoadingSpinner size="md" />
                  <p className="text-text-muted mt-3">AI is finding your optimal next chapter...</p>
                </div>
              ) : recommendation ? (
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
              ) : null}
            </CardContent>
          </Card>

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

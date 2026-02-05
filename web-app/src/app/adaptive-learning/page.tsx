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

import { useState } from 'react';
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

  // Fetch AI features
  const { data: aiStatus, isLoading: statusLoading } = useV3AIStatus();
  const { data: analysis, isLoading: analysisLoading, error: analysisError } = useV3KnowledgeAnalysis();
  const { data: recommendation, isLoading: recLoading } = useV3Recommendations();

  // Check if user can access AI features
  const canAccessAI = aiStatus?.llm_enabled && analysisError?.message?.includes('403') !== true;

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
            <div className="text-5xl mb-4">✨</div>
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
                <span className="text-2xl">🎯</span>
                Knowledge Gap Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analysis ? (
                <div className="space-y-6">
                  {/* Weak Topics */}
                  {analysis.weak_topics && analysis.weak_topics.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                        <span className="text-lg">📚</span>
                        Areas to Improve
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.weak_topics.map((topic, i) => (
                          <Badge key={i} variant="warning">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Strong Topics */}
                  {analysis.strong_topics && analysis.strong_topics.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                        <span className="text-lg">💪</span>
                        Your Strengths
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.strong_topics.map((topic, i) => (
                          <Badge key={i} variant="success">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommended Review */}
                  {analysis.recommended_review && analysis.recommended_review.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                        <span className="text-lg">🔄</span>
                        Recommended Review
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.recommended_review.map((chapterId, i) => (
                          <Link key={i} href={`/chapters/${chapterId}`}>
                            <Badge variant="info" className="cursor-pointer hover:opacity-80">
                              Chapter {chapterId}
                            </Badge>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Explanation */}
                  {analysis.explanation && (
                    <div className="bg-bg-elevated rounded-lg p-4 border-l-4 border-accent-primary">
                      <p className="text-sm text-text-secondary">{analysis.explanation}</p>
                      {analysis.confidence_score !== undefined && (
                        <p className="text-xs text-text-muted mt-2">
                          Confidence: {Math.round(analysis.confidence_score * 100)}%
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-text-secondary">
                  Take more quizzes to see your knowledge gap analysis.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Personalized Recommendation */}
          {recommendation && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <span className="text-2xl">🧭</span>
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
                        <span className="text-text-muted">
                          ⏱️ {recommendation.estimated_completion_minutes} min
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
                <span className="text-2xl">🗺️</span>
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
                                <span className="text-white text-xs">✓</span>
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

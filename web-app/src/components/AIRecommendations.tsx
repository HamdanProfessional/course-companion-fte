'use client';

/**
 * AI Recommendations Component - Phase 2 Feature
 *
 * Displays AI-powered recommendations when Phase 2 is enabled:
 * - Personalized chapter recommendations
 * - Knowledge gap analysis
 * - Study guidance
 *
 * Professional/Modern SaaS Theme
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { Bot, AlertTriangle, Target, BookOpen, Zap } from 'lucide-react';
import {
  useChapterRecommendations,
  useKnowledgeAnalysis,
  useIsPhase2Enabled,
  useCanAccessPhase2,
} from '@/hooks';
import Link from 'next/link';

interface AIRecommendationsProps {
  userId: string;
}

export function AIRecommendations({ userId }: AIRecommendationsProps) {
  const { isPhase2Enabled, isLoading: checkingPhase2 } = useIsPhase2Enabled();
  const { canAccess, requiresUpgrade, tier } = useCanAccessPhase2(userId);
  const { data: recommendations, isLoading: loadingRecs, error: recsError } = useChapterRecommendations(userId);
  const { data: analysis, isLoading: loadingAnalysis, error: analysisError } = useKnowledgeAnalysis(userId);

  // Don't render if Phase 2 is not enabled
  if (checkingPhase2) {
    return (
      <Card variant="default">
        <CardContent className="p-6">
          <LoadingSpinner size="sm" />
        </CardContent>
      </Card>
    );
  }

  if (!isPhase2Enabled) {
    return null;
  }

  // Show upgrade prompt for free users
  if (requiresUpgrade && tier) {
    return (
      <Card variant="elevated" className="border-l-4 border-l-accent-warning">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">🔒</span>
            AI-Powered Features
            <Badge variant="premium">Pro</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-text-secondary mb-4">
            Unlock personalized recommendations, knowledge gap analysis, and AI-powered study guidance.
          </p>
          <div className="flex gap-3">
            <Link href="/profile">
              <Button size="md" variant="primary">
                Upgrade to Pro
              </Button>
            </Link>
            <Link href="/chapters">
              <Button size="md" variant="secondary">
                Continue with Free Plan
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show loading state
  if (loadingRecs || loadingAnalysis) {
    return (
      <Card variant="elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
              <Bot className="w-5 h-5 text-cosmic-primary" />
            </div>
            AI-Powered Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LoadingSpinner size="md" />
          <p className="text-sm text-text-secondary mt-4">Analyzing your learning progress...</p>
        </CardContent>
      </Card>
    );
  }

  // Show error state
  if (recsError || analysisError) {
    return (
      <Card variant="default">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-accent-warning">
            <AlertTriangle className="w-6 h-6" />
            AI Recommendations Unavailable
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-text-secondary">
            Unable to load AI recommendations. Phase 2 features may not be enabled on the server.
          </p>
        </CardContent>
      </Card>
    );
  }

  // No recommendations yet
  if (!recommendations) {
    return null;
  }

  return (
    <Card variant="elevated" className="border-l-4 border-l-accent-primary">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
            <Bot className="w-5 h-5 text-cosmic-primary" />
          </div>
          AI-Powered Recommendations
          <Badge variant="premium">Phase 2</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Chapter Recommendation */}
        {recommendations.next_chapter_id && (
          <div className="bg-accent-primary/10 rounded-lg p-4 border border-accent-primary/30">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center flex-shrink-0">
                <BookOpen className="w-7 h-7 text-cosmic-primary" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-text-primary mb-1">Recommended Next Chapter</h4>
                <p className="text-lg font-bold text-accent-primary mb-2">
                  {recommendations.next_chapter_title}
                </p>
                <p className="text-sm text-text-secondary mb-3">
                  {recommendations.reason}
                </p>
                <Link href={`/chapters/${recommendations.next_chapter_id}`}>
                  <Button size="md" variant="primary">
                    Start Learning →
                  </Button>
                </Link>
              </div>
            </div>

            {/* Alternative Paths */}
            {recommendations.alternative_paths && recommendations.alternative_paths.length > 0 && (
              <div className="mt-4 pt-4 border-t border-accent-primary/20">
                <p className="text-xs font-semibold text-text-secondary mb-2">Alternative Paths:</p>
                <div className="space-y-2">
                  {recommendations.alternative_paths.map((alt, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="text-text-primary">{alt.title}</span>
                      <span className="text-xs text-text-muted">{alt.reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Knowledge Gap Analysis */}
        {analysis && analysis.weak_topics && analysis.weak_topics.length > 0 && (
          <div className="bg-accent-warning/10 rounded-lg p-4 border border-accent-warning/30">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center flex-shrink-0">
                <Target className="w-6 h-6 text-accent-warning" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-text-primary mb-2">Focus Areas</h4>
                <p className="text-sm text-text-secondary mb-3">
                  Based on your quiz performance, consider reviewing:
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysis.weak_topics.map((topic, index) => (
                    <Badge key={index} variant="warning">
                      {topic}
                    </Badge>
                  ))}
                </div>
                {analysis.explanation && (
                  <p className="text-xs text-text-muted mt-3 italic">
                    💡 {analysis.explanation}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Strengths */}
        {analysis && analysis.strong_topics && analysis.strong_topics.length > 0 && (
          <div className="bg-accent-success/10 rounded-lg p-4 border border-accent-success/30">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center flex-shrink-0">
                <Zap className="w-6 h-6 text-accent-success" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-text-primary mb-2">Your Strengths</h4>
                <div className="flex flex-wrap gap-2">
                  {analysis.strong_topics.map((topic, index) => (
                    <Badge key={index} variant="success">
                      ✓ {topic}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Difficulty Match */}
        {recommendations.difficulty_match && (
          <div className="flex items-center justify-between text-xs text-text-muted pt-2 border-t border-border-default">
            <span>Difficulty Match:</span>
            <Badge variant="info">{recommendations.difficulty_match}</Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

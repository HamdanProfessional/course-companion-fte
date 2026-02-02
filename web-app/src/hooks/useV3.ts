/**
 * Custom hooks for Phase 3 Unified API v3.
 * Using the new tutorApi client with LLM features enabled.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import tutorApi, * as V3Types from '@/lib/api-v3';

// Default demo user ID (from database)
const DEFAULT_USER_ID = '82b8b862-059a-416a-9ef4-e582a4870efa';

// ============================================================================
// Content Hooks
// ============================================================================

/**
 * Hook for fetching chapters with completion status (v3)
 */
export function useV3Chapters() {
  return useQuery({
    queryKey: ['v3', 'chapters'],
    queryFn: () => tutorApi.getChapters(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for fetching chapter content (v3)
 */
export function useV3Chapter(chapterId: string) {
  return useQuery({
    queryKey: ['v3', 'chapter', chapterId],
    queryFn: () => tutorApi.getChapter(chapterId),
    enabled: !!chapterId,
  });
}

/**
 * Hook for fetching chapter navigation (v3)
 */
export function useV3Navigation(chapterId: string) {
  return useQuery({
    queryKey: ['v3', 'navigation', chapterId],
    queryFn: () => tutorApi.getNavigation(chapterId),
    enabled: !!chapterId,
  });
}

/**
 * Hook for "continue learning" (v3)
 */
export function useV3ContinueLearning() {
  return useQuery({
    queryKey: ['v3', 'continue-learning'],
    queryFn: () => tutorApi.getContinueLearning(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for content search (v3)
 */
export function useV3Search(query: string, limit = 10) {
  return useQuery({
    queryKey: ['v3', 'search', query, limit],
    queryFn: () => tutorApi.search(query, limit),
    enabled: !!query && query.length >= 2,
  });
}

// ============================================================================
// Quiz Hooks (v3)
// ============================================================================

/**
 * Hook for getting quiz by chapter (v3)
 */
export function useV3QuizByChapter(chapterId: string) {
  return useQuery({
    queryKey: ['v3', 'quiz', 'chapter', chapterId],
    queryFn: () => tutorApi.getQuizByChapter(chapterId),
    enabled: !!chapterId,
  });
}

/**
 * Hook for submitting quiz (v3)
 */
export function useV3QuizSubmit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ quizId, submission }: { quizId: string; submission: V3Types.QuizSubmission }) =>
      tutorApi.submitQuiz(quizId, submission),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['v3', 'progress'] });
      queryClient.invalidateQueries({ queryKey: ['v3', 'quiz-history'] });
    },
  });
}

/**
 * Hook for quiz insights (v3)
 */
export function useV3QuizInsights(quizId: string) {
  return useQuery({
    queryKey: ['v3', 'quiz', 'insights', quizId],
    queryFn: () => tutorApi.getQuizInsights(quizId),
    enabled: !!quizId,
  });
}

/**
 * Hook for quiz history (v3)
 */
export function useV3QuizHistory(quizId: string, limit = 10) {
  return useQuery({
    queryKey: ['v3', 'quiz', 'history', quizId, limit],
    queryFn: () => tutorApi.getQuizHistory(quizId, limit),
    enabled: !!quizId,
  });
}

// ============================================================================
// Progress Hooks (v3)
// ============================================================================

/**
 * Hook for progress summary (v3)
 */
export function useV3ProgressSummary() {
  return useQuery({
    queryKey: ['v3', 'progress', 'summary'],
    queryFn: () => tutorApi.getProgressSummary(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for chapters progress (v3)
 */
export function useV3ChaptersProgress() {
  return useQuery({
    queryKey: ['v3', 'progress', 'chapters'],
    queryFn: () => tutorApi.getChaptersProgress(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for updating progress (v3)
 */
export function useV3UpdateProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ chapterId, quizScore }: { chapterId: string; quizScore?: number }) =>
      tutorApi.updateProgress(chapterId, quizScore),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['v3', 'progress'] });
      queryClient.invalidateQueries({ queryKey: ['v3', 'chapters'] });
    },
  });
}

/**
 * Hook for streak calendar (v3)
 */
export function useV3StreakCalendar(year?: number, month?: number) {
  return useQuery({
    queryKey: ['v3', 'streak', 'calendar', year, month],
    queryFn: () => tutorApi.getStreakCalendar(year, month),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for score history (v3)
 */
export function useV3ScoreHistory(limit = 30) {
  return useQuery({
    queryKey: ['v3', 'score-history', limit],
    queryFn: () => tutorApi.getScoreHistory(limit),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for achievements (v3)
 */
export function useV3Achievements() {
  return useQuery({
    queryKey: ['v3', 'achievements'],
    queryFn: () => tutorApi.getAchievements(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for daily checkin (v3)
 */
export function useV3DailyCheckin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => tutorApi.dailyCheckin(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['v3', 'progress'] });
      queryClient.invalidateQueries({ queryKey: ['v3', 'streak'] });
      queryClient.invalidateQueries({ queryKey: ['v3', 'achievements'] });
    },
  });
}

// ============================================================================
// AI Features Hooks (v3)
// ============================================================================

/**
 * Hook for AI status (v3)
 */
export function useV3AIStatus() {
  return useQuery({
    queryKey: ['v3', 'ai', 'status'],
    queryFn: () => tutorApi.getAIStatus(),
  });
}

/**
 * Hook for knowledge analysis (v3)
 */
export function useV3KnowledgeAnalysis() {
  return useQuery({
    queryKey: ['v3', 'ai', 'knowledge-analysis'],
    queryFn: () => tutorApi.getKnowledgeAnalysis(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for chapter recommendations (v3)
 */
export function useV3Recommendations() {
  return useQuery({
    queryKey: ['v3', 'ai', 'recommendations'],
    queryFn: () => tutorApi.getRecommendations(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for mentor chat (v3)
 */
export function useV3MentorChat() {
  return useMutation({
    mutationFn: (request: V3Types.MentorChatRequest) => tutorApi.mentorChat(request),
  });
}

/**
 * Hook for topic explanation (v3)
 */
export function useV3ExplainTopic() {
  return useMutation({
    mutationFn: (request: V3Types.ContentExplanationRequest) => tutorApi.explainTopic(request),
  });
}

/**
 * Hook for LLM quiz grading (v3)
 */
export function useV3LLMGrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ quizId, answers }: { quizId: string; answers: Record<string, any> }) =>
      tutorApi.gradeQuizWithAI(quizId, answers),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['v3', 'progress'] });
    },
  });
}

/**
 * Hook for LLM usage costs (v3) - Pro only
 */
export function useV3LLMCosts() {
  return useQuery({
    queryKey: ['v3', 'ai', 'costs'],
    queryFn: () => tutorApi.getLLMUsageCosts(),
    enabled: typeof window !== 'undefined',
    retry: false,
  });
}

// ============================================================================
// Access & Subscription Hooks (v3)
// ============================================================================

/**
 * Hook for subscription plans (v3)
 */
export function useV3SubscriptionPlans() {
  return useQuery({
    queryKey: ['v3', 'access', 'plans'],
    queryFn: () => tutorApi.listSubscriptionPlans(),
  });
}

/**
 * Hook for subscription info (v3)
 */
export function useV3SubscriptionInfo() {
  return useQuery({
    queryKey: ['v3', 'access', 'subscription'],
    queryFn: () => tutorApi.getSubscriptionInfo(),
    enabled: typeof window !== 'undefined',
  });
}

/**
 * Hook for access check (v3)
 */
export function useV3CheckAccess(resource: string) {
  return useQuery({
    queryKey: ['v3', 'access', 'check', resource],
    queryFn: () => tutorApi.checkAccess(resource),
    enabled: !!resource,
  });
}

/**
 * Hook for upgrading tier (v3)
 */
export function useV3UpgradeTier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      newTier,
      paymentMethodId,
      billingCycle,
    }: {
      newTier: 'PREMIUM' | 'PRO';
      paymentMethodId?: string;
      billingCycle?: 'monthly' | 'yearly';
    }) => tutorApi.upgradeTier(newTier, paymentMethodId, billingCycle),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['v3', 'access'] });
      queryClient.invalidateQueries({ queryKey: ['userTier'] });
    },
  });
}

/**
 * Hook for data export (v3)
 */
export function useV3DataExport() {
  return useMutation({
    mutationFn: (options?: {
      include_progress?: boolean;
      include_quiz_history?: boolean;
      include_streaks?: boolean;
      format?: 'json' | 'csv' | 'pdf';
    }) => tutorApi.requestDataExport(options),
  });
}

// Export all types
export * from '@/lib/api-v3';

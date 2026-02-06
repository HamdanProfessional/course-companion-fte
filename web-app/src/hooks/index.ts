/**
 * Custom hooks for Course Companion FTE.
 * Using React Query for server state and Zustand for client state.
 */

import { useQuery } from '@tanstack/react-query';
import { backendApi, type Chapter, type Quiz, type Progress, type Streak } from '@/lib/api';
import { getCurrentUser } from '@/lib/auth';
import { useIsPhase2Enabled } from './usePhase2';

// Export backendApi for use in components
export { backendApi };
export type { Chapter, Quiz, Progress, Streak };

/**
 * Helper function to get current user ID from localStorage
 * Returns null if user is not logged in
 */
function getCurrentUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('user_id');
}

/**
 * Hook for fetching chapters.
 */
export function useChapters() {
  return useQuery({
    queryKey: ['chapters'],
    queryFn: () => backendApi.getChapters(),
    enabled: typeof window !== 'undefined', // Only run on client
  });
}

/**
 * Hook for fetching a single chapter.
 */
export function useChapter(chapterId: string) {
  return useQuery({
    queryKey: ['chapter', chapterId],
    queryFn: () => backendApi.getChapter(chapterId),
    enabled: !!chapterId,
  });
}

/**
 * Hook for fetching quizzes.
 */
export function useQuizzes() {
  return useQuery({
    queryKey: ['quizzes'],
    queryFn: () => backendApi.getQuizzes(),
  });
}

/**
 * Hook for fetching a single quiz.
 */
export function useQuiz(quizId: string) {
  return useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => backendApi.getQuiz(quizId),
    enabled: !!quizId,
  });
}

/**
 * Hook for fetching user progress.
 * Uses provided userId or falls back to logged-in user from localStorage.
 */
export function useProgress(userId?: string) {
  const id = userId || getCurrentUserId();

  return useQuery({
    queryKey: ['progress', id],
    queryFn: () => backendApi.getProgress(id!),
    enabled: !!id && typeof window !== 'undefined', // Only run on client
  });
}

/**
 * Hook for fetching user streak.
 * Uses provided userId or falls back to logged-in user from localStorage.
 */
export function useStreak(userId?: string) {
  const id = userId || getCurrentUserId();

  return useQuery({
    queryKey: ['streak', id],
    queryFn: () => backendApi.getStreak(id!),
    enabled: !!id && typeof window !== 'undefined', // Only run on client
  });
}

/**
 * Hook for getting current user.
 */
export function useAuth() {
  return useQuery({
    queryKey: ['user'],
    queryFn: getCurrentUser,
  });
}

/**
 * Hook for fetching user tier.
 * Uses provided userId or falls back to logged-in user from localStorage.
 * Note: Disabled during SSR to prevent server-side fetch issues.
 */
export function useUserTier(userId?: string) {
  const id = userId || getCurrentUserId();

  return useQuery({
    queryKey: ['userTier', id],
    queryFn: async () => {
      if (!id) return 'FREE';

      // First, check localStorage for immediate tier (updated by upgrade flow)
      const localTier = localStorage.getItem('user_tier');
      if (localTier && ['FREE', 'PREMIUM', 'PRO'].includes(localTier)) {
        console.log('useUserTier: Using tier from localStorage:', localTier);
        return localTier;
      }

      // Fall back to API if not in localStorage
      try {
        const response = await backendApi.getUserTier(id);
        console.log('useUserTier: Fetched tier from API:', response.tier);
        return response.tier;
      } catch (error) {
        // Return default tier if request fails
        console.error('Failed to fetch user tier:', error);
        return 'FREE';
      }
    },
    enabled: !!id && typeof window !== 'undefined', // Only run on client
    retry: 1,
    staleTime: 0, // Always fetch fresh data to avoid stale cache
  });
}

/**
 * Hook to check if user can access Phase 2 features.
 * Phase 2 requires PREMIUM or PRO tier.
 */
export function useCanAccessPhase2(userId?: string) {
  const { data: tier, isLoading } = useUserTier(userId);
  const { isPhase2Enabled } = useIsPhase2Enabled();

  return {
    canAccess: tier === 'PREMIUM' || tier === 'PRO',
    tier,
    isPhase2Enabled,
    requiresUpgrade: tier === 'FREE',
    isLoading,
  };
}

// Phase 2 LLM-Powered Hooks
export {
  useKnowledgeAnalysis,
  useChapterRecommendations,
  useLearningPath,
  useMentorAsk,
  useStudyGuidance,
  usePracticeProblems,
  useLLMQuizSubmit,
  useQuizInsights,
  usePhase2Status,
  useIsPhase2Enabled,
} from './usePhase2';

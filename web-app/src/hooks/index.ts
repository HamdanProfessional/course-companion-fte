/**
 * Custom hooks for Course Companion FTE.
 * Using React Query for server state and Zustand for client state.
 */

import { useQuery } from '@tanstack/react-query';
import { backendApi, type Chapter, type Quiz, type Progress, type Streak } from '@/lib/api';
import { getCurrentUser } from '@/lib/auth';

/**
 * Hook for fetching chapters.
 */
export function useChapters() {
  return useQuery({
    queryKey: ['chapters'],
    queryFn: () => backendApi.getChapters(),
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
 */
export function useProgress(userId?: string) {
  const id = userId || '00000000-0000-0000-0000-000000000001';
  return useQuery({
    queryKey: ['progress', id],
    queryFn: () => backendApi.getProgress(id),
    enabled: !!id,
  });
}

/**
 * Hook for fetching user streak.
 */
export function useStreak(userId?: string) {
  const id = userId || '00000000-0000-0000-0000-000000000001';
  return useQuery({
    queryKey: ['streak', id],
    queryFn: () => backendApi.getStreak(id),
    enabled: !!id,
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

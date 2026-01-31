/**
 * React hooks for Phase 2 LLM-powered features.
 *
 * These hooks connect to the Phase 2 API endpoints:
 * - Adaptive Learning
 * - AI Mentor
 * - LLM Quiz Grading
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://92.113.147.250:8180';

// Types
interface KnowledgeGapAnalysis {
  weak_topics: string[];
  strong_topics: string[];
  recommended_review: string[];
  confidence_score: number;
  explanation: string;
}

interface ChapterRecommendation {
  next_chapter_id: string;
  next_chapter_title: string;
  reason: string;
  alternative_paths: Array<{
    id: string;
    title: string;
    reason: string;
  }>;
  estimated_completion_minutes: number;
  difficulty_match: string;
}

interface LearningPathRequest {
  user_id: string;
  learning_goals: string[];
  available_time_hours: number;
}

interface LearningPath {
  path: Array<{
    chapter_id: string;
    title: string;
    order: number;
    estimated_minutes: number;
    reason: string;
  }>;
  milestones: Array<{
    week: number;
    chapters: string[];
    goal: string;
    total_hours: number;
  }>;
  total_hours: number;
  rationale: string;
}

interface MentorQuestion {
  question: string;
  context?: {
    current_chapter?: string;
    recent_quiz_scores?: number[];
  };
}

interface MentorResponse {
  answer: string;
  related_chapters: Array<{
    id: string;
    title: string;
    reason: string;
  }>;
  practice_problems: Array<{
    topic: string;
    difficulty: string;
    description: string;
  }>;
  follow_up_questions: string[];
  confidence: number;
}

interface StudyGuidance {
  learning_pace: string;
  strengths: string[];
  areas_for_improvement: string[];
  recommended_focus: string[];
  study_tips: string[];
  estimated_completion_weeks: number;
}

interface PracticeProblemsRequest {
  topic: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  count: number;
}

interface PracticeProblem {
  title: string;
  description: string;
  difficulty: string;
  estimated_minutes: number;
  hints: string[];
  solution_approach: string;
  learning_outcome: string;
}

interface LLMQuizSubmission {
  answers: Record<string, string>;
}

interface LLMQuizResult {
  quiz_id: string;
  total_score: number;
  max_score: number;
  percentage: number;
  passed: boolean;
  multiple_choice_results: Record<string, {
    question: string;
    user_answer: string;
    correct_answer: string;
    is_correct: boolean;
    points_earned: number;
    explanation: string;
  }>;
  llm_graded_results: Array<{
    question_id: string;
    score: number;
    max_score: number;
    feedback: string;
    corrections: string[];
    strengths: string[];
    suggestions: string[];
  }>;
  summary: string;
  graded_by: string;
}

// =============================================================================
// Adaptive Learning Hooks
// =============================================================================

/**
 * Fetch knowledge gap analysis from quiz performance
 */
export function useKnowledgeAnalysis(userId: string | undefined) {
  return useQuery({
    queryKey: ['adaptive', 'knowledge-analysis', userId],
    queryFn: async (): Promise<KnowledgeGapAnalysis> => {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/adaptive/analysis?user_id=${userId}`
      );

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to fetch knowledge analysis');
      }

      return response.json();
    },
    enabled: !!userId && typeof window !== 'undefined',
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}

/**
 * Fetch personalized chapter recommendations
 */
export function useChapterRecommendations(userId: string | undefined) {
  return useQuery({
    queryKey: ['adaptive', 'recommendations', userId],
    queryFn: async (): Promise<ChapterRecommendation> => {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/adaptive/recommendations?user_id=${userId}`
      );

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to fetch recommendations');
      }

      return response.json();
    },
    enabled: !!userId && typeof window !== 'undefined',
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  });
}

/**
 * Generate personalized learning path
 */
export function useLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: LearningPathRequest): Promise<LearningPath> => {
      const response = await fetch(`${BACKEND_URL}/api/v1/adaptive/path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to generate learning path');
      }

      return response.json();
    },
    onSuccess: (data, variables) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['adaptive'] });
    },
  });
}

// =============================================================================
// AI Mentor Hooks
// =============================================================================

/**
 * Ask AI mentor a question
 */
export function useMentorAsk() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, question, context }: {
      userId: string;
      question: string;
      context?: MentorQuestion['context'];
    }): Promise<MentorResponse> => {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/mentor/ask?user_id=${userId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, context }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to ask mentor');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['mentor'] });
    },
  });
}

/**
 * Fetch personalized study guidance
 */
export function useStudyGuidance(userId: string | undefined) {
  return useQuery({
    queryKey: ['mentor', 'guidance', userId],
    queryFn: async (): Promise<StudyGuidance> => {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/mentor/guidance?user_id=${userId}`
      );

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to fetch study guidance');
      }

      return response.json();
    },
    enabled: !!userId && typeof window !== 'undefined',
    staleTime: 60 * 60 * 1000, // 1 hour
    retry: 1,
  });
}

/**
 * Generate practice problems
 */
export function usePracticeProblems() {
  return useMutation({
    mutationFn: async (request: PracticeProblemsRequest): Promise<{
      problems: PracticeProblem[];
      topic: string;
      count: number;
    }> => {
      const response = await fetch(`${BACKEND_URL}/api/v1/mentor/practice-problems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to generate practice problems');
      }

      return response.json();
    },
  });
}

// =============================================================================
// LLM Quiz Hooks
// =============================================================================

/**
 * Submit quiz for LLM grading
 */
export function useLLMQuizSubmit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      quizId,
      userId,
      answers
    }: {
      quizId: string;
      userId: string;
      answers: LLMQuizSubmission['answers'];
    }): Promise<LLMQuizResult> => {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/quizzes/${quizId}/grade-llm?user_id=${userId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ answers }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to submit quiz');
      }

      return response.json();
    },
    onSuccess: (data, variables) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['quiz', variables.quizId] });
      queryClient.invalidateQueries({ queryKey: ['progress', variables.userId] });
    },
  });
}

/**
 * Fetch quiz performance insights
 */
export function useQuizInsights(quizId: string | undefined, userId: string | undefined) {
  return useQuery({
    queryKey: ['quiz', 'insights', quizId, userId],
    queryFn: async (): Promise<StudyGuidance> => {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/quizzes/${quizId}/insights?user_id=${userId}`
      );

      if (!response.ok) {
        const error = await response.json();
        if (response.status === 503 && !error.phase_2_enabled) {
          throw new Error('Phase 2 features are not enabled');
        }
        throw new Error(error.detail || 'Failed to fetch quiz insights');
      }

      return response.json();
    },
    enabled: !!quizId && !!userId && typeof window !== 'undefined',
    staleTime: 30 * 60 * 1000, // 30 minutes
    retry: 1,
  });
}

// =============================================================================
// Phase 2 Status Hook
// =============================================================================

/**
 * Check if Phase 2 features are enabled
 */
export function usePhase2Status() {
  return useQuery({
    queryKey: ['phase2', 'status'],
    queryFn: async () => {
      const response = await fetch(`${BACKEND_URL}/api/v1/adaptive/status`);
      if (!response.ok) {
        throw new Error('Failed to check Phase 2 status');
      }
      return response.json();
    },
    staleTime: 15 * 60 * 1000, // 15 minutes
    retry: false,
  });
}

/**
 * Hook that returns whether Phase 2 is enabled and ready to use
 */
export function useIsPhase2Enabled() {
  const { data, isLoading, error } = usePhase2Status();

  return {
    isPhase2Enabled: data?.phase_2_enabled || false,
    llmProvider: data?.llm_provider || null,
    isLoading,
    error,
  };
}

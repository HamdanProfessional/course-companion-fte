/**
 * Teacher Dashboard Hooks
 *
 * Hooks for fetching teacher-specific data including:
 * - Analytics and statistics
 * - Student lists and progress
 * - Quiz performance data
 * - Engagement metrics
 */

import { useQuery } from '@tanstack/react-query';
import tutorApi from '@/lib/api-v3';

// =============================================================================
// Types
// =============================================================================

export interface TeacherStats {
  total_students: number;
  active_students: number;
  average_score: number;
  completion_rate: number;
  students_at_risk: number;
  students_failing_quizzes: number;
  students_with_stale_streaks: number;
}

export interface TeacherStudent {
  user_id: string;
  name: string;
  email: string;
  progress: number;
  streak: number;
  last_activity: string;
  tier: 'FREE' | 'PRO' | 'PREMIUM';
  quiz_scores?: number[];
  completed_chapters?: number;
  total_chapters?: number;
  joined_date?: string;
}

export interface QuizStats {
  total_attempts: number;
  average_score: number;
  pass_rate: number;
  completion_rate: number;
}

export interface QuizPerformance {
  quiz_id: string;
  quiz_title: string;
  total_attempts: number;
  average_score: number;
  highest_score: number;
  lowest_score: number;
  pass_rate: number;
}

export interface QuestionAnalysis {
  question_id: string;
  question_text: string;
  total_attempts: number;
  correct_rate: number;
  average_time: number;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface EngagementMetrics {
  average_session_time: string;
  active_students: number;
  completion_rate: number;
  weekly_activity: number[];
}

export interface AtRiskStudent {
  user_id: string;
  name: string;
  email: string;
  risk_level: 'high' | 'medium' | 'low';
  risk_factors: string[];
  last_activity: string;
  progress: number;
  streak: number;
}

export interface RecentActivity {
  activity_id: string;
  student_name: string;
  activity_type: 'quiz_completed' | 'chapter_completed' | 'streak_achieved' | 'login';
  description: string;
  timestamp: string;
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * Fetch teacher dashboard statistics
 * GET /api/v3/tutor/teacher/analytics
 */
export function useTeacherAnalytics() {
  return useQuery({
    queryKey: ['teacher', 'analytics'],
    queryFn: async () => {
      const response = await tutorApi.request<TeacherStats>('/api/v3/tutor/teacher/analytics');
      return response;
    },
  });
}

/**
 * Fetch list of all students with their progress
 * GET /api/v3/tutor/teacher/students
 */
export function useTeacherStudents() {
  return useQuery({
    queryKey: ['teacher', 'students'],
    queryFn: async () => {
      const response = await tutorApi.request<TeacherStudent[]>('/api/v3/tutor/teacher/students');
      return response;
    },
  });
}

/**
 * Fetch quiz statistics and performance
 * GET /api/v3/tutor/teacher/analytics/quiz-stats
 * GET /api/v3/tutor/teacher/analytics/quiz-performance
 * GET /api/v3/tutor/teacher/analytics/question-analysis
 */
export function useTeacherQuizAnalytics() {
  const quizStats = useQuery({
    queryKey: ['teacher', 'quiz-stats'],
    queryFn: async () => {
      const response = await tutorApi.request<QuizStats>('/api/v3/tutor/teacher/analytics/quiz-stats');
      return response;
    },
  });

  const quizPerformance = useQuery({
    queryKey: ['teacher', 'quiz-performance'],
    queryFn: async () => {
      const response = await tutorApi.request<QuizPerformance[]>('/api/v3/tutor/teacher/analytics/quiz-performance');
      return response;
    },
  });

  const questionAnalysis = useQuery({
    queryKey: ['teacher', 'question-analysis'],
    queryFn: async () => {
      const response = await tutorApi.request<QuestionAnalysis[]>('/api/v3/tutor/teacher/analytics/question-analysis');
      return response;
    },
  });

  return {
    quizStats: quizStats.data,
    quizPerformance: quizPerformance.data,
    questionAnalysis: questionAnalysis.data,
    isLoading: quizStats.isLoading || quizPerformance.isLoading || questionAnalysis.isLoading,
    error: quizStats.error || quizPerformance.error || questionAnalysis.error,
    refetch: () => Promise.all([quizStats.refetch(), quizPerformance.refetch(), questionAnalysis.refetch()]),
  };
}

/**
 * Fetch engagement metrics
 * GET /api/v3/tutor/teacher/engagement/metrics
 */
export function useTeacherEngagement() {
  const metrics = useQuery({
    queryKey: ['teacher', 'engagement-metrics'],
    queryFn: async () => {
      const response = await tutorApi.request<EngagementMetrics>('/api/v3/tutor/teacher/engagement/metrics');
      return response;
    },
  });

  const atRiskStudents = useQuery({
    queryKey: ['teacher', 'at-risk-students'],
    queryFn: async () => {
      const response = await tutorApi.request<AtRiskStudent[]>('/api/v3/tutor/teacher/engagement/at-risk');
      return response;
    },
  });

  const recentActivity = useQuery({
    queryKey: ['teacher', 'recent-activity'],
    queryFn: async () => {
      const response = await tutorApi.request<RecentActivity[]>('/api/v3/tutor/teacher/engagement/activity-feed');
      return response;
    },
  });

  return {
    metrics: metrics.data,
    atRiskStudents: atRiskStudents.data,
    recentActivity: recentActivity.data,
    isLoading: metrics.isLoading || atRiskStudents.isLoading || recentActivity.isLoading,
    error: metrics.error || atRiskStudents.error || recentActivity.error,
    refetch: () => Promise.all([metrics.refetch(), atRiskStudents.refetch(), recentActivity.refetch()]),
  };
}

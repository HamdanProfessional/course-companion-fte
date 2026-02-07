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
      // TODO: Replace with actual API call when endpoint is ready
      // const response = await tutorApi.get<TeacherStats>('/teacher/analytics');
      // return response.data;

      // Temporary placeholder data
      return {
        total_students: 0,
        active_students: 0,
        average_score: 0,
        completion_rate: 0,
        students_at_risk: 0,
        students_failing_quizzes: 0,
        students_with_stale_streaks: 0,
      } as TeacherStats;
    },
    enabled: false, // Disabled until backend endpoint is ready
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
      // TODO: Replace with actual API call when endpoint is ready
      // const response = await tutorApi.get<TeacherStudent[]>('/teacher/students');
      // return response.data;

      return [] as TeacherStudent[];
    },
    enabled: false, // Disabled until backend endpoint is ready
  });
}

/**
 * Fetch quiz statistics and performance
 * GET /api/v3/tutor/teacher/analytics/quiz-stats
 * GET /api/v3/tutor/teacher/analytics/quiz-performance
 */
export function useTeacherQuizAnalytics() {
  const quizStats = useQuery({
    queryKey: ['teacher', 'quiz-stats'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // const response = await tutorApi.get<QuizStats>('/teacher/analytics/quiz-stats');
      // return response.data;

      return {
        total_attempts: 0,
        average_score: 0,
        pass_rate: 0,
        completion_rate: 0,
      } as QuizStats;
    },
    enabled: false,
  });

  const quizPerformance = useQuery({
    queryKey: ['teacher', 'quiz-performance'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // const response = await tutorApi.get<QuizPerformance[]>('/teacher/analytics/quiz-performance');
      // return response.data;

      return [] as QuizPerformance[];
    },
    enabled: false,
  });

  return {
    quizStats: quizStats.data,
    quizPerformance: quizPerformance.data,
    isLoading: quizStats.isLoading || quizPerformance.isLoading,
    error: quizStats.error || quizPerformance.error,
    refetch: () => Promise.all([quizStats.refetch(), quizPerformance.refetch()]),
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
      // TODO: Replace with actual API call
      // const response = await tutorApi.get<EngagementMetrics>('/teacher/engagement/metrics');
      // return response.data;

      return {
        average_session_time: '0 min',
        active_students: 0,
        completion_rate: 0,
        weekly_activity: [],
      } as EngagementMetrics;
    },
    enabled: false,
  });

  const atRiskStudents = useQuery({
    queryKey: ['teacher', 'at-risk-students'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // const response = await tutorApi.get<AtRiskStudent[]>('/teacher/engagement/at-risk');
      // return response.data;

      return [] as AtRiskStudent[];
    },
    enabled: false,
  });

  const recentActivity = useQuery({
    queryKey: ['teacher', 'recent-activity'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // const response = await tutorApi.get<RecentActivity[]>('/teacher/engagement/activity-feed');
      // return response.data;

      return [] as RecentActivity[];
    },
    enabled: false,
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

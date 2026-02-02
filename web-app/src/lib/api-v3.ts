/**
 * API v3 Client - Phase 3 Unified Tutor API
 *
 * This client provides access to the unified Phase 3 API with:
 * - Single endpoint structure: /api/v3/tutor/
 * - LLM features enabled by default
 * - Enhanced gamification and analytics
 * - Subscription management
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

export interface ChapterListItem {
  id: string;
  title: string;
  order: number;
  difficulty_level: string;
  estimated_time: number;
  completed: boolean;
  quiz_id: string | null;
}

export interface ChapterContent {
  id: string;
  title: string;
  order: number;
  difficulty_level: string;
  estimated_time: number;
  content: string | null;
  summary: string | null;
  quiz_id: string | null;
  completed: boolean;
}

export interface ChapterNavigation {
  current: ChapterListItem | null;
  previous: ChapterListItem | null;
  next: ChapterListItem | null;
  can_continue: boolean;
}

export interface ChapterListResponse {
  chapters: ChapterListItem[];
  total: number;
  completion_percentage: number;
}

export interface QuestionItem {
  id: string;
  question_text: string;
  options: Record<string, string>;
  order: number;
  type: 'multiple_choice' | 'open_ended';
}

export interface QuizDetail {
  id: string;
  chapter_id: string;
  title: string;
  difficulty: string;
  questions: QuestionItem[];
  total_questions: number;
  passing_score: number;
}

export interface QuizSubmission {
  answers: Record<string, any>;
  grading_mode: 'auto' | 'llm' | 'hybrid';
}

export interface QuestionResult {
  question_id: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string | null;
  is_correct: boolean | null;
  points_earned: number;
  max_points: number;
  explanation: string | null;
  feedback: string | null;
}

export interface QuizGradingResult {
  quiz_id: string;
  attempt_id: string;
  total_score: number;
  max_score: number;
  percentage: number;
  passed: boolean;
  grading_mode: string;
  results: QuestionResult[];
  summary: string;
  completed_at: string;
}

export interface ProgressSummary {
  user_id: string;
  completion_percentage: number;
  completed_chapters: string[];
  total_chapters: number;
  current_chapter_id: string | null;
  last_activity: string;
  total_quizzes_taken: number;
  average_score: number;
  current_streak: number;
  longest_streak: number;
  total_achievements: number;
  unlocked_achievements: number;
}

export interface ChapterProgress {
  chapter_id: string;
  chapter_title: string;
  chapter_order: number;
  completed: boolean;
  completed_at: string | null;
  quiz_taken: boolean;
  best_quiz_score: number | null;
}

export interface AchievementItem {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked_at: string | null;
  progress: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface StreakDay {
  date: string;
  active: boolean;
  streak_day: number | null;
}

export interface StreakCalendar {
  year: number;
  month: number;
  days: StreakDay[];
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
}

export interface ScoreHistoryItem {
  date: string;
  quiz_id: string;
  quiz_title: string;
  score: number;
  passed: boolean;
}

export interface MentorMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface MentorChatRequest {
  question: string;
  chapter_context?: string;
  conversation_history?: MentorMessage[];
}

export interface MentorChatResponse {
  answer: string;
  follow_up_questions: string[];
  related_chapters: string[];
  confidence: number;
}

export interface AdaptiveAnalysis {
  weak_topics: string[];
  strong_topics: string[];
  recommended_review: string[];
  confidence_score: number;
  explanation: string;
}

export interface ChapterRecommendation {
  next_chapter_id: string;
  next_chapter_title: string;
  reason: string;
  alternative_paths: Record<string, any>[];
  estimated_completion_minutes: number;
  difficulty_match: string;
}

export interface ContentExplanationRequest {
  chapter_id: string;
  topic: string;
  complexity_level: 'beginner' | 'intermediate' | 'advanced';
  include_examples: boolean;
}

export interface ContentExplanationResponse {
  explanation: string;
  examples: string[];
  analogies: string[];
  key_points: string[];
  difficulty_level: string;
}

export interface SubscriptionPlan {
  tier: 'FREE' | 'PREMIUM' | 'PRO';
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  limits: Record<string, any>;
}

export interface SubscriptionInfo {
  user_id: string;
  current_tier: 'FREE' | 'PREMIUM' | 'PRO';
  tier_name: string;
  subscribed_at: string | null;
  subscription_status: string;
  next_billing_date: string | null;
  cancel_at_period_end: boolean;
}

export interface AccessCheckResponse {
  has_access: boolean;
  tier: 'FREE' | 'PREMIUM' | 'PRO';
  reason: string | null;
  upgrade_url: string | null;
  requirements: string | null;
}

// =============================================================================
// API Client Class
// =============================================================================

class TutorV3Client {
  private baseUrl: string;

  constructor(baseUrl: string = BACKEND_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  private getUserId(): string {
    // Get user ID from session or localStorage
    if (typeof window !== 'undefined') {
      const userId = localStorage.getItem('userId');
      if (userId) return userId;
    }
    throw new Error('User ID not found. Please log in.');
  }

  // =========================================================================
  // Content APIs
  // =========================================================================

  /**
   * Get all chapters with completion status
   */
  async getChapters(): Promise<ChapterListResponse> {
    const userId = this.getUserId();
    return this.request<ChapterListResponse>(
      `/api/v3/tutor/content/chapters?user_id=${userId}`
    );
  }

  /**
   * Get full chapter content
   */
  async getChapter(chapterId: string): Promise<ChapterContent> {
    const userId = this.getUserId();
    return this.request<ChapterContent>(
      `/api/v3/tutor/content/chapters/${chapterId}?user_id=${userId}`
    );
  }

  /**
   * Get navigation context for a chapter
   */
  async getNavigation(chapterId: string): Promise<ChapterNavigation> {
    const userId = this.getUserId();
    return this.request<ChapterNavigation>(
      `/api/v3/tutor/content/chapters/${chapterId}/navigation?user_id=${userId}`
    );
  }

  /**
   * Search content
   */
  async search(query: string, limit = 10): Promise<{ query: string; results: any[]; total: number }> {
    return this.request(
      `/api/v3/tutor/content/search?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  /**
   * Get "continue learning" recommendation
   */
  async getContinueLearning(): Promise<{
    chapter_id: string;
    title: string;
    order: number;
    reason: string;
    url: string;
  }> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/content/continue?user_id=${userId}`
    );
  }

  // =========================================================================
  // Quiz APIs
  // =========================================================================

  /**
   * Get quiz by chapter ID
   */
  async getQuizByChapter(chapterId: string): Promise<QuizDetail> {
    const userId = this.getUserId();
    return this.request<QuizDetail>(
      `/api/v3/tutor/quizzes/by-chapter/${chapterId}?user_id=${userId}`
    );
  }

  /**
   * Submit quiz for grading
   */
  async submitQuiz(
    quizId: string,
    submission: QuizSubmission
  ): Promise<QuizGradingResult> {
    const userId = this.getUserId();
    return this.request<QuizGradingResult>(
      `/api/v3/tutor/quizzes/${quizId}/submit?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify(submission),
      }
    );
  }

  /**
   * Get quiz performance insights
   */
  async getQuizInsights(quizId: string): Promise<{
    attempts_analyzed: number;
    average_score: number;
    best_score: number;
    improvement: number;
    trend: string;
    strengths: string[];
    focus_areas: string[];
    recommendations: string[];
    encouragement: string;
  }> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/quizzes/${quizId}/insights?user_id=${userId}`
    );
  }

  /**
   * Get quiz attempt history
   */
  async getQuizHistory(quizId: string, limit = 10): Promise<{
    attempt_id: string;
    quiz_id: string;
    score: number;
    passed: boolean;
    completed_at: string;
  }[]> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/quizzes/${quizId}/history?user_id=${userId}&limit=${limit}`
    );
  }

  // =========================================================================
  // Progress APIs
  // =========================================================================

  /**
   * Get overall progress summary
   */
  async getProgressSummary(): Promise<ProgressSummary> {
    const userId = this.getUserId();
    return this.request<ProgressSummary>(
      `/api/v3/tutor/progress/summary?user_id=${userId}`
    );
  }

  /**
   * Get progress for all chapters
   */
  async getChaptersProgress(): Promise<ChapterProgress[]> {
    const userId = this.getUserId();
    return this.request<ChapterProgress[]>(
      `/api/v3/tutor/progress/chapters?user_id=${userId}`
    );
  }

  /**
   * Update progress (mark chapter complete)
   */
  async updateProgress(chapterId: string, quizScore?: number): Promise<any> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/progress/update?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify({
          chapter_id: chapterId,
          quiz_score: quizScore,
        }),
      }
    );
  }

  /**
   * Get streak calendar
   */
  async getStreakCalendar(year?: number, month?: number): Promise<StreakCalendar> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: String(userId) });
    if (year) params.append('year', String(year));
    if (month) params.append('month', String(month));
    return this.request<StreakCalendar>(
      `/api/v3/tutor/progress/streak/calendar?${params}`
    );
  }

  /**
   * Get quiz score history for charts
   */
  async getScoreHistory(limit = 30): Promise<ScoreHistoryItem[]> {
    const userId = this.getUserId();
    return this.request<ScoreHistoryItem[]>(
      `/api/v3/tutor/progress/quiz-scores?user_id=${userId}&limit=${limit}`
    );
  }

  /**
   * Get all achievements
   */
  async getAchievements(): Promise<AchievementItem[]> {
    const userId = this.getUserId();
    return this.request<AchievementItem[]>(
      `/api/v3/tutor/progress/achievements?user_id=${userId}`
    );
  }

  /**
   * Record daily checkin
   */
  async dailyCheckin(): Promise<{
    streak_updated: boolean;
    current_streak: number;
    longest_streak: number;
    new_achievements: AchievementItem[];
  }> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/progress/checkin?user_id=${userId}`,
      { method: 'POST' }
    );
  }

  // =========================================================================
  // AI Features APIs
  // =========================================================================

  /**
   * Get AI features status
   */
  async getAIStatus(): Promise<{
    phase: string;
    llm_enabled: boolean;
    llm_provider: string | null;
    model: string;
    features: Record<string, boolean>;
    requirements: Record<string, string>;
  }> {
    return this.request('/api/v3/tutor/ai/status');
  }

  /**
   * Get knowledge gap analysis
   */
  async getKnowledgeAnalysis(): Promise<AdaptiveAnalysis> {
    const userId = this.getUserId();
    return this.request<AdaptiveAnalysis>(
      `/api/v3/tutor/ai/adaptive/analysis?user_id=${userId}`
    );
  }

  /**
   * Get personalized chapter recommendations
   */
  async getRecommendations(): Promise<ChapterRecommendation> {
    const userId = this.getUserId();
    return this.request<ChapterRecommendation>(
      `/api/v3/tutor/ai/adaptive/recommendations?user_id=${userId}`
    );
  }

  /**
   * Chat with AI mentor
   */
  async mentorChat(request: MentorChatRequest): Promise<MentorChatResponse> {
    const userId = this.getUserId();
    return this.request<MentorChatResponse>(
      `/api/v3/tutor/ai/mentor/chat?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Get AI-generated explanation for a topic
   */
  async explainTopic(request: ContentExplanationRequest): Promise<ContentExplanationResponse> {
    const userId = this.getUserId();
    return this.request<ContentExplanationResponse>(
      `/api/v3/tutor/ai/explain?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Grade quiz with LLM (detailed feedback)
   */
  async gradeQuizWithAI(quizId: string, answers: Record<string, any>): Promise<any> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/ai/quiz/grade-llm?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify({ quiz_id: quizId, answers }),
      }
    );
  }

  /**
   * Get LLM usage costs (Pro only)
   */
  async getLLMUsageCosts(): Promise<{
    user_id: string;
    total_requests: number;
    total_cost_usd: number;
    cost_breakdown: Record<string, any>;
    average_cost_per_request: number;
    period: string;
  }> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/ai/usage/costs?user_id=${userId}`
    );
  }

  // =========================================================================
  // Access & Subscription APIs
  // =========================================================================

  /**
   * List all subscription plans
   */
  async listSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    return this.request<SubscriptionPlan[]>('/api/v3/tutor/access/plans');
  }

  /**
   * Get current subscription info
   */
  async getSubscriptionInfo(): Promise<SubscriptionInfo> {
    const userId = this.getUserId();
    return this.request<SubscriptionInfo>(
      `/api/v3/tutor/access/subscription?user_id=${userId}`
    );
  }

  /**
   * Check access to a resource
   */
  async checkAccess(resource: string): Promise<AccessCheckResponse> {
    const userId = this.getUserId();
    return this.request<AccessCheckResponse>(
      `/api/v3/tutor/access/check?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify({ resource }),
      }
    );
  }

  /**
   * Upgrade subscription tier
   */
  async upgradeTier(
    newTier: 'PREMIUM' | 'PRO',
    paymentMethodId?: string,
    billingCycle: 'monthly' | 'yearly' = 'monthly'
  ): Promise<{
    user_id: string;
    old_tier: string;
    new_tier: string;
    upgraded_at: string;
  }> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/access/upgrade?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify({
          new_tier: newTier,
          payment_method_id: paymentMethodId,
          billing_cycle: billingCycle,
        }),
      }
    );
  }

  /**
   * Request data export (GDPR)
   */
  async requestDataExport(options: {
    include_progress: boolean;
    include_quiz_history: boolean;
    include_streaks: boolean;
    format: 'json' | 'csv' | 'pdf';
  } = {
    include_progress: true,
    include_quiz_history: true,
    include_streaks: true,
    format: 'json',
  }): Promise<{
    export_id: string;
    status: string;
    expires_at: string;
    download_url: string | null;
  }> {
    const userId = this.getUserId();
    return this.request(
      `/api/v3/tutor/access/export-data?user_id=${userId}`,
      {
        method: 'POST',
        body: JSON.stringify(options),
      }
    );
  }
}

// Export singleton instance
export const tutorApi = new TutorV3Client();

// Also export as default for convenience
export default tutorApi;

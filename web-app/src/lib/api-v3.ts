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
      const userId = localStorage.getItem('user_id');
      if (userId) return userId;
    }
    // Throw error if user not authenticated (don't use hardcoded fallback)
    throw new Error('User not authenticated');
  }

  // =========================================================================
  // Content APIs
  // =========================================================================

  /**
   * Get all chapters with completion status
   */
  async getChapters(): Promise<ChapterListResponse> {
    return this.request<ChapterListResponse>(
      `/api/v1/chapters`
    );
  }

  /**
   * Get full chapter content
   */
  async getChapter(chapterId: string): Promise<ChapterContent> {
    return this.request<ChapterContent>(
      `/api/v1/chapters/${chapterId}`
    );
  }

  /**
   * Get navigation context for a chapter (stub)
   */
  async getNavigation(chapterId: string): Promise<ChapterNavigation> {
    // Stub - not available in v1
    return {
      current: null,
      previous: null,
      next: null,
      can_continue: true,
    };
  }

  /**
   * Search content
   */
  async search(query: string, limit = 10): Promise<{ query: string; results: any[]; total: number }> {
    return this.request(
      `/api/v1/search?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  /**
   * Get "continue learning" recommendation (stub)
   */
  async getContinueLearning(): Promise<{
    chapter_id: string;
    title: string;
    order: number;
    reason: string;
    url: string;
  }> {
    // Stub - not available in v1
    return {
      chapter_id: '1',
      title: 'Introduction to AI Agents',
      order: 1,
      reason: 'Start here',
      url: '/chapters/1',
    };
  }

  // =========================================================================
  // Quiz APIs
  // =========================================================================

  /**
   * Get quiz by chapter ID
   */
  async getQuizByChapter(chapterId: string): Promise<QuizDetail> {
    return this.request<QuizDetail>(
      `/api/v1/quizzes`
    );
  }

  /**
   * Submit quiz for grading
   */
  async submitQuiz(
    quizId: string,
    submission: QuizSubmission
  ): Promise<QuizGradingResult> {
    return this.request<QuizGradingResult>(
      `/api/v1/quizzes/${quizId}/submit`,
      {
        method: 'POST',
        body: JSON.stringify(submission),
      }
    );
  }

  /**
   * Get quiz performance insights (stub)
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
    // Stub - not available in v1
    return {
      attempts_analyzed: 0,
      average_score: 0,
      best_score: 0,
      improvement: 0,
      trend: 'none',
      strengths: [],
      focus_areas: [],
      recommendations: ['Take the quiz to see insights'],
      encouragement: 'Good luck!',
    };
  }

  /**
   * Get quiz attempt history (stub)
   */
  async getQuizHistory(quizId: string, limit = 10): Promise<{
    attempt_id: string;
    quiz_id: string;
    score: number;
    passed: boolean;
    completed_at: string;
  }[]> {
    // Stub - not available in v1
    return [];
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
      `/api/v1/progress/${userId}`
    );
  }

  /**
   * Get progress for all chapters (stub - returns basic data)
   */
  async getChaptersProgress(): Promise<ChapterProgress[]> {
    // Stub implementation - not available in v1
    return [];
  }

  /**
   * Update progress (mark chapter complete)
   */
  async updateProgress(chapterId: string, quizScore?: number): Promise<any> {
    const userId = this.getUserId();
    return this.request(
      `/api/v1/progress/${userId}`,
      {
        method: 'PUT',
        body: JSON.stringify({ chapter_id: chapterId }),
      }
    );
  }

  /**
   * Get streak calendar (stub - returns basic data)
   */
  async getStreakCalendar(year?: number, month?: number): Promise<StreakCalendar> {
    const userId = this.getUserId();
    return this.request<StreakCalendar>(
      `/api/v1/streaks/${userId}`
    );
  }

  /**
   * Get quiz score history for charts (stub)
   */
  async getScoreHistory(limit = 30): Promise<ScoreHistoryItem[]> {
    // Stub implementation - not available in v1
    return [];
  }

  /**
   * Get all achievements (stub)
   */
  async getAchievements(): Promise<AchievementItem[]> {
    // Stub implementation - not available in v1
    return [];
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
      `/api/v1/streaks/${userId}/checkin`,
      { method: 'POST' }
    );
  }

  // =========================================================================
  // AI Features APIs (STUBS - Phase 2 features not available in v1)
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
    // Stub - Phase 2 features not available
    return {
      phase: '1',
      llm_enabled: false,
      llm_provider: null,
      model: 'none',
      features: {},
      requirements: {},
    };
  }

  /**
   * Get knowledge gap analysis (stub)
   */
  async getKnowledgeAnalysis(): Promise<AdaptiveAnalysis> {
    // Stub - Phase 2 features not available
    return {
      weak_topics: [],
      strong_topics: [],
      recommended_review: [],
      confidence_score: 0,
      explanation: 'Phase 2 AI features are not available in v1 API',
    };
  }

  /**
   * Get personalized chapter recommendations (stub)
   */
  async getRecommendations(): Promise<ChapterRecommendation> {
    // Stub - Phase 2 features not available
    throw new Error('Recommendations not available in v1 API');
  }

  /**
   * Chat with AI mentor (stub)
   */
  async mentorChat(request: MentorChatRequest): Promise<MentorChatResponse> {
    // Stub - Phase 2 features not available
    throw new Error('AI Mentor not available in v1 API');
  }

  /**
   * Get AI-generated explanation for a topic (stub)
   */
  async explainTopic(request: ContentExplanationRequest): Promise<ContentExplanationResponse> {
    // Stub - Phase 2 features not available
    throw new Error('AI Explanations not available in v1 API');
  }

  /**
   * Grade quiz with LLM (detailed feedback) (stub)
   */
  async gradeQuizWithAI(quizId: string, answers: Record<string, any>): Promise<any> {
    // Stub - Phase 2 features not available
    throw new Error('AI Grading not available in v1 API');
  }

  /**
   * Get LLM usage costs (Pro only) (stub)
   */
  async getLLMUsageCosts(): Promise<{
    user_id: string;
    total_requests: number;
    total_cost_usd: number;
    cost_breakdown: Record<string, any>;
    average_cost_per_request: number;
    period: string;
  }> {
    // Stub - Phase 2 features not available
    throw new Error('LLM Costs tracking not available in v1 API');
  }

  // =========================================================================
  // Access & Subscription APIs (STUBS - Limited availability in v1)
  // =========================================================================

  /**
   * List all subscription plans (stub)
   */
  async listSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    // Stub - returns basic plans
    return [
      {
        tier: 'FREE',
        name: 'Free',
        price_monthly: 0,
        price_yearly: 0,
        features: ['Access to first 3 chapters'],
        limits: { chapters: 3 },
      },
    ];
  }

  /**
   * Get current subscription info
   */
  async getSubscriptionInfo(): Promise<SubscriptionInfo> {
    const userId = this.getUserId();
    return this.request<SubscriptionInfo>(
      `/api/v1/user/${userId}/tier`
    ).then(tier => ({
      user_id: userId,
      current_tier: tier.tier as 'FREE' | 'PREMIUM' | 'PRO',
      tier_name: tier.tier,
      subscribed_at: null,
      subscription_status: 'active',
      next_billing_date: null,
      cancel_at_period_end: false,
    }));
  }

  /**
   * Check access to a resource
   */
  async checkAccess(resource: string): Promise<AccessCheckResponse> {
    const userId = this.getUserId();
    return this.request<{ tier: string }>(
      `/api/v1/user/${userId}/tier`
    ).then(tier => ({
      has_access: true,
      tier: tier.tier as 'FREE' | 'PREMIUM' | 'PRO',
      reason: null,
      upgrade_url: null,
      requirements: null,
    }));
  }

  /**
   * Upgrade subscription tier (stub)
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
    // Stub - not available in v1
    throw new Error('Tier upgrade not available in v1 API');
  }

  /**
   * Request data export (GDPR) (stub)
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
    // Stub - not available in v1
    throw new Error('Data export not available in v1 API');
  }
}

// Export singleton instance
export const tutorApi = new TutorV3Client();

// Also export as default for convenience
export default tutorApi;

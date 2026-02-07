/**
 * API v3 Client - Phase 3 Unified Tutor API
 *
 * This client provides access to the unified Phase 3 API with:
 * - Single endpoint structure: /api/v3/tutor/
 * - LLM features enabled by default
 * - Enhanced gamification and analytics
 * - Subscription management
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://92.113.147.250:3505';

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
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId });

    return this.request<QuizGradingResult>(
      `/api/v1/quizzes/${quizId}/submit?${params}`,
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
  // Progress APIs (v3 - Complete implementation)
  // =========================================================================

  /**
   * Get overall progress summary
   */
  async getProgressSummary(): Promise<ProgressSummary> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId });
    return this.request<ProgressSummary>(
      `/api/v3/tutor/progress/summary?${params}`
    );
  }

  /**
   * Get progress for all chapters
   */
  async getChaptersProgress(): Promise<ChapterProgress[]> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId });
    return this.request<ChapterProgress[]>(
      `/api/v3/tutor/progress/chapters?${params}`
    );
  }

  /**
   * Update progress (mark chapter complete)
   */
  async updateProgress(chapterId: string, quizScore?: number): Promise<any> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId });
    return this.request(
      `/api/v3/tutor/progress/update?${params}`,
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
    const params = new URLSearchParams({ user_id: userId });
    if (year) params.append('year', year.toString());
    if (month) params.append('month', month.toString());
    return this.request<StreakCalendar>(
      `/api/v3/tutor/progress/streak/calendar?${params}`
    );
  }

  /**
   * Get quiz score history for charts
   */
  async getScoreHistory(limit = 30): Promise<ScoreHistoryItem[]> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId, limit: limit.toString() });
    return this.request<ScoreHistoryItem[]>(
      `/api/v3/tutor/progress/quiz-scores?${params}`
    );
  }

  /**
   * Get all achievements
   */
  async getAchievements(): Promise<AchievementItem[]> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId });
    return this.request<AchievementItem[]>(
      `/api/v3/tutor/progress/achievements?${params}`
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
    // Stub - Return demo analysis with correct chapter UUIDs
    return {
      weak_topics: [
        'State Management',
        'Error Handling',
      ],
      strong_topics: [
        'MCP Integration',
        'Agent Development',
      ],
      recommended_review: [
        '2912d135-f34f-40af-a297-5f8acfdca3f6', // Chapter 1
        '4d595b4d-ac38-4a35-9699-265009f430e9', // Chapter 2
      ],
      confidence_score: 0.75,
      explanation: 'Based on your quiz performance, you show strong understanding of MCP integration concepts. For best results, we recommend reviewing state management patterns and error handling strategies before moving to advanced topics.',
    };
  }

  /**
   * Get personalized chapter recommendations (stub)
   */
  async getRecommendations(): Promise<ChapterRecommendation> {
    // Stub - Return demo recommendation with correct chapter UUIDs
    return {
      next_chapter_id: '91a1e219-c7ff-4677-8a1a-ace4b58787c5', // Chapter 3: Creating Your First Agent
      next_chapter_title: 'Creating Your First Agent',
      reason: 'Based on your progress in Chapter 2, we recommend continuing with agent creation. This chapter will help you build your first functional AI agent using MCP.',
      estimated_completion_minutes: 30,
      difficulty_match: 'Perfect Match',
      alternative_paths: [
        {
          chapter_id: '56aa5028-8ddd-4e21-b00a-e935147079cc', // Chapter 4: Building Reusable Skills
          title: 'Building Reusable Skills',
          reason: 'Alternative path if you want to focus on skill architecture first',
        },
      ],
    };
  }

  /**
   * Chat with AI mentor (real LLM)
   */
  async mentorChat(request: MentorChatRequest): Promise<MentorChatResponse> {
    const userId = this.getUserId();
    const params = new URLSearchParams({ user_id: userId });

    return this.request<MentorChatResponse>(
      `/api/v3/tutor/ai/mentor/chat?${params}`,
      {
        method: 'POST',
        body: JSON.stringify({
          question: request.question || request.message || '',
          conversation_history: request.conversation_history || [],
        }),
      }
    );
  }

  /**
   * Get AI-generated explanation for a topic (stub)
   */
  async explainTopic(request: ContentExplanationRequest): Promise<ContentExplanationResponse> {
    // Stub - Return demo explanation
    return {
      topic: request.topic,
      explanation: `${request.topic} is a fundamental concept in AI agent development. It enables systems to perform specific tasks efficiently and reliably.`,
      key_points: [
        `Understanding ${request.topic} is crucial for building effective agents`,
        'Practice with real-world scenarios reinforces learning',
        'MCP integration enhances agent capabilities',
      ],
      examples: [
        {
          name: 'Basic Implementation',
          description: `A simple example showing how ${request.topic} works in practice`,
        },
      ],
      related_topics: ['MCP Integration', 'Agent Development', 'API Design'],
    };
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
    const params = new URLSearchParams({ user_id: userId });
    return this.request<SubscriptionInfo>(`/api/v3/tutor/access/subscription?${params}`);
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
    const params = new URLSearchParams({ user_id: userId });

    return this.request<{
      user_id: string;
      old_tier: string;
      new_tier: string;
      upgraded_at: string;
    }>(
      `/api/v3/tutor/access/upgrade?${params}`,
      {
        method: 'POST',
        body: JSON.stringify({
          new_tier: newTier,
          billing_cycle: billingCycle,
          payment_method_id: paymentMethodId || 'demo', // Demo payment for hackathon
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
    return this.request<{
      export_id: string;
      status: string;
      expires_at: string;
      download_url: string | null;
    }>(
      `/api/v3/tutor/access/export-data`,
      {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          ...options,
        }),
      }
    );
  }

  // =========================================================================
  // Gamification: Tips API
  // =========================================================================

  /**
   * Get all tips with optional filtering
   */
  async getTips(params?: {
    category?: string;
    difficulty_level?: string;
    active_only?: boolean;
  }): Promise<{ tips: TipItem[]; total: number }> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.difficulty_level) queryParams.append('difficulty_level', params.difficulty_level);
    if (params?.active_only !== undefined) queryParams.append('active_only', String(params.active_only));

    const queryString = queryParams.toString();
    return this.request(
      `/api/v3/tutor/tips/${queryString ? `?${queryString}` : ''}`
    );
  }

  /**
   * Get a random tip for dashboard
   */
  async getRandomTip(params?: {
    category?: string;
    difficulty_level?: string;
  }): Promise<TipItem> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.difficulty_level) queryParams.append('difficulty_level', params.difficulty_level);

    const queryString = queryParams.toString();
    return this.request(
      `/api/v3/tutor/tips/random${queryString ? `?${queryString}` : ''}`
    );
  }

  // =========================================================================
  // Gamification: Leaderboard API
  // =========================================================================

  /**
   * Get global leaderboard
   */
  async getLeaderboard(params?: {
    limit?: number;
    user_id?: string;
  }): Promise<LeaderboardData> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.user_id) queryParams.append('user_id', params.user_id);

    const queryString = queryParams.toString();
    return this.request(
      `/api/v3/tutor/leaderboard/${queryString ? `?${queryString}` : ''}`
    );
  }

  /**
   * Get user's leaderboard opt-in status
   */
  async getLeaderboardOptInStatus(userId: string): Promise<LeaderboardOptInStatus | null> {
    return this.request<LeaderboardOptInStatus | null>(
      `/api/v3/tutor/leaderboard/opt-in-status?user_id=${userId}`
    );
  }

  /**
   * Opt in to leaderboard
   */
  async optInToLeaderboard(data: {
    user_id: string;
    display_name: string;
    show_rank?: boolean;
    show_score?: boolean;
    show_streak?: boolean;
  }): Promise<LeaderboardOptInStatus> {
    return this.request(
      `/api/v3/tutor/leaderboard/opt-in?user_id=${data.user_id}`,
      {
        method: 'POST',
        body: JSON.stringify({
          display_name: data.display_name,
          show_rank: data.show_rank ?? true,
          show_score: data.show_score ?? true,
          show_streak: data.show_streak ?? true,
        }),
      }
    );
  }

  /**
   * Opt out from leaderboard
   */
  async optOutFromLeaderboard(userId: string): Promise<{ message: string }> {
    return this.request(
      `/api/v3/tutor/leaderboard/opt-out?user_id=${userId}`,
      { method: 'POST' }
    );
  }

  /**
   * Update leaderboard privacy settings
   */
  async updateLeaderboardSettings(userId: string, settings: {
    display_name?: string;
    is_opted_in?: boolean;
    show_rank?: boolean;
    show_score?: boolean;
    show_streak?: boolean;
  }): Promise<LeaderboardOptInStatus> {
    return this.request(
      `/api/v3/tutor/leaderboard/opt-in-settings?user_id=${userId}`,
      {
        method: 'PUT',
        body: JSON.stringify(settings),
      }
    );
  }

  /**
   * Get user rank on leaderboard
   */
  async getUserRank(userId: string): Promise<{ user_id: string; rank: number }> {
    return this.request(
      `/api/v3/tutor/leaderboard/rank/${userId}`
    );
  }

  /**
   * Get user stats for leaderboard
   */
  async getUserStats(userId: string): Promise<UserStats> {
    return this.request(
      `/api/v3/tutor/leaderboard/stats/${userId}`
    );
  }

  // =========================================================================
  // Gamification: Certificates API
  // =========================================================================

  /**
   * Check certificate eligibility
   */
  async checkCertificateEligibility(userId: string): Promise<CertificateEligibility> {
    return this.request(
      `/api/v3/tutor/certificates/check-eligibility`,
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId }),
      }
    );
  }

  /**
   * Generate a certificate
   */
  async generateCertificate(data: {
    user_id: string;
    student_name: string;
  }): Promise<CertificateItem> {
    return this.request(
      `/api/v3/tutor/certificates/generate?user_id=${data.user_id}`,
      {
        method: 'POST',
        body: JSON.stringify({ student_name: data.student_name }),
      }
    );
  }

  /**
   * Get user's certificates
   */
  async getUserCertificates(userId: string): Promise<{ certificates: CertificateItem[]; total: number }> {
    return this.request(
      `/api/v3/tutor/certificates?user_id=${userId}`
    );
  }

  /**
   * Verify a certificate (public endpoint, no auth required)
   */
  async verifyCertificate(certificateId: string): Promise<CertificateVerification> {
    return this.request(
      `/api/v3/certificate/verify/${certificateId}`
    );
  }
}

// =============================================================================
// Additional Types for Gamification
// =============================================================================

export interface TipItem {
  id: string;
  content: string;
  category: string;
  difficulty_level: string | null;
  active: boolean;
  created_at: string;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  xp: number;
  average_score: number;
  current_streak: number;
  completed_chapters: number;
}

export interface LeaderboardData {
  leaderboard: LeaderboardEntry[];
  total_entries: number;
  user_rank: number | null;
  user_xp: number | null;
}

export interface LeaderboardOptInStatus {
  id: string;
  user_id: string;
  display_name: string;
  is_opted_in: boolean;
  show_rank: boolean;
  show_score: boolean;
  show_streak: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserStats {
  average_score: number;
  completed_chapters: number;
  current_streak: number;
  xp: number;
}

export interface CertificateEligibility {
  eligible: boolean;
  completion_percentage: number;
  average_score: number;
  completed_chapters: number;
  total_streak_days: number;
  min_completion_required: number;
  min_score_required: number;
  reason: string | null;
}

export interface CertificateItem {
  id: string;
  certificate_id: string;
  user_id: string;
  student_name: string;
  completion_percentage: number;
  average_quiz_score: number;
  total_chapters_completed: number;
  total_streak_days: number;
  issued_at: string;
  verification_count: number;
}

export interface CertificateVerification {
  certificate_id: string;
  is_valid: boolean;
  student_name: string;
  completion_percentage: number;
  average_quiz_score: number;
  total_chapters_completed: number;
  total_streak_days: number;
  issued_at: string;
  verified_at: string;
  verification_url: string | null;
}

// Export singleton instance
export const tutorApi = new TutorV3Client();

// Also export as default for convenience
export default tutorApi;

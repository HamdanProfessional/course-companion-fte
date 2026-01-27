/**
 * TypeScript type definitions for Course Companion FTE Backend API.
 * Zero-LLM compliance: All types are for deterministic backend data only.
 */

// ============================================================================
// Domain Types
// ============================================================================

/**
 * User subscription tiers.
 */
export type UserTier = 'free' | 'premium' | 'pro';

/**
 * Content difficulty levels.
 */
export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced';

/**
 * Multiple choice answer options.
 */
export type AnswerChoice = 'A' | 'B' | 'C' | 'D';

// ============================================================================
// Chapter Types
// ============================================================================

/**
 * Chapter metadata (list view).
 */
export interface Chapter {
  id: string;
  title: string;
  order: number;
  difficulty_level: DifficultyLevel;
  estimated_time: number;
}

/**
 * Chapter detail with content.
 */
export interface ChapterDetail extends Chapter {
  content: string | null;
  r2_content_key: string | null;
  quiz_id: string | null;
}

/**
 * Search result item.
 */
export interface SearchResult {
  chapter_id: string;
  title: string;
  snippet: string;
  relevance_score: number;
}

/**
 * Search response.
 */
export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

// ============================================================================
// Quiz Types
// ============================================================================

/**
 * Quiz question (without correct answer).
 */
export interface Question {
  id: string;
  quiz_id: string;
  question_text: string;
  options: Record<string, string>;
  explanation: string | null;
  order: number;
}

/**
 * Quiz with questions.
 */
export interface Quiz {
  id: string;
  title: string;
  difficulty: DifficultyLevel;
  chapter_id: string;
  created_at: string;
  questions: Question[];
}

/**
 * Quiz submission request.
 */
export interface QuizSubmission {
  answers: Record<string, AnswerChoice>;
}

/**
 * Quiz result item.
 */
export interface QuizResultItem {
  question_id: string;
  question_text: string;
  selected_answer: AnswerChoice;
  correct_answer: AnswerChoice;
  is_correct: boolean;
  explanation: string | null;
}

/**
 * Quiz grading result.
 */
export interface QuizResult {
  quiz_id: string;
  score: number;
  passed: boolean;
  total_questions: number;
  correct_answers: number;
  results: QuizResultItem[];
}

/**
 * Quiz attempt history item.
 */
export interface QuizAttempt {
  id: string;
  score: number;
  completed_at: string;
}

// ============================================================================
// Progress Types
// ============================================================================

/**
 * User progress.
 */
export interface Progress {
  id: string;
  user_id: string;
  completed_chapters: string[];
  current_chapter_id: string | null;
  completion_percentage: number;
  last_activity: string;
}

/**
 * Progress update request.
 */
export interface ProgressUpdate {
  chapter_id: string;
}

/**
 * User streak.
 */
export interface Streak {
  id: string;
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_checkin: string | null;
}

// ============================================================================
// Access Control Types
// ============================================================================

/**
 * Access check request.
 */
export interface AccessCheck {
  user_id: string;
  resource: string;
}

/**
 * Access check response.
 */
export interface AccessResponse {
  access_granted: boolean;
  tier: UserTier;
  reason: string | null;
  upgrade_url: string | null;
}

/**
 * User tier information.
 */
export interface UserTierInfo {
  user_id: string;
  tier: UserTier;
  created_at: string;
}

/**
 * Tier update request.
 */
export interface TierUpdate {
  new_tier: UserTier;
}

/**
 * Tier update response.
 */
export interface TierUpdateResponse {
  user_id: string;
  old_tier: UserTier;
  new_tier: UserTier;
  upgraded_at: string;
}

// ============================================================================
// API Client Types
// ============================================================================

/**
 * Backend client configuration.
 */
export interface BackendConfig {
  baseUrl: string;
  defaultUserId: string;
  timeout?: number;
}

/**
 * API error types.
 */
export class BackendClientError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'BackendClientError';
  }
}

export class BackendConnectionError extends BackendClientError {
  constructor(message: string) {
    super(message);
    this.name = 'BackendConnectionError';
  }
}

export class BackendAuthError extends BackendClientError {
  constructor(message: string) {
    super(message);
    this.name = 'BackendAuthError';
  }
}

export class BackendAccessDeniedError extends BackendClientError {
  constructor(message: string) {
    super(message);
    this.name = 'BackendAccessDeniedError';
  }
}

export class BackendNotFoundError extends BackendClientError {
  constructor(message: string) {
    super(message);
    this.name = 'BackendNotFoundError';
  }
}

// ============================================================================
// Intent Detection Types
// ============================================================================

/**
 * Intent types for routing to skills.
 */
export type IntentType =
  | 'explain'        // concept-explainer skill
  | 'quiz'           // quiz-master skill
  | 'socratic'       // socratic-tutor skill
  | 'progress'       // progress-motivator skill
  | 'general';       // Default tutoring mode

/**
 * Intent detection result.
 */
export interface Intent {
  type: IntentType;
  confidence: number;
  skill: string;
  keywords: string[];
}

// ============================================================================
// Conversation Context Types
// ============================================================================

/**
 * Conversation context for maintaining state across turns.
 */
export interface ConversationContext {
  user_id: string;
  current_chapter_id?: string;
  current_quiz_id?: string;
  last_intent?: IntentType;
  turn_count: number;
  skill_active?: string;
}

/**
 * Skill loading request.
 */
export interface SkillLoadRequest {
  skill: string;
  context: ConversationContext;
  user_message: string;
}

/**
 * Skill load response.
 */
export interface SkillLoadResponse {
  skill: string;
  loaded: boolean;
  response: string;
}

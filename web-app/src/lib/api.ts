/**
 * Backend API client for Course Companion FTE web application.
 * Zero-LLM compliance: Makes HTTP requests to deterministic backend only.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface Chapter {
  id: string;
  title: string;
  content: string | null;
  order: number;
  difficulty_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'beginner' | 'intermediate' | 'advanced';
  estimated_time: number;
  r2_content_key: string | null;
  quiz_id: string | null;
}

export interface Quiz {
  id: string;
  title: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'beginner' | 'intermediate' | 'advanced';
  chapter_id: string;
  created_at: string;
  questions: Question[];
}

export interface Question {
  id: string;
  quiz_id: string;
  question_text: string;
  options: Record<string, string>;
  explanation: string | null;
  order: number;
}

export interface Progress {
  id: string;
  user_id: string;
  completed_chapters: string[];
  current_chapter_id: string | null;
  completion_percentage: number;
  last_activity: string;
}

export interface Streak {
  id: string;
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_checkin: string | null;
}

export interface QuizResult {
  quiz_id: string;
  score: number;
  passed: boolean;
  total_questions: number;
  correct_answers: number;
  results: QuizResultItem[];
}

export interface QuizResultItem {
  question_id: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string | null;
}

export interface SearchResult {
  chapter_id: string;
  title: string;
  snippet: string;
  relevance_score: number;
}

/**
 * Backend API client class.
 */
class BackendClient {
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

  // Content APIs
  async getChapters(): Promise<Chapter[]> {
    const chapters = await this.request<any[]>('/api/v1/chapters');
    // Normalize difficulty_level to lowercase for Badge component compatibility
    return chapters.map(chapter => ({
      ...chapter,
      difficulty_level: chapter.difficulty_level?.toLowerCase() || 'beginner',
    }));
  }

  async getChapter(chapterId: string): Promise<Chapter> {
    const chapter = await this.request<any>(`/api/v1/chapters/${chapterId}`);
    // Normalize difficulty_level to lowercase for Badge component compatibility
    return {
      ...chapter,
      difficulty_level: chapter.difficulty_level?.toLowerCase() || 'beginner',
    };
  }

  async searchContent(query: string, limit = 10): Promise<{ query: string; results: SearchResult[]; total: number }> {
    return this.request(`/api/v1/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  }

  // Quiz APIs
  async getQuizzes(): Promise<Quiz[]> {
    const quizzes = await this.request<any[]>('/api/v1/quizzes');
    // Normalize difficulty to lowercase for Badge component compatibility
    return quizzes.map(quiz => ({
      ...quiz,
      difficulty: quiz.difficulty?.toLowerCase() || 'beginner',
    }));
  }

  async getQuiz(quizId: string): Promise<Quiz> {
    const quiz = await this.request<any>(`/api/v1/quizzes/${quizId}`);
    // Normalize difficulty to lowercase for Badge component compatibility
    return {
      ...quiz,
      difficulty: quiz.difficulty?.toLowerCase() || 'beginner',
    };
  }

  async submitQuiz(quizId: string, answers: Record<string, string>): Promise<QuizResult> {
    return this.request<QuizResult>(`/api/v1/quizzes/${quizId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  }

  // Progress APIs
  async getProgress(userId: string): Promise<Progress> {
    return this.request<Progress>(`/api/v1/progress/${userId}`);
  }

  async updateProgress(userId: string, chapterId: string): Promise<Progress> {
    return this.request<Progress>(`/api/v1/progress/${userId}`, {
      method: 'PUT',
      body: JSON.stringify({ chapter_id: chapterId }),
    });
  }

  async getStreak(userId: string): Promise<Streak> {
    return this.request<Streak>(`/api/v1/streaks/${userId}`);
  }

  async recordCheckin(userId: string): Promise<Streak> {
    return this.request<Streak>(`/api/v1/streaks/${userId}/checkin`, {
      method: 'POST',
    });
  }

  async getUserTier(userId: string): Promise<{ tier: string }> {
    return this.request<{ tier: string }>(`/api/v1/user/${userId}/tier`);
  }

  // Access Control APIs
  async checkAccess(userId: string, resource: string): Promise<{
    access_granted: boolean;
    tier: string;
    reason: string | null;
    upgrade_url: string | null;
  }> {
    return this.request('/api/v1/access/check', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, resource }),
    });
  }
}

// Export singleton instance
export const backendApi = new BackendClient();

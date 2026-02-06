/**
 * Test data constants for E2E tests
 */

export const TEST_USERS = {
  FREE: {
    email: 'demo@example.com',
    password: 'password123',
    userId: '82b8b862-059a-416a-9ef4-e582a4870efa',
    tier: 'FREE',
  },
  PREMIUM: {
    email: 'premium@example.com',
    password: 'password123',
    tier: 'PREMIUM',
  },
  PRO: {
    email: 'pro@example.com',
    password: 'password123',
    tier: 'PRO',
  },
} as const;

export const INVALID_CREDENTIALS = {
  email: 'invalid@example.com',
  password: 'wrongpassword',
};

export const NEW_USER = {
  email: `test-${Date.now()}@example.com`,
  password: 'testPassword123',
  confirmPassword: 'testPassword123',
};

export const PAGES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  CHAPTERS: '/chapters',
  QUIZZES: '/quizzes',
  PROGRESS: '/progress',
  PROFILE: '/profile',
} as const;

export const CHAPTER_COUNT = 10;
export const QUIZ_COUNT = 10;
export const QUESTIONS_PER_QUIZ = 5;

// Expected values for demo user
export const DEMO_USER_EXPECTED = {
  completedChapters: 2,
  streak: 5,
  progressPercentage: 20,
};

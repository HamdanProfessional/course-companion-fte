/**
 * Authentication utilities for Course Companion FTE.
 * This is a simplified auth setup - in production, integrate with backend JWT.
 */

export interface User {
  id: string;
  email: string;
  tier: 'free' | 'premium' | 'pro';
  created_at: string;
}

/**
 * Get mock user for demo purposes.
 * In production, this would decode JWT from backend.
 */
export function getMockUser(): User {
  return {
    id: '00000000-0000-0000-0000-000000000001',
    email: 'student@example.com',
    tier: 'free',
    created_at: new Date().toISOString(),
  };
}

/**
 * Get current user from session.
 * TODO: Implement proper JWT validation with backend.
 */
export async function getCurrentUser(): Promise<User | null> {
  // For demo purposes, return mock user
  // In production, validate JWT token with backend
  return getMockUser();
}

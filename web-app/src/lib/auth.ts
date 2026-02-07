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
 * Reads from localStorage where login/register stores the data.
 * TODO: Implement proper JWT validation with backend.
 */
export async function getCurrentUser(): Promise<User | null> {
  if (typeof window === 'undefined') return null;

  const userId = localStorage.getItem('user_id');
  const email = localStorage.getItem('user_email');
  const tier = localStorage.getItem('user_tier');
  const token = localStorage.getItem('token');

  // If no token or user_id, user is not logged in
  if (!token || !userId) {
    return null;
  }

  // Normalize tier to lowercase
  const normalizedTier = tier?.toLowerCase() || 'free';

  return {
    id: userId,
    email: email || '',
    tier: (normalizedTier === 'premium' || normalizedTier === 'pro') ? normalizedTier : 'free',
    created_at: localStorage.getItem('created_at') || new Date().toISOString(),
  };
}

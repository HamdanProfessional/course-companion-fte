import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Authentication Middleware
 *
 * NOTE: Middleware cannot access localStorage.
 * Auth checks are handled client-side in each protected page.
 * This middleware only handles static assets and basic routing.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow all routes - auth is handled client-side
  // Each protected page (dashboard, chapters, etc.) checks localStorage themselves
  return NextResponse.next();
}

/**
 * Matcher configuration
 *
 * Specifies which routes should be protected by this middleware.
 * All protected routes require authentication.
 */
export const config = {
  matcher: [
    // Protect main dashboard and feature pages
    '/dashboard/:path*',
    '/chapters/:path*',
    '/quizzes/:path*',
    '/progress/:path*',
    '/profile/:path*',
    '/subscription/:path*',
    '/adaptive-learning/:path*',
    '/ai-mentor/:path*',
    // Protect admin routes
    '/admin/:path*',
  ],
};

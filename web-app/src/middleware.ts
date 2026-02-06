import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Authentication Middleware
 *
 * NOTE: Currently disabled - authentication is handled client-side
 * by individual pages. This middleware can be re-enabled when
 * server-side authentication is properly implemented with cookies.
 */

export function middleware(request: NextRequest) {
  // Allow all requests - authentication is handled client-side
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
    /*
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
    */
  ],
};

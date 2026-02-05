import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Authentication Middleware
 *
 * Protects routes by checking for authentication token.
 * Redirects unauthenticated users to login page.
 *
 * Public routes: /, /login, /register
 * Protected routes: /dashboard, /chapters, /quizzes, /progress, /profile, /subscription
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes without authentication
  const publicRoutes = ['/', '/login', '/register'];
  if (publicRoutes.includes(pathname)) {
    return NextResponse.next();
  }

  // Also allow static assets and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/static') ||
    pathname.includes('.') // Static files
  ) {
    return NextResponse.next();
  }

  // Check for authentication token in cookies or authorization header
  const token =
    request.cookies.get('token')?.value ||
    request.headers.get('authorization')?.replace('Bearer ', '');

  // Get user ID from localStorage hint (sent via custom header)
  const userId = request.headers.get('x-user-id');

  if (!token || !userId) {
    // User is not authenticated - redirect to login
    const url = new URL('/login', request.url);
    url.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(url);
  }

  // User is authenticated - proceed to protected route
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

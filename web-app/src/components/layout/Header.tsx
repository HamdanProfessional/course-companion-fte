/**
 * Header component for Course Companion FTE.
 */
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export function Header() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-primary-600">
              Course Companion FTE
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/dashboard" className="text-gray-700 hover:text-primary-600">
              Dashboard
            </Link>
            <Link href="/chapters" className="text-gray-700 hover:text-primary-600">
              Chapters
            </Link>
            <Link href="/progress" className="text-gray-700 hover:text-primary-600">
              Progress
            </Link>
            <Link href="/profile" className="text-gray-700 hover:text-primary-600">
              Profile
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">student@example.com</span>
            <Button variant="outline" size="sm">
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}

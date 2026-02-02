'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { SearchBar } from '@/components/SearchBar';

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Chapters', href: '/chapters' },
  { name: 'Quizzes', href: '/quizzes' },
  { name: 'Progress', href: '/progress' },
];

// Phase 3 AI Features (shown separately)
const aiFeatures = [
  { name: 'Adaptive Learning', href: '/adaptive-learning', badge: 'AI' },
  { name: 'AI Mentor', href: '/ai-mentor', badge: 'AI' },
];

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border-default bg-bg-primary/95 backdrop-blur supports-[backdrop-filter]:bg-bg-primary/60">
      <nav className="container flex items-center justify-between h-16" aria-label="Global">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-accent-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <span className="text-xl font-bold text-text-primary">Course Companion</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:items-center md:gap-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-accent-primary text-white'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                {item.name}
              </Link>
            );
          })}

          {/* Divider */}
          <div className="w-px h-6 bg-border-default mx-2" />

          {/* AI Features */}
          {aiFeatures.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
                  isActive
                    ? 'bg-accent-secondary text-white'
                    : 'text-text-secondary hover:text-accent-secondary hover:bg-accent-secondary/10'
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                {item.name}
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-accent-secondary text-white">
                  {item.badge}
                </span>
              </Link>
            );
          })}

          {/* Search Bar */}
          <div className="w-64 ml-4">
            <SearchBar placeholder="Search..." />
          </div>
        </div>

        {/* User menu - desktop */}
        <div className="hidden md:flex md:items-center md:gap-4">
          <Link href="/profile">
            <Button variant="ghost" size="sm">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </Button>
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="md:hidden">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle menu"
          >
            <span className="sr-only">Open main menu</span>
            {mobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </Button>
        </div>
      </nav>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border-default bg-bg-secondary">
          <div className="container px-2 py-3 space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'block px-4 py-2 rounded-lg text-base font-medium transition-colors',
                    isActive
                      ? 'bg-accent-primary text-white'
                      : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              );
            })}

            {/* AI Features Section */}
            <div className="pt-4 pb-2">
              <div className="px-4 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider">
                AI Features
              </div>
            </div>
            {aiFeatures.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'block px-4 py-2 rounded-lg text-base font-medium transition-colors flex items-center justify-between',
                    isActive
                      ? 'bg-accent-secondary text-white'
                      : 'text-text-secondary hover:text-accent-secondary hover:bg-accent-secondary/10'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-accent-secondary text-white">
                    {item.badge}
                  </span>
                </Link>
              );
            })}

            <Link
              href="/profile"
              className="block px-4 py-2 rounded-lg text-base font-medium text-text-secondary hover:text-text-primary hover:bg-bg-elevated transition-colors"
              onClick={() => setMobileMenuOpen(false)}
            >
              Profile
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}

'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

// Dynamically import SearchBar to prevent SSR issues
const SearchBar = dynamic(() => import('@/components/SearchBar').then(mod => ({ default: mod.SearchBar })), {
  ssr: false,
  loading: () => <div className="w-64 h-10" />,
});

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
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="sticky top-0 z-40 w-full border-b border-glass-border bg-glass-surface/80 backdrop-blur-xl"
    >
      <nav className="container flex items-center justify-between h-16" aria-label="Global">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2 group">
          <motion.div
            whileHover={{ rotate: 360, scale: 1.1 }}
            transition={{ duration: 0.6 }}
            className="w-10 h-10 bg-gradient-to-br from-cosmic-primary to-cosmic-blue rounded-xl flex items-center justify-center shadow-glow-purple"
          >
            <span className="text-white font-bold text-lg">C</span>
          </motion.div>
          <span className="text-xl font-bold text-gradient">Course Companion</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:items-center md:gap-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <motion.div key={item.name} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  href={item.href}
                  className={cn(
                    'px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200',
                    isActive
                      ? 'bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white shadow-glow-purple'
                      : 'text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.name}
                </Link>
              </motion.div>
            );
          })}

          {/* Divider */}
          <div className="w-px h-6 bg-glass-border mx-2" />

          {/* AI Features */}
          {aiFeatures.map((item) => {
            const isActive = pathname === item.href;
            return (
              <motion.div key={item.name} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  href={item.href}
                  className={cn(
                    'px-3 py-2 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2',
                    isActive
                      ? 'bg-gradient-to-r from-cosmic-pink to-cosmic-purple text-white shadow-nebula'
                      : 'text-text-secondary hover:text-cosmic-purple hover:bg-cosmic-purple/10'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.name}
                  <motion.span
                    whileHover={{ scale: 1.1 }}
                    className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white"
                  >
                    {item.badge}
                  </motion.span>
                </Link>
              </motion.div>
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
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('user_id');
              localStorage.removeItem('user_email');
              localStorage.removeItem('user_role');
              localStorage.removeItem('user_tier');
              window.location.href = '/login';
            }}
            title="Logout"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </Button>
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
            <AnimatePresence mode="wait">
              {mobileMenuOpen ? (
                <motion.svg
                  key="close"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </motion.svg>
              ) : (
                <motion.svg
                  key="menu"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </motion.svg>
              )}
            </AnimatePresence>
          </Button>
        </div>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden border-t border-glass-border bg-glass-surface backdrop-blur-xl overflow-hidden"
          >
            <div className="container px-2 py-3 space-y-1">
              {navigation.map((item, index) => {
                const isActive = pathname === item.href;
                return (
                  <motion.div
                    key={item.name}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Link
                      href={item.href}
                      className={cn(
                        'block px-4 py-2 rounded-xl text-base font-semibold transition-all duration-200',
                        isActive
                          ? 'bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white'
                          : 'text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10'
                      )}
                      aria-current={isActive ? 'page' : undefined}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  </motion.div>
                );
              })}

              {/* AI Features Section */}
              <div className="pt-4 pb-2">
                <div className="px-4 py-2 text-xs font-bold text-cosmic-primary uppercase tracking-wider">
                  AI Features
                </div>
              </div>
              {aiFeatures.map((item, index) => {
                const isActive = pathname === item.href;
                return (
                  <motion.div
                    key={item.name}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.2 + index * 0.05 }}
                  >
                    <Link
                      href={item.href}
                      className={cn(
                        'block px-4 py-2 rounded-xl text-base font-semibold transition-all duration-200 flex items-center justify-between',
                        isActive
                          ? 'bg-gradient-to-r from-cosmic-pink to-cosmic-purple text-white'
                          : 'text-text-secondary hover:text-cosmic-purple hover:bg-cosmic-purple/10'
                      )}
                      aria-current={isActive ? 'page' : undefined}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white">
                        {item.badge}
                      </span>
                    </Link>
                  </motion.div>
                );
              })}

              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <Link
                  href="/profile"
                  className="block px-4 py-2 rounded-xl text-base font-semibold text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10 transition-all duration-200"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Profile
                </Link>
              </motion.div>

              {/* Logout Button */}
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.35 }}
              >
                <button
                  onClick={() => {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user_id');
                    localStorage.removeItem('user_email');
                    localStorage.removeItem('user_role');
                    localStorage.removeItem('user_tier');
                    window.location.href = '/login';
                  }}
                  className="w-full text-left px-4 py-2 rounded-xl text-base font-semibold text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all duration-200"
                >
                  Logout
                </button>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}

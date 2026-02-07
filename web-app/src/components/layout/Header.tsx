'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import { usePathname } from 'next/navigation';
import { BookOpen, Menu, X, User, LogOut, Home, FileText, ClipboardList, BarChart3, Brain, Sparkles, Search, Users, MessageSquare, GraduationCap, Target, Settings, AlertCircle, Infinity, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

// Dynamically import SearchBar to prevent SSR issues
const SearchBar = dynamic(() => import('@/components/SearchBar').then(mod => ({ default: mod.SearchBar })), {
  ssr: false,
  loading: () => <div className="w-64 h-10" />,
});

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Chapters', href: '/chapters', icon: FileText },
  { name: 'Quizzes', href: '/quizzes', icon: ClipboardList },
];

// Learning Tools dropdown (for mega menu)
const learningTools = [
  { name: 'Infinite Quiz', href: '/infinite-quiz', icon: Infinity },
  { name: 'Progress', href: '/progress', icon: BarChart3 },
  { name: 'Time Machine', href: '/time-machine', icon: Clock },
  { name: 'Mistake Bank', href: '/mistake-bank', icon: AlertCircle },
];

// Phase 3 AI Features (shown separately)
const aiFeatures = [
  { name: 'Adaptive Learning', href: '/adaptive-learning', icon: Brain, badge: 'AI' },
  { name: 'AI Mentor', href: '/ai-mentor', icon: Sparkles, badge: 'AI' },
];

// Teacher-specific navigation
const teacherNavigation = [
  { name: 'Teacher Dashboard', href: '/teacher-dashboard', icon: GraduationCap },
  { name: 'Students', href: '/teacher-dashboard/students', icon: Users },
  { name: 'Analytics', href: '/teacher-dashboard/analytics', icon: BarChart3 },
  { name: 'Content', href: '/teacher-dashboard/content', icon: FileText },
  { name: 'Engagement', href: '/teacher-dashboard/engagement', icon: MessageSquare },
];

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  // Get user role from localStorage
  const [userRole, setUserRole] = React.useState<string | null>(null);

  React.useEffect(() => {
    const role = localStorage.getItem('user_role');
    setUserRole(role);
  }, []);

  const isTeacher = userRole === 'teacher';
  const navigationToShow = isTeacher ? teacherNavigation : navigation;

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_tier');
    window.location.href = '/login';
  };

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="sticky top-0 z-40 w-full border-b border-glass-border bg-glass-surface/90 backdrop-blur-xl"
    >
      <nav className="container flex items-center justify-between h-16 px-4" aria-label="Global">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2 md:gap-3 group">
          <motion.div
            whileHover={{ scale: 1.1 }}
            transition={{ duration: 0.2 }}
            className="w-9 h-9 md:w-10 md:h-10 bg-gradient-to-br from-cosmic-primary to-cosmic-blue rounded-xl flex items-center justify-center shadow-glow-purple flex-shrink-0"
          >
            <BookOpen className="w-4 h-4 md:w-5 md:h-5 text-white" />
          </motion.div>
          <div className="hidden sm:block">
            <h1 className="text-base md:text-lg font-bold text-gradient whitespace-nowrap">Course Companion</h1>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex lg:items-center lg:gap-1.5 ml-4">
          {navigationToShow.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <motion.div key={item.name} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link
                  href={item.href}
                  className={cn(
                    'px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 whitespace-nowrap',
                    isActive
                      ? 'bg-gradient-to-r from-cosmic-primary/20 to-cosmic-purple/20 text-cosmic-primary border border-cosmic-primary/30'
                      : 'text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {item.name}
                </Link>
              </motion.div>
            );
          })}

          {/* Divider - hide for teachers */}
          {!isTeacher && <div className="w-px h-6 bg-glass-border mx-2" />}

          {/* AI Features - hide for teachers */}
          {!isTeacher && (
            <>
              {aiFeatures.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <motion.div key={item.name} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Link
                      href={item.href}
                      className={cn(
                        'px-2 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1.5 whitespace-nowrap',
                        isActive
                          ? 'bg-gradient-to-r from-cosmic-pink/20 to-cosmic-purple/20 text-cosmic-purple border border-cosmic-purple/30'
                          : 'text-text-secondary hover:text-cosmic-purple hover:bg-cosmic-purple/10'
                      )}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      <span className="hidden xl:inline">{item.name}</span>
                      <motion.span
                        whileHover={{ scale: 1.1 }}
                        className="px-1 py-0.5 rounded text-[10px] font-bold bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white flex-shrink-0"
                      >
                        {item.badge}
                      </motion.span>
                    </Link>
                  </motion.div>
                );
              })}

              {/* Learning Tools Dropdown */}
              <div className="relative group">
                <button className="px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10">
                  <Target className="w-4 h-4" />
                  <span className="hidden xl:inline">Learning Tools</span>
                </button>
                <div className="absolute top-full left-0 mt-2 w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="bg-bg-elevated border border-border-default rounded-xl shadow-xl p-2">
                    {learningTools.map((item) => {
                      const isActive = pathname === item.href;
                      const Icon = item.icon;
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className={cn(
                            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                            isActive
                              ? 'bg-cosmic-primary/20 text-cosmic-primary'
                              : 'text-text-secondary hover:bg-cosmic-primary/10 hover:text-cosmic-primary'
                          )}
                        >
                          <Icon className="w-4 h-4 flex-shrink-0" />
                          {item.name}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Search Bar */}
          <div className="w-56 ml-2">
            <SearchBar placeholder="Search..." />
          </div>
        </div>

        {/* User menu - desktop */}
        <div className="hidden lg:flex lg:items-center lg:gap-2">
          <Link href="/profile">
            <Button variant="ghost" size="sm" className="gap-2">
              <User className="w-4 h-4" />
              <span className="hidden xl:inline">Profile</span>
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            title="Logout"
            className="gap-2 text-red-400 hover:text-red-300 hover:bg-red-500/10"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden xl:inline">Logout</span>
          </Button>
        </div>

        {/* Mobile menu button */}
        <div className="flex lg:hidden items-center gap-2">
          <Link href="/profile" className="p-2">
            <User className="w-5 h-5 text-text-secondary hover:text-cosmic-primary" />
          </Link>
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
                <motion.div
                  key="close"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.2 }}
                >
                  <X className="w-6 h-6" />
                </motion.div>
              ) : (
                <motion.div
                  key="menu"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.2 }}
                >
                  <Menu className="w-6 h-6" />
                </motion.div>
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
            className="lg:hidden border-t border-glass-border bg-glass-surface backdrop-blur-xl overflow-hidden"
          >
            <div className="container px-2 py-3 space-y-1">
              {navigationToShow.map((item, index) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
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
                        'flex items-center gap-3 px-4 py-3 rounded-xl text-base font-semibold transition-all duration-200',
                        isActive
                          ? 'bg-gradient-to-r from-cosmic-primary/20 to-cosmic-purple/20 text-cosmic-primary border border-cosmic-primary/30'
                          : 'text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10'
                      )}
                      aria-current={isActive ? 'page' : undefined}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <Icon className="w-5 h-5" />
                      {item.name}
                    </Link>
                  </motion.div>
                );
              })}

              {/* AI Features Section - hide for teachers */}
              {!isTeacher && (
                <>
                  <div className="pt-4 pb-2">
                    <div className="px-4 py-2 text-xs font-bold text-cosmic-primary uppercase tracking-wider">
                      AI Features
                    </div>
                  </div>
                  {aiFeatures.map((item, index) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
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
                        'flex items-center justify-between px-4 py-3 rounded-xl text-base font-semibold transition-all duration-200',
                        isActive
                          ? 'bg-gradient-to-r from-cosmic-pink/20 to-cosmic-purple/20 text-cosmic-purple border border-cosmic-purple/30'
                          : 'text-text-secondary hover:text-cosmic-purple hover:bg-cosmic-purple/10'
                      )}
                      aria-current={isActive ? 'page' : undefined}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="w-5 h-5" />
                        {item.name}
                      </div>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white">
                        {item.badge}
                      </span>
                    </Link>
                  </motion.div>
                );
              })}
                </>

                {/* Learning Tools Section - hide for teachers */}
                {!isTeacher && (
                  <>
                    <div className="pt-4 pb-2">
                      <div className="px-4 py-2 text-xs font-bold text-accent-warning uppercase tracking-wider">
                        Learning Tools
                      </div>
                    </div>
                    {learningTools.map((item, index) => {
                      const isActive = pathname === item.href;
                      const Icon = item.icon;
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
                              'flex items-center gap-3 px-4 py-3 rounded-xl text-base font-semibold transition-all duration-200',
                              isActive
                                ? 'bg-gradient-to-r from-accent-warning/20 to-accent-warning/10 text-accent-warning border border-accent-warning/30'
                                : 'text-text-secondary hover:text-accent-warning hover:bg-accent-warning/10'
                            )}
                            aria-current={isActive ? 'page' : undefined}
                            onClick={() => setMobileMenuOpen(false)}
                          >
                            <Icon className="w-5 h-5" />
                            {item.name}
                          </Link>
                        </motion.div>
                      );
                    })}
                  </>
                )}

                {/* Search bar for mobile */}
                <div className="px-2 py-3">
                <SearchBar placeholder="Search..." />
              </div>

              {/* Logout Button */}
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-base font-semibold text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all duration-200"
                >
                  <LogOut className="w-5 h-5" />
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

/**
 * Enhanced Individual chapter page with improved UI/UX
 * Features: Nebula theme, code highlighting, table of contents, reading progress
 */
'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer } from '@/components/layout/PageContainer';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { useChapter, useProgress, useChapters, backendApi } from '@/hooks';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  BookOpen,
  Clock,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  List,
  X,
  ArrowLeft,
  Sparkles,
  Target,
  Lightbulb,
  FileCode,
} from 'lucide-react';

export default function ChapterPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: chapter, isLoading } = useChapter(params.id);
  const { data: progress } = useProgress();
  const { data: allChapters } = useChapters();
  const [showTableOfContents, setShowTableOfContents] = useState(false);
  const [readingProgress, setReadingProgress] = useState(0);
  const [activeSection, setActiveSection] = useState('');

  // Get total chapter count dynamically
  const totalChapters = allChapters?.length || 4;

  // Get current user ID from localStorage
  const getUserId = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('user_id') || '00000000-0000-0000-0000-000000000001';
    }
    return '00000000-0000-0000-0000-000000000001';
  };

  const isCompleted = progress?.completed_chapters?.includes(params.id);

  const markCompleteMutation = useMutation({
    mutationFn: () => backendApi.updateProgress(getUserId(), params.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['progress'] });
      queryClient.invalidateQueries({ queryKey: ['chapters'] });
    },
  });

  // Track reading progress
  useEffect(() => {
    const handleScroll = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.scrollY;
      const progress = (scrollTop / (documentHeight - windowHeight)) * 100;
      setReadingProgress(Math.min(progress, 100));

      // Update active section based on scroll position
      const headings = document.querySelectorAll('.book-content h2');
      headings.forEach((heading) => {
        const rect = heading.getBoundingClientRect();
        if (rect.top >= 0 && rect.top < 200) {
          setActiveSection(heading.textContent || '');
        }
      });
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Extract table of contents from content
  const extractTableOfContents = (content: string) => {
    if (!content) return [];
    const headings = content.match(/^##\s+(.+)$/gm) || [];
    return headings.map((h) => h.replace('## ', '').trim());
  };

  const tableOfContents = chapter?.content ? extractTableOfContents(chapter.content) : [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!chapter) {
    return (
      <PageContainer>
        <div className="text-center py-12">
          <div className="w-20 h-20 mx-auto mb-4 rounded-xl bg-gradient-to-br from-cosmic-primary/20 via-cosmic-purple/20 to-cosmic-pink/20 flex items-center justify-center shadow-lg shadow-cosmic-purple/20">
            <BookOpen className="w-12 h-12 text-cosmic-primary" />
          </div>
          <h1 className="text-2xl font-bold text-text-primary">Chapter not found</h1>
          <p className="text-text-secondary mt-2">The chapter you're looking for doesn't exist.</p>
          <Link href="/chapters">
            <Button variant="outline" className="mt-6">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Chapters
            </Button>
          </Link>
        </div>
      </PageContainer>
    );
  }

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: {
        variant: 'beginner' as const,
        label: 'Beginner',
        color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-emerald-500/10',
        icon: <Target className="w-3.5 h-3.5" />
      },
      intermediate: {
        variant: 'intermediate' as const,
        label: 'Intermediate',
        color: 'bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-amber-500/10',
        icon: <Lightbulb className="w-3.5 h-3.5" />
      },
      advanced: {
        variant: 'advanced' as const,
        label: 'Advanced',
        color: 'bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-rose-500/10',
        icon: <Sparkles className="w-3.5 h-3.5" />
      },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  const difficultyBadge = getDifficultyBadge(chapter.difficulty_level);

  return (
    <PageContainer>
      {/* Breadcrumbs */}
      <Breadcrumbs />

      {/* Reading Progress Bar (Fixed at top) */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-bg-elevated z-50">
        <div
          className="h-full bg-gradient-to-r from-cosmic-primary via-cosmic-purple to-cosmic-pink transition-all duration-300"
          style={{ width: `${readingProgress}%` }}
        />
      </div>

      {/* Table of Contents Sidebar (Mobile) */}
      {showTableOfContents && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowTableOfContents(false)} />
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-bg-elevated border-l border-border-subtle shadow-xl overflow-y-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-text-primary flex items-center gap-2">
                  <List className="w-5 h-5 text-cosmic-primary" />
                  Contents
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowTableOfContents(false)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
              <nav className="space-y-2">
                {tableOfContents.map((item, index) => (
                  <a
                    key={index}
                    href={`#section-${index}`}
                    className={`block py-2 px-3 rounded-lg text-sm transition-all ${
                      activeSection === item
                        ? 'bg-cosmic-primary/10 text-cosmic-primary font-medium'
                        : 'text-text-secondary hover:bg-bg-primary hover:text-text-primary'
                    }`}
                    onClick={() => setShowTableOfContents(false)}
                  >
                    {item}
                  </a>
                ))}
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Chapter Container */}
      <div className="max-w-5xl mx-auto">
        {/* Chapter Header */}
        <div className="mb-8 pb-8 border-b border-border-subtle">
          {/* Back Button */}
          <Link href="/chapters">
            <Button variant="ghost" size="sm" className="mb-4 text-text-secondary hover:text-text-primary group">
              <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
              Back to Chapters
            </Button>
          </Link>

          {/* Chapter Meta */}
          <div className="flex flex-wrap items-center gap-3 mb-5">
            <span className="text-xs font-bold text-text-primary bg-gradient-to-r from-cosmic-primary/20 via-cosmic-purple/20 to-cosmic-pink/20 border border-cosmic-primary/30 px-4 py-1.5 rounded-full shadow-sm">
              Chapter {chapter.order}
            </span>
            <Badge className={`${difficultyBadge.color} shadow-sm`}>
              {difficultyBadge.icon}
              <span className="ml-1.5">{difficultyBadge.label}</span>
            </Badge>
            <span className="text-sm text-text-muted flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              {chapter.estimated_time} min read
            </span>
            {isCompleted && (
              <Badge variant="success" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-sm">
                <CheckCircle2 className="w-4 h-4 mr-1" />
                Completed
              </Badge>
            )}
          </div>

          {/* Chapter Title */}
          <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4 leading-tight">
            <span className="bg-gradient-to-r from-cosmic-primary via-cosmic-purple to-cosmic-pink bg-clip-text text-transparent">
              {chapter.title}
            </span>
          </h1>

          {/* Table of Contents Toggle (Mobile) */}
          <div className="lg:hidden">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowTableOfContents(true)}
              className="text-sm"
            >
              <List className="w-4 h-4 mr-2" />
              Table of Contents
            </Button>
          </div>
        </div>

        {/* Desktop Table of Contents Sidebar */}
        <div className="hidden lg:block fixed right-8 top-32 w-64 max-h-[calc(100vh-200px)] overflow-y-auto">
          <div className="sticky top-8">
            <div className="bg-bg-elevated rounded-lg border border-border-subtle p-4 shadow-lg">
              <h3 className="font-semibold text-text-primary mb-3 flex items-center gap-2 text-sm">
                <FileCode className="w-4 h-4 text-cosmic-primary" />
                On This Page
              </h3>
              <nav className="space-y-1">
                {tableOfContents.map((item, index) => (
                  <a
                    key={index}
                    href={`#section-${index}`}
                    className={`block py-1.5 px-2 rounded text-xs transition-all ${
                      activeSection === item
                        ? 'bg-cosmic-primary/10 text-cosmic-primary font-medium border-l-2 border-cosmic-primary'
                        : 'text-text-secondary hover:bg-bg-primary hover:text-text-primary'
                    }`}
                  >
                    {item}
                  </a>
                ))}
              </nav>
            </div>
          </div>
        </div>

        {/* Enhanced Book Content */}
        <div className="bg-gradient-to-br from-bg-elevated via-bg-elevated to-bg-elevated/50 rounded-xl border border-border-subtle p-8 md:p-12 mb-8 shadow-lg shadow-cosmic-purple/5 relative overflow-hidden">
          {/* Decorative gradient elements */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-cosmic-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-cosmic-pink/5 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />

          <article className="prose prose-invert prose-lg max-w-none book-content relative z-10">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children, id }) => (
                  <h1 id={id} className="text-3xl font-bold text-text-primary mt-10 mb-5 first:mt-0 scroll-mt-24">
                    {children}
                  </h1>
                ),
                h2: ({ children, id }) => (
                  <h2
                    id={id || `section-${tableOfContents.indexOf(String(children))}`}
                    className="text-2xl font-semibold text-text-primary mt-12 mb-5 flex items-center gap-3 scroll-mt-24"
                  >
                    <span className="flex-1">{children}</span>
                    <a href={`#${id}`} className="opacity-0 hover:opacity-100 transition-opacity text-cosmic-primary">
                      <FileCode className="w-5 h-5" />
                    </a>
                  </h2>
                ),
                h3: ({ children, id }) => (
                  <h3 id={id} className="text-xl font-semibold text-text-primary mt-8 mb-4 scroll-mt-24">
                    {children}
                  </h3>
                ),
                h4: ({ children }) => (
                  <h4 className="text-lg font-medium text-text-primary mt-6 mb-3">
                    {children}
                  </h4>
                ),
                p: ({ children }) => (
                  <p className="text-text-secondary leading-8 mb-6 text-justify">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="space-y-3 mb-6 ml-6 list-none">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="space-y-3 mb-6 ml-6 list-decimal marker:text-cosmic-primary">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="text-text-secondary leading-7 flex items-start gap-3">
                    <span className="text-cosmic-primary mt-1">•</span>
                    <span>{children}</span>
                  </li>
                ),
                code: ({ className, children }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 text-cosmic-primary px-2 py-1 rounded-md text-sm font-mono border border-cosmic-primary/20">
                      {children}
                    </code>
                  ) : (
                    <code className={className}>{children}</code>
                  );
                },
                pre: ({ children }) => (
                  <div className="relative group mb-6">
                    <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="text-xs text-text-muted bg-bg-elevated px-2 py-1 rounded">
                        {String(children).match(/class="language-(\w+)"/)?.[1] || 'code'}
                      </span>
                    </div>
                    <pre className="bg-gradient-to-br from-bg-primary to-bg-elevated border border-cosmic-primary/20 rounded-xl p-5 overflow-x-auto shadow-lg">
                      {children}
                    </pre>
                  </div>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-cosmic-primary pl-6 py-4 my-6 bg-gradient-to-r from-cosmic-primary/5 to-transparent rounded-r-lg italic text-text-secondary">
                    {children}
                  </blockquote>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    className="text-cosmic-primary hover:text-cosmic-pink underline decoration-cosmic-primary/30 hover:decoration-cosmic-pink/50 underline-offset-4 font-medium transition-all"
                  >
                    {children}
                  </a>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-6 rounded-xl border border-border-subtle overflow-hidden">
                    <table className="min-w-full divide-y divide-border-subtle">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10">
                    {children}
                  </thead>
                ),
                th: ({ children }) => (
                  <th className="px-6 py-4 text-left text-xs font-bold text-text-primary uppercase tracking-wider">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-6 py-4 text-sm text-text-secondary">
                    {children}
                  </td>
                ),
                hr: () => (
                  <hr className="my-8 border-t border-cosmic-primary/20" />
                ),
                strong: ({ children }) => (
                  <strong className="text-text-primary font-semibold">
                    {children}
                  </strong>
                ),
              }}
            >
              {chapter.content || '*No content available for this chapter yet.*'}
            </ReactMarkdown>
          </article>
        </div>

        {/* Progress Summary */}
        <div className="mb-6 p-5 bg-gradient-to-r from-cosmic-primary/10 via-cosmic-purple/10 to-cosmic-pink/10 rounded-xl border border-cosmic-primary/20">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-text-primary flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-cosmic-primary" />
              Course Progress
            </span>
            <span className="text-sm font-bold text-cosmic-primary">
              Chapter {chapter.order} of {totalChapters}
            </span>
          </div>
          <div className="w-full bg-bg-elevated rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cosmic-primary via-cosmic-purple to-cosmic-pink rounded-full transition-all duration-500"
              style={{ width: `${(chapter.order / totalChapters) * 100}%` }}
            />
          </div>
          <p className="text-xs text-text-muted mt-2">
            {Math.round((chapter.order / totalChapters) * 100)}% complete • {totalChapters - chapter.order} chapters remaining
          </p>
        </div>

        {/* Enhanced Action Bar */}
        <Card className="border-t-4 border-cosmic-primary shadow-lg shadow-cosmic-primary/10">
          <div className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap gap-3">
                <Button
                  variant={isCompleted ? 'secondary' : 'primary'}
                  size="lg"
                  onClick={() => markCompleteMutation.mutate()}
                  disabled={isCompleted || markCompleteMutation.isPending}
                  isLoading={markCompleteMutation.isPending}
                  className="min-w-[180px] shadow-lg shadow-cosmic-primary/20"
                >
                  {isCompleted ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 mr-2" />
                      Chapter Complete
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-5 h-5 mr-2" />
                      Mark as Complete
                    </>
                  )}
                </Button>

                {chapter.quiz_id && (
                  <Link href={`/quizzes/${chapter.quiz_id}`}>
                    <Button
                      variant="outline"
                      size="lg"
                      className="min-w-[180px] border-cosmic-primary/30 hover:border-cosmic-primary hover:bg-cosmic-primary/10"
                    >
                      <Sparkles className="w-5 h-5 mr-2" />
                      Take Quiz
                    </Button>
                  </Link>
                )}
              </div>

              <div className="flex items-center gap-2 text-sm text-text-muted">
                <Clock className="w-4 h-4" />
                {readingProgress.toFixed(0)}% read
              </div>
            </div>
          </div>
        </Card>

        {/* Chapter Navigation */}
        <div className="mt-8 flex justify-between items-center">
          <Link href="/chapters">
            <Button variant="outline" className="group">
              <List className="w-4 h-4 mr-2" />
              All Chapters
            </Button>
          </Link>
        </div>
      </div>

      {/* Enhanced Custom CSS */}
      <style jsx global>{`
        .book-content {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
          line-height: 1.8;
          color: #e2e8f0;
        }

        .book-content h1,
        .book-content h2,
        .book-content h3,
        .book-content h4 {
          color: #f1f5f9;
          font-weight: 600;
        }

        .book-content p {
          margin-bottom: 1.5rem;
        }

        .book-content code {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
          color: #a78bfa;
          padding: 0.2rem 0.5rem;
          border-radius: 0.375rem;
          font-size: 0.875em;
          border: 1px solid rgba(139, 92, 246, 0.2);
        }

        .book-content pre {
          background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
          border: 1px solid rgba(139, 92, 246, 0.2);
          border-radius: 0.75rem;
          padding: 1.25rem;
          overflow-x: auto;
          margin-bottom: 1.5rem;
        }

        .book-content pre code {
          background: transparent;
          padding: 0;
          color: #e2e8f0;
          border: none;
        }

        .book-content blockquote {
          border-left: 4px solid #8b5cf6;
          padding-left: 1.5rem;
          margin: 1.5rem 0;
          color: #94a3b8;
          font-style: italic;
          background: linear-gradient(90deg, rgba(139, 92, 246, 0.05) 0%, transparent 100%);
        }

        .book-content ul,
        .book-content ol {
          margin-bottom: 1.5rem;
        }

        .book-content li {
          margin-bottom: 0.75rem;
        }

        .book-content a {
          color: #8b5cf6;
          text-decoration: underline;
          text-decoration-thickness: 1px;
          text-underline-offset: 4px;
          transition: all 0.2s ease;
        }

        .book-content a:hover {
          color: #ec4899;
          text-decoration-color: #ec4899;
        }

        .book-content table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 1.5rem;
        }

        .book-content th,
        .book-content td {
          padding: 0.875rem;
          text-align: left;
          border-bottom: 1px solid #334155;
        }

        .book-content th {
          background: linear-gradient(90deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
          font-weight: 600;
          color: #f1f5f9;
        }

        .book-content tr:hover {
          background: rgba(139, 92, 246, 0.05);
        }

        .book-content img {
          max-width: 100%;
          height: auto;
          border-radius: 0.75rem;
          margin: 1.5rem 0;
          box-shadow: 0 10px 40px rgba(139, 92, 246, 0.1);
        }

        .book-content hr {
          border: none;
          border-top: 2px solid rgba(139, 92, 246, 0.2);
          margin: 2rem 0;
        }

        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }

        /* Custom scrollbar for book content */
        .book-content::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }

        .book-content::-webkit-scrollbar-track {
          background: rgba(139, 92, 246, 0.05);
          border-radius: 4px;
        }

        .book-content::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #8b5cf6 0%, #ec4899 100%);
          border-radius: 4px;
        }

        .book-content::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #a78bfa 0%, #f472b6 100%);
        }
      `}</style>
    </PageContainer>
  );
}

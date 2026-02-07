/**
 * Individual chapter page - Book-like reader experience.
 */
'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer } from '@/components/layout/PageContainer';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { useChapter, useProgress, backendApi } from '@/hooks';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BookOpen } from 'lucide-react';

export default function ChapterPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: chapter, isLoading } = useChapter(params.id);
  const { data: progress } = useProgress();

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
          <div className="w-20 h-20 mx-auto mb-4 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
            <BookOpen className="w-12 h-12 text-cosmic-primary" />
          </div>
          <h1 className="text-2xl font-bold text-text-primary">Chapter not found</h1>
          <p className="text-text-secondary mt-2">The chapter you're looking for doesn't exist.</p>
          <Link href="/chapters">
            <Button variant="outline" className="mt-6">
              ← Back to Chapters
            </Button>
          </Link>
        </div>
      </PageContainer>
    );
  }

  const getDifficultyBadge = (level: string) => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner', color: 'bg-green-500/10 text-green-400 border-green-500/20' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate', color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' },
      advanced: { variant: 'advanced' as const, label: 'Advanced', color: 'bg-red-500/10 text-red-400 border-red-500/20' },
    };
    return badges[level.toLowerCase() as keyof typeof badges] || badges.beginner;
  };

  const difficultyBadge = getDifficultyBadge(chapter.difficulty_level);

  return (
    <PageContainer>
      {/* Breadcrumbs */}
      <Breadcrumbs />

      {/* Book-like Reader Container */}
      <div className="max-w-4xl mx-auto">
        {/* Chapter Header */}
        <div className="mb-8 pb-6 border-b border-border-default">
          {/* Back Button */}
          <Link href="/chapters">
            <Button variant="ghost" size="sm" className="mb-4 text-text-secondary hover:text-text-primary">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Chapters
            </Button>
          </Link>

          {/* Chapter Meta */}
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <span className="text-xs font-semibold text-text-secondary bg-bg-elevated border border-border-subtle px-3 py-1.5 rounded-full">
              Chapter {chapter.order}
            </span>
            <Badge className={difficultyBadge.color}>
              {difficultyBadge.label}
            </Badge>
            <span className="text-sm text-text-muted flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {chapter.estimated_time} min read
            </span>
            {isCompleted && (
              <Badge variant="success" className="bg-green-500/10 text-green-400 border-green-500/20">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Completed
              </Badge>
            )}
          </div>

          {/* Chapter Title */}
          <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4 leading-tight">
            {chapter.title}
          </h1>

          {/* Chapter Description/Intro */}
          {chapter.content && (
            <p className="text-lg text-text-secondary leading-relaxed">
              Learn the fundamentals and master the concepts step by step.
            </p>
          )}
        </div>

        {/* Book Content - Typography focused */}
        <div className="bg-bg-elevated rounded-lg border border-border-subtle p-8 md:p-12 mb-8 shadow-sm">
          <article className="prose prose-invert prose-lg max-w-none book-content">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Custom heading styles
                h1: ({ children }) => (
                  <h1 className="text-3xl font-bold text-text-primary mt-8 mb-4 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-2xl font-semibold text-text-primary mt-8 mb-4 flex items-center gap-3">
                    <span className="flex-1">{children}</span>
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-xl font-semibold text-text-primary mt-6 mb-3">
                    {children}
                  </h3>
                ),
                // Custom paragraph styles
                p: ({ children }) => (
                  <p className="text-text-secondary leading-8 mb-6">
                    {children}
                  </p>
                ),
                // Custom list styles
                ul: ({ children }) => (
                  <ul className="space-y-3 mb-6 ml-6 list-disc">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="space-y-3 mb-6 ml-6 list-decimal">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="text-text-secondary leading-7">
                    {children}
                  </li>
                ),
                // Custom code block styles
                code: ({ className, children }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="bg-bg-primary text-accent-secondary px-2 py-1 rounded text-sm font-mono">
                      {children}
                    </code>
                  ) : (
                    <code className={className}>{children}</code>
                  );
                },
                pre: ({ children }) => (
                  <pre className="bg-bg-primary border border-border-subtle rounded-lg p-4 mb-6 overflow-x-auto">
                    {children}
                  </pre>
                ),
                // Custom blockquote styles
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-accent-primary pl-6 py-2 my-6 bg-accent-primary/5 italic text-text-secondary">
                    {children}
                  </blockquote>
                ),
                // Custom link styles
                a: ({ href, children }) => (
                  <a href={href} className="text-accent-primary hover:text-accent-secondary underline font-medium">
                    {children}
                  </a>
                ),
                // Custom table styles
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-6">
                    <table className="min-w-full divide-y divide-border-subtle">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-bg-elevated">{children}</thead>
                ),
                th: ({ children }) => (
                  <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">
                    {children}
                  </td>
                ),
              }}
            >
              {chapter.content || '*No content available for this chapter yet.*'}
            </ReactMarkdown>
          </article>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-muted">Reading Progress</span>
            <span className="text-sm font-medium text-text-primary">Chapter {chapter.order} of 10</span>
          </div>
          <div className="w-full bg-bg-elevated rounded-full h-2">
            <div
              className="bg-accent-primary h-2 rounded-full transition-all"
              style={{ width: `${(chapter.order / 10) * 100}%` }}
            />
          </div>
        </div>

        {/* Action Bar */}
        <Card className="border-t-4 border-accent-primary">
          <div className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap gap-3">
                <Button
                  variant={isCompleted ? 'secondary' : 'primary'}
                  size="lg"
                  onClick={() => markCompleteMutation.mutate()}
                  disabled={isCompleted || markCompleteMutation.isPending}
                  isLoading={markCompleteMutation.isPending}
                  className="min-w-[160px]"
                >
                  {isCompleted ? (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Chapter Complete
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Mark as Complete
                    </>
                  )}
                </Button>

                {chapter.quiz_id && (
                  <Link href={`/quizzes/${chapter.quiz_id}`}>
                    <Button variant="outline" size="lg" className="min-w-[160px]">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Take Quiz
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Chapter Navigation */}
        <div className="mt-8 flex justify-between items-center">
          <Link href={`/chapters`}>
            <Button variant="outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              All Chapters
            </Button>
          </Link>
        </div>
      </div>

      {/* Custom CSS for book styling */}
      <style jsx global>{`
        .book-content {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
          line-height: 1.8;
          color: #e2e8f0;
        }

        .book-content h1,
        .book-content h2,
        .book-content h3 {
          color: #f1f5f9;
          font-weight: 600;
        }

        .book-content p {
          margin-bottom: 1.5rem;
        }

        .book-content code {
          background: #1e293b;
          color: #38bdf8;
          padding: 0.2rem 0.4rem;
          border-radius: 0.25rem;
          font-size: 0.875em;
        }

        .book-content pre {
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 0.5rem;
          padding: 1rem;
          overflow-x: auto;
          margin-bottom: 1.5rem;
        }

        .book-content pre code {
          background: transparent;
          padding: 0;
          color: #e2e8f0;
        }

        .book-content blockquote {
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
          margin: 1.5rem 0;
          color: #94a3b8;
          font-style: italic;
        }

        .book-content ul,
        .book-content ol {
          margin-bottom: 1.5rem;
          padding-left: 1.5rem;
        }

        .book-content li {
          margin-bottom: 0.5rem;
        }

        .book-content a {
          color: #3b82f6;
          text-decoration: underline;
        }

        .book-content a:hover {
          color: #60a5fa;
        }

        .book-content table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 1.5rem;
        }

        .book-content th,
        .book-content td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #334155;
        }

        .book-content th {
          background: #1e293b;
          font-weight: 600;
        }

        .book-content img {
          max-width: 100%;
          height: auto;
          border-radius: 0.5rem;
          margin: 1.5rem 0;
        }

        .book-content hr {
          border: none;
          border-top: 1px solid #334155;
          margin: 2rem 0;
        }
      `}</style>
    </PageContainer>
  );
}

'use client';

import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { BookOpen, FileEdit, BarChart3, AlertTriangle, Info, Hourglass, Search, Trophy, Flame, Award, Inbox } from 'lucide-react';

/**
 * EmptyState component for consistent empty state UI across the app.
 *
 * Provides visual feedback when there's no data to display,
 * with optional action buttons to guide users.
 */
export interface EmptyStateProps {
  /** Icon or emoji to display */
  icon?: string | React.ReactNode;
  /** Title of the empty state */
  title: string;
  /** Description explaining why it's empty */
  description?: string;
  /** Optional action button text */
  actionLabel?: string;
  /** Optional action button href */
  actionHref?: string;
  /** Optional action button onClick handler */
  actionOnClick?: () => void;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Whether to show in a card */
  card?: boolean;
  /** Additional className */
  className?: string;
}

export function EmptyState({
  icon = <Inbox className="w-8 h-8" />,
  title,
  description,
  actionLabel,
  actionHref,
  actionOnClick,
  size = 'md',
  card = true,
  className = '',
}: EmptyStateProps) {
  const sizes = {
    sm: {
      icon: 'text-3xl',
      title: 'text-lg',
      padding: 'p-8',
    },
    md: {
      icon: 'text-4xl',
      title: 'text-xl',
      padding: 'p-12',
    },
    lg: {
      icon: 'text-6xl',
      title: 'text-2xl',
      padding: 'p-16',
    },
  };

  const sizeStyles = sizes[size];

  const content = (
    <div className={`text-center ${className}`}>
      {/* Icon */}
      {typeof icon === 'string' ? (
        <div className={`${sizeStyles.icon} mb-4`}>{icon}</div>
      ) : (
        <div className="mb-4 flex justify-center">{icon}</div>
      )}

      {/* Title */}
      <h3 className={`font-semibold ${sizeStyles.title} text-text-primary mb-2`}>
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className="text-text-secondary mt-2 max-w-md mx-auto">
          {description}
        </p>
      )}

      {/* Action Button */}
      {actionLabel && (actionHref || actionOnClick) && (
        <div className="mt-6">
          {actionHref ? (
            <Button variant="primary" asChild>
              <a href={actionHref}>{actionLabel}</a>
            </Button>
          ) : (
            <Button variant="primary" onClick={actionOnClick}>
              {actionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );

  if (card) {
    return (
      <Card>
        <CardContent className={`${sizeStyles.padding}`}>
          {content}
        </CardContent>
      </Card>
    );
  }

  return content;
}

/**
 * Pre-configured empty states for common scenarios
 */
export const EmptyStates = {
  NoChapters: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
        <BookOpen className="w-10 h-10 text-cosmic-primary" />
      </div>}
      title="No chapters available"
      description="Check back later for new course content."
      {...props}
    />
  ),

  NoQuizzes: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
        <FileEdit className="w-10 h-10 text-cosmic-primary" />
      </div>}
      title="No quizzes available"
      description="Quizzes will appear here as you progress through chapters."
      {...props}
    />
  ),

  NoProgress: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
        <BarChart3 className="w-10 h-10 text-cosmic-primary" />
      </div>}
      title="No progress yet"
      description="Start learning to track your progress."
      actionLabel="Browse Chapters"
      actionHref="/chapters"
      {...props}
    />
  ),

  NoSearchResults: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-primary/10 flex items-center justify-center">
        <Search className="w-6 h-6 text-accent-primary" />
      </div>}
      title="No results found"
      description="Try different keywords or browse categories."
      size="sm"
      {...props}
    />
  ),

  NoAchievements: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-accent-premium/20 to-accent-premium/10 flex items-center justify-center">
        <Trophy className="w-10 h-10 text-accent-premium" />
      </div>}
      title="No achievements yet"
      description="Complete chapters and quizzes to earn achievements!"
      actionLabel="Start Learning"
      actionHref="/chapters"
      {...props}
    />
  ),

  NoStreak: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
        <Flame className="w-6 h-6 text-accent-warning" />
      </div>}
      title="Start your streak"
      description="Practice daily to build a learning streak."
      size="sm"
      {...props}
    />
  ),

  Loading: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
        <Hourglass className="w-8 h-8 text-cosmic-primary" />
      </div>}
      title="Loading..."
      description="Please wait while we fetch your data."
      size="sm"
      card={false}
      {...props}
    />
  ),

  Error: (props?: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
        <AlertTriangle className="w-10 h-10 text-accent-warning" />
      </div>}
      title="Something went wrong"
      description="Unable to load data. Please try again later."
      actionLabel="Retry"
      actionOnClick={() => window.location.reload()}
      {...props}
    />
  ),
};

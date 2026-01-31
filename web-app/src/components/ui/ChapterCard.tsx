import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { Progress } from './Progress';
import { Badge } from './Badge';

export interface ChapterCardProps {
  id: string;
  title: string;
  description?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  progress: number;
  totalQuizzes?: number;
  completedQuizzes?: number;
  locked?: boolean;
  onClick?: () => void;
  className?: string;
}

export const ChapterCard = React.forwardRef<HTMLDivElement, ChapterCardProps>(
  ({
    id,
    title,
    description,
    difficulty,
    progress,
    totalQuizzes,
    completedQuizzes,
    locked = false,
    onClick,
    className,
  }, ref) => {
    const difficultyColors: Record<string, 'beginner' | 'intermediate' | 'advanced'> = {
      beginner: 'beginner',
      intermediate: 'intermediate',
      advanced: 'advanced',
    };

    return (
      <Card
        ref={ref}
        className={cn(
          'cursor-pointer transition-all duration-200',
          locked && 'opacity-60 cursor-not-allowed',
          !locked && 'hover:scale-[1.02] hover:shadow-lg',
          className
        )}
        onClick={!locked ? onClick : undefined}
      >
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <CardTitle className="text-lg">{title}</CardTitle>
                {locked && (
                  <svg className="w-4 h-4 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                )}
              </div>
              {difficulty && (
                <Badge variant={difficultyColors[difficulty]} className="mb-2">
                  {difficulty}
                </Badge>
              )}
            </div>
          </div>
          {description && (
            <p className="text-sm text-text-secondary line-clamp-2">{description}</p>
          )}
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-secondary">Progress</span>
              <span className="font-medium text-text-primary">{progress}%</span>
            </div>
            <Progress value={progress} size="sm" />
            {totalQuizzes !== undefined && completedQuizzes !== undefined && (
              <div className="flex items-center justify-between text-xs text-text-secondary">
                <span>{completedQuizzes} of {totalQuizzes} quizzes completed</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }
);

ChapterCard.displayName = 'ChapterCard';

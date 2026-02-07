/**
 * QuizCard component - displays quiz information with link to take quiz.
 */

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { FileEdit } from 'lucide-react';

interface QuizCardProps {
  id: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  chapterId: string;
  chapterTitle?: string;
  questionCount?: number;
  completed?: boolean;
  bestScore?: number;
}

export function QuizCard({
  id,
  title,
  difficulty,
  chapterId,
  chapterTitle,
  questionCount = 5,
  completed = false,
  bestScore,
}: QuizCardProps) {
  const getDifficultyBadge = () => {
    const badges = {
      beginner: { variant: 'beginner' as const, label: 'Beginner' },
      intermediate: { variant: 'intermediate' as const, label: 'Intermediate' },
      advanced: { variant: 'advanced' as const, label: 'Advanced' },
    };
    return badges[difficulty];
  };

  const difficultyBadge = getDifficultyBadge();

  return (
    <Link href={`/quizzes/${id}`} className="block group">
      <Card
        variant="default"
        className={`transition-all hover:shadow-lg ${
          completed
            ? 'border-accent-success/30 bg-accent-success/5'
            : 'border-border-default hover:border-accent-primary'
        }`}
      >
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={difficultyBadge.variant}>
                  {difficultyBadge.label}
                </Badge>
                {completed && (
                  <Badge variant="success">Completed</Badge>
                )}
              </div>
              <h3 className="font-semibold text-text-primary group-hover:text-accent-primary transition-colors mb-1">
                {title}
              </h3>
              {chapterTitle && (
                <p className="text-sm text-text-secondary mb-2">
                  Chapter: {chapterTitle}
                </p>
              )}
              <div className="flex items-center gap-4 text-sm text-text-muted">
                <span className="flex items-center gap-1">
                  <FileEdit className="w-4 h-4" />
                  {questionCount} questions
                </span>
                {bestScore !== undefined && (
                  <span className={bestScore >= 70 ? 'text-accent-success' : 'text-accent-warning'}>
                    Best: {bestScore}%
                  </span>
                )}
              </div>
            </div>
            <Button
              variant={completed ? 'secondary' : 'primary'}
              size="md"
              className="shrink-0"
            >
              {completed ? 'Retake' : 'Start Quiz'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

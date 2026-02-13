'use client';

/**
 * DifficultyBadge Component
 *
 * Standardized difficulty badge for course content.
 * Consistent styling and icons across chapters and quizzes.
 */

import * as React from 'react';
import { Badge } from '@/components/ui/Badge';
import { Sprout, TrendingUp, Rocket, type LucideIcon } from 'lucide-react';
import { DIFFICULTY_BADGE } from '@/lib/constants';

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced';

export interface DifficultyBadgeProps {
  level: DifficultyLevel;
  showLabel?: boolean;
  className?: string;
}

const DIFFICULTY_ICONS: Record<DifficultyLevel, LucideIcon> = {
  beginner: Sprout,
  intermediate: TrendingUp,
  advanced: Rocket,
};

export const DifficultyBadge = React.forwardRef<HTMLDivElement, DifficultyBadgeProps>(
  ({ level, showLabel = true, className }, ref) => {
    const config = DIFFICULTY_BADGE[level.toUpperCase() as keyof typeof DIFFICULTY_BADGE];
    const Icon = DIFFICULTY_ICONS[level];

    return (
      <Badge
        ref={ref}
        variant={config.variant}
        className={cn('gap-1', config.color, className)}
      >
        <Icon className="w-3 h-3" />
        {showLabel && config.label}
      </Badge>
    );
  }
);

DifficultyBadge.displayName = 'DifficultyBadge';

/**
 * Hook to get difficulty badge configuration
 */
export function useDifficultyBadge(level: string) {
  const normalizedLevel = level.toLowerCase() as DifficultyLevel;
  return DIFFICULTY_BADGE[normalizedLevel.toUpperCase() as keyof typeof DIFFICULTY_BADGE] || DIFFICULTY_BADGE.BEGINNER;
}

'use client';

import * as React from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import { Clock, Trophy } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card } from './Card';
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
    const [isHovered, setIsHovered] = React.useState(false);
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const rotateX = useTransform(mouseY, [-0.5, 0.5], [5, -5]);
    const rotateY = useTransform(mouseX, [-0.5, 0.5], [-5, 5]);

    const difficultyGradients: Record<string, string> = {
      beginner: 'from-green-400 to-emerald-500',
      intermediate: 'from-amber-400 to-orange-500',
      advanced: 'from-red-400 to-rose-500',
    };

    const difficultyBadges: Record<string, 'beginner' | 'intermediate' | 'advanced'> = {
      beginner: 'beginner',
      intermediate: 'intermediate',
      advanced: 'advanced',
    };

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
      if (locked) return;
      const rect = e.currentTarget.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      mouseX.set(x);
      mouseY.set(y);
    };

    const isComplete = progress >= 100;

    return (
      <motion.div
        ref={ref}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => {
          setIsHovered(false);
          mouseX.set(0);
          mouseY.set(0);
        }}
        style={{
          rotateX,
          rotateY,
          transformStyle: 'preserve-3d',
        }}
        whileHover={!locked ? { scale: 1.02 } : undefined}
        onClick={!locked ? onClick : undefined}
        className={cn(
          'relative cursor-pointer',
          locked && 'opacity-60 cursor-not-allowed',
          className
        )}
      >
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 p-6 shadow-xl">
          {/* Animated background gradient on hover */}
          {isHovered && !locked && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.1 }}
              className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20"
            />
          )}

          <div className="relative">
            {/* Difficulty badge */}
            {difficulty && (
              <motion.div
                whileHover={{ scale: 1.1 }}
                className={`inline-block px-3 py-1 rounded-full text-xs font-semibold text-white
                          bg-gradient-to-r ${difficultyGradients[difficulty]} mb-4`}
              >
                {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </motion.div>
            )}

            <motion.h3
              className="text-xl font-bold text-white mb-2"
              animate={isHovered ? { color: ['#ffffff', '#a855f7', '#ffffff'] } : {}}
              transition={{ duration: 0.5 }}
            >
              {title}
            </motion.h3>
            {description && (
              <p className="text-gray-400 text-sm mb-4 line-clamp-2">{description}</p>
            )}

            {/* Progress bar */}
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-400 mb-1">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} size="sm" color={isComplete ? 'green' : 'blue'} />
            </div>

            {/* Footer with icons */}
            <div className="flex items-center justify-between text-sm text-gray-400">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>30 min</span>
                </div>
              </div>
              {isComplete && (
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                  className="flex items-center gap-1 text-emerald-400"
                >
                  <Trophy className="h-5 w-5" />
                  <span className="font-semibold">Complete</span>
                </motion.div>
              )}
              {locked && (
                <div className="flex items-center gap-1 text-text-muted">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    );
  }
);

ChapterCard.displayName = 'ChapterCard';

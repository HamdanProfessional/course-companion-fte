'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'purple' | 'orange';
  showPercentage?: boolean;
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, max = 100, size = 'md', color = 'blue', showPercentage = false, ...props }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    const sizes = {
      sm: 'h-2',
      md: 'h-4',
      lg: 'h-6',
    };

    const gradients = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-emerald-400 to-teal-500',
      purple: 'from-purple-500 to-pink-600',
      orange: 'from-amber-400 to-orange-500',
    };

    const glowColors = {
      blue: 'shadow-blue-500/50',
      green: 'shadow-emerald-500/50',
      purple: 'shadow-purple-500/50',
      orange: 'shadow-orange-500/50',
    };

    return (
      <div className="w-full">
        <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden" {...props}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className={cn(
              'absolute left-0 top-0 bg-gradient-to-r rounded-full',
              gradients[color],
              sizes[size]
            )}
          />
          {percentage >= 100 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
              className={cn(
                'absolute inset-0 bg-gradient-to-r blur-lg rounded-full',
                gradients[color]
              )}
            />
          )}
        </div>
        {showPercentage && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-right text-sm text-gray-400 mt-1"
          >
            {Math.round(percentage)}%
          </motion.p>
        )}
      </div>
    );
  }
);

Progress.displayName = 'Progress';

// Circular Progress Component with animation
export interface CircularProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

export const CircularProgress = React.forwardRef<HTMLDivElement, CircularProgressProps>(
  ({ className, value, max = 100, size = 120, strokeWidth = 8, color = 'blue', ...props }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (percentage / 100) * circumference;

    const colors = {
      blue: '#3B82F6',
      green: '#10B981',
      purple: '#8B5CF6',
      orange: '#F59E0B',
    };

    return (
      <div ref={ref} className={cn('relative inline-flex items-center justify-center', className)} {...props}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-bg-elevated"
          />
          {/* Progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={colors[color]}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: 'easeOut' }}
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 8px ${colors[color]})` }}
          />
        </svg>
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="absolute text-lg font-semibold text-text-primary"
        >
          {Math.round(percentage)}%
        </motion.div>
      </div>
    );
  }
);

CircularProgress.displayName = 'CircularProgress';

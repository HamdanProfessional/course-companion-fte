'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'premium' | 'info' | 'beginner' | 'intermediate' | 'advanced';
  glow?: boolean;
}

export const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', glow = true, children, ...props }, ref) => {
    const variants = {
      default: 'bg-cosmic-secondary text-text-secondary border border-glass-border',
      success: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
      warning: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
      danger: 'bg-red-500/20 text-red-400 border border-red-500/30',
      premium: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
      info: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
      beginner: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
      intermediate: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
      advanced: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
    };

    const glowVariants = {
      default: '',
      success: 'shadow-glow-green',
      warning: 'shadow-glow-orange',
      danger: 'shadow-glow-red',
      premium: 'shadow-glow-purple',
      info: 'shadow-glow-blue',
      beginner: 'shadow-glow-green',
      intermediate: 'shadow-glow-blue',
      advanced: 'shadow-glow-purple',
    };

    return (
      <motion.div
        ref={ref}
        whileHover={glow ? { scale: 1.05 } : {}}
        className={cn(
          'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-sm transition-all',
          variants[variant],
          glow && glowVariants[variant as keyof typeof glowVariants],
          className
        )}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

Badge.displayName = 'Badge';

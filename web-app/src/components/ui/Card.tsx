'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'borderless' | 'cosmic' | 'glass';
  glow?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'cosmic', glow = false, ...props }, ref) => {
    const variants = {
      default: 'card',
      elevated: 'card-elevated',
      borderless: 'card-borderless',
      cosmic: 'bg-glass-surface border border-glass-border backdrop-blur-xl hover:shadow-glow-purple',
      glass: 'bg-glass-surface border border-glass-border backdrop-blur-xl',
    };

    return (
      <motion.div
        ref={ref}
        whileHover={glow ? { scale: 1.01, boxShadow: '0 0 40px rgba(139, 92, 246, 0.3)' } : {}}
        transition={{ duration: 0.2 }}
        className={cn('rounded-2xl relative overflow-hidden', variants[variant], className)}
        {...props}
      />
    );
  }
);

Card.displayName = 'Card';

export const CardHeader = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
    );
  }
);

CardHeader.displayName = 'CardHeader';

export const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => {
    return (
      <h3 ref={ref} className={cn('text-2xl font-bold leading-none tracking-tight text-text-primary', className)} {...props} />
    );
  }
);

CardTitle.displayName = 'CardTitle';

export const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => {
    return <p ref={ref} className={cn('text-sm text-text-secondary leading-relaxed', className)} {...props} />;
  }
);

CardDescription.displayName = 'CardDescription';

export const CardContent = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />;
  }
);

CardContent.displayName = 'CardContent';

export const CardFooter = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn('flex items-center p-6 pt-0', className)} {...props} />;
  }
);

CardFooter.displayName = 'CardFooter';

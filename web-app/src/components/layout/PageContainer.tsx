'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'full';
}

export function PageContainer({
  children,
  size = 'lg',
  className,
  ...props
}: PageContainerProps) {
  const sizes = {
    sm: 'max-w-4xl',
    md: 'max-w-5xl',
    lg: 'max-w-7xl',
    full: 'max-w-full',
  };

  return (
    <div
      className={cn('container mx-auto px-4 sm:px-6 lg:px-8 py-8', sizes[size], className)}
      {...props}
    >
      {children}
    </div>
  );
}

// Page header component for consistent page titles
export interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, description, actions, className }: PageHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn('mb-8', className)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <motion.h1
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl font-bold text-gradient tracking-tight"
          >
            {title}
          </motion.h1>
          {description && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-2 text-lg text-text-secondary leading-relaxed"
            >
              {description}
            </motion.p>
          )}
        </div>
        {actions && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="ml-4"
          >
            {actions}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

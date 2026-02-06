'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  cosmic?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, cosmic = true, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);

    return (
      <div className="w-full">
        <motion.div
          animate={isFocused ? { scale: 1.01 } : { scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <input
            type={type}
            ref={ref}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            className={cn(
              'flex h-11 w-full rounded-xl px-4 py-3 text-sm transition-all duration-200',
              'focus-visible:outline-none',
              'disabled:cursor-not-allowed disabled:opacity-50',
              cosmic
                ? 'bg-glass-surface border-glass-border text-text-primary placeholder-text-secondary focus:border-cosmic-primary focus:shadow-glow-purple focus:ring-1 focus:ring-cosmic-primary/50'
                : 'input',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500/50',
              className
            )}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={error ? `${props.id}-error` : undefined}
            {...props}
          />
        </motion.div>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-1 text-xs text-red-400"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Textarea component
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
  cosmic?: boolean;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, cosmic = true, ...props }, ref) => {
    return (
      <div className="w-full">
        <textarea
          ref={ref}
          className={cn(
            'flex min-h-[80px] w-full rounded-xl px-4 py-3 text-sm transition-all duration-200',
            'focus-visible:outline-none resize-y',
            'disabled:cursor-not-allowed disabled:opacity-50',
            cosmic
              ? 'bg-glass-surface border-glass-border text-text-primary placeholder-text-secondary focus:border-cosmic-primary focus:shadow-glow-purple focus:ring-1 focus:ring-cosmic-primary/50'
              : 'input',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500/50',
            className
          )}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${props.id}-error` : undefined}
          {...props}
        />
        {error && (
          <p id={`${props.id}-error`} className="mt-1 text-xs text-red-400">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

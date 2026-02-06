'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  cosmic?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, cosmic = true, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-xl font-semibold transition-all duration-200 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50';

    const variants = {
      primary: cosmic
        ? 'bg-gradient-to-r from-cosmic-primary via-cosmic-purple to-cosmic-blue text-white hover:shadow-glow-purple hover:scale-105'
        : 'btn-primary px-6 py-3 text-white',
      secondary: cosmic
        ? 'bg-glass-surface border border-glass-border text-text-primary hover:bg-glass-hover hover:border-cosmic-primary hover:shadow-glow-purple'
        : 'btn-secondary px-6 py-3',
      outline: cosmic
        ? 'border-2 border-cosmic-primary text-cosmic-primary hover:bg-cosmic-primary/10 hover:shadow-glow-purple hover:scale-105'
        : 'border-2 border-accent-primary text-accent-primary hover:bg-accent-primary/10 px-6 py-3',
      ghost: cosmic
        ? 'text-text-secondary hover:text-cosmic-primary hover:bg-cosmic-primary/10 hover:shadow-glow-purple'
        : 'btn-ghost px-6 py-3',
      danger: cosmic
        ? 'bg-gradient-to-r from-red-500 to-rose-600 text-white hover:shadow-glow-red hover:scale-105'
        : 'btn-danger px-6 py-3 text-white',
      success: cosmic
        ? 'bg-gradient-to-r from-emerald-400 to-teal-500 text-white hover:shadow-glow-green hover:scale-105'
        : 'btn-success px-6 py-3 text-white',
    };

    const sizes = {
      sm: 'h-9 text-sm px-4 py-2',
      md: 'h-10 text-base px-6 py-3',
      lg: 'h-12 text-lg px-8 py-4',
    };

    return (
      <motion.button
        ref={ref}
        disabled={disabled || isLoading}
        whileHover={cosmic ? { scale: 1.02 } : {}}
        whileTap={cosmic ? { scale: 0.98 } : {}}
        transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        className={cn(baseStyles, variants[variant], sizes[size], 'active:scale-95', className)}
        {...props}
      >
        {isLoading ? (
          <div className="flex items-center gap-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
            />
            Loading...
          </div>
        ) : children}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

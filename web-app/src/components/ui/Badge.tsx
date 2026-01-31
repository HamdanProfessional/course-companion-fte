import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'premium' | 'info' | 'beginner' | 'intermediate' | 'advanced';
}

export const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const variants = {
      default: 'badge-default',
      success: 'badge-success',
      warning: 'badge-warning',
      danger: 'badge-danger',
      premium: 'badge-premium',
      info: 'badge-info',
      beginner: 'badge-beginner',
      intermediate: 'badge-intermediate',
      advanced: 'badge-advanced',
    };

    return (
      <div
        ref={ref}
        className={cn('badge', variants[variant], className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Badge.displayName = 'Badge';

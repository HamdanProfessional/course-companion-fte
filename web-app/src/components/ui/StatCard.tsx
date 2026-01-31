import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from './Card';

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ title, value, change, icon, trend = 'neutral', className }, ref) => {
    const trendColors = {
      up: 'text-accent-success',
      down: 'text-accent-danger',
      neutral: 'text-text-secondary',
    };

    const trendIcons = {
      up: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      ),
      down: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      ),
      neutral: null,
    };

    return (
      <Card ref={ref} className={cn('hover:scale-[1.02]', className)}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-text-secondary">{title}</p>
              <p className="text-3xl font-bold text-text-primary mt-2">{value}</p>
              {change !== undefined && (
                <div className={cn('flex items-center gap-1 mt-2 text-sm', trendColors[trend])}>
                  {trendIcons[trend]}
                  <span>{Math.abs(change)}% from last week</span>
                </div>
              )}
            </div>
            {icon && (
              <div className="ml-4 flex h-12 w-12 items-center justify-center rounded-lg bg-bg-elevated text-accent-primary">
                {icon}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }
);

StatCard.displayName = 'StatCard';

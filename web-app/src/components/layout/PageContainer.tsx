import * as React from 'react';
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
    <div className={cn('mb-8', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-text-primary tracking-tight">{title}</h1>
          {description && (
            <p className="mt-2 text-lg text-text-secondary leading-relaxed">{description}</p>
          )}
        </div>
        {actions && <div className="ml-4">{actions}</div>}
      </div>
    </div>
  );
}

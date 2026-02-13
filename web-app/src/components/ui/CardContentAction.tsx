'use client';

/**
 * CardContentAction Component
 *
 * Standardized action area for card content across the application.
 * Ensures consistent button sizing, spacing, and alignment.
 *
 * Usage:
 * - Chapters page: Primary action + optional secondary action
 * - Quizzes page: Score display + primary action
 * - Locked content: Upgrade prompt
 */

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Button, ButtonProps } from '@/components/ui/Button';
import { Lock, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { CARD_SPACING, BUTTON_SIZE } from '@/lib/constants';

export interface ActionButton {
  label: string;
  href: string;
  variant?: ButtonProps['variant'];
  disabled?: boolean;
  icon?: React.ReactNode;
  suffix?: React.ReactNode;
}

export interface LockedContentProps {
  title: string;
  description: string;
  upgradeHref: string;
  tier?: 'FREE' | 'PREMIUM' | 'PRO';
}

export interface CardContentActionProps {
  children?: React.ReactNode;
  className?: string;
}

/**
 * Container for card actions with consistent spacing
 */
export const CardContentAction = React.forwardRef<HTMLDivElement, CardContentActionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex flex-col', CARD_SPACING.CONTENT_GAP, className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardContentAction.displayName = 'CardContentAction';

/**
 * Standardized primary action button
 */
export const ActionButton = React.forwardRef<
  HTMLAnchorElement,
  ActionButton & { className?: string; fullWidth?: boolean }
>(({ label, href, variant = 'primary', disabled = false, icon, suffix, className, fullWidth = true }, ref) => {
  return (
    <Link href={href} className={fullWidth ? 'block' : 'inline-block'}>
      <Button
        ref={ref as any}
        variant={variant}
        size={BUTTON_SIZE.SMALL}
        disabled={disabled}
        className={cn('gap-2', fullWidth && 'w-full', className)}
      >
        {icon}
        {label}
        {suffix}
      </Button>
    </Link>
  );
});

ActionButton.displayName = 'ActionButton';

/**
 * Standardized locked content display
 */
export const LockedContent = React.forwardRef<HTMLDivElement, LockedContentProps & { className?: string }>(
  ({ title, description, upgradeHref, tier, className }, ref) => {
    return (
      <div
        ref={ref}
        className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-4 text-center"
      >
        <p className="text-sm text-accent-warning font-medium mb-1 flex items-center justify-center gap-2">
          <Lock className="w-4 h-4" />
          {title}
        </p>
        <p className="text-xs text-text-muted mb-3">{description}</p>
        <Link href={upgradeHref} className="inline-block">
          <Button variant="outline" size={BUTTON_SIZE.SMALL} className="w-full">
            Upgrade Now
          </Button>
        </Link>
      </div>
    );
  }
);

LockedContent.displayName = 'LockedContent';

/**
 * Standardized warning display (e.g., retry limit reached)
 */
export const WarningContent = React.forwardRef<
  HTMLDivElement,
  {
    title: string;
    description: string;
    actionLabel?: string;
    actionHref?: string;
    className?: string;
  }
>(({ title, description, actionLabel, actionHref, className }, ref) => {
  return (
    <div
      ref={ref}
      className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-3 text-center"
    >
      <p className="text-sm text-accent-warning font-medium mb-1 flex items-center justify-center gap-2">
        <AlertCircle className="w-4 h-4" />
        {title}
      </p>
      <p className="text-xs text-text-muted mb-3">{description}</p>
      {actionLabel && actionHref && (
        <Link href={actionHref} className="inline-block">
          <Button variant="outline" size={BUTTON_SIZE.SMALL} className="w-full">
            {actionLabel}
          </Button>
        </Link>
      )}
    </div>
  );
});

WarningContent.displayName = 'WarningContent';

/**
 * Standardized info display (e.g., attempts remaining)
 */
export const InfoContent = React.forwardRef<
  HTMLDivElement,
  { children: React.ReactNode; className?: string; variant?: 'primary' | 'secondary' | 'warning' }
>(({ children, className, variant = 'primary' }, ref) => {
  const variantStyles = {
    primary: 'bg-accent-primary/10 border-accent-primary/30',
    secondary: 'bg-accent-secondary/10 border-accent-secondary/30',
    warning: 'bg-accent-warning/10 border-accent-warning/30',
  };

  return (
    <div
      ref={ref}
      className={cn('border rounded-lg p-3', variantStyles[variant], className)}
    >
      {children}
    </div>
  );
});

InfoContent.displayName = 'InfoContent';

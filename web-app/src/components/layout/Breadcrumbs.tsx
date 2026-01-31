'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

interface Breadcrumb {
  label: string;
  href: string;
}

export function Breadcrumbs({ className }: { className?: string }) {
  const pathname = usePathname();

  // Generate breadcrumbs from pathname
  const generateBreadcrumbs = (): Breadcrumb[] => {
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs: Breadcrumb[] = [];

    // Add home/dashboard as first breadcrumb
    if (segments.length > 0) {
      breadcrumbs.push({ label: 'Dashboard', href: '/dashboard' });
    }

    // Build breadcrumb path
    let path = '';
    for (let i = 0; i < segments.length; i++) {
      path = `${path}/${segments[i]}`;

      // Skip dashboard (already added)
      if (segments[i] === 'dashboard') continue;

      // Format label: capitalize first letter, handle special cases
      let label = segments[i]
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

      // Handle ID segments (likely chapter/quiz IDs)
      if (segments[i].match(/^[0-9a-f-]{36}$/i) || /^\d+$/.test(segments[i])) {
        label = `ID: ${segments[i].substring(0, 8)}...`;
      }

      breadcrumbs.push({ label, href: path });
    }

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  // Don't show breadcrumbs on dashboard
  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center space-x-1 text-sm mb-4', className)}>
      <ol className="flex items-center space-x-1">
        {breadcrumbs.map((breadcrumb, index) => {
          const isLast = index === breadcrumbs.length - 1;

          return (
            <li key={breadcrumb.href} className="flex items-center">
              {index > 0 && (
                <svg
                  className="w-4 h-4 text-text-muted mx-1"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              {isLast ? (
                <span className="text-text-primary font-medium" aria-current="page">
                  {breadcrumb.label}
                </span>
              ) : (
                <Link
                  href={breadcrumb.href}
                  className="text-text-secondary hover:text-accent-primary transition-colors"
                >
                  {breadcrumb.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

// Static breadcrumbs component for custom breadcrumb control
export function StaticBreadcrumbs({
  breadcrumbs,
  className,
}: {
  breadcrumbs: Breadcrumb[];
  className?: string;
}) {
  if (breadcrumbs.length === 0) {
    return null;
  }

  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center space-x-1 text-sm mb-4', className)}>
      <ol className="flex items-center space-x-1">
        {breadcrumbs.map((breadcrumb, index) => {
          const isLast = index === breadcrumbs.length - 1;

          return (
            <li key={breadcrumb.href} className="flex items-center">
              {index > 0 && (
                <svg
                  className="w-4 h-4 text-text-muted mx-1"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              {isLast ? (
                <span className="text-text-primary font-medium" aria-current="page">
                  {breadcrumb.label}
                </span>
              ) : (
                <Link
                  href={breadcrumb.href}
                  className="text-text-secondary hover:text-accent-primary transition-colors"
                >
                  {breadcrumb.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

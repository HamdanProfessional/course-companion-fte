import * as React from 'react';
import { cn } from '@/lib/utils';

export interface TooltipProps {
  content: string;
  children: React.ReactNode;
  side?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export const Tooltip = React.forwardRef<HTMLDivElement, TooltipProps>(
  ({ content, children, side = 'top', className }, ref) => {
    const [isVisible, setIsVisible] = React.useState(false);
    const tooltipRef = React.useRef<HTMLDivElement>(null);

    const positionStyles = {
      top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
      bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
      left: 'right-full top-1/2 -translate-y-1/2 mr-2',
      right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    };

    return (
      <div
        ref={ref}
        className="relative inline-block"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
      >
        {children}
        {isVisible && (
          <div
            ref={tooltipRef}
            className={cn(
              'absolute z-50 px-3 py-1.5 text-xs font-medium text-white bg-bg-elevated border border-border-default rounded-lg shadow-lg whitespace-nowrap',
              'pointer-events-none fade-in',
              positionStyles[side],
              className
            )}
            role="tooltip"
          >
            {content}
            {/* Arrow */}
            <div
              className={cn(
                'absolute w-2 h-2 bg-bg-elevated border border-border-default rotate-45',
                side === 'top' && 'top-full left-1/2 -translate-x-1/2 -mt-1 border-t-0 border-l-0',
                side === 'bottom' && 'bottom-full left-1/2 -translate-x-1/2 -mt-1 border-b-0 border-r-0',
                side === 'left' && 'left-full top-1/2 -translate-y-1/2 -ml-1 border-l-0 border-t-0',
                side === 'right' && 'right-full top-1/2 -translate-y-1/2 -ml-1 border-r-0 border-b-0'
              )}
            />
          </div>
        )}
      </div>
    );
  }
);

Tooltip.displayName = 'Tooltip';

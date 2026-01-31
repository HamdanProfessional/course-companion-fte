import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-xl font-semibold transition-all duration-200 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 active:scale-95';

    const variants = {
      primary: 'btn-primary px-6 py-3 text-white',
      secondary: 'btn-secondary px-6 py-3',
      outline: 'border-2 border-accent-primary text-accent-primary hover:bg-accent-primary/10 px-6 py-3',
      ghost: 'btn-ghost px-6 py-3',
      danger: 'btn-danger px-6 py-3 text-white',
      success: 'btn-success px-6 py-3 text-white',
    };

    const sizes = {
      sm: 'h-9 text-sm px-4 py-2',
      md: 'h-10 text-base px-6 py-3',
      lg: 'h-12 text-lg px-8 py-4',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 0 5.373 0 0 0 0h12zm0 0a6 6 0 016 0H4v6h2V6z"></path>
            </svg>
            Loading...
          </>
        ) : children}
      </button>
    );
  }
);

Button.displayName = 'Button';

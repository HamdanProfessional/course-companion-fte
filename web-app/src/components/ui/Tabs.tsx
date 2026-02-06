'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface TabsProps {
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export interface TabsContextValue {
  value: string;
  onValueChange: (value: string) => void;
}

const TabsContext = React.createContext<TabsContextValue | undefined>(undefined);

export const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ defaultValue, value, onValueChange, children, className }, ref) => {
    const [internalValue, setInternalValue] = React.useState(defaultValue || '');

    const currentValue = value !== undefined ? value : internalValue;
    const handleValueChange = onValueChange ?? setInternalValue;

    return (
      <TabsContext.Provider value={{ value: currentValue, onValueChange: handleValueChange }}>
        <div ref={ref} className={className}>
          {children}
        </div>
      </TabsContext.Provider>
    );
  }
);

Tabs.displayName = 'Tabs';

export interface TabsListProps extends React.HTMLAttributes<HTMLDivElement> {}

export const TabsList = React.forwardRef<HTMLDivElement, TabsListProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center gap-2 rounded-xl bg-glass-surface border border-glass-border p-1.5 backdrop-blur-xl',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

TabsList.displayName = 'TabsList';

export interface TabsTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string;
}

export const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ className, value, children, ...props }, ref) => {
    const context = React.useContext(TabsContext);

    if (!context) {
      throw new Error('TabsTrigger must be used within a Tabs component');
    }

    const isActive = context.value === value;

    return (
      <motion.button
        ref={ref}
        type="button"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          'inline-flex items-center justify-center whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cosmic-primary',
          'disabled:pointer-events-none disabled:opacity-50',
          isActive
            ? 'bg-gradient-to-r from-cosmic-primary to-cosmic-purple text-white shadow-glow-purple'
            : 'text-text-secondary hover:text-text-primary hover:bg-cosmic-secondary',
          className
        )}
        onClick={() => context.onValueChange(value)}
        aria-selected={isActive}
        role="tab"
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);

TabsTrigger.displayName = 'TabsTrigger';

export interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export const TabsContent = React.forwardRef<HTMLDivElement, TabsContentProps>(
  ({ className, value, children, ...props }, ref) => {
    const context = React.useContext(TabsContext);

    if (!context) {
      throw new Error('TabsContent must be used within a Tabs component');
    }

    if (context.value !== value) {
      return null;
    }

    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className={cn('mt-4 focus-visible:outline-none', className)}
        role="tabpanel"
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

TabsContent.displayName = 'TabsContent';

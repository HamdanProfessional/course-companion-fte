/**
 * Layout component for dashboard pages.
 * Note: Header is now in root layout.tsx to avoid duplication
 */
import { ReactNode } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen">
      {/* Header is rendered in root layout.tsx to avoid duplication */}
      {children}
    </div>
  );
}

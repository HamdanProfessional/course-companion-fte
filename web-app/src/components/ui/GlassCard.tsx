'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'dark' | 'nebula' | 'stellar';
  hover?: boolean;
  glow?: boolean;
}

export function GlassCard({
  children,
  className = '',
  variant = 'dark',
  hover = true,
  glow = false,
}: GlassCardProps) {
  const variants = {
    dark: 'bg-glass-surface border-glass-border',
    nebula: 'bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 border-cosmic-primary/30',
    stellar: 'bg-gradient-to-br from-cosmic-blue/20 to-cosmic-cyan/20 border-cosmic-blue/30',
  };

  return (
    <motion.div
      whileHover={hover ? {
        scale: 1.01,
        boxShadow: glow ? '0 0 40px rgba(139, 92, 246, 0.3)' : '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        transition: { duration: 0.2 }
      } : undefined}
      className={`relative backdrop-blur-xl ${variants[variant]}
                  border rounded-2xl p-6 ${className}`}
    >
      {/* Cosmic gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent rounded-2xl pointer-events-none" />
      <div className="relative">{children}</div>
    </motion.div>
  );
}

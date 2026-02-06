'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  variant?: 'nebula' | 'cosmic' | 'stellar' | 'success' | 'warning';
  className?: string;
}

export const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ title, value, change, icon, trend = 'neutral', variant = 'nebula', className }, ref) => {
    const [isHovered, setIsHovered] = React.useState(false);

    const gradients = {
      nebula: 'from-cosmic-primary via-cosmic-purple to-cosmic-blue',
      cosmic: 'from-cosmic-pink via-cosmic-purple to-cosmic-blue',
      stellar: 'from-cosmic-primary via-cosmic-blue to-cosmic-cyan',
      success: 'from-emerald-400 to-teal-500',
      warning: 'from-amber-400 to-orange-500',
    };

    const glowColors = {
      nebula: 'shadow-glow-purple',
      cosmic: 'shadow-nebula',
      stellar: 'shadow-glow-blue',
      success: 'shadow-glow-green',
      warning: 'shadow-glow-orange',
    };

    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{
          scale: 1.05,
          y: -8,
          transition: { duration: 0.3 }
        }}
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        className={cn(
          'relative overflow-hidden rounded-2xl bg-gradient-to-br p-6 text-white cursor-pointer',
          gradients[variant],
          className
        )}
      >
        {/* Animated nebula pattern */}
        <motion.div
          className="absolute inset-0 opacity-20"
          animate={{
            backgroundPosition: isHovered ? ['0% 0%', '100% 100%'] : ['0% 0%', '0% 0%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: 'reverse',
          }}
          style={{
            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(255,255,255,0.2) 0%, transparent 50%)',
            backgroundSize: '200% 200%',
          }}
        />

        {/* Twinkling sparkles */}
        {isHovered && (
          <>
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: [0, 1, 0], scale: [0, 1, 0] }}
                transition={{ duration: 1.5, delay: i * 0.2, repeat: Infinity }}
                style={{
                  position: 'absolute',
                  top: `${20 + i * 30}%`,
                  right: `${10 + i * 5}%`,
                }}
              >
                <Sparkles className="w-4 h-4 text-white" />
              </motion.div>
            ))}
          </>
        )}

        <div className="relative">
          <motion.div
            whileHover={{ rotate: 360, scale: 1.2 }}
            transition={{ duration: 0.6, type: 'spring' }}
            className="mb-4"
          >
            {icon && (
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-white/20 backdrop-blur-sm">
                {icon}
              </div>
            )}
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-sm font-medium opacity-90"
          >
            {title}
          </motion.p>

          <motion.h3
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-bold mt-2"
          >
            {value}
          </motion.h3>

          {change !== undefined && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className={cn(
                'mt-2 text-sm flex items-center gap-1',
                trend === 'up' ? 'text-green-200' : trend === 'down' ? 'text-red-200' : 'text-white/70'
              )}
            >
              <span>{trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}</span>
              <span>{Math.abs(change)}% from last week</span>
            </motion.div>
          )}
        </div>

        {/* Glow effect overlay */}
        {isHovered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            className={cn('absolute inset-0 rounded-2xl pointer-events-none', glowColors[variant])}
          />
        )}
      </motion.div>
    );
  }
);

StatCard.displayName = 'StatCard';

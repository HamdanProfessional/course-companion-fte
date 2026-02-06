'use client';

import { motion } from 'framer-motion';
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface AnimatedButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'nebula' | 'cosmic' | 'stellar' | 'success' | 'danger';
  className?: string;
}

export function AnimatedButton({
  children,
  variant = 'nebula',
  className = '',
  ...props
}: AnimatedButtonProps) {
  const gradientClasses = {
    nebula: 'bg-gradient-to-r from-cosmic-primary to-cosmic-purple hover:shadow-glow-purple',
    cosmic: 'bg-gradient-to-r from-cosmic-pink via-cosmic-purple to-cosmic-blue hover:shadow-nebula',
    stellar: 'bg-gradient-to-r from-cosmic-primary via-cosmic-blue to-cosmic-cyan hover:shadow-glow-blue',
    success: 'bg-gradient-to-r from-emerald-400 to-teal-500 hover:shadow-glow-green',
    danger: 'bg-gradient-to-r from-red-500 to-rose-600 hover:shadow-glow-red',
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className={`px-6 py-3 rounded-lg text-white font-semibold ${gradientClasses[variant]} transition-shadow duration-300 ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  );
}

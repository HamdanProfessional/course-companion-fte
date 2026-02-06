'use client';

import { motion } from 'framer-motion';

interface ShimmerProps {
  width?: string;
  height?: string;
  className?: string;
}

export function Shimmer({ width = '100%', height = '100%', className = '' }: ShimmerProps) {
  return (
    <motion.div
      className={`bg-gradient-to-r from-gray-700 via-gray-600 to-gray-700 rounded ${className}`}
      style={{ width, height }}
      animate={{
        backgroundPosition: ['200% 0', '-200% 0'],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );
}

'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function StarfieldBackground() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Generate random star positions
  const smallStars = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 8,
  }));

  const mediumStars = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 12,
  }));

  const largeStars = Array.from({ length: 15 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 15,
    color: ['#8b5cf6', '#0ea5e9', '#06b6d4'][i % 3],
  }));

  const shootingStars = Array.from({ length: 3 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 50,
    delay: i * 10,
  }));

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-cosmic-bg">
      {/* Nebula glow effects */}
      <motion.div
        className="absolute inset-0 opacity-20"
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%'],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          repeatType: 'reverse',
        }}
        style={{
          backgroundImage: `
            radial-gradient(ellipse at 20% 30%, rgba(139, 92, 246, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 70%, rgba(14, 165, 233, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(236, 72, 153, 0.2) 0%, transparent 50%)
          `,
          backgroundSize: '200% 200%',
        }}
      />

      {/* Small stars */}
      {smallStars.map((star) => (
        <motion.div
          key={`small-${star.id}`}
          className="absolute w-0.5 h-0.5 bg-white rounded-full"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
          }}
          animate={{
            opacity: [0.3, 1, 0.3],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 8,
            delay: star.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Medium stars */}
      {mediumStars.map((star) => (
        <motion.div
          key={`medium-${star.id}`}
          className="absolute w-1 h-1 bg-white rounded-full"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
          }}
          animate={{
            opacity: [0.5, 1, 0.5],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: 12,
            delay: star.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Large colored stars */}
      {largeStars.map((star) => (
        <motion.div
          key={`large-${star.id}`}
          className="absolute w-1.5 h-1.5 rounded-full"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            backgroundColor: star.color,
            boxShadow: `0 0 10px ${star.color}`,
          }}
          animate={{
            opacity: [0.6, 1, 0.6],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: 15,
            delay: star.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Shooting stars */}
      {shootingStars.map((star) => (
        <motion.div
          key={`shooting-${star.id}`}
          className="absolute w-20 h-0.5"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent)',
          }}
          animate={{
            x: [0, 300],
            y: [0, 300],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 3,
            delay: star.delay,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      ))}

      {/* Floating dust particles */}
      <motion.div
        className="absolute inset-0 opacity-30"
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%'],
        }}
        transition={{
          duration: 60,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          backgroundImage: 'radial-gradient(1px 1px at 20% 30%, rgba(139, 92, 246, 0.5), transparent), radial-gradient(1px 1px at 60% 70%, rgba(14, 165, 233, 0.5), transparent), radial-gradient(1px 1px at 50% 50%, rgba(236, 72, 153, 0.5), transparent)',
          backgroundSize: '200px 200px',
        }}
      />
    </div>
  );
}

'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function StarfieldBackground() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Reduced number of stars to prevent GPU leak
  const smallStars = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 8,
  }));

  const mediumStars = Array.from({ length: 8 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 12,
  }));

  const largeStars = Array.from({ length: 5 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 15,
    color: ['#8b5cf6', '#0ea5e9', '#06b6d4'][i % 3],
  }));

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-cosmic-bg">
      {/* Static nebula glow effects - no animation to reduce GPU usage */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            radial-gradient(ellipse at 20% 30%, rgba(139, 92, 246, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 70%, rgba(14, 165, 233, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(236, 72, 153, 0.2) 0%, transparent 50%)
          `,
          backgroundSize: '200% 200%',
        }}
      />

      {/* Small stars - CSS animation for better performance */}
      {smallStars.map((star) => (
        <div
          key={`small-${star.id}`}
          className="absolute w-0.5 h-0.5 bg-white rounded-full animate-pulse"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            animationDelay: `${star.delay}s`,
            animationDuration: '3s',
            opacity: 0.6,
          }}
        />
      ))}

      {/* Medium stars - CSS animation */}
      {mediumStars.map((star) => (
        <div
          key={`medium-${star.id}`}
          className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            animationDelay: `${star.delay}s`,
            animationDuration: '4s',
            opacity: 0.7,
          }}
        />
      ))}

      {/* Large colored stars - slower animation */}
      {largeStars.map((star) => (
        <div
          key={`large-${star.id}`}
          className="absolute w-1.5 h-1.5 rounded-full animate-pulse"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            backgroundColor: star.color,
            boxShadow: `0 0 10px ${star.color}`,
            animationDelay: `${star.delay}s`,
            animationDuration: '5s',
            opacity: 0.8,
          }}
        />
      ))}
    </div>
  );
}

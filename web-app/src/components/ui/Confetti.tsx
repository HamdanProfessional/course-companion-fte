'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function Confetti() {
  const [particles, setParticles] = useState<Array<{ id: number; x: number; delay: number }>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      delay: Math.random() * 0.5,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          initial={{ y: -50, opacity: 1, rotate: 0 }}
          animate={{
            y: window.innerHeight + 50,
            opacity: 0,
            rotate: 720,
          }}
          transition={{
            duration: 3,
            delay: particle.delay,
            ease: 'easeOut',
          }}
          className="absolute w-3 h-3"
          style={{
            left: `${particle.x}%`,
            backgroundColor: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'][
              particle.id % 5
            ],
          }}
        />
      ))}
    </div>
  );
}

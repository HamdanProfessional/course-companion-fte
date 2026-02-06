'use client';

import { motion, useMotionValue, useSpring } from 'framer-motion';
import { useEffect, useState } from 'react';

export function CustomCursor() {
  const [isActive, setIsActive] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);

  const springConfig = { damping: 25, stiffness: 700 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  useEffect(() => {
    const moveCursor = (e: MouseEvent) => {
      cursorX.set(e.clientX - 16);
      cursorY.set(e.clientY - 16);
    };

    const handleMouseDown = () => setIsActive(true);
    const handleMouseUp = () => setIsActive(false);

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'BUTTON' || target.tagName === 'A' || target.closest('[data-interactive]')) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    window.addEventListener('mousemove', moveCursor);
    window.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('mouseover', handleMouseOver);

    return () => {
      window.removeEventListener('mousemove', moveCursor);
      window.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('mouseover', handleMouseOver);
    };
  }, [cursorX, cursorY]);

  return (
    <>
      {/* Main cursor */}
      <motion.div
        style={{
          translateX: cursorXSpring,
          translateY: cursorYSpring,
        }}
        className="fixed top-0 left-0 w-8 h-8 rounded-full pointer-events-none z-50 mix-blend-difference hidden md:block"
        animate={{
          scale: isActive ? 0.8 : isHovering ? 1.5 : 1,
        }}
        transition={{ type: 'spring', stiffness: 700, damping: 25 }}
      >
        <motion.div
          className="w-full h-full rounded-full"
          animate={{
            backgroundColor: isActive ? 'rgba(139, 92, 246, 0.9)' : isHovering ? 'rgba(14, 165, 233, 0.6)' : 'rgba(139, 92, 246, 0.4)',
            boxShadow: isHovering ? '0 0 20px rgba(139, 92, 246, 0.8)' : '0 0 10px rgba(139, 92, 246, 0.5)',
          }}
          transition={{ duration: 0.2 }}
        />
      </motion.div>

      {/* Trailing glow */}
      <motion.div
        style={{
          translateX: useSpring(cursorX, { damping: 40, stiffness: 100 }),
          translateY: useSpring(cursorY, { damping: 40, stiffness: 100 }),
        }}
        className="fixed top-0 left-0 w-6 h-6 rounded-full pointer-events-none z-40 hidden md:block"
        animate={{
          scale: isActive ? 1.2 : 1,
        }}
        transition={{ duration: 0.3 }}
      >
        <div
          className="w-full h-full rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%)',
          }}
        />
      </motion.div>
    </>
  );
}

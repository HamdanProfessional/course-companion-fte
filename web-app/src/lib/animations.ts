import { Variants, Transition } from 'framer-motion';

// Page transition variants
export const pageVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.3 } },
};

// Stagger children for list animations
export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
};

// Card hover effects
export const cardHover = {
  scale: 1.02,
  transition: { duration: 0.2, ease: 'easeInOut' } as Transition,
};

// Button click feedback
export const buttonTap = {
  scale: 0.95,
  transition: { duration: 0.1 } as Transition,
};

// Achievement celebration
export const celebrateVariants: Variants = {
  initial: { scale: 0, rotate: -180, opacity: 0 },
  animate: {
    scale: 1,
    rotate: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 15,
    },
  },
};

// Progress bar animation
export const progressAnimation = {
  initial: { width: 0 },
  animate: (width: number) => ({
    width,
    transition: { duration: 1, ease: 'easeOut' },
  }),
};

// Floating animation for special elements
export const floatAnimation = {
  y: [0, -10, 0],
  transition: {
    duration: 3,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

// Fade in variants
export const fadeInVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.5 } },
  exit: { opacity: 0, transition: { duration: 0.3 } },
};

// Slide in from left
export const slideInLeftVariants: Variants = {
  initial: { x: -20, opacity: 0 },
  animate: { x: 0, opacity: 1, transition: { duration: 0.4 } },
};

// Slide in from bottom
export const slideInUpVariants: Variants = {
  initial: { y: 20, opacity: 0 },
  animate: { y: 0, opacity: 1, transition: { duration: 0.4 } },
};

// Scale in
export const scaleInVariants: Variants = {
  initial: { scale: 0.9, opacity: 0 },
  animate: { scale: 1, opacity: 1, transition: { duration: 0.3 } },
};

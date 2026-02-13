/**
 * UI Constants for Course Companion FTE
 *
 * Centralized spacing, sizing, and layout constants
 * to ensure consistency across the application.
 */

/**
 * Grid gap values for card layouts
 */
export const GRID_GAP = {
  CARD_GRID: 'gap-6',  // Consistent gap for all card grids (chapters, quizzes, etc.)
  SMALL: 'gap-4',      // Smaller gap for compact layouts
  TIGHT: 'gap-2',      // Tight gap for related items
} as const;

/**
 * Button sizing variants
 */
export const BUTTON_SIZE = {
  SMALL: 'sm',
  MEDIUM: 'md',
  LARGE: 'lg',
} as const;

/**
 * Card content spacing
 */
export const CARD_SPACING = {
  CONTENT_GAP: 'gap-3',  // Gap between elements in card content
  INNER_PADDING: 'p-6',  // Inner padding for cards
  HEADER_PADDING: 'p-6', // Padding for card headers
} as const;

/**
 * Badge positioning
 */
export const BADGE_PLACEMENT = {
  TOP_RIGHT: 'top-0 right-0',
  TOP_LEFT: 'top-0 left-0',
} as const;

/**
 * Responsive grid columns
 */
export const GRID_COLUMNS = {
  RESPONSIVE_CARDS: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  TWO_COLUMN: 'grid-cols-1 md:grid-cols-2',
} as const;

/**
 * Animation durations (ms)
 */
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 200,
  SLOW: 300,
} as const;

/**
 * Z-index layers
 */
export const Z_INDEX = {
  DROPDOWN: 1000,
  MODAL: 1050,
  TOOLTIP: 1100,
  NOTIFICATION: 1200,
} as const;

/**
 * Icon sizes
 */
export const ICON_SIZE = {
  XS: 'w-3 h-3',
  SM: 'w-4 h-4',
  MD: 'w-5 h-5',
  LG: 'w-6 h-6',
  XL: 'w-8 h-8',
} as const;

/**
 * Text sizes for consistent typography
 */
export const TEXT_SIZE = {
  XS: 'text-xs',
  SM: 'text-sm',
  BASE: 'text-base',
  LG: 'text-lg',
  XL: 'text-xl',
} as const;

/**
 * Border radius values
 */
export const BORDER_RADIUS = {
  SM: 'rounded-lg',
  MD: 'rounded-xl',
  LG: 'rounded-2xl',
  FULL: 'rounded-full',
} as const;

/**
 * Default padding values
 */
export const PADDING = {
  XS: 'p-2',
  SM: 'p-3',
  MD: 'p-4',
  LG: 'p-6',
  XL: 'p-8',
} as const;

/**
 * Tier badge colors
 */
export const TIER_COLORS = {
  FREE: {
    bg: 'bg-text-muted/10',
    text: 'text-text-muted',
    border: 'border-text-muted/20',
  },
  PREMIUM: {
    bg: 'bg-purple-500/20',
    text: 'text-purple-400',
    border: 'border-purple-500/30',
  },
  PRO: {
    bg: 'bg-gradient-to-r from-purple-500/20 to-pink-500/20',
    text: 'text-purple-400',
    border: 'border-purple-500/30',
  },
} as const;

/**
 * Difficulty badge configurations
 */
export const DIFFICULTY_BADGE = {
  BEGINNER: {
    variant: 'beginner' as const,
    label: 'Beginner',
    color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  },
  INTERMEDIATE: {
    variant: 'intermediate' as const,
    label: 'Intermediate',
    color: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  },
  ADVANCED: {
    variant: 'advanced' as const,
    label: 'Advanced',
    color: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  },
} as const;

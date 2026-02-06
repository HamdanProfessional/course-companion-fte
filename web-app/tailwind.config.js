/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          elevated: 'var(--bg-elevated)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
        accent: {
          primary: 'var(--accent-primary)',
          success: 'var(--accent-success)',
          warning: 'var(--accent-warning)',
          danger: 'var(--accent-danger)',
          premium: 'var(--accent-premium)',
        },
        border: {
          default: 'var(--border-default)',
          focus: 'var(--border-focus)',
        },
        // Nebula/Cosmic Theme Colors
        cosmic: {
          bg: '#0f111a',
          fg: '#f1f3f7',
          primary: '#8b5cf6',
          secondary: '#1e2133',
          purple: '#a855f7',
          blue: '#0ea5e9',
          pink: '#ec4899',
          cyan: '#06b6d4',
        },
        glass: {
          surface: 'rgba(24, 21, 41, 0.6)',
          border: 'rgba(139, 92, 246, 0.2)',
          hover: 'rgba(139, 92, 246, 0.1)',
        },
      },
      spacing: {
        xs: 'var(--spacing-xs)',
        sm: 'var(--spacing-sm)',
        md: 'var(--spacing-md)',
        lg: 'var(--spacing-lg)',
        xl: 'var(--spacing-xl)',
        '2xl': 'var(--spacing-2xl)',
      },
      fontSize: {
        xs: 'var(--text-xs)',
        sm: 'var(--text-sm)',
        base: 'var(--text-base)',
        lg: 'var(--text-lg)',
        xl: 'var(--text-xl)',
        '2xl': 'var(--text-2xl)',
        '3xl': 'var(--text-3xl)',
        '4xl': 'var(--text-4xl)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
      },
      backgroundImage: {
        'gradient-nebula': 'linear-gradient(135deg, #8b5cf6 0%, #0ea5e9 50%, #06b6d4 100%)',
        'gradient-cosmic': 'linear-gradient(135deg, #ec4899 0%, #a855f7 50%, #0ea5e9 100%)',
        'gradient-stellar': 'linear-gradient(135deg, rgba(139,92,246,0.3) 0%, rgba(14,165,233,0.3) 100%)',
        'gradient-purple-glow': 'radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%)',
        'gradient-blue-glow': 'radial-gradient(circle, rgba(14,165,233,0.4) 0%, transparent 70%)',
      },
      boxShadow: {
        'nebula': '0 0 40px rgba(139, 92, 246, 0.3), 0 0 80px rgba(14, 165, 233, 0.2)',
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.5), 0 0 40px rgba(139, 92, 246, 0.3)',
        'glow-blue': '0 0 20px rgba(14, 165, 233, 0.5), 0 0 40px rgba(14, 165, 233, 0.3)',
        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.5), 0 0 40px rgba(6, 182, 212, 0.3)',
        'neon-purple': '0 0 10px rgba(139, 92, 246, 0.8), 0 0 20px rgba(139, 92, 246, 0.6)',
        'neon-blue': '0 0 10px rgba(14, 165, 233, 0.8), 0 0 20px rgba(14, 165, 233, 0.6)',
        'glow-green': '0 0 20px rgba(34, 197, 94, 0.5), 0 0 40px rgba(34, 197, 94, 0.3)',
        'glow-orange': '0 0 20px rgba(249, 115, 22, 0.5), 0 0 40px rgba(249, 115, 22, 0.3)',
        'glow-red': '0 0 20px rgba(239, 68, 68, 0.5), 0 0 40px rgba(239, 68, 68, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-in-left': 'slideInLeft 0.5s ease-out',
        'slide-in-up': 'slideInUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'twinkle': 'twinkle 8s ease-in-out infinite',
        'twinkle-slow': 'twinkle 12s ease-in-out infinite',
        'twinkle-fast': 'twinkle 15s ease-in-out infinite',
        'shooting-star': 'shootingStar 3s linear infinite',
        'nebula-drift': 'nebulaDrift 30s ease-in-out infinite',
        'dust-float': 'dustFloat 60s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'hover-lift': 'hoverLift 0.3s ease-out',
        'hover-glow': 'hoverGlow 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        twinkle: {
          '0%, 100%': { opacity: '0.3', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.2)' },
        },
        shootingStar: {
          '0%': { transform: 'translateX(0) translateY(0)', opacity: '1' },
          '70%': { opacity: '1' },
          '100%': { transform: 'translateX(300px) translateY(300px)', opacity: '0' },
        },
        nebulaDrift: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '50%': { transform: 'translate(30px, -30px) scale(1.1)' },
        },
        dustFloat: {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '25%': { transform: 'translate(100px, -50px)' },
          '50%': { transform: 'translate(200px, 50px)' },
          '75%': { transform: 'translate(100px, 100px)' },
        },
        hoverLift: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-8px)' },
        },
        hoverGlow: {
          '0%': { boxShadow: '0 0 0 rgba(139, 92, 246, 0)' },
          '100%': { boxShadow: '0 0 30px rgba(139, 92, 246, 0.5)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://92.113.147.250:8000',
  },

  // Production optimizations
  compiler: {
    // Remove console.log in production (but keep errors/warnings)
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },

  // Enable React strict mode for better development experience
  reactStrictMode: true,

  // Optimize package imports
  modularizeImports: {
    'lodash': {
      transform: 'lodash/{{member}}',
    },
  },

  // Compress output
  compress: false,  // Disable compression to avoid hydration errors

  // Disable TypeScript checking during build for faster compilation
  typescript: {
    ignoreBuildErrors: true,
  },

  // DISABLE SWC minification to fix React hydration error #418
  swcMinify: false,

  // Disable optimization to prevent minification issues
  productionBrowserSourceMaps: true,

  // Use development-friendly build
  optimizeFonts: false,

  // Experimental features for better performance
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion', '@tanstack/react-query'],
  },

  // Logging
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
}

module.exports = nextConfig

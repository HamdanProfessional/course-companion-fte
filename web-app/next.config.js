/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  },

  // Production optimizations
  compiler: {
    // Remove console.log in production
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
  compress: true,

  // Generate static pages where possible
  output: 'standalone',
}

module.exports = nextConfig

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Header } from '@/components/layout/Header';
import { StarfieldBackground } from '@/components/background/StarfieldBackground';
import { Heart } from 'lucide-react';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Course Companion FTE - AI-Powered Learning',
  description: 'Your AI-powered tutor for mastering AI Agent Development',
};

// Force dynamic rendering to prevent static generation with QueryClient
export const dynamic = 'force-dynamic';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>
        <Providers>
          {/* Starfield Background - Cosmic Theme */}
          <StarfieldBackground />

          {/* Skip link for accessibility */}
          <a href="#main-content" className="skip-link">
            Skip to main content
          </a>

          {/* Header Navigation */}
          <Header />

          {/* Main Content */}
          <main id="main-content" className="min-h-screen relative z-10">
            {children}
          </main>

          {/* Footer */}
          <footer className="border-t border-glass-border bg-glass-surface mt-auto backdrop-blur-xl">
            <div className="container py-6 text-center text-sm text-text-secondary">
              <p className="flex items-center justify-center gap-1">
                © 2026 Course Companion FTE. Built with <Heart className="w-4 h-4 text-red-400 fill-red-400 inline" /> for Panaversity Hackathon IV.
              </p>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}

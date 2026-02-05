import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Header } from '@/components/layout/Header';

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
          {/* Skip link for accessibility */}
          <a href="#main-content" className="skip-link">
            Skip to main content
          </a>

          {/* Header Navigation */}
          <Header />

          {/* Main Content */}
          <main id="main-content" className="min-h-screen">
            {children}
          </main>

          {/* Footer */}
          <footer className="border-t border-border-default bg-bg-secondary mt-auto">
            <div className="container py-6 text-center text-sm text-text-secondary">
              <p>© 2026 Course Companion FTE. Built with ❤️ for Panaversity Hackathon IV.</p>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}

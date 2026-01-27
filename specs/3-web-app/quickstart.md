# Quickstart Guide: Web Application for Course Companion FTE

**Feature**: 3-web-app
**Prerequisites**: Node.js 18+, Git, Backend API deployed
**Estimated Setup Time**: 20 minutes

---

## Overview

This guide will get you up and running with the Course Companion FTE web application locally. By the end, you'll have:
- Next.js 14 app running locally
- Connected to backend API
- Authentication working
- Dashboard, chapters, quizzes, and progress tracking functional

---

## 1. Prerequisites

### Required Software
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Git**: [Download here](https://git-scm.com/downloads)
- **npm or yarn**: Comes with Node.js

### Required Services
- **Backend API**: Must be deployed (see `specs/1-zero-backend-api/quickstart.md`)
- **Backend URL**: Note your backend API URL for configuration

---

## 2. Create Next.js Project

```bash
# Navigate to repository root
cd course-companion-fte

# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest web-app --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Navigate to web-app directory
cd web-app

# Install additional dependencies
npm install @tanstack/react-query@5
npm install next-auth@5
npm install recharts
npm install zustand
npm install axios
npm install @hookform/resolvers react-hook-form zod

# Install dev dependencies
npm install -D @types/node
```

---

## 3. Project Structure

```
web-app/
├── src/
│   ├── app/                          # Next.js 14 App Router
│   │   ├── (auth)/                   # Auth route group
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/              # Dashboard route group (protected)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── chapters/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── quizzes/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── results/
│   │   │   │           └── page.tsx
│   │   │   ├── progress/
│   │   │   │   └── page.tsx
│   │   │   ├── profile/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...nextauth]/
│   │   │           └── route.ts
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                       # Reusable UI components
│   │   ├── dashboard/                # Dashboard components
│   │   ├── quizzes/                  # Quiz components
│   │   └── layout/                   # Layout components
│   ├── lib/
│   │   ├── api/                      # API client
│   │   ├── auth/                     # Auth utilities
│   │   └── utils/                    # Helper functions
│   ├── hooks/                        # Custom React hooks
│   └── types/                        # TypeScript types
├── public/                           # Static assets
├── .env.local                        # Environment variables
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

---

## 4. Environment Configuration

Create `.env.local`:

```bash
# Backend API
NEXT_PUBLIC_BACKEND_URL=https://your-backend-api.com

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-super-secret-nextauth-key

# Application
NEXT_PUBLIC_APP_NAME=Course Companion FTE
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Generate NextAuth Secret

```bash
# Generate secure random string
openssl rand -base64 32
```

---

## 5. Setup Tailwind CSS

The `create-next-app` command should have already set up Tailwind. Verify:

**tailwind.config.ts**:
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [],
}
export default config
```

**src/app/globals.css**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-start-rgb: 0, 0, 0;
    --background-end-rgb: 0, 0, 0;
  }
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}
```

---

## 6. Setup React Query

Create `src/app/providers.tsx`:

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            gcTime: 5 * 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

Update `src/app/layout.tsx`:

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Course Companion FTE',
  description: 'Your AI-powered tutor for personalized learning',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

## 7. Setup NextAuth

Create `src/app/api/auth/[...nextauth]/route.ts`:

```typescript
import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';

export const { handlers, auth } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials),
        });

        if (!res.ok) return null;

        const user = await res.json();
        return user;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.token;
        token.user = user;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      session.user = token.user;
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
});

export const { GET, POST } = handlers;
```

---

## 8. Create API Client

Create `src/lib/api/backend.ts`:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  // Note: In a real app, get token from session
  // const token = getToken();
  // if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const backendApi = {
  // Chapters
  getChapters: () => api.get('/chapters'),
  getChapter: (id: string) => api.get(`/chapters/${id}`),

  // Quizzes
  getQuizzes: () => api.get('/quizzes'),
  getQuiz: (id: string) => api.get(`/quizzes/${id}`),
  submitQuiz: (id: string, answers: Record<string, string>) =>
    api.post(`/quizzes/${id}/submit`, { answers }),

  // Progress
  getProgress: (userId: string) => api.get(`/progress/${userId}`),
  updateProgress: (userId: string, chapterId: string) =>
    api.put(`/progress/${userId}`, { chapter_id: chapterId }),

  // Streak
  getStreak: (userId: string) => api.get(`/streaks/${userId}`),
  recordCheckin: (userId: string) => api.post(`/streaks/${userId}/checkin`),

  // Access
  checkAccess: (userId: string, resource: string) =>
    api.post('/access/check', { user_id: userId, resource }),
};

export default backendApi;
```

---

## 9. Create TypeScript Types

Create `src/types/index.ts`:

```typescript
export interface User {
  id: string;
  email: string;
  tier: 'free' | 'premium' | 'pro';
  created_at: string;
}

export interface Chapter {
  id: string;
  title: string;
  content?: string;
  order: number;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: number;
  next_chapter_id?: string;
  previous_chapter_id?: string;
}

export interface Quiz {
  id: string;
  chapter_id: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  questions: Question[];
}

export interface Question {
  id: string;
  quiz_id: string;
  question_text: string;
  options: Record<string, string>;
  correct_answer: 'A' | 'B' | 'C' | 'D';
  explanation?: string;
  order: number;
}

export interface Progress {
  id: string;
  user_id: string;
  completed_chapters: string[];
  current_chapter_id: string | null;
  last_activity: string;
}

export interface Streak {
  id: string;
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_checkin: string | null;
}
```

---

## 10. Run Development Server

```bash
# Start development server
npm run dev

# Server will start at: http://localhost:3000
```

**Expected output**:
```
  ▲ Next.js 14.0.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.5:3000

 ✓ Ready in 2.3s
```

---

## 11. Verify Setup

Visit http://localhost:3000 and verify:
- ✅ Homepage loads
- ✅ No console errors
- ✅ Styles render correctly (Tailwind)
- ✅ Can navigate to /login

---

## 12. Build for Production

```bash
# Create production build
npm run build

# Test production build locally
npm start

# Or use Vercel CLI
vercel build
vercel deploy
```

---

## Troubleshooting

### Issue: Module not found
```bash
# Solution: Install dependencies
npm install
```

### Issue: Environment variables not working
```bash
# Solution: Verify .env.local exists and restart dev server
cat .env.local
npm run dev
```

### Issue: Tailwind styles not working
```bash
# Solution: Verify globals.css is imported in layout.tsx
cat src/app/layout.tsx | grep globals.css
```

### Issue: API calls failing
```bash
# Solution: Verify backend URL is correct
echo $NEXT_PUBLIC_BACKEND_URL
curl $NEXT_PUBLIC_BACKEND_URL/health
```

### Issue: NextAuth not working
```bash
# Solution: Verify NEXTAUTH_URL and NEXTAUTH_SECRET are set
echo $NEXTAUTH_URL
echo $NEXTAUTH_SECRET
```

---

## Next Steps

1. **Implement Authentication**: Create login and registration pages
2. **Build Dashboard**: Create main dashboard with progress and streak
3. **Add Chapter Navigation**: Implement chapter list and detail pages
4. **Build Quiz Interface**: Create quiz taking and results pages
5. **Add Progress Visualization**: Implement charts and gamification
6. **Create Profile Page**: Add settings and account management
7. **Deploy to Vercel**: Follow deployment guide in `plan.md`

---

## Useful Commands

```bash
# Development
npm run dev              # Start dev server

# Building
npm run build            # Create production build
npm run start            # Run production build

# Testing
npm test                 # Run tests
npm run test:e2e         # Run E2E tests

# Linting
npm run lint             # Run ESLint
npm run lint:fix         # Fix lint issues

# Type checking
npx tsc --noEmit         # Type check without emitting files

# Deployment
vercel                   # Deploy to Vercel
vercel --prod            # Deploy to production
```

---

## Deployment to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_BACKEND_URL
# NEXTAUTH_SECRET
# NEXTAUTH_URL
```

---

**Need Help?**
- Check `plan.md` for architecture decisions
- Review `data-model.md` for frontend state management
- See `contracts/` for API integration specs
- Open an issue on GitHub

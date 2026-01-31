# Research: Web Application for Course Companion FTE

**Feature**: 3-web-app
**Phase**: 0 - Research & Technical Decisions
**Date**: 2026-01-28

## Overview

This document consolidates research findings for implementing the standalone Next.js 14 web application for the Course Companion FTE platform.

---

## Decision 1: Next.js 14 with App Router

**Context**: Need modern React framework for web application with SSR and optimal performance.

**Decision**: Use Next.js 14 with App Router for the web application.

### Rationale
- **Latest Features**: App Router provides server components, improved data fetching, and better performance
- **Server-Side Rendering**: Built-in SSR for fast initial page loads and SEO
- **File-Based Routing**: Simple and intuitive routing system
- **API Routes**: Built-in API routes for serverless functions
- **Great DX**: Excellent developer experience with Fast Refresh and TypeScript support
- **Vercel Integration**: Seamless deployment to Vercel (same team)

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Create React App | Simple, familiar | No SSR, manual config, deprecated | Missing critical features for modern web app |
| Vite + React | Fast dev server, simple | Manual SSR setup | More configuration needed |
| Remix | Great nested routing | Steeper learning curve | Next.js has larger ecosystem |
| Gatsby | JAMstack, GraphQL-heavy | Overkill for dynamic app | Too complex for this use case |

### Implementation

```bash
# Create Next.js 14 app
npx create-next-app@latest web-app --typescript --tailwind --app
```

**Directory Structure**:
```
app/
├── (auth)/login/page.tsx       # Login page
├── (auth)/register/page.tsx    # Registration page
├── (dashboard)/
│   ├── dashboard/page.tsx      # Dashboard (protected)
│   ├── chapters/[id]/page.tsx  # Chapter detail
│   ├── quizzes/[id]/page.tsx   # Quiz interface
│   ├── progress/page.tsx       # Progress visualization
│   └── profile/page.tsx        # Student profile
└── layout.tsx                  # Root layout
```

---

## Decision 2: React Query for Data Fetching

**Context**: Need efficient data fetching with caching and state management.

**Decision**: Use TanStack Query (React Query) for server state management.

### Rationale
- **Automatic Caching**: Built-in caching with stale-while-revalidate
- **Background Refetch**: Keeps data fresh without manual refresh
- **Optimistic Updates**: Smooth UX with instant feedback
- **TypeScript Support**: Excellent type inference
- **DevTools**: Great debugging tools
- **Minimal Boilerplate**: Less code than Redux or Context API

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| SWR | Simpler API, smaller | Fewer features | React Query has better ecosystem |
| Redux Toolkit | Powerful, popular | More boilerplate, overkill | Too complex for API state |
| Context API | Built-in, simple | No caching, manual refetch | Missing critical features |
| Apollo Client | GraphQL-first | Overkill for REST | We're using REST APIs |

### Implementation

```typescript
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        cacheTime: 5 * 60 * 1000, // 5 minutes
        refetchOnWindowFocus: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// Custom hook
export function useChapters() {
  return useQuery({
    queryKey: ['chapters'],
    queryFn: () => fetch('/api/v1/chapters').then(res => res.json()),
  });
}

// Usage in component
function ChapterList() {
  const { data: chapters, isLoading, error } = useChapters();

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  return (
    <ul>
      {chapters.map(chapter => (
        <li key={chapter.id}>{chapter.title}</li>
      ))}
    </ul>
  );
}
```

---

## Decision 3: NextAuth.js for Authentication

**Context**: Need secure authentication with backend API integration.

**Decision**: Use NextAuth.js v5 with custom credentials provider.

### Rationale
- **Battle-Tested**: Used by thousands of production apps
- **Flexible Providers**: Supports OAuth, credentials, email, etc.
- **Secure**: Built-in CSRF protection, JWT handling
- **Easy Integration**: Simple to integrate with custom backend API
- **TypeScript**: First-class TypeScript support
- **Active Development**: Regular updates and security patches

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Custom JWT implementation | Full control | Security risks, more work | Don't roll your own auth |
| Clerk | Feature-rich | External service, cost | Want to keep auth in-house |
| Auth0 | Enterprise features | Costly, complex | Overkill for this use case |
| Lucia | Lightweight, modern | Less mature, fewer features | NextAuth has larger ecosystem |

### Implementation

```typescript
// app/api/auth/[...nextauth]/route.ts
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
        // Call backend API to validate credentials
        const res = await fetch(`${process.env.BACKEND_URL}/auth/login`, {
          method: 'POST',
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
});

export const { GET, POST } = handlers;
```

---

## Decision 4: Recharts for Data Visualization

**Context**: Need charts for progress visualization and gamification.

**Decision**: Use Recharts for data visualization.

### Rationale
- **React-Native**: Built specifically for React
- **Composable**: Declarative component API
- **SSR Compatible**: Works with Next.js server components
- **TypeScript**: Excellent type support
- **Lightweight**: Smaller bundle than Chart.js
- **Responsive**: Handles responsive charts out of the box

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Chart.js | Popular, many chart types | Not React-native, wrapper needed | More boilerplate |
| Victory | Beautiful, feature-rich | Larger bundle size | Performance concerns |
| D3.js | Most powerful | Steep learning curve, verbose | Overkill for our needs |
| Nivo | Great defaults | Larger bundle, less control | Bundle size concerns |

### Implementation

```typescript
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis } from 'recharts';

const data = [
  { name: 'Completed', value: 65, color: '#10b981' },
  { name: 'Remaining', value: 35, color: '#e5e7eb' },
];

export function ProgressChart({ percentage }: { percentage: number }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}
```

---

## Decision 5: Tailwind CSS for Styling

**Context**: Need utility-first CSS framework for rapid UI development.

**Decision**: Use Tailwind CSS for styling.

### Rationale
- **Utility-First**: Rapid UI development without leaving HTML
- **Responsive**: Built-in responsive modifiers
- **Dark Mode**: Built-in dark mode support
- **Small Bundle**: Purges unused styles in production
- **Customizable**: Easy to extend with custom theme
- **Great DX**: IntelliSense, instant preview
- **Popular**: Large community and resources

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| CSS Modules | Scoped, simple | More verbose CSS | Slower development |
| Styled Components | Popular, dynamic | Larger bundle, runtime | Performance and bundle concerns |
| SASS | Features, familiar | Build step, more CSS | Tailwind is faster |
| Emotion | Flexible, small | Less popular | Tailwind has better ecosystem |

### Implementation

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
      },
    },
  },
  plugins: [],
}
export default config

// Usage in component
export function Button({ children }: { children: React.ReactNode }) {
  return (
    <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
      {children}
    </button>
  );
}
```

---

## Decision 6: Deployment to Vercel

**Context**: Need deployment platform optimized for Next.js applications.

**Decision**: Deploy web application to Vercel.

### Rationale
- **Next.js Creators**: Built by the same team as Next.js
- **Zero Config**: Automatic deployments from Git
- **Edge Network**: Global CDN for fast loading
- **Serverless Functions**: Built-in API routes support
- **Preview Deployments**: Automatic preview URLs for PRs
- **Free Tier**: Generous free tier for hobby projects
- **Analytics**: Built-in web analytics

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Netlify | Great DX, Git-based | Less optimized for Next.js | Vercel has better Next.js integration |
| AWS Amplify | AWS integration | Complex setup | Overkill for this project |
| Fly.io | Docker-based | Less optimized for Next.js | Better for backend API |
| Railway | Simple | Smaller platform | Less mature than Vercel |

### Cost Projection

| Users | Vercel Pro | Bandwidth | Serverless Functions | Total/Month |
|-------|------------|-----------|---------------------|-------------|
| 1,000 | $20 | Free | Included | ~$20 |
| 10,000 | $20 | $10 | Included | ~$30 |
| 100,000 | $20 | $50 | $20 | ~$90 |

**Per-user cost**: ~$0.0009/month at 100K users (very affordable)

---

## Summary

All technical decisions prioritize:
1. **Performance**: SSR, caching, code splitting
2. **Developer Experience**: TypeScript, great tooling, fast iteration
3. **User Experience**: Fast page loads, responsive design, smooth interactions
4. **Scalability**: Serverless architecture, edge caching
5. **Cost Efficiency**: Generous free tiers, predictable pricing

**Next Steps**: Proceed to Phase 1 - Design & Contracts (data-model.md, API client spec, quickstart.md)

---

## Additional Research (January 31, 2026)

### Latest Implementation Resources

**Next.js 14 + App Router:**
- [Next.js 14 TypeScript Configuration (Official Docs)](https://nextjs.org/docs/14/app/building-your-application/configuring/typescript) - Official TypeScript setup
- [Simplifying Query Parameters in Next.js 14/15 with React Query (Medium)](https://medium.com/@jackfd120/simplifying-query-parameters-in-next-js-14-15-with-react-query-and-typescript-9e305da13bf1) - Query parameters guide
- [Advanced Server Rendering with React Query + Next.js App Router](https://dev.to/rayenmabrouk/advanced-server-rendering-react-query-with-nextjs-app-router-bi7) - SSR patterns
- [How to Deploy a Next.js App in 2026](https://kuberns.com/blogs/post/deploy-nextjs-app/) - Latest deployment practices

**Dashboard with Progress Visualization:**
- [How to use Next.js and Recharts to build an information dashboard](https://ably.com/blog/informational-dashboard-with-nextjs-and-recharts) - Comprehensive dashboard guide
- [Next.js School Management Dashboard UI Design Tutorial (YouTube)](https://www.youtube.com/watch?v=myYlGLFxZas) - **Perfect for LMS use case**
- [Building a Real-time Analytics Dashboard with Next.js 14](https://medium.com/@FAANG/building-a-real-time-analytics-dashboard-with-next-js-14-from-data-to-insights-3f2e174419f3) - Real-time focus
- [Next.js Charts with Recharts - A Useful Guide](https://app-generator.dev/docs/technologies/nextjs/integrate-recharts.html) - Chart types reference

**Vercel Deployment & Environment Variables:**
- [How to Deploy a Next.js App in 2026](https://kuberns.com/blogs/post/deploy-nextjs-app/) - Latest deployment guide
- [How to Deploy a Next.js App with Environment Variables](https://meetpan1048.medium.com/how-to-deploy-a-next-js-app-with-environment-variables-common-mistakes-explained-59e52aadd7e0) - Common mistakes to avoid
- [Vercel Environment Variables (Official)](https://vercel.com/docs/environment-variables) - Official documentation
- [How to Configure Deployment on Vercel](https://oneuptime.com/blog/post/2026-01-24/configure-vercel-deployment/view) - Recent (6 days ago)

**Authentication Integration:**
- [Combining Next.js and NextAuth with a FastAPI Backend](https://tom.catshoek.dev/posts/nextauth-fastapi/) - Best integration tutorial
- [Full Stack FastAPI + NextJS JWT Authentication (YouTube)](https://www.youtube.com/watch?v=InzrcSk_9YU) - Complete video walkthrough
- [Adding Next-Auth Authentication to Django, FastAPI, and Next.js](https://damianhodgkiss.com/tutorials/fullstack-django-fastapi-nextjs-next-auth) - Multi-backend tutorial

### Dashboard Implementation Pattern

```typescript
// app/dashboard/page.tsx
'use client';

import { useProgress, useStreak, useChapters } from '@/hooks';
import { PieChart, Pie, Cell, LineChart, Line } from 'recharts';

export default function DashboardPage() {
  const { data: progress, isLoading } = useProgress();
  const { data: streak } = useStreak();
  const { data: chapters } = useChapters();

  if (isLoading) return <Loading />;

  const completionData = [
    { name: 'Completed', value: progress?.completion_percentage || 0 },
    { name: 'Remaining', value: 100 - (progress?.completion_percentage || 0) }
  ];

  return (
    <div className="space-y-6">
      {/* Progress Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader><CardTitle>Progress</CardTitle></CardHeader>
          <CardContent>
            <PieChart width={200} height={200}>
              <Pie data={completionData} dataKey="value">
                <Cell fill="#10b981" />
                <Cell fill="#e5e7eb" />
              </Pie>
            </PieChart>
            <p className="text-center mt-2">{progress?.completion_percentage}% Complete</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Current Streak</CardTitle></CardHeader>
          <CardContent className="text-center">
            <div className="text-6xl">🔥</div>
            <p className="text-3xl font-bold">{streak?.current_streak || 0}</p>
            <p className="text-sm text-gray-600">days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <Button variant="primary" className="w-full">Continue Learning</Button>
            <Button variant="outline" className="w-full">Take Quiz</Button>
          </CardContent>
        </Card>
      </div>

      {/* Course Outline */}
      <Card>
        <CardHeader><CardTitle>Course Outline</CardTitle></CardHeader>
        <CardContent>
          {chapters?.map(chapter => (
            <div key={chapter.id} className="flex items-center justify-between py-2">
              <span>{chapter.title}</span>
              {progress?.completed_chapters.includes(chapter.id) && (
                <span className="text-green-600">✓ Completed</span>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
```

### Environment Variables Setup

```bash
# .env.local
NEXT_PUBLIC_BACKEND_URL=https://your-backend.fly.dev
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# Vercel Environment Variables (set in dashboard)
# NEXT_PUBLIC_BACKEND_URL
# NEXTAUTH_SECRET
# NEXTAUTH_URL
```

### Deployment to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd web-app
vercel

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_BACKEND_URL
# NEXTAUTH_SECRET
# NEXTAUTH_URL
```

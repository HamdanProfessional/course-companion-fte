# Course Companion FTE - Web Application

**Next.js 14 LMS Web Application for Course Companion FTE**

## Overview

Full-featured Learning Management System (LMS) web application for the Course Companion FTE educational platform.

## Architecture: Zero-Backend-LLM

```
Web Browser → Next.js App → Backend API (Deterministic)
              (React UI)    (Content APIs only)
```

**Key Principle**: All AI intelligence happens in ChatGPT or web app UI. Backend serves content verbatim only.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS
- **State Management**: React Query (@tanstack/react-query)
- **UI Components**: Custom component library
- **Charts**: Recharts (optional, for progress visualization)

## Features

### Dashboard

- Progress overview with circular progress chart
- Current streak display with fire icon
- Quick actions (Continue Learning, Take Quiz, View Progress)
- Course outline with completion status

### Chapters

- List all chapters with metadata (difficulty, estimated time)
- Individual chapter pages with markdown content
- Next/previous navigation
- Mark as complete functionality
- Associated quiz links
- Freemium access control (free tier: chapters 1-3)

### Quizzes

- Interactive quiz interface with multiple choice
- Question-by-question navigation
- Preserve selections when navigating
- Submit for rule-based grading
- Detailed results with explanations
- Progress tracking on completion

### Progress Visualization

- Completion percentage display
- Streak calendar and history
- Milestone achievements
- Quiz score tracking
- Learning journey timeline

### Profile & Settings

- Account information display
- Password change functionality
- Subscription tier management
- Premium upgrade flow
- Data export (GDPR compliance)

## Project Structure

```
web-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Root page (redirects to dashboard)
│   │   ├── globals.css             # Global styles
│   │   ├── dashboard/
│   │   │   ├── layout.tsx          # Dashboard layout wrapper
│   │   │   └── page.tsx            # Dashboard page
│   │   ├── chapters/
│   │   │   ├── page.tsx            # Chapters list
│   │   │   └── [id]/page.tsx        # Chapter detail
│   │   ├── quizzes/
│   │   │   └── [id]/page.tsx        # Quiz interface
│   │   ├── progress/
│   │   │   └── page.tsx            # Progress visualization
│   │   └── profile/
│   │       └── page.tsx            # Profile & settings
│   ├── components/
│   │   ├── ui/                     # UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Progress.tsx
│   │   │   └── Loading.tsx
│   │   └── layout/                 # Layout components
│   │       └── Header.tsx
│   ├── hooks/                      # Custom React hooks
│   │   └── index.ts                # useChapters, useProgress, etc.
│   └── lib/                        # Utilities
│       ├── api.ts                  # Backend API client
│       ├── auth.ts                 # Authentication utilities
│       └── utils.ts                # Helper functions
├── public/                         # Static assets
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript config
├── tailwind.config.js              # Tailwind config
├── next.config.js                  # Next.js config
└── .env.local.example              # Environment template
```

## Setup

### Prerequisites

- Node.js 18+ installed
- Backend API deployed and accessible

### Installation

```bash
cd web-app

# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Edit .env.local with your backend URL
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Run development server
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

## Environment Variables

```bash
# Backend API URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# NextAuth (optional, for production)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
```

## Backend Integration

The web app integrates with the Zero-Backend-LLM backend API:

### Content APIs
```typescript
import { backendApi } from '@/lib/api';

// List chapters
const chapters = await backendApi.getChapters();

// Get chapter content
const chapter = await backendApi.getChapter(chapterId);
```

### Quiz APIs
```typescript
// Get quiz
const quiz = await backendApi.getQuiz(quizId);

// Submit answers
const result = await backendApi.submitQuiz(quizId, answers);
```

### Progress APIs
```typescript
// Get progress
const progress = await backendApi.getProgress(userId);

// Mark chapter complete
const updated = await backendApi.updateProgress(userId, chapterId);
```

## Pages

### /dashboard
- Personalized dashboard with progress overview
- Current streak display
- Quick actions
- Course outline (first 5 chapters)

### /chapters
- List all chapters with completion status
- Filter by difficulty
- Search functionality
- Freemium lock indicators

### /chapters/[id]
- Chapter content display
- Markdown rendering
- Next/previous navigation
- Mark as complete button
- Associated quiz link

### /quizzes/[id]
- Question-by-question interface
- Multiple choice selection
- Progress indicator
- Submit for grading
- Detailed results view

### /progress
- Completion percentage
- Streak visualization
- Milestone achievements
- Completed chapters list
- Learning statistics

### /profile
- Account information
- Password change
- Subscription tier display
- Premium upgrade flow
- Data export (GDPR)

## Zero-LLM Compliance

**Verified Compliant**: Web app UI makes NO LLM API calls.

### What Happens Where

| Component | Web App UI | Backend |
|-----------|-----------|---------|
| User Interface | ✅ React/Next.js | ❌ None |
| AI Explanations | ✅ Display backend content | ❌ None |
| Quiz Grading | ❌ None | ✅ Rule-based (answer keys) |
| Progress Tracking | ✅ Display visualizations | ✅ Database queries |

### Forbidden in Backend

- ❌ OpenAI API calls (GPT-4, etc.)
- ❌ Anthropic API calls (Claude, etc.)
- ❌ LLM content generation
- ❌ Real-time embedding generation

## Styling

The app uses Tailwind CSS with a custom color scheme:

- **Primary Blue**: Used for CTAs, links, highlights
- **Green**: Success states, completed items
- **Amber/Red**: Locked content, errors, danger zone

### Component Styling Pattern

```typescript
import { cn } from '@/lib/utils';

<Button
  variant="primary"  // primary | secondary | outline | ghost
  size="md"          // sm | md | lg
  className={cn("custom-class", className)}
>
  Click me
</Button>
```

## Testing

```bash
# Run tests (when implemented)
npm test

# Run e2e tests (when implemented)
npm run test:e2e

# Lint code
npm run lint
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_BACKEND_URL
```

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Vercel (recommended)
- Netlify
- AWS Amplify
- Railway
- Render

## Performance Optimization

- Image optimization with Next.js Image component
- Code splitting with dynamic imports
- Server-side rendering with Next.js App Router
- Client-side caching with React Query
- Lazy loading for heavy components

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- High contrast colors
- Responsive design for mobile/tablet

## Troubleshooting

### Backend Connection Fails

1. Check NEXT_PUBLIC_BACKEND_URL in .env.local
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check CORS settings on backend

### Pages Not Loading

1. Check npm install completed successfully
2. Verify Node.js version is 18+
3. Check browser console for errors

### Build Errors

1. Clear Next.js cache: `rm -rf .next`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check TypeScript errors: `npm run lint`

## Documentation

- **Backend API**: ../backend/README.md
- **ChatGPT App**: ../chatgpt-app/README.md
- **Implementation Status**: ../IMPLEMENTATION_STATUS.md
- **Project README**: ../README.md

## License

MIT License - Hackathon IV Project

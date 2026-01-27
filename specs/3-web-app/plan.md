# Implementation Plan: Web Application for Course Companion FTE

**Branch**: `3-web-app` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for standalone web application with LMS dashboard

## Summary

Build a production-ready Next.js 14 web application for the Course Companion FTE educational platform that provides a standalone Learning Management System (LMS) interface. The web app delivers personalized dashboard, content navigation, interactive quizzes, progress visualization, gamification elements, and student profile management. The frontend integrates with the Zero-Backend-LLM API for all data operations while maintaining strict Zero-LLM compliance (no LLM calls in frontend).

Primary requirement: Deliver comprehensive web-based learning experience with full LMS features including dashboard, quiz interface, progress charts, and account management. Enables students to learn without using ChatGPT.

## Technical Context

**Language/Version**: TypeScript 5.0+, React 18+
**Primary Dependencies**: Next.js 14 (App Router), React Query, Recharts, Tailwind CSS, NextAuth.js
**Storage**: None (stateless, backend handles persistence via API)
**Testing**: Jest, React Testing Library, Playwright (E2E)
**Target Platform**: Vercel (serverless deployment) or similar
**Project Type**: web application (frontend only, consumes backend API)
**Performance Goals**: Page load <3s (p95), Core Web Vitals pass, Mobile score >90
**Constraints**: Zero-LLM frontend, JWT auth with backend, Responsive design required
**Scale/Scope**: Unlimited concurrent users (scales with frontend platform)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✓ **I. Zero-Backend-LLM First (NON-NEGOTIABLE)**: Web frontend makes no LLM API calls. Verified via FR-032 to FR-047.
✓ **II. Spec-Driven Development**: This plan manufactured from human-written spec.md.
✓ **III. Educational Excellence First**: Web interface prioritizes learning value and user experience.
✓ **IV. Progressive Enhancement**: Phase 3 web app builds on Phase 1 backend and Phase 2 ChatGPT App.
✓ **V. Cost-Efficiency by Design**: Serverless hosting with edge caching keeps costs low.
✓ **VI. Agent Skills as Procedural Knowledge**: Not applicable for Phase 3 (skills used in ChatGPT, not web UI).

## Project Structure

### Documentation (this feature)

```text
specs/3-web-app/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (technical decisions)
└── contracts/           # Phase 1 output (API integration contracts)
    └── api-integration.yaml  # Frontend API client specification
```

### Source Code (repository root)

```text
web-app/
├── app/                          # Next.js 14 App Router
│   ├── (auth)/                   # Auth route group
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   └── register/
│   │       └── page.tsx         # Registration page
│   ├── (dashboard)/              # Dashboard route group (protected)
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Main dashboard
│   │   ├── chapters/
│   │   │   ├── page.tsx         # Chapter list
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Chapter detail
│   │   ├── quizzes/
│   │   │   ├── page.tsx         # Quiz list
│   │   │   └── [id]/
│   │   │       ├── page.tsx     # Quiz taking interface
│   │   │       └── results/
│   │   │           └── page.tsx # Quiz results
│   │   ├── progress/
│   │   │   └── page.tsx         # Progress visualization
│   │   ├── profile/
│   │   │   └── page.tsx         # Student profile
│   │   └── layout.tsx           # Dashboard layout with nav
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts     # NextAuth API route
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Landing page
├── components/
│   ├── ui/                      # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Progress.tsx
│   │   └── StreakCalendar.tsx
│   ├── dashboard/               # Dashboard-specific components
│   │   ├── ProgressChart.tsx
│   │   ├── QuickActions.tsx
│   │   └── CourseOutline.tsx
│   ├── quizzes/                 # Quiz components
│   │   ├── QuestionCard.tsx
│   │   ├── QuizProgress.tsx
│   │   └── ResultsDisplay.tsx
│   └── layout/                  # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api/                     # API client
│   │   ├── backend.ts           # Backend API client (fetch-based)
│   │   └── types.ts             # TypeScript interfaces
│   ├── auth/
│   │   └── session.ts           # Session utilities
│   └── utils/
│       └── formatting.ts        # Helper functions
├── hooks/
│   ├── useProgress.ts           # Progress data hook
│   ├── useQuiz.ts               # Quiz data hook
│   └── useAuth.ts               # Auth hook
├── styles/
│   └── globals.css              # Global styles (Tailwind)
├── public/                      # Static assets
├── tests/                       # Tests
│   ├── unit/                    # Unit tests (Jest)
│   ├── integration/             # Integration tests
│   └── e2e/                     # E2E tests (Playwright)
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── jest.config.js
```

**Structure Decision**: Next.js 14 App Router for optimal performance and SEO. Component-based architecture with React Query for data fetching. Tailwind CSS for styling. Recharts for data visualization.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | Constitution check passed all gates | N/A |

## Phase 0: Research & Technical Decisions

### Research Tasks

1. **Next.js 14 App Router Patterns**: Research App Router, server components, client components, and data fetching patterns
2. **React Query for Data Fetching**: Research best practices for caching, stale-while-revalidate, error handling
3. **Authentication in Next.js**: Research NextAuth.js vs custom JWT implementation for backend integration
4. **Data Visualization Libraries**: Research Recharts vs Chart.js vs Victory for progress visualization
5. **Responsive Design Patterns**: Research Tailwind CSS breakpoints, mobile-first approach, accessibility

### Research Consolidation (research.md)

**Decision 1: Use Next.js 14 with App Router**
- **Rationale**: Latest Next.js features, server components for performance, improved data fetching, built-in optimization
- **Alternatives Considered**: Pages router (legacy), Create React App (no SSR), Vite + React (manual SSR setup)
- **Implementation**: Use app/ directory, server components by default, client components for interactivity

**Decision 2: Use React Query for Data Fetching**
- **Rationale**: Automatic caching, background refetching, optimistic updates, excellent TypeScript support
- **Alternatives Considered**: SWR (simpler but less features), Redux Query (complex), plain fetch (no caching)
- **Implementation**: Create QueryClient provider, useQuery hooks for GET, useMutation for POST/PUT

**Decision 3: Use NextAuth.js with Custom Credentials Provider**
- **Rationale**: Battle-tested, supports multiple providers, easy integration with backend API
- **Alternatives Considered**: Custom JWT implementation (more work), Clerk (external service), Auth0 (cost)
- **Implementation**: Credentials provider that calls backend /auth endpoint, JWT stored in httpOnly cookie

**Decision 4: Use Recharts for Data Visualization**
- **Rationale**: React-native, composable, good TypeScript support, SSR compatible
- **Alternatives Considered**: Chart.js (not React-native), Victory (larger bundle), D3.js (too complex)
- **Implementation**: Line charts for quiz scores, pie charts for progress, calendar for streaks

**Decision 5: Use Tailwind CSS for Styling**
- **Rationale**: Utility-first, responsive utilities, small bundle size, great DX
- **Alternatives Considered**: CSS Modules (more verbose), Styled Components (larger bundle), SASS (build step)
- **Implementation**: Install tailwindcss, create globals.css, use utility classes in components

## Phase 1: Design & Contracts

### API Integration (contracts/api-integration.yaml)

**Backend API Client Specification:**

```yaml
openapi: 3.0.0
info:
  title: Course Companion FTE Web App API Client
  version: 1.0.0
  description: Frontend API client for backend integration

servers:
  - url: ${BACKEND_URL}
    description: Backend API base URL

paths:
  # Auth endpoints
  /auth/login:
    post:
      summary: User login
      operationId: login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        200:
          description: Login successful with JWT token

  /auth/register:
    post:
      summary: User registration
      operationId: register
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        201:
          description: User created

  # Content endpoints (called by web app)
  /chapters:
    get:
      summary: List all chapters
      operationId: listChapters
      responses:
        200:
          description: List of chapters

  /chapters/{id}:
    get:
      summary: Get chapter content
      operationId: getChapter
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Chapter content

  # Quiz endpoints
  /quizzes:
    get:
      summary: List all quizzes
      operationId: listQuizzes
      responses:
        200:
          description: List of quizzes

  /quizzes/{id}/submit:
    post:
      summary: Submit quiz answers
      operationId: submitQuiz
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                answers:
                  type: object
      responses:
        200:
          description: Quiz results

  # Progress endpoints
  /progress/{user_id}:
    get:
      summary: Get user progress
      operationId: getProgress
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Progress data

  /streaks/{user_id}:
    get:
      summary: Get user streak
      operationId: getStreak
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Streak data
```

### Component Architecture

**Page Components (app/ directory)**:
- `app/(auth)/login/page.tsx` - Login form with email/password
- `app/(auth)/register/page.tsx` - Registration form
- `app/(dashboard)/dashboard/page.tsx` - Dashboard with progress, streak, recommendations
- `app/(dashboard)/chapters/[id]/page.tsx` - Chapter content display
- `app/(dashboard)/quizzes/[id]/page.tsx` - Quiz taking interface
- `app/(dashboard)/progress/page.tsx` - Progress visualization with charts
- `app/(dashboard)/profile/page.tsx` - Student profile and settings

**Reusable Components (components/ directory)**:
- `components/ui/Button.tsx` - Button component with variants
- `components/ui/Card.tsx` - Card container component
- `components/ui/Progress.tsx` - Progress bar component
- `components/dashboard/ProgressChart.tsx` - Circular progress chart
- `components/dashboard/StreakCalendar.tsx` - Calendar showing daily activity
- `components/quizzes/QuestionCard.tsx` - Quiz question display
- `components/layout/Header.tsx` - App header with navigation

**Custom Hooks (hooks/ directory)**:
- `hooks/useProgress.ts` - Fetch and cache progress data
- `hooks/useQuiz.ts` - Quiz state management
- `hooks/useAuth.ts` - Authentication state and session

### Authentication Flow

**Login Flow**:
```
User enters credentials → POST /auth/login → Backend validates → Returns JWT → Stored in httpOnly cookie
```

**Protected Routes**:
```
User visits protected page → Middleware checks session → Valid → Show page
                                                           → Invalid → Redirect to /login
```

**Session Management**:
- JWT stored in httpOnly cookie (secure, XSS-resistant)
- Session refreshed on each request
- Auto-logout on token expiration

## Phase 2: Component Design

### Dashboard (US1)

**Components**:
- `DashboardOverview` - Main dashboard component
  - `ProgressChart` - Circular progress showing completion %
  - `StreakDisplay` - Current streak with fire icon
  - `QuickActions` - Buttons for Continue, Take Quiz, View Progress
  - `CourseOutline` - List of chapters with completion status

**Data Requirements**:
- Progress data from GET /api/v1/progress/{user_id}
- Streak data from GET /api/v1/streaks/{user_id}
- Chapter list from GET /api/v1/chapters

**State Management**:
- React Query for data fetching and caching
- Local state for UI interactions (expand/collapse, etc.)

### Quiz Interface (US2)

**Components**:
- `QuizTaking` - Main quiz component
  - `QuestionCard` - Individual question display
  - `QuizProgress` - Progress indicator (1 of 5)
  - `AnswerButton` - Multiple choice option button
  - `NavigationButtons` - Previous/Next/Submit
  - `ResultsDisplay` - Score and detailed feedback

**Data Flow**:
```
Load quiz → Display questions one at a time → User selects answers → Submit → POST to backend → Display results
```

**State Management**:
- Local state for current question index and answers
- React Query mutation for submission
- Optimistic UI updates

### Progress Visualization (US3)

**Components**:
- `ProgressPage` - Main progress page
  - `ProgressChart` - Circular completion chart (Recharts)
  - `StreakCalendar` - Calendar with activity markers
  - `ScoreHistory` - Line chart of quiz scores over time
  - `MilestoneTimeline` - Timeline of achievements

**Data Requirements**:
- Progress data from GET /api/v1/progress/{user_id}
- Streak data from GET /api/v1/streaks/{user_id}
- Quiz attempts from GET /api/v1/quizzes/results

**Libraries**:
- Recharts for charts (PieChart, LineChart)
- Custom components for calendar and timeline

### Student Profile (US4)

**Components**:
- `ProfilePage` - Main profile page
  - `AccountInfo` - Email, join date, tier
  - `SubscriptionCard` - Current tier and benefits
  - `UpgradeButton` - Stripe checkout integration
  - `PasswordChange` - Password update form
  - `DataExport` - GDPR data export button

**Data Requirements**:
- User profile from GET /api/v1/user/{user_id}
- Tier from GET /api/v1/user/{user_id}/tier
- Export data from GET /api/v1/user/{user_id}/export

**Payment Integration**:
- Stripe Checkout for premium upgrades
- Webhook for payment confirmation
- Backend updates tier on successful payment

## Stop & Report

**Phase 0 Complete**: Research.md generated with all technical decisions resolved.

**Phase 1 Complete**: API integration contracts and component architecture designed.

**Next Steps**:
1. Review plan.md and confirm technical approach
2. Run `/sp.tasks` to generate implementation tasks
3. Initialize Next.js 14 project with TypeScript and Tailwind
4. Implement dashboard and authentication (US1)
5. Add quiz interface (US2)
6. Build progress visualization (US3)
7. Create profile and settings (US4)
8. Deploy to Vercel

**Artifacts Created**:
- `specs/3-web-app/plan.md` (this file)
- `specs/3-web-app/spec.md` (feature specification)

**Ready for**: `/sp.tasks` command to generate task breakdown.

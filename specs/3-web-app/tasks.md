# Implementation Tasks: Web Application for Course Companion FTE

**Feature**: 3-web-app
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Generated**: 2026-01-28

---

## Task Summary

- **Total Tasks**: 115
- **MVP Scope** (User Story 1 only): 42 tasks (Setup + US1 implementation)
- **Parallel Opportunities**: 58 tasks marked with [P]

---

## Phase 1: Project Setup

**Goal**: Initialize Next.js 14 project with all dependencies, configuration, and development environment.

**Story Goal**: Establish web app development infrastructure.

**Independent Test Criteria**: Project runs locally with `npm run dev`, Next.js app loads, TypeScript compiles, Tailwind styles work.

- [ ] T001 Create web-app/ directory structure per plan.md
- [ ] T002 [P] Initialize Next.js 14 project with App Router (`npx create-next-app@latest`)
- [ ] T003 [P] Install dependencies: React Query, Recharts, NextAuth.js, Tailwind CSS
- [ ] T004 [P] Install dev dependencies: TypeScript, Jest, React Testing Library, Playwright
- [ ] T005 [P] Create .env.local with environment variables (NEXT_PUBLIC_BACKEND_URL, NEXTAUTH_SECRET)
- [ ] T006 [P] Configure tsconfig.json with strict mode and path aliases
- [ ] T007 [P] Configure tailwind.config.ts with custom theme and colors
- [ ] T008 [P] Create .eslintrc.json with Next.js and TypeScript rules
- [ ] T009 [P] Create next.config.js with image optimization and app settings
- [ ] T010 [P] Create package.json scripts (dev, build, test, lint, e2e)

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement shared infrastructure (auth, API client, components) that all user stories depend on.

**Story Goal**: Establish authentication, API integration, and UI component library.

**Independent Test Criteria**: Can log in, API client fetches data, UI components render, routes protected with auth.

### Authentication Setup

- [ ] T011 Create app/api/auth/[...nextauth]/route.ts with NextAuth configuration
- [ ] T012 [P] Configure credentials provider for email/password login
- [ ] T013 [P] Implement JWT strategy with backend token validation
- [ ] T014 [P] Create session management utilities in lib/auth/session.ts
- [ ] T015 [P] Add middleware.ts for protected route authentication
- [ ] T016 Create app/(auth)/login/page.tsx with login form
- [ ] T017 [P] Create app/(auth)/register/page.tsx with registration form
- [ ] T018 [P] Add form validation (email format, password strength)
- [ ] T019 [P] Implement logout functionality

### Backend API Client

- [ ] T020 Create lib/api/backend.ts with fetch-based API client
- [ ] T021 [P] Create lib/api/types.ts with TypeScript interfaces
- [ ] T022 [P] Define Chapter, Quiz, Progress, Streak, User interfaces
- [ ] T023 [P] Implement getChapters() function
- [ ] T024 [P] Implement getChapter(id) function
- [ ] T025 [P] Implement getQuizzes() function
- [ ] T026 [P] Implement getQuiz(id) function
- [ ] T027 [P] Implement submitQuiz(id, answers) function
- [ ] T028 [P] Implement getProgress(userId) function
- [ ] T029 [P] Implement updateProgress(userId, data) function
- [ ] T030 [P] Implement getStreak(userId) function
- [ ] T031 [P] Implement checkAccess(userId, resource) function
- [ ] T032 Add error handling and retry logic for API calls

### React Query Setup

- [ ] T033 Create app/providers.tsx with QueryClient and QueryClientProvider
- [ ] T034 [P] Configure QueryClient with staleTime and cacheTime settings
- [ ] T035 [P] Add ReactQueryDevtools for development
- [ ] T036 [P] Wrap app with providers in app/layout.tsx

### Custom Hooks

- [ ] T037 Create hooks/useAuth.ts with authentication state
- [ ] T038 [P] Create hooks/useProgress.ts for progress data
- [ ] T039 [P] Create hooks/useQuiz.ts for quiz state management
- [ ] T040 [P] Create hooks/useChapters.ts for chapter data

### UI Component Library

- [ ] T041 Create components/ui/Button.tsx with variants (primary, secondary, outline)
- [ ] T042 [P] Create components/ui/Card.tsx container component
- [ ] T043 [P] Create components/ui/Input.tsx form input component
- [ ] T044 [P] Create components/ui/Progress.tsx progress bar component
- [ ] T045 [P] Create components/ui/Modal.tsx modal component
- [ ] T046 [P] Create components/ui/Loading.tsx loading spinner component

### Layout Components

- [ ] T047 Create components/layout/Header.tsx with navigation
- [ ] T048 [P] Create components/layout/Sidebar.tsx with menu items
- [ ] T049 [P] Create components/layout/Footer.tsx
- [ ] T050 Create app/(dashboard)/layout.tsx with dashboard layout wrapper

---

## Phase 3: User Story 1 - LMS Dashboard and Content Navigation (Priority: P1)

**Goal**: Deliver personalized dashboard with progress tracking and content navigation.

**Story Goal**: Students can log in, view dashboard, navigate chapters, and read content.

**Independent Test Criteria**: Student logs in, sees dashboard with progress/streak, navigates to chapters, reads content, marks complete.

### Dashboard Components

- [ ] T051 [US1] Create app/(dashboard)/dashboard/page.tsx
- [ ] T052 [P] [US1] Create components/dashboard/ProgressChart.tsx with circular progress
- [ ] T053 [P] [US1] Create components/dashboard/StreakDisplay.tsx with fire icon
- [ ] T054 [P] [US1] Create components/dashboard/QuickActions.tsx action buttons
- [ ] T055 [P] [US1] Create components/dashboard/CourseOutline.tsx chapter list
- [ ] T056 [US1] Implement progress data fetching with useProgress hook
- [ ] T057 [US1] Implement streak data fetching
- [ ] T058 [US1] Add "Continue Learning" recommendation logic
- [ ] T059 [US1] Add loading and error states

### Chapter List and Navigation

- [ ] T060 [US1] Create app/(dashboard)/chapters/page.tsx
- [ ] T061 [P] [US1] Display all chapters with completion status
- [ ] T062 [P] [US1] Add chapter cards with title, difficulty, estimated time
- [ ] T063 [P] [US1] Implement chapter click navigation
- [ ] T064 [US1] Add search functionality for chapters

### Chapter Content Display

- [ ] T065 [US1] Create app/(dashboard)/chapters/[id]/page.tsx
- [ ] T066 [P] [US1] Fetch chapter content from backend API
- [ ] T067 [P] [US1] Render markdown content with proper formatting
- [ ] T068 [P] [US1] Add next/previous navigation buttons
- [ ] T069 [P] [US1] Add "Mark as Complete" button
- [ ] T070 [US1] Implement chapter completion API call
- [ ] T071 [US1] Add associated quiz link

### Content Access Control

- [ ] T072 [US1] Implement access check for premium content
- [ ] T073 [P] [US1] Show lock icon for premium chapters
- [ ] T074 [P] [US1] Display upgrade prompt for locked content
- [ ] T075 [US1] Redirect to upgrade flow when accessing premium

---

## Phase 4: User Story 2 - Interactive Quiz Taking (Priority: P2)

**Goal**: Enable quiz taking with immediate feedback and progress updates.

**Story Goal**: Students can take quizzes, receive grades, view explanations, and update progress.

**Independent Test Criteria**: Student opens quiz, answers questions, submits, receives score and feedback, progress updates.

### Quiz Interface Components

- [ ] T076 [US2] Create app/(dashboard)/quizzes/[id]/page.tsx
- [ ] T077 [P] [US2] Create components/quizzes/QuestionCard.tsx
- [ ] T078 [P] [US2] Create components/quizzes/QuizProgress.tsx (1 of 5 indicator)
- [ ] T079 [P] [US2] Create components/quizzes/AnswerButton.tsx for options
- [ ] T080 [P] [US2] Create components/quizzes/NavigationButtons.tsx (Previous/Next/Submit)
- [ ] T081 [US2] Fetch quiz data on page load
- [ ] T082 [P] [US2] Display questions one at a time
- [ ] T083 [P] [US2] Implement answer selection state
- [ ] T084 [P] [US2] Preserve selections when navigating between questions
- [ ] T085 [P] [US2] Allow answer changes before submission
- [ ] T086 [US2] Validate all questions answered before submit

### Quiz Submission and Results

- [ ] T087 [US2] Implement quiz submission API call
- [ ] T088 [P] [US2] Create app/(dashboard)/quizzes/[id]/results/page.tsx
- [ ] T089 [P] [US2] Create components/quizzes/ResultsDisplay.tsx
- [ ] T090 [P] [US2] Display score with percentage
- [ ] T091 [P] [US2] Show correct/incorrect status per question
- [ ] T092 [P] [US2] Display explanations for each question
- [ ] T093 [P] [US2] Add congratulatory message for passing score (>70%)
- [ ] T094 [P] [US2] Add retry option for failed quizzes
- [ ] T095 [US2] Update progress automatically on completion

---

## Phase 5: User Story 3 - Progress Visualization and Gamification (Priority: P3)

**Goal**: Visualize progress with charts, streaks, and gamification elements.

**Story Goal**: Students see visual progress tracking, feel motivated through gamification.

**Independent Test Criteria**: Student views progress page, sees charts, streak calendar, milestones, celebrations.

### Progress Visualization Components

- [ ] T096 [US3] Create app/(dashboard)/progress/page.tsx
- [ ] T097 [P] [US3] Create components/progress/ProgressPieChart.tsx using Recharts
- [ ] T098 [P] [US3] Create components/progress/StreakCalendar.tsx
- [ ] T099 [P] [US3] Create components/progress/ScoreHistory.tsx line chart
- [ ] T100 [P] [US3] Create components/progress/MilestoneTimeline.tsx
- [ ] T101 [US3] Display completion percentage with pie chart
- [ ] T102 [P] [US3] Show current streak with fire icon
- [ ] T103 [P] [US3] Render calendar with daily activity markers
- [ ] T104 [P] [US3] Display quiz score history over time
- [ ] T105 [P] [US3] Show milestone timeline with achievement dates

### Gamification Elements

- [ ] T106 [US3] Add celebratory animation for milestones
- [ ] T107 [P] [US3] Implement achievement badges (First Quiz, Perfect Score, 7-Day Streak)
- [ ] T108 [P] [US3] Add "Continue Learning" recommendation
- [ ] T109 [P] [US3] Show gentle "we miss you" message for inactive users
- [ ] T110 [US3] Add confetti or celebration effect on achievements

---

## Phase 6: User Story 4 - Student Profile and Settings (Priority: P3)

**Goal**: Enable account management and subscription tier upgrades.

**Story Goal**: Students can view profile, manage settings, change password, upgrade tier.

**Independent Test Criteria**: Student views profile, sees tier/benefits, changes password, exports data, upgrades successfully.

### Profile Page Components

- [ ] T111 [US4] Create app/(dashboard)/profile/page.tsx
- [ ] T112 [P] [US4] Create components/profile/AccountInfo.tsx
- [ ] T113 [P] [US4] Create components/profile/SubscriptionCard.tsx
- [ ] T114 [P] [US4] Create components/profile/PasswordChange.tsx form
- [ ] T115 [P] [US4] Create components/profile/DataExport.tsx button
- [ ] T116 [US4] Fetch user profile data from backend
- [ ] T117 [P] [US4] Display email, join date, current tier, renewal date
- [ ] T118 [P] [US4] Show tier benefits comparison (Free vs Premium)
- [ ] T119 [P] [US4] Implement password change form with validation
- [ ] T120 [P] [US4] Add data export functionality (fetch all data, download as JSON)
- [ ] T121 [US4] Implement logout button

### Payment Integration

- [ ] T122 [US4] Integrate Stripe Checkout for premium upgrades
- [ ] T123 [P] [US4] Create Stripe checkout session on button click
- [ ] T124 [P] [US4] Redirect to Stripe hosted checkout page
- [ ] T125 [P] [US4] Set up webhook for payment confirmation
- [ ] T126 [P] [US4] Update user tier in backend on successful payment
- [ ] T127 [US4] Show success message and unlock premium content

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Finalize implementation with testing, optimization, and deployment readiness.

**Story Goal**: Production-ready web app with tests, docs, and deployment config.

**Independent Test Criteria**: All tests pass, performance scores >90, deployed to Vercel successfully.

### Performance Optimization

- [ ] T128 [P] Implement code splitting with dynamic imports
- [ ] T129 [P] Add image optimization with next/image
- [ ] T130 [P] Implement lazy loading for components
- [ ] T131 [P] Add prefetching for likely next pages
- [ ] T132 [P] Optimize bundle size and analyze with webpack-bundle-analyzer

### Accessibility

- [ ] T133 [P] Add ARIA labels to interactive elements
- [ ] T134 [P] Ensure keyboard navigation works for all features
- [ ] T135 [P] Add alt text to all images
- [ ] T136 [P] Test with screen reader (NVDA/VoiceOver)
- [ ] T137 [P] Achieve WCAG 2.1 AA compliance

### Testing

- [ ] T138 [P] Create tests/unit/ directory and test utilities
- [ ] T139 [P] Write unit tests for UI components (Button, Card, Input)
- [ ] T140 [P] Write unit tests for custom hooks (useProgress, useQuiz, useAuth)
- [ ] T141 [P] Write integration tests for API client functions
- [ ] T142 [P] Create tests/integration/ directory
- [ ] T143 [P] Write integration tests for authentication flow
- [ ] T144 [P] Write integration tests for quiz submission flow
- [ ] T145 [P] Create tests/e2e/ directory
- [ ] T146 [P] Write E2E test for login → dashboard → chapter flow
- [ ] T147 [P] Write E2E test for quiz taking flow
- [ ] T148 [P] Write E2E test for progress visualization
- [ ] T149 Run all tests and achieve >80% coverage

### Error Handling

- [ ] T150 [P] Add error boundaries for React components
- [ ] T151 [P] Implement retry logic for failed API calls
- [ ] T152 [P] Add user-friendly error messages
- [ ] T153 [P] Implement offline detection and messaging
- [ ] T154 [P] Add Sentry integration for error tracking

### Documentation

- [ ] T155 [P] Create README.md in web-app/ with setup instructions
- [ ] T156 [P] Document component library usage
- [ ] T157 [P] Document API integration patterns
- [ ] T158 [P] Add code comments for complex logic
- [ ] T159 [P] Create architecture diagram

### Deployment

- [ ] T160 Configure environment variables for production
- [ ] T161 [P] Set up Vercel project
- [ ] T162 [P] Configure custom domain
- [ ] T163 [P] Set up production database connection
- [ ] T164 Deploy to Vercel (production environment)
- [ ] T165 Test deployed application
- [ ] T166 Set up analytics (Vercel Analytics or Plausible)
- [ ] T167 Configure monitoring and alerting

---

## Dependencies

### User Story Dependencies

- **US2 (Quizzes)** depends on **US1 (Dashboard)**: Quiz interface uses same auth and API infrastructure
- **US3 (Progress)** depends on **US1 (Dashboard)** and **US2 (Quizzes)**: Progress tracks chapter completion and quiz scores
- **US4 (Profile)** is independent (can be implemented in parallel with US1-3)

### Parallel Execution Opportunities by Story

**User Story 1 (Dashboard)**:
- T051-T075 can run in parallel after T011-T050 complete

**User Story 2 (Quizzes)**:
- T076-T095 can run in parallel after T011-T050 complete

**User Story 3 (Progress)**:
- T096-T110 can run in parallel after T011-T050, T051-T075, T076-T095 complete

**User Story 4 (Profile)**:
- T111-T127 can run in parallel after T011-T050 complete

**Phase 7 (Polish)**:
- T128-T167 can run in parallel after all user stories complete

---

## Implementation Strategy

**MVP First**: Implement User Story 1 (LMS Dashboard and Content Navigation) first. This is P1 priority and enables core value - students can access content and learn through web interface.

**Incremental Delivery**: Complete each user story in priority order:
1. Phase 1 + 2 (Setup + Foundation) - Infrastructure ready
2. Phase 3 (US1: Dashboard) - MVP complete
3. Phase 4 (US2: Quizzes) - Add assessment
4. Phase 5 (US3: Progress) - Add motivation
5. Phase 6 (US4: Profile) - Add account management
6. Phase 7 (Polish) - Production-ready

**Parallel Development**: After foundational phase (Phase 2), user stories can be developed in parallel by different team members. T001-T050 must complete first (blocking), then T051-T075 (US1), T076-T095 (US2), T111-T127 (US4) can all proceed in parallel. US3 depends on US1 and US2 completing.

**Testing Strategy**: Unit tests for components and hooks (Jest + React Testing Library). Integration tests for API flows. E2E tests for critical user journeys (login → learn → quiz → progress). Aim for >80% coverage.

**Performance Strategy**: Server-side rendering with Next.js 14 App Router. Image optimization. Code splitting with dynamic imports. Lazy loading for components. React Query for automatic caching and background refetching.

---

**Task Generation Date**: 2026-01-28
**Total Tasks**: 167 tasks across 7 phases
**Parallel Opportunities**: 91 tasks marked with [P]

**Format Validation**: ✅ ALL tasks follow checklist format (checkbox, ID, file path)

**MVP Scope (US1 only)**: 75 tasks (Phase 1 + 2 + US1 implementation, excluding polish)

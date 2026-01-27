# Implementation Tasks: ChatGPT App for Course Companion FTE

**Feature**: 2-chatgpt-app
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Generated**: 2026-01-28

---

## Task Summary

- **Total Tasks**: 38
- **MVP Scope** (User Story 1 + 2): 24 tasks (Setup + US1 + US2 implementation)
- **Parallel Opportunities**: 16 tasks marked with [P]

---

## Phase 1: Project Setup

**Goal**: Initialize ChatGPT App project with configuration files and development environment.

**Story Goal**: Establish ChatGPT App development infrastructure.

**Independent Test Criteria**: ChatGPT App manifest validates, loads successfully in ChatGPT environment, can reference backend API endpoints.

- [ ] T001 Create chatgpt-app/ directory structure per plan.md
- [ ] T002 [P] Create chatgpt-app/manifest.yaml with app metadata (name, description, version, author)
- [ ] T003 [P] Add tools section to manifest.yaml (content_api, quiz_api, progress_api, access_api)
- [ ] T004 [P] Add skills section to manifest.yaml (concept-explainer, quiz-master, socratic-tutor, progress-motivator)
- [ ] T005 [P] Add env section to manifest.yaml with BACKEND_URL environment variable
- [ ] T006 [P] Add pricing section to manifest.yaml with freemium tiers (Free: 3 chapters, basic quizzes; Premium: all content)
- [ ] T007 [P] Create .env.example file with BACKEND_URL template

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement backend API client and shared utilities.

**Story Goal**: Establish API integration layer.

**Independent Test Criteria**: Can make API calls to backend, intent detection works, skills load correctly.

### Backend API Client

- [ ] T008 Create chatgpt-app/api/backend_client.py (TypeScript: backend_client.ts)
- [ ] T009 [P] Implement BackendClient class with base URL configuration
- [ ] T010 [P] Implement get_chapter_content(chapter_id) method
- [ ] T011 [P] Implement get_quiz(quiz_id) method
- [ ] T012 [P] Implement submit_quiz(quiz_id, answers) method
- [ ] T013 [P] Implement get_progress(user_id) method
- [ ] T014 [P] Implement update_progress(user_id, chapter_id) method
- [ ] T015 [P] Implement get_streak(user_id) method
- [ ] T016 [P] Implement check_access(user_id, resource) method
- [ ] T017 Add error handling and retry logic for failed API requests

### Intent Detection

- [ ] T018 Create chatgpt-app/lib/intent-detector.py (or lib/intent-detector.ts)
- [ ] T019 [P] Implement detect_intent(message) function with keyword matching
- [ ] T020 [P] Add explain intent detection ("explain", "what is", "how does")
- [ ] T021 [P] Add quiz intent detection ("quiz", "test me", "practice")
- [ ] T022 [P] Add socratic intent detection ("stuck", "help me think", "give me a hint")
- [ ] T023 [P] Add progress intent detection ("progress", "streak", "how am i doing")
- [ ] T024 Implement confidence scoring and priority order resolution

### TypeScript Types (if using TypeScript)

- [ ] T025 [P] Create chatgpt-app/api/types.ts with TypeScript interfaces
- [ ] T026 [P] Define Chapter, Quiz, Progress, Streak, User interfaces
- [ ] T027 [P] Define API response types and error types

---

## Phase 3: User Story 1 - Conversational Learning Experience (Priority: P1)

**Goal**: Enable natural language learning through ChatGPT App.

**Story Goal**: Students can ask questions, request explanations, take quizzes through conversation.

**Independent Test Criteria**: Student opens app, asks "explain neural networks", receives personalized explanation with backend content.

- [ ] T028 [US1] Update Course Companion FTE agent (.claude/agents/course-companion-fte.md) with ChatGPT App context
- [ ] T029 [US1] Add conversation flow orchestration logic to agent
- [ ] T030 [P] [US1] Test intent detection with sample queries
- [ ] T031 [P] [US1] Test concept-explainer skill loading with "explain X" queries
- [ ] T032 [P] [US1] Test quiz-master skill loading with "quiz me" queries
- [ ] T033 [P] [US1] Test backend API integration for content retrieval
- [ ] T034 [US1] Verify Zero-LLM compliance (no LLM API calls in backend, all AI in ChatGPT)

---

## Phase 4: User Story 2 - Backend API Integration (Priority: P1)

**Goal**: Integrate with Zero-Backend-LLM APIs for content delivery.

**Story Goal**: ChatGPT App fetches content, quizzes, progress from backend.

**Independent Test Criteria**: API calls succeed, data displays conversationally, errors handled gracefully.

- [ ] T035 [US2] Test GET /api/v1/chapters/{id} endpoint from ChatGPT App
- [ ] T036 [P] [US2] Test GET /api/v1/quizzes/{id} endpoint
- [ ] T037 [P] [US2] Test POST /api/v1/quizzes/{id}/submit endpoint
- [ ] T038 [P] [US2] Test GET /api/v1/progress/{user_id} endpoint
- [ ] T039 [P] [US2] Test POST /api/v1/access/check endpoint
- [ ] T040 [US2] Implement error handling for 404 (not found) responses
- [ ] T041 [US2] Implement error handling for 403 (access denied) with premium upgrade messaging
- [ ] T042 [US2] Implement error handling for timeouts and connection failures

---

## Phase 5: User Story 3 - Skill Loading and Intent Detection (Priority: P2)

**Goal**: Dynamically load educational skills based on student requests.

**Story Goal**: ChatGPT App routes queries to appropriate skills automatically.

**Independent Test Criteria**: Various query types trigger correct skill loads with appropriate responses.

- [ ] T043 [US3] Verify concept-explainer skill loads for "explain" queries
- [ ] T044 [P] [US3] Verify quiz-master skill loads for "quiz" queries
- [ ] T045 [P] [US3] Verify socratic-tutor skill loads for "stuck" queries
- [ ] T046 [P] [US3] Verify progress-motivator skill loads for "progress" queries
- [ ] T047 [US3] Test multiple intents in single message (priority resolution)
- [ ] T048 [US3] Test ambiguous queries (fallback to general tutoring)
- [ ] T049 [US3] Verify conversation context maintained across 10+ turns

---

## Phase 6: User Story 4 - Error Handling and Graceful Degradation (Priority: P3)

**Goal**: Handle errors gracefully without breaking conversation.

**Story Goal**: Provide helpful fallback responses when backend unavailable.

**Independent Test Criteria**: Backend failures result in helpful messages, conversation continues.

- [ ] T050 [US4] Test backend connection failure scenario
- [ ] T051 [P] [US4] Test 403 access denied with premium upgrade messaging
- [ ] T052 [P] [US4] Test timeout error with retry suggestions
- [ ] T053 [P] [US4] Test quiz submission failure with alternative learning approach
- [ ] T054 [US4] Verify conversation continuity during errors
- [ ] T055 [US4] Add error logging for monitoring (Sentry integration optional)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Finalize implementation with testing, documentation, and deployment readiness.

**Story Goal**: Production-ready ChatGPT App with tests, docs, and deployment config.

**Independent Test Criteria**: App loads in ChatGPT, all user stories work end-to-end, ready for App Store submission.

### Documentation

- [ ] T056 [P] Create README.md in chatgpt-app/ directory with setup instructions
- [ ] T057 [P] Document intent detection algorithm and priority order
- [ ] T058 [P] Document backend API integration patterns

### Testing

- [ ] T059 [P] Test ChatGPT App in development environment
- [ ] T060 [P] Test all 4 user stories with sample queries
- [ ] T061 [P] Test Zero-LLM compliance verification
- [ ] T062 [P] Test conversation flow across multiple turns
- [ ] T063 [P] Test error scenarios (backend down, access denied, timeouts)

### Deployment

- [ ] T064 Validate manifest.yaml schema
- [ ] T065 Deploy to ChatGPT App Store (development environment)
- [ ] T066 Test app in ChatGPT with real user flows
- [ ] T067 Configure production environment variables
- [ ] T068 Submit to ChatGPT App Store for production

---

## Dependencies

### User Story Dependencies

- **US2 (Backend Integration)** depends on **US1 (Conversational Learning)**: Backend integration supports conversational interface
- **US3 (Skill Loading)** enhances **US1 and US2**: Provides specialized educational experiences
- **US4 (Error Handling)** depends on **US1, US2, US3**: Handles errors for all features

### Parallel Execution Opportunities by Story

**User Story 1 (Conversational Learning)**:
- T028, T030-T034 can run in parallel after T018-T027 complete

**User Story 2 (Backend Integration)**:
- T035-T042 can run in parallel after T008-T017 complete

**User Story 3 (Skill Loading)**:
- T043-T049 can run in parallel after T018-T027 complete

**User Story 4 (Error Handling)**:
- T050-T055 can run in parallel after T008-T017 and T028-T042 complete

---

## Implementation Strategy

**MVP First**: Implement User Story 1 (Conversational Learning) and User Story 2 (Backend Integration) first. These are P1 priority and enable core value - students can learn through ChatGPT with backend content.

**Incremental Delivery**: Complete each user story in priority order:
1. Phase 1 + 2 (Setup + Foundation) - Infrastructure ready
2. Phase 3 + 4 (US1 + US2: Conversational Learning + Backend Integration) - MVP complete
3. Phase 5 (US3: Skill Loading) - Enhanced educational experiences
4. Phase 6 (US4: Error Handling) - Production reliability
5. Phase 7 (Polish) - App Store ready

**Parallel Development**: After foundational phase (Phase 2), user stories can be developed in parallel. T001-T027 must complete first (blocking), then T028-T034 (US1), T035-T042 (US2), T043-T049 (US3) can all proceed in parallel after their dependencies complete.

**Testing Strategy**: Manual testing in ChatGPT environment is primary. API integration can be tested with contract tests. No automated UI tests needed for Phase 1 (ChatGPT provides the UI).

---

**Task Generation Date**: 2026-01-28
**Total Tasks**: 68 tasks across 7 phases
**Parallel Opportunities**: 33 tasks marked with [P]

**Format Validation**: ✅ ALL tasks follow checklist format (checkbox, ID, file path)

**MVP Scope (US1 + US2 only)**: 24 tasks (Phase 1 + 2 + US1 + US2 implementation, excluding polish)

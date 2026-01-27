# Implementation Tasks: Zero-Backend-LLM Course Companion API

**Feature**: 1-zero-backend-api
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Generated**: 2026-01-28

---

## Task Summary

- **Total Tasks**: 47
- **MVP Scope** (User Story 1 only): 12 tasks (Setup + US1 implementation)
- **Parallel Opportunities**: 15 tasks marked with [P]

---

## Phase 1: Project Setup

**Goal**: Initialize FastAPI project with all dependencies, configuration, and development environment.

**Story Goal**: Establish development infrastructure.

**Independent Test Criteria**: Project runs locally with `uvicorn src.api.main:app`, API docs accessible at `/docs`, database connection successful.

- [ ] T001 Create backend project directory structure per plan.md
- [ ] T002 [P] Create requirements.txt with dependencies (FastAPI, SQLAlchemy, Pydantic, asyncpg, boto3, python-jose, uvicorn, pytest, httpx)
- [ ] T003 [P] Create pyproject.toml with project metadata
- [ ] T004 [P] Create .env.example with environment variable templates (DATABASE_URL, R2 credentials, JWT_SECRET, CORS_ORIGINS)
- [ ] T005 [P] Create Dockerfile for container image (Python 3.11 slim base)
- [ ] T006 Create fly.toml for Fly.io deployment configuration
- [ ] T007 [P] Create backend/src/__init__.py (empty module initializer)
- [ ] T008 [P] Create backend/src/core/config.py with environment variable loading and settings
- [ ] T009 [P] Create backend/src/core/database.py with PostgreSQL connection setup and session management
- [ ] T010 Create backend/src/core/security.py with JWT utilities and password hashing functions

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement shared infrastructure (models, schemas, middleware) that all user stories depend on.

**Story Goal**: Establish data models and API framework.

**Independent Test Criteria**: Database tables exist, can create models via SQLAlchemy, API framework initialized with middleware.

**Tests (Optional - not requested in spec)**: If TDD approach desired, add contract tests for foundational components here.

### Database Models

- [ ] T011 Create backend/src/models/__init__.py
- [ ] T012 [P] Create User model in backend/src/models/database.py with id, email, hashed_password, tier, created_at
- [ ] T013 [P] Create Chapter model in backend/src/models/database.py with id, title, content, order, difficulty, estimated_time, r2_content_key
- [ ] T014 [P] Create Quiz model in backend/src/models/database.py with id, chapter_id, title, difficulty, created_at
- [ ] T015 [P] Create Question model in backend/src/models/database.py with id, quiz_id, question_text, options (JSON), correct_answer, explanation
- [ ] T016 [P] Create Progress model in backend/src/models/database.py with id, user_id, completed_chapters (JSON), current_chapter_id, last_activity
- [ ] T017 [P] Create Streak model in backend/src/models/database.py with id, user_id, current_streak, longest_streak, last_checkin
- [ ] T018 [P] Create QuizAttempt model in backend/src/models/database.py with id, user_id, quiz_id, score, answers (JSON), completed_at
- [ ] T019 Add model relationships and foreign keys in backend/src/models/database.py

### Pydantic Schemas

- [ ] T020 Create backend/src/models/schemas.py
- [ ] T021 [P] Create Chapter schemas (Chapter, ChapterCreate, ChapterList)
- [ ] T022 [P] Create Quiz schemas (Quiz, Question, QuizSubmission, QuizResult)
- [ ] T023 [P] Create Progress schemas (Progress, ProgressUpdate)
- [ ] T024 [P] Create Streak schemas (Streak, StreakUpdate)
- [ ] T025 [P] Create Access control schemas (AccessCheck, AccessResponse, TierUpdate)
- [ ] T026 [P] Create User schemas (UserCreate, UserResponse, UserLogin)

### API Framework

- [ ] T027 Create backend/src/api/main.py with FastAPI app initialization
- [ ] T028 [P] Configure CORS middleware in backend/src/api/main.py
- [ ] T029 [P] Add JWT authentication middleware in backend/src/api/main.py
- [ ] T030 [P] Configure rate limiting in backend/src/api/main.py (60 req/min using SlowAPI)
- [ ] T031 [P] Add exception handlers for 404, 403, 500 errors in backend/src/api/main.py

---

## Phase 3: User Story 1 - Content Discovery and Delivery (Priority: P1)

**Goal**: Deliver course content through REST APIs with chapter navigation, search, and metadata.

**Story Goal**: Students can access, navigate, and search course material.

**Independent Test Criteria**: Student can retrieve chapter list, get specific chapter content, navigate to next/previous, and search for topics - all via API calls.

### Content Services

- [ ] T032 [US1] Create backend/src/storage/r2_client.py with boto3 S3 client for Cloudflare R2
- [ ] T033 [US1] Create backend/src/storage/cache.py with in-memory caching for frequently accessed content
- [ ] T034 [P] [US1] Create backend/src/services/content_service.py with business logic for content retrieval
- [ ] T035 [P] [US1] Implement get_chapter_content() in content_service.py to fetch from R2 or cache
- [ ] T036 [P] [US1] Implement search_content() in content_service.py for keyword and semantic search

### Content API Endpoints

- [ ] T037 [US1] Create backend/src/api/content.py with content router
- [ ] T038 [P] [US1] Implement GET /api/v1/chapters endpoint (list all chapters)
- [ ] T039 [P] [US1] Implement GET /api/v1/chapters/{id} endpoint (get chapter detail)
- [ ] T040 [P] [US1] Implement GET /api/v1/chapters/{id}/next endpoint (get next chapter)
- [ ] T041 [P] [US1] Implement GET /api/v1/chapters/{id}/previous endpoint (get previous chapter)
- [ ] T042 [US1] Implement GET /api/v1/search?q={query} endpoint (search content)

---

## Phase 4: User Story 2 - Knowledge Assessment via Quizzes (Priority: P2)

**Goal**: Enable quiz taking with rule-based grading and detailed feedback.

**Story Goal**: Students can take quizzes and receive immediate graded results with explanations.

**Independent Test Criteria**: Student can retrieve quiz, submit answers, receive score and detailed feedback - all rule-based, no LLM.

### Quiz Services

- [ ] T043 [US2] Create backend/src/services/quiz_service.py with business logic for quiz operations
- [ ] T044 [P] [US2] Implement get_quiz() in quiz_service.py to load quiz with questions
- [ ] T045 [P] [US2] Implement grade_quiz() in quiz_service.py with rule-based answer key matching
- [ ] T046 [P] [US2] Implement calculate_score() in quiz_service.py (percentage correct)

### Quiz API Endpoints

- [ ] T047 [US2] Create backend/src/api/quiz.py with quiz router
- [ ] T048 [P] [US2] Implement GET /api/v1/quizzes endpoint (list all quizzes)
- [ ] T049 [P] [US2] Implement GET /api/v1/quizzes/{id} endpoint (get quiz with questions)
- [ ] T050 [P] [US2] Implement POST /api/v1/quizzes/{id}/submit endpoint (submit answers, get results)
- [ ] T051 [US2] Implement GET /api/v1/quizzes/{id}/results endpoint (get attempt history)

---

## Phase 5: User Story 3 - Learning Progress Tracking (Priority: P3)

**Goal**: Track student progress, streaks, and engagement.

**Story Goal**: Students can view their progress, see streaks, and get motivated by achievements.

**Independent Test Criteria**: Student can complete chapter, update progress, view streak, and see percentage complete - all persists across sessions.

### Progress Services

- [ ] T052 [US3] Create backend/src/services/progress_service.py with business logic for progress tracking
- [ ] T053 [P] [US3] Implement update_progress() in progress_service.py to add completed chapters
- [ ] T054 [P] [US3] Implement calculate_progress_percentage() in progress_service.py
- [ ] T055 [P] [US3] Create backend/src/services/streak_service.py with streak calculation logic
- [ ] T056 [P] [US3] Implement record_checkin() in streak_service.py to update streaks
- [ ] T057 [P] [US3] Implement check_streak_continuity() in streak_service.py (same-day checkins)

### Progress API Endpoints

- [ ] T058 [US3] Create backend/src/api/progress.py with progress router
- [ ] T059 [P] [US3] Implement GET /api/v1/progress/{user_id} endpoint (get user progress)
- [ ] T060 [P] [US3] Implement PUT /api/v1/progress/{user_id} endpoint (update progress)
- [ ] T061 [P] [US3] Implement GET /api/v1/streaks/{user_id} endpoint (get streak info)
- [ ] T062 [US3] Implement POST /api/v1/streaks/{user_id}/checkin endpoint (record activity)

---

## Phase 6: User Story 4 - Freemium Access Control (Priority: P2)

**Goal**: Enforce freemium tiers - free users get 3 chapters, premium users get all content.

**Story Goal**: Access control gates premium content and enforces monetization.

**Independent Test Criteria**: Free user can access chapters 1-3, denied 4+ with 403. Premium user can access all chapters.

### Access Services

- [ ] T063 [US4] Create backend/src/services/access_service.py with business logic for tier enforcement
- [ ] T064 [P] [US4] Implement check_access() in access_service.py for chapter access rules
- [ ] T065 [P] [US4] Implement get_user_tier() in access_service.py
- [ ] T066 [P] [US4] Implement upgrade_user_tier() in access_service.py

### Access API Endpoints

- [ ] T067 [US4] Create backend/src/api/access.py with access router
- [ ] T068 [P] [US4] Implement POST /api/v1/access/check endpoint (check access rights)
- [ ] T069 [P] [US4] Implement GET /api/v1/user/{user_id}/tier endpoint (get user tier)
- [ ] T070 [US4] Implement POST /api/v1/access/upgrade endpoint (upgrade user tier)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Finalize implementation with testing, documentation, and deployment readiness.

**Story Goal**: Production-ready API with tests, docs, and deployment config.

**Independent Test Criteria**: All tests pass, API docs accessible, can deploy to Fly.io successfully.

### Documentation

- [ ] T071 [P] Create README.md in project root with setup instructions
- [ ] T072 [P] Create architecture diagram showing Zero-Backend-LLM flow (Student → ChatGPT → Backend → DB/R2)
- [ ] T073 [P] Create API documentation (auto-generated OpenAPI/Swagger)

### Testing

- [ ] T074 [P] Create tests/unit/ directory and test models (database models)
- [ ] T075 [P] Create tests/unit/ and test services (content, quiz, progress, access)
- [ ] T076 [P] Create tests/integration/ and test database operations
- [ ] T077 [P] Create tests/contract/ and validate API contracts against OpenAPI specs
- [ ] T078 [P] Create tests/integration/ and test R2 storage operations

### Deployment

- [ ] T079 [P] Test Docker build locally
- [ ] T080 Deploy to Fly.io (development environment)
- [ ] T081 Configure environment variables in Fly.io
- [ ] T082 Run database migrations on Neon PostgreSQL
- [ ] T083 Test API endpoints in deployed environment

---

## Dependencies

### User Story Dependencies

- **US2 (Quizzes)** depends on **US1 (Content)**: Quiz questions reference chapter content
- **US3 (Progress)** depends on **US1 (Content)** and **US2 (Quizzes)**: Progress tracks chapter completion and quiz attempts
- **US4 (Access Control)** is independent (can be implemented in parallel with US1-3)

### Parallel Execution Opportunities by Story

**User Story 1 (Content)**:
- T032, T033, T034, T035, T036 can run in parallel after T027-T031 complete

**User Story 2 (Quizzes)**:
- T043, T044, T045, T046 can run in parallel after T027-T031 complete
- T047-T051 can run in parallel after T043-T046 complete

**User Story 3 (Progress)**:
- T052-T057 can run in parallel after T027-T031 complete
- T058-T062 can run in parallel after T052-T057 complete

**User Story 4 (Access Control)**:
- T063-T066 can run in parallel after T027-T031 complete
- T067-T070 can run in parallel after T063-T066 complete

---

## Implementation Strategy

**MVP First**: Implement User Story 1 (Content Discovery and Delivery) first. This is P1 priority and enables core value - students can access and learn from course material.

**Incremental Delivery**: Complete each user story in priority order:
1. Phase 1 + 2 (Setup + Foundation)
2. Phase 3 (US1: Content APIs) - MVP complete
3. Phase 5 (US4: Access Control) - Enable monetization
4. Phase 4 (US2: Quizzes) - Add assessment
5. Phase 6 (US3: Progress) - Add engagement tracking
6. Phase 7 (Polish) - Production-ready

**Parallel Development**: After foundational phase (Phase 2), user stories can be developed in parallel by different team members. T001-T031 must complete first (blocking), then T032-T042 (US1), T043-T051 (US2), T052-T062 (US3), T063-T070 (US4) can all proceed in parallel.

**Testing Strategy**: Contract tests generated from OpenAPI specs validate API contracts automatically. Unit tests for services. Integration tests for database and storage. No E2E tests needed for Phase 1 (backend-only, E2E will be ChatGPT App or Web App).

---

**Task Generation Date**: 2026-01-28
**Total Tasks**: 83 tasks across 7 phases
**Parallel Opportunities**: 42 tasks marked with [P]

**Format Validation**: ✅ ALL tasks follow checklist format (checkbox, ID, file path)

**MVP Scope (US1 only)**: 12 tasks (Phase 1 + 2 + US1 implementation, excluding polish)

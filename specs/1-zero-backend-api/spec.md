# Feature Specification: Zero-Backend-LLM Course Companion API

**Feature Branch**: `1-zero-backend-api`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "Zero-Backend-LLM backend API for Course Companion FTE educational platform"

## User Scenarios & Testing

### User Story 1 - Content Discovery and Delivery (Priority: P1)

A student using the ChatGPT App or Web App wants to learn course material. They navigate through chapters, read content at their own pace, and get contextually relevant information served deterministically from the backend.

**Why this priority**: P1 - This is the core value proposition. Without content delivery, there is no educational product. This enables all other features.

**Independent Test**: Can be fully tested by accessing chapter content via API endpoints and receiving verbatim course material. Delivers immediate educational value to students.

**Acceptance Scenarios**:

1. **Given** a student requests chapter content, **When** they access GET /api/v1/chapters/{id}, **Then** they receive the full chapter content verbatim from storage with metadata (title, order, difficulty)
2. **Given** a student completes a chapter, **When** they access GET /api/v1/chapters/{id}/next, **Then** they receive the next sequential chapter or null if last chapter
3. **Given** a student searches for a topic, **When** they access GET /api/v1/search?q=neural+networks, **Then** they receive relevant chapter sections matching their query

---

### User Story 2 - Knowledge Assessment via Quizzes (Priority: P2)

A student wants to test their understanding of course material. They take quizzes composed of multiple-choice questions, receive immediate grading, and see detailed feedback on correct and incorrect answers.

**Why this priority**: P2 - Validates learning and reinforces concepts. Depends on P1 (content delivery) for quiz questions and answers.

**Independent Test**: Can be fully tested by taking a quiz, submitting answers, and receiving graded results with explanations. Delivers educational assessment value.

**Acceptance Scenarios**:

1. **Given** a student requests a quiz, **When** they access GET /api/v1/quizzes/{id}, **Then** they receive quiz questions, options, and metadata
2. **Given** a student submits quiz answers, **When** they POST to /api/v1/quizzes/{id}/submit with their answers, **Then** they receive a score (graded rule-based), correct/incorrect status per question, and explanations
3. **Given** a student answers incorrectly, **When** they view results, **Then** they see the correct answer and a detailed explanation (all pre-written, no LLM generation)

---

### User Story 3 - Learning Progress Tracking (Priority: P3)

A student wants to track their learning journey. They see which chapters they've completed, their current streak, overall progress percentage, and achievements earned.

**Why this priority**: P3 - Provides motivation and engagement. Depends on P1 and P2 for tracking activity.

**Independent Test**: Can be fully tested by completing chapters/quizzes and viewing progress updates. Delivers motivational value through gamification.

**Acceptance Scenarios**:

1. **Given** a student completes a chapter, **When** progress is updated via PUT /api/v1/progress/{user_id}, **Then** their completed chapters list updates and percentage recalculates
2. **Given** a student returns daily, **When** they check in via POST /api/v1/streaks/{user_id}/checkin, **Then** their current streak increments and displays
3. **Given** a student views progress, **When** they access GET /api/v1/progress/{user_id}, **Then** they see completion status, current chapter, streak info, and last activity date

---

### User Story 4 - Freemium Access Control (Priority: P2)

A free user tries to access premium content. The system enforces access rules - first 3 chapters are free, all content requires premium tier. Premium upgrade unlocks all chapters and features.

**Why this priority**: P2 - Enables monetization and validates business model. Critical for sustainability.

**Independent Test**: Can be fully tested by accessing content with different user tiers and verifying enforcement. Delivers business value.

**Acceptance Scenarios**:

1. **Given** a free user accesses chapters 1-3, **When** they request GET /api/v1/chapters/{id} for id in [1,2,3], **Then** they receive full content (access granted)
2. **Given** a free user attempts chapter 4+, **When** they request GET /api/v1/chapters/{id} for id >= 4, **Then** they receive 403 Forbidden with upgrade message (access denied)
3. **Given** a system checks access rights, **When** they call GET /api/v1/access/check?user_id={id}&resource=chapter-4, **Then** they receive access_granted: boolean, tier: "free"|"premium"|"pro", and upgrade_url if denied

---

### Edge Cases

- What happens when a student requests a non-existent chapter ID?
- What happens when quiz submission includes invalid answer keys?
- What happens when a user has no prior progress data (first-time user)?
- What happens when streak checkin happens multiple times in one day?
- What happens when search query returns no results?
- What happens when database connection fails during content retrieval?
- What happens when a premium user downgrades to free tier (already accessed premium content)?

## Requirements

### Functional Requirements

#### Content Delivery (FR-001 to FR-006)
- **FR-001**: System MUST serve course chapter content verbatim from storage without modification
- **FR-002**: System MUST support chapter sequencing (next/previous navigation)
- **FR-003**: System MUST support keyword and semantic search across course content
- **FR-004**: System MUST return chapter metadata (title, order, difficulty, estimated_time)
- **FR-005**: System MUST store content in Cloudflare R2 and retrieve via API
- **FR-006**: System MUST cache frequently accessed content to optimize performance

#### Quiz Management (FR-007 to FR-012)
- **FR-007**: System MUST serve quiz questions with multiple-choice options
- **FR-008**: System MUST grade quiz submissions using pre-defined answer keys (rule-based, no LLM)
- **FR-009**: System MUST provide detailed explanations for all answers (correct and incorrect)
- **FR-010**: System MUST calculate quiz scores as percentage of correct answers
- **FR-011**: System MUST store quiz attempt history (user_id, quiz_id, score, completed_at)
- **FR-012**: System MUST link quizzes to specific chapters for context

#### Progress Tracking (FR-013 to FR-019)
- **FR-013**: System MUST track completed chapters per user
- **FR-014**: System MUST track current chapter (where student left off)
- **FR-015**: System MUST track daily activity streaks (consecutive days of activity)
- **FR-016**: System MUST calculate overall progress percentage (completed_chapters / total_chapters)
- **FR-017**: System MUST record last activity timestamp per user
- **FR-018**: System MUST persist progress data across sessions (PostgreSQL database)
- **FR-019**: System MUST update last_activity timestamp on any learning action (chapter read, quiz taken)

#### Access Control (FR-020 to FR-025)
- **FR-020**: System MUST enforce freemium tiers (free, premium, pro)
- **FR-021**: System MUST grant free users access to first 3 chapters only
- **FR-022**: System MUST grant premium users access to all chapters and quizzes
- **FR-023**: System MUST validate access rights before serving premium content
- **FR-024**: System MUST return appropriate HTTP status codes (200 OK, 403 Forbidden) for access control
- **FR-025**: System MUST provide upgrade messaging when access is denied

#### Zero-LLM Enforcement (FR-026 to FR-028)
- **FR-026**: System MUST NOT contain any LLM API calls in Phase 1 backend code
- **FR-027**: System MUST NOT perform content generation using LLM (all content pre-generated)
- **FR-028**: System MUST NOT perform RAG summarization using LLM (serve content verbatim only)

### Key Entities

- **Chapter**: Represents a unit of course content with title, content, order, difficulty_level, estimated_time, quiz_id
- **Quiz**: Represents an assessment with title, chapter_id, questions, difficulty
- **Question**: Represents a quiz question with question_text, options (A,B,C,D), correct_answer, explanation
- **User**: Represents a student with id, email, tier (free/premium/pro), created_at
- **Progress**: Represents user's learning journey with user_id, completed_chapters (list), current_chapter_id, last_activity
- **Streak**: Represents user's engagement consistency with user_id, current_streak, longest_streak, last_checkin
- **QuizAttempt**: Represents a quiz attempt with id, user_id, quiz_id, score, answers (JSON), completed_at

## Success Criteria

### Measurable Outcomes

- **SC-001**: API response time (p95) < 200ms for content retrieval
- **SC-002**: System handles 100 concurrent users without performance degradation
- **SC-003**: Content delivery accuracy: 100% verbatim from storage (no modification)
- **SC-004**: Quiz grading accuracy: 100% correct based on answer keys
- **SC-005**: Monthly cost for 10K users: $16-41 total ($0.002-0.004 per user per month)
- **SC-006**: Uptime target: >99.5% for all API endpoints
- **SC-007**: Zero LLM API calls in Phase 1 backend (verified via code review + API audit)
- **SC-008**: Data persistence: All progress data survives server restarts (PostgreSQL)
- **SC-009**: Access control accuracy: 100% enforcement of freemium gates
- **SC-010**: Search relevancy: >90% of searches return relevant results (keyword/semantic)

### Quality Attributes

- **Maintainability**: Code follows Type Hints, Pydantic models, docstrings on all endpoints
- **Testability**: >80% test coverage for critical paths (unit, integration, contract tests)
- **Security**: JWT authentication, rate limiting (60 req/min), input validation, SQL injection prevention
- **Scalability**: Scales from 10 to 100,000 users with <2x infrastructure cost increase
- **Observability**: Structured logging, error tracking (Sentry), metrics dashboard

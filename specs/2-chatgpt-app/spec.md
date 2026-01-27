# Feature Specification: ChatGPT App for Course Companion FTE

**Feature Branch**: `2-chatgpt-app`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "ChatGPT App that provides conversational interface to Course Companion FTE, integrates with backend APIs, and loads educational skills dynamically"

## User Scenarios & Testing

### User Story 1 - Conversational Learning Experience (Priority: P1)

A student opens the Course Companion FTE ChatGPT App and starts learning. They ask questions, request explanations, take quizzes, and track progress through natural conversation. The app detects their intent, loads appropriate educational skills, and integrates seamlessly with backend APIs to serve content verbatim.

**Why this priority**: P1 - This is the primary interface for Phase 1. Enables 800M+ ChatGPT users to access the Course Companion. Core value delivery mechanism.

**Independent Test**: Can be fully tested by opening in ChatGPT, asking questions ("explain neural networks", "quiz me", "how am I doing?"), and verifying appropriate skill loading and backend API integration. Delivers complete educational experience through conversation.

**Acceptance Scenarios**:

1. **Given** a student asks "explain neural networks", **When** the app receives this message, **Then** it loads the concept-explainer skill, fetches chapter content from backend, and provides a personalized explanation at the learner's level
2. **Given** a student requests "quiz me", **When** the app detects quiz intent, **Then** it loads the quiz-master skill, retrieves quiz questions from backend, presents them conversationally, grades answers rule-based, and provides encouraging feedback
3. **Given** a student asks "how am I doing?", **When** the app detects progress intent, **Then** it loads the progress-motivator skill, fetches their progress data from backend, and celebrates their achievements
4. **Given** a student says "I'm stuck on this problem", **When** the app detects need for guidance, **Then** it loads the socratic-tutor skill and asks targeted questions to guide discovery

---

### User Story 2 - Backend API Integration (Priority: P1)

A student's learning journey requires data from the backend. The ChatGPT App fetches content, quizzes, and progress information through REST API calls, presenting this information conversationally while maintaining strict Zero-LLM compliance (no backend LLM calls).

**Why this priority**: P1 - Enables all content delivery and data persistence. Critical for functional ChatGPT App.

**Independent Test**: Can be fully tested by making API calls to retrieve chapters, submit quiz answers, and update progress. Verifies data flows correctly between ChatGPT and backend.

**Acceptance Scenarios**:

1. **Given** a student requests chapter content, **When** the app calls GET /api/v1/chapters/{id}, **Then** it receives the full chapter content verbatim and can present it to the student
2. **Given** a student submits quiz answers, **When** the app POSTs to /api/v1/quizzes/{id}/submit, **Then** it receives graded results with score and explanations
3. **Given** a student completes a chapter, **When** the app calls PUT /api/v1/progress/{user_id}, **Then** their progress updates and persists in the database
4. **Given** a free user tries to access premium content, **When** the app calls POST /api/v1/access/check, **Then** it receives access_denied and explains premium upgrade gracefully

---

### User Story 3 - Skill Loading and Intent Detection (Priority: P2)

The ChatGPT App dynamically loads educational skills (concept-explainer, quiz-master, socratic-tutor, progress-motivator) based on student requests. Each skill contains procedural knowledge for specific educational tasks, and the app routes student queries to the appropriate skill automatically.

**Why this priority**: P2 - Core differentiator. Enables the Course Companion FTE agent to deliver specialized educational experiences through modular, loadable skills.

**Independent Test**: Can be fully tested by sending various queries and verifying the correct skill loads with appropriate responses. Delivers adaptive, contextually appropriate educational interactions.

**Acceptance Scenarios**:

1. **Given** a student asks "explain X", **When** the app detects "explain" intent, **Then** it loads concept-explainer skill and provides explanation at learner's level
2. **Given** a student says "test me", **When** the app detects quiz intent, **Then** it loads quiz-master skill and presents quiz conversationally
3. **Given** a student says "help me think", **When** the app detects socratic intent, **Then** it loads socratic-tutor skill and asks guiding questions
4. **Given** a student asks about progress, **When** the app detects progress intent, **Then** it loads progress-motivator skill and celebrates achievements

---

### User Story 4 - Error Handling and Graceful Degradation (Priority: P3)

Backend APIs may be unavailable or return errors. The ChatGPT App must handle these gracefully, providing fallback educational value and helpful error messages without breaking the conversation.

**Why this priority**: P3 - Production reliability. Ensures good user experience even during backend issues. Depends on P1 and P2.

**Independent Test**: Can be tested by simulating backend failures (network errors, 403/404 responses) and verifying the app maintains conversation and provides helpful guidance.

**Acceptance Scenarios**:

1. **Given** backend connection fails, **When** a student requests content, **Then** the app explains the issue and offers to help with available knowledge or suggests retrying
2. **Given** a user is denied access to premium content, **When** access check returns 403, **Then** the app explains premium benefits gracefully and provides upgrade path
3. **Given** an API call times out, **When** the error occurs, **Then** the app apologizes for the delay and suggests trying again
4. **Given** quiz submission fails, **When** grading endpoint returns error, **Then** the app offers to help the student understand the material differently

---

### Edge Cases

- What happens when a student sends a message that's too long or contains unsupported content?
- What happens when multiple intents are detected in a single message?
- What happens when the app cannot determine the student's intent clearly?
- What happens when backend returns unexpected data format or schema mismatch?
- What happens when the student is brand new (no user_id yet)?
- What happens when skills fail to load or become unavailable?
- What happens when the student asks for help outside the course scope?

## Requirements

### Functional Requirements

#### Intent Detection and Routing (FR-001 to FR-005)
- **FR-001**: System MUST detect student intent from natural language messages (explain, quiz, stuck, progress)
- **FR-002**: System MUST load appropriate educational skill based on detected intent
- **FR-003**: System MUST support multiple intents in development mode for testing
- **FR-004**: System MUST route queries with no clear intent to general tutoring mode
- **FR-005**: System MUST maintain conversation context across multiple turns

#### Backend API Integration (FR-006 to FR-014)
- **FR-006**: System MUST call GET /api/v1/chapters/{id} to retrieve chapter content
- **FR-007**: System MUST call GET /api/v1/chapters/{id}/next for navigation
- **FR-008**: System MUST call GET /api/v1/search?q={query} to search content
- **FR-009**: System MUST call GET /api/v1/quizzes/{id} to get quiz questions
- **FR-010**: System MUST call POST /api/v1/quizzes/{id}/submit to submit answers
- **FR-011**: System MUST call GET /api/v1/progress/{user_id} to get student progress
- **FR-012**: System MUST call PUT /api/v1/progress/{user_id} to update progress
- **FR-013**: System MUST call GET /api/v1/streaks/{user_id} to get streak info
- **FR-014**: System MUST call POST /api/v1/streaks/{user_id}/checkin to record daily activity
- **FR-015**: System MUST call POST /api/v1/access/check to verify content access rights

#### Skill Loading and Execution (FR-016 to FR-020)
- **FR-016**: System MUST load concept-explainer skill when "explain", "what is", "how does" detected
- **FR-017**: System MUST load quiz-master skill when "quiz", "test me", "practice" detected
- **FR-018**: System MUST load socratic-tutor skill when "stuck", "help me think", "give me a hint" detected
- **FR-019**: System MUST load progress-motivator skill when "progress", "streak", "how am I doing" detected
- **FR-020**: System MUST make skill metadata (name, description) available for routing decisions

#### ChatGPT App Configuration (FR-021 to FR-026)
- **FR-021**: System MUST expose backend API endpoints as tools in ChatGPT App manifest
- **FR-022**: System MUST configure environment variables for backend URL and API keys
- **FR-023**: System MUST define freemium tiers in app pricing (Free: first 3 chapters, basic quizzes; Premium: all content, progress tracking)
- **FR-024**: System MUST set app metadata (name, description, version, author)
- **FR-025**: System MUST configure tools with proper endpoint URLs and authentication
- **FR-026**: System MUST define skill references in app manifest for course-companion-fte agent

#### Error Handling (FR-027 to FR-032)
- **FR-027**: System MUST handle backend connection errors gracefully with fallback responses
- **FR-028**: System MUST provide helpful error messages when content is not found (404)
- **FR-029**: System MUST explain access denied (403) with premium upgrade information
- **FR-030**: System MUST handle timeout errors with retry suggestions
- **FR-031**: System MUST maintain conversation continuity even during errors
- **FR-032**: System MUST log all errors for monitoring (Sentry integration)

#### Zero-LLM Compliance (FR-033 to FR-035)
- **FR-033**: ChatGPT App MUST NOT make LLM API calls on behalf of the backend
- **FR-034**: All AI intelligence MUST happen within ChatGPT using Course Companion FTE agent and skills
- **FR-035**: Backend MUST remain Zero-LLM (validated via code review)

### Key Entities

- **ChatGPT App Manifest**: YAML configuration defining app metadata, tools, pricing, and skill references
- **Intent Detection Result**: Detected intent type (explain, quiz, socratic, progress, general) with confidence score
- **Backend API Client**: TypeScript/Python client for making API calls to backend
- **Skill Loader**: Component that dynamically loads skills based on intent
- **Conversation Context**: Maintains conversation history and context for routing

## Success Criteria

### Measurable Outcomes

- **SC-001**: 95%+ of student queries correctly routed to appropriate skill
- **SC-002**: Backend API calls complete successfully in <500ms 95% of the time
- **SC-003**: Error messages are helpful and action-oriented in 100% of error cases
- **SC-004**: Free users understand premium benefits when access is denied
- **SC-005**: Conversation context maintained across 10+ turns without degradation
- **SC-006**: Skill loading happens within 2 seconds (including API calls)
- **SC-007**: Zero LLM API calls made by ChatGPT App (all AI in ChatGPT, backend is deterministic)
- **SC-008**: 90%+ student satisfaction with conversational learning experience

### Quality Attributes

- **Maintainability**: Clean separation between intent detection, skill loading, and API integration
- **Testability**: Intent detection can be tested with sample queries, API integration can be mocked
- **Extensibility**: Easy to add new skills and intents
- **Observability**: Logging for all skill loads, API calls, and errors
- **Performance**: Response generation happens within 2 seconds (including skill loading and API calls)

## Dependencies

### External Dependencies

- **Backend API** (1-zero-backend-api): All content, quizzes, progress, and access control data
- **Course Companion FTE Agent** (.claude/agents/course-companion-fte.md): Main educational agent
- **Educational Skills** (.claude/skills/): concept-explainer, quiz-master, socratic-trot, progress-motivator
- **OpenAI Apps SDK**: Framework for building ChatGPT Apps
- **Backend Hosting**: Fly.io or similar for backend API deployment

### Technical Constraints

- **Zero-LLM Backend**: Backend API contains no LLM calls (enforced by constitution)
- **ChatGPT Platform Limitations**: Must work within ChatGPT's conversation interface
- **API Rate Limits**: Backend enforces 60 req/minute, app must handle gracefully
- **Token Limits**: Skills and responses must fit within ChatGPT context window
- **No Persistent Storage in ChatGPT App**: All data persistence via backend APIs

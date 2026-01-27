# Implementation Plan: ChatGPT App for Course Companion FTE

**Branch**: `2-chatgpt-app` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for ChatGPT App with conversational interface

## Summary

Build a production-ready ChatGPT App for the Course Companion FTE educational platform that provides a conversational interface to students, dynamically loads educational skills (concept-explainer, quiz-master, socratic-tutor, progress-motivator), integrates with Zero-Backend-LLM backend APIs, and delivers personalized tutoring through natural language. The app MUST maintain strict separation - all AI intelligence happens in ChatGPT using the Course Companion FTE agent, backend remains completely deterministic (no LLM calls).

Primary requirement: Deliver conversational learning experience through ChatGPT App with intent detection, skill loading, backend API integration, and graceful error handling. Enables 800M+ ChatGPT users to access Course Companion FTE without leaving ChatGPT interface.

## Technical Context

**Language/Version**: TypeScript 5.0+ (or Python 3.11+ for Python-based app)
**Primary Dependencies**: OpenAI Apps SDK, Backend API client (axios/fetch), Course Companion FTE agent reference
**Storage**: None (stateless, backend handles persistence)
**Testing**: Manual testing in ChatGPT environment, API contract tests
**Target Platform**: ChatGPT App Platform (hosted by OpenAI)
**Project Type**: single (ChatGPT App configuration, no separate frontend/backend)
**Performance Goals**: Skill loading <2 seconds, API responses <500ms (p95), Conversation continuity across 10+ turns
**Constraints**: Must work within ChatGPT's conversation interface, Token limits for context window, No persistent storage in app
**Scale/Scope**: Unlimited concurrent users (scales with ChatGPT platform)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✓ **I. Zero-Backend-Backend-LLM First (NON-NEGOTIABLE)**: ChatGPT App does NOT make LLM API calls. All AI in ChatGPT. Verified via FR-033 to FR-035.
✓ **II. Spec-Driven Development**: This plan manufactured from human-written spec.md.
✓ **III. Educational Excellence First**: Conversational interface prioritizes learning value.
✓ **IV. Progressive Enhancement**: Phase 1 complete before Phase 2 (Hybrid).
✓ **V. Cost-Efficiency by Design**: No infra costs - ChatGPT platform hosts app.
✓ **VI. Agent Skills as Procedural Knowledge**: Skills load dynamically for educational tasks.

## Project Structure

### Documentation (this feature)

```text
specs/2-chatgpt-app/
├── plan.md              # This file
├── research.md          # Phase 0 output (technical decisions)
├── agent-context.md     # Phase 1 output (agent reference)
└── contracts/           # Phase 1 output (backend API client)
    └── api-client.yaml  # API specification for backend integration
```

### Source Code (repository root)

```text
# ChatGPT App configuration (no source code directory)
.claude/
├── agents/
│   └── course-companion-fte.md    # Main educational agent reference
└── skills/
    ├── concept-explainer/          # Educational skill
    ├── quiz-master/                  # Educational skill
    ├── socratic-tutor/               # Educational skill
    └── progress-motivator/           # Educational skill

chatgpt-app/
├── manifest.yaml                     # ChatGPT App definition
├── api/
│   ├── backend_client.py            # Backend API integration (TypeScript/Python)
│   └── types.ts                      # TypeScript interfaces (if using TS)
└── lib/
    ├── intent-detector.ts           # Intent detection logic
    └── skill-loader.ts              # Dynamic skill loading
```

**Structure Decision**: ChatGPT App configuration (manifest.yaml) + optional client code for backend integration. Most "code" is YAML configuration and skill markdown files. Course Companion FTE agent is referenced from `.claude/agents/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | Constitution check passed all gates | N/A |

## Phase 0: Research & Technical Decisions

### Research Tasks

1. **OpenAI Apps SDK Pattern**: Research ChatGPT App manifest structure, tool configuration, environment variables, and deployment process
2. **Intent Detection Strategy**: Research best practices for detecting user intent from natural language in conversational AI context
3. **Skill Loading Mechanism**: Research how to reference and load Agent Skills in ChatGPT App (skills field in manifest)
4. **Backend API Client Pattern**: Research best practices for making HTTP requests from ChatGPT App (fetch/axios, error handling, retry logic)
5. **Error Handling in ChatGPT**: Research how to provide helpful fallback responses when backend is unavailable

### Research Consolidation (research.md)

**Decision 1: Use OpenAI Apps SDK manifest.yaml format**
- **Rationale**: Official format, well-documented, supports tools, skills, environment variables, pricing
- **Alternatives Considered**: Programmatic app creation (less documented), Third-party platforms (not official)
- **Implementation**: Create manifest.yaml with tools, skills, env, and pricing sections

**Decision 2: Intent Detection via Keyword Matching (Phase 1)**
- **Rationale**: Simple, reliable, works for 95%+ of cases, easy to maintain
- **Alternatives Considered**: ML classifier (overkill for 4 intents), LLM-based intent detection (violates Zero-LLM for client-side), Regex patterns (too rigid)
- **Implementation**: Match keywords in student message: "explain", "what is" → concept-explainer; "quiz", "test me" → quiz-master; "stuck", "help" → socratic-tutor; "progress", "streak" → progress-motivator

**Decision 3: Skills Referenced in Manifest, Loaded by ChatGPT**
- **Rationale**: Skills field in manifest.yaml allows Course Companion FTE agent to load skills dynamically. ChatGPT platform handles loading.
- **Alternatives Considered**: Embed skill content in app prompt (exceeds token limits), Load skills via HTTP request (unnecessary complexity)
- **Implementation**: Add skills section to manifest.yaml referencing: concept-explainer, quiz-master, socratic-tutor, progress-motivator

**Decision 4: Backend API Client using fetch (JavaScript/TypeScript)**
- **Rationale**: Native browser API, no dependencies, works in ChatGPT Apps environment
- **Alternatives Considered**: axios (extra dependency), ky (less popular), Python requests (if using Python-based app)
- **Implementation**: Use fetch with async/await, proper error handling, retry logic for failed requests

**Decision 5: Fallback Responses for Backend Unavailability**
- **Rationale**: Provides value even when backend is down, maintains conversation continuity
- **Alternatives Considered**: Show error and block (poor UX), Retry indefinitely (confusing), End conversation (abrupt)
- **Implementation**: Store minimal content knowledge to help when backend unavailable, offer retry suggestions

## Phase 1: Design & Contracts

### Agent Context (agent-context.md)

**Course Companion FTE Agent Reference:**

The ChatGPT App manifests the Course Companion FTE agent which:
- Runs in ChatGPT when student opens the app
- Has 4 educational skills loaded (concept-explainer, guide, quiz-master, progress-motivator)
- Receives student messages and detects intent
- Delegates to appropriate skill based on intent
- Calls backend APIs to fetch content, quizzes, progress data
- Generates personalized responses using skill guidance

**Agent Flow:**
```
Student Message → Intent Detection → Skill Load → Backend API Call (if needed) → Response Generation
```

**Skill Loading:**

Skills are referenced in manifest.yaml:
```yaml
skills:
  - concept-explainer
  - quiz-master
  - socratic-tutor
  - progress-motivator
```

ChatGPT platform loads these skills when the app starts. Each skill is loaded from `.claude/skills/{skill-name}/SKILL.md`.

### Backend API Client (contracts/api-client.yaml)

**Backend API Specification:**

```yaml
openapi: 3.0.0
info:
  title: Course Companion FTE Backend API
  version: 1.0.0
  description: Zero-LLM backend API for ChatGPT App integration
servers:
  - url: ${BACKEND_URL}
    description: Backend API base URL (from environment variables)

paths:
  # Content APIs
  /chapters:
    get:
      summary: List all chapters
      operationId: listChapters
      tags: [Content]
      responses:
        200:
          description: List of chapters
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Chapter'

  /chapters/{chapter_id}:
    get:
      summary: Get chapter content
      operationId: getChapter
      tags: [Content]
      parameters:
        - name: chapter_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Chapter content
        404:
          description: Chapter not found

  # Quiz APIs
  /quizzes/{quiz_id}:
    get:
      summary: Get quiz
      operationId: getQuiz
      tags: [Quiz]
      parameters:
        - name: quiz_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Quiz with questions

  /quizzes/{quiz_id}/submit:
    post:
      summary: Submit quiz
      operationId: submitQuiz
      tags: [Quiz]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                answers:
                  type: object
                  additionalProperties:
                    type: string
      responses:
        200:
          description: Quiz results

  # Progress APIs
  /progress/{user_id}:
    get:
      summary: Get progress
      operationId: getProgress
      tags: [Progress]
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
      summary: Get streak
      operationId: getStreak
      tags: [Progress]
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Streak data

components:
  schemas:
    Chapter:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        content:
          type: string
        order:
          type: integer
        difficulty_level:
          type: string
          enum: [beginner, intermediate, advanced]
```

**Note**: Full API specification available in backend API contracts (specs/1-zero-backend-api/contracts/).

### ChatGPT App Manifest (manifest.yaml)

**File**: `chatgpt-app/manifest.yaml`

```yaml
name: Course Companion FTE
description: Your AI-powered tutor for mastering [Course Name]. Get personalized explanations, take quizzes, track progress, and learn 24/7.

version: 1.0.0
author: Your Team

# Tools - Backend API Integration
tools:
  - name: content_api
    description: Retrieve course content, chapters, and sections
    type: http
    endpoint: ${BACKEND_URL}/api/v1

  - name: quiz_api
    description: Get quizzes, submit answers, view results
    type: http
    endpoint: ${BACKEND_URL}/api/v1

  - name: progress_api
    description: Track learning progress and streaks
    type: http
    endpoint: ${BACKEND_URL}/api/v1

  - name: access_api
    description: Check and manage user access tiers
    type: http
    endpoint: ${BACKEND_URL}/api/v1

# Environment Variables
env:
  BACKEND_URL: "https://your-backend.com"

# Pricing and Access
pricing:
  type: freemium
  free_tier:
    - "First 3 chapters"
    - Basic quizzes"
    - Progress tracking"
  premium_tier:
    - "All chapters"
    - Advanced quizzes"
    - Detailed analytics"

# Skills Reference
skills:
  - concept-explainer
  - quiz-master
  - socratic-tutor
  - progress-motivator
```

### Intent Detection Logic (research.md)

**Intent Detection Algorithm:**

```python
def detect_intent(message: str) -> Intent:
    """
    Detect student intent from natural language message.
    Returns intent with confidence score.
    """
    message_lower = message.lower()

    # Check for explain intent
    if any(keyword in message_lower for keyword in ["explain", "what is", "how does", "help me understand"]):
        return Intent(type="explain", confidence=0.9)

    # Check for quiz intent
    if any(keyword in message_lower for keyword in ["quiz", "test me", "practice", "check my knowledge"]):
        return Intent(type="quiz", confidence=0.95)

    # Check for socratic intent
    if any(keyword in message_lower for keyword in ["stuck", "help me think", "give me a hint", "i'm lost"]):
        return Intent(type="socratic", confidence=0.85)

    # Check for progress intent
    if any(keyword in message_lower for keyword in ["progress", "streak", "how am i doing", "my stats"]):
        return Intent(type="progress", confidence=0.9)

    # Default to general tutoring
    return Intent(type="general", confidence=0.5)
```

**Priority Order (Conflict Resolution):**
1. Quiz intent (highest priority - explicit "test me")
2. Explain intent (high value - core learning)
3. Socratic intent (medium priority - targeted help)
4. Progress intent (medium priority - tracking)
5. General tutoring (fallback)

## Stop & Report

**Phase 0 Complete**: Research.md generated with all technical decisions resolved.

**Phase 1 Complete**: Agent context, API client spec, and manifest template created.

**Next Steps**:
1. Review plan.md and confirm technical approach
2. Run `/sp.tasks` to generate implementation tasks
3. Create manifest.yaml file with tools and skills configuration
4. Test ChatGPT App in development environment
5. Deploy to ChatGPT App Store for production

**Artifacts Created**:
- `specs/2-chatgpt-app/plan.md` (this file)
- `specs/2-chatgpt-app/spec.md` (feature specification)

**Ready for**: `/sp.tasks` command to generate task breakdown.

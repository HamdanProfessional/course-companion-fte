# Implementation Plan: Zero-Backend-LLM Course Companion API

**Branch**: `1-zero-backend-api` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for Zero-Backend-LLM backend API

## Summary

Build a production-ready FastAPI backend for the Course Companion FTE educational platform that serves course content, manages quizzes, tracks student progress, and enforces freemium access control. The backend MUST be completely deterministic (Zero-LLM) - all AI intelligence happens in ChatGPT using the Course Companion FTE agent. This ensures near-zero marginal cost per user ($0.002-0.004/month) and scalability to 100K+ users.

Primary requirement: Deliver 6 core features (content delivery, navigation, search, quizzes, progress tracking, access control) through FastAPI REST APIs with PostgreSQL database and Cloudflare R2 storage, while maintaining strict Zero-LLM compliance for hackathon Phase 1.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, asyncpg, boto3 (R2), python-jose [JWT], uvicorn, gunicorn
**Storage**: PostgreSQL (Neon serverless), Cloudflare R2 (course content)
**Testing**: pytest, pytest-asyncio, httpx
**Target Platform**: Linux server (Fly.io deployment)
**Project Type**: web application (backend API only)
**Performance Goals**: <200ms p95 latency for content retrieval, 100+ concurrent users, <100MB memory per worker
**Constraints**: Zero LLM API calls in Phase 1 (disqualification risk), <$41/month for 10K users
**Scale/Scope**: 10 to 100,000 users, ~10 chapters, ~50 quiz questions, 4 user tiers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✓ **I. Zero-Backend-LLM First (NON-NEGOTIABLE)**: Backend contains NO LLM API calls. All AI in ChatGPT. Verified via FR-026 to FR-028.
✓ **II. Spec-Driven Development**: This plan manufactured from human-written spec.md.
✓ **III. Educational Excellence First**: Features prioritize learning value (content delivery, assessment, progress tracking, gamification).
✓ **IV. Progressive Enhancement**: Phase 1 (Zero-LLM) complete before Phase 2 (Hybrid).
✓ **V. Cost-Efficiency by Design**: Serverless stack (Neon, R2, Fly.io) targets $0.002-0.004 per user/month.
✓ **VI. Agent Skills as Procedural Knowledge**: Backend serves content; ChatGPT uses skills for tutoring.

## Project Structure

### Documentation (this feature)

```text
specs/1-zero-backend-api/
├── plan.md              # This file
├── spec.md              # Feature specification (created)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (development setup)
└── contracts/           # Phase 1 output (OpenAPI specs)
    ├── content-api.yaml
    ├── quiz-api.yaml
    ├── progress-api.yaml
    └── access-api.yaml
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── content.py           # Content endpoints (chapters, search)
│   │   ├── quiz.py              # Quiz endpoints (get, submit, results)
│   │   ├── progress.py          # Progress endpoints (track, streaks)
│   │   └── access.py            # Access control endpoints (check, upgrade)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLAlchemy models (User, Chapter, Quiz, etc.)
│   │   └── schemas.py           # Pydantic schemas (request/response)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── content_service.py    # Business logic for content delivery
│   │   ├── quiz_service.py       # Business logic for quiz grading
│   │   ├── progress_service.py   # Business logic for streak calculation
│   │   └── access_service.py     # Business logic for tier enforcement
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── r2_client.py         # Cloudflare R2 integration
│   │   └── cache.py             # Caching layer (Redis optional)
│   └── core/
│       ├── __init__.py
│       ├── config.py            # Environment variables and settings
│       ├── security.py          # JWT auth, password hashing
│       └── database.py          # Database connection and session management
├── tests/
│   ├── contract/                # Contract tests (API spec validation)
│   │   ├── test_content_api.py
│   │   ├── test_quiz_api.py
│   │   └── test_progress_api.py
│   ├── integration/             # Integration tests
│   │   ├── test_database.py
│   │   └── test_r2_storage.py
│   └── unit/                    # Unit tests
│       ├── test_models.py
│       ├── test_services.py
│       └── test_schemas.py
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project metadata
├── Dockerfile                    # Container image
├── fly.toml                     # Fly.io deployment config
└── .env.example                 # Environment variables template

infrastructure/
├── terraform/                    # Infrastructure as code (optional)
│   ├── neon_database.tf
│   └── r2_bucket.tf
└── github_actions/              # CI/CD workflows
    └── deploy.yml
```

**Structure Decision**: Web application structure with separate backend/ directory (frontend will be added in Phase 3). Backend follows FastAPI best practices with layered architecture (API → Services → Models/Storage).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | Constitution check passed all gates | N/A |

## Phase 0: Research & Technical Decisions

### Research Tasks

1. **Cloudflare R2 Integration Pattern**: Research best practices for serving content from R2 via FastAPI (boto3 SDK, CDN integration, caching strategies)
2. **Neon PostgreSQL Serverless**: Validate connection pooling behavior, cold start performance, and autoscaling characteristics for 10K+ users
3. **Rate Limiting Strategies**: Evaluate SlowAPI vs. built-in solutions for API rate limiting (60 req/minute per endpoint)
4. **JWT Authentication**: FastAPI security best practices for token validation, refresh mechanisms, and middleware integration
5. **Semantic Search without LLM**: Research embedding-based search using pre-computed vectors (store embeddings, not generate them)

### Research Consolidation (research.md)

**Decision 1: Use boto3 SDK for Cloudflare R2**
- **Rationale**: Native Python SDK, S3-compatible API, community support, proven reliability
- **Alternatives Considered**: MinIO (self-hosted, more complexity), Azure Blob (costlier), AWS S3 (more expensive)
- **Implementation**: Use boto3 s3 client with R2 endpoint URL

**Decision 2: Use asyncpg for Async PostgreSQL**
- **Rationale**: Fast async PostgreSQL driver, compatible with SQLAlchemy 2.0, better performance than sync drivers
- **Alternatives Considered**: psycopg2 (sync only), databases (too abstract), asyncmy (less mature)
- **Implementation**: SQLAlchemy with asyncpg driver

**Decision 3: Use SlowAPI for Rate Limiting**
- **Rationale**: FastAPI-native integration, flexible in-memory or Redis backend, easy per-endpoint limits
- **Alternatives Considered**: Nginx rate limiting (infra-level, harder to configure), custom middleware (reinventing wheel)
- **Implementation**: @limiter.limit("60/minute") decorators on endpoints

**Decision 4: Pre-compute Embeddings for Search (Phase 1)**
- **Rationale**: Allows semantic search without LLM API calls. Store embeddings in R2, retrieve top-K matches
- **Alternatives Considered**: Keyword-only search (less accurate), Real-time embedding generation (violates Zero-LLM)
- **Implementation**: Pre-generate embeddings during content upload, use cosine similarity for ranking

**Decision 5: Use python-jose[cryptography] for JWT**
- **Rationale**: Secure JWT library, supports HS256 and RS256, compatible with FastAPI security
- **Alternatives Considered**: Authlib (more complex), PyJWT (less secure defaults)
- **Implementation**: HTTPBearer security scheme in FastAPI

## Phase 1: Design & Contracts

### Data Model (data-model.md)

**Core Entities:**

**User**
```python
id: UUID (PK)
email: Email (unique, indexed)
hashed_password: String
tier: Enum (free, premium, pro)
created_at: DateTime
last_login: DateTime
```

**Chapter**
```python
id: UUID (PK)
title: String
content: Text (markdown)
order: Integer (unique, indexed)
difficulty_level: Enum (beginner, intermediate, advanced)
estimated_time: Integer (minutes)
quiz_id: UUID (FK)
r2_content_key: String  # Key in Cloudflare R2
next_chapter_id: UUID (FK, nullable)
previous_chapter_id: UUID (FK, nullable)
```

**Quiz**
```python
id: UUID (PK)
chapter_id: UUID (FK)
title: String
difficulty: Enum (beginner, intermediate, advanced)
created_at: DateTime
```

**Question**
```python
id: UUID (PK)
quiz_id: UUID (FK)
question_text: String
options: JSON  // {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
correct_answer: Enum ("A", "B", "C", "D")
explanation: String
order: Integer
```

**Progress**
```python
id: UUID (PK)
user_id: UUID (FK)
completed_chapters: JSON  // Array of chapter IDs
current_chapter_id: UUID (FK)
last_activity: DateTime
```

**Streak**
```python
id: UUID (PK)
user_id: UUID (FK, unique)
current_streak: Integer
longest_streak: Integer
last_checkin: Date
```

**QuizAttempt**
```python
id: UUID (PK)
user_id: UUID (FK)
quiz_id: UUID (FK)
score: Integer
answers: JSON  // {question_id: answer, ...}
completed_at: DateTime
```

**Relationships:**
- User 1:N Progress (one user, one progress record)
- User 1:1 Streak (one user, one streak record)
- Chapter 1:1 Quiz (each chapter has one quiz)
- Chapter 1:N Question (each chapter has multiple questions)
- User N:QuizAttempt (one user, many quiz attempts)

### API Contracts (contracts/*.yaml)

**content-api.yaml:**
```yaml
openapi: 3.0.0
info:
  title: Content API
  version: 1.0.0
paths:
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
                items: { $ref: '#/components/schemas/Chapter' }
  /chapters/{chapter_id}:
    get:
      summary: Get chapter content
      operationId: getChapter
      tags: [Content]
      parameters:
        - name: chapter_id
          in: path
          required: true
          schema: { type: string }
      responses:
        200:
          description: Chapter content
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ChapterDetail' }
        404:
          description: Chapter not found
  /chapters/{chapter_id}/next:
    get:
      summary: Get next chapter
      operationId: getNextChapter
      tags: [Content]
      responses:
        200:
          description: Next chapter or null
  /chapters/{chapter_id}/previous:
    get:
      summary: Get previous chapter
      operationId: getPreviousChapter
      tags: [Content]
      responses:
        200:
          description: Previous chapter or null
  /search:
    get:
      summary: Search course content
      operationId: searchContent
      tags: [Content]
      parameters:
        - name: q
          in: query
          required: true
          schema: { type: string }
      responses:
        200:
          description: Search results
components:
  schemas:
    Chapter:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        order:
          type: integer
        difficulty_level:
          type: string
          enum: [beginner, intermediate, advanced]
        estimated_time:
          type: integer
    ChapterDetail:
      allOf:
        - $ref: '#/components/schemas/Chapter'
        - type: object
          properties:
            content:
              type: string
            quiz_id:
              type: string
```

**quiz-api.yaml:**
```yaml
paths:
  /quizzes:
    get:
      summary: List all quizzes
      operationId: listQuizzes
      tags: [Quiz]
      responses:
        200:
          description: List of quizzes
  /quizzes/{quiz_id}:
    get:
      summary: Get quiz details
      operationId: getQuiz
      tags: [Quiz]
      responses:
        200:
          description: Quiz with questions
  /quizzes/{quiz_id}/submit:
    post:
      summary: Submit quiz answers
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
        400:
          description: Invalid answers
  /quizzes/{quiz_id}/results:
    get:
      summary: Get quiz results
      operationId: getQuizResults
      tags: [Quiz]
      responses:
        200:
          description: Quiz attempt history
```

**progress-api.yaml:**
```yaml
paths:
  /progress/{user_id}:
    get:
      summary: Get user progress
      operationId: getProgress
      tags: [Progress]
      responses:
        200:
          description: User progress data
    put:
      summary: Update user progress
      operationId: updateProgress
      tags: [Progress]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                chapter_id:
                  type: string
      responses:
        200:
          description: Updated progress
  /streaks/{user_id}:
    get:
      summary: Get user streak
      operationId: getStreak
      tags: [Progress]
      responses:
        200:
          description: User streak data
  /streaks/{user_id}/checkin:
    post:
      summary: Record daily activity
      operationId: recordCheckin
      tags: [Progress]
      responses:
        200:
          description: Streak updated
```

**access-api.yaml:**
```yaml
paths:
  /access/check:
    post:
      summary: Check user access rights
      operationId: checkAccess
      tags: [Access]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
                resource:
                  type: string
      responses:
        200:
          description: Access check result
  /user/{user_id}/tier:
    get:
      summary: Get user tier
      operationId: getUserTier
      tags: [Access]
      responses:
        200:
          description: User tier information
  /access/upgrade:
    post:
      summary: Upgrade user tier
      operationId: upgradeTier
      tags: [Access]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
                new_tier:
                  type: string
                  enum: [premium, pro]
      responses:
        200:
          description: Tier upgraded
```

### Quickstart Guide (quickstart.md)

**Development Setup:**

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your values (DATABASE_URL, R2 credentials, JWT_SECRET)

# 4. Run database migrations (if using Alembic)
alembic upgrade head

# 5. Start development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Testing:**

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=src --cov-report=html
```

**API Documentation:**

```bash
# Access auto-generated OpenAPI docs
# Start server, then visit:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Agent Context Update

Run agent context update script to inform Claude Code about new technologies:
```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This updates `.claude/` with:
- FastAPI framework knowledge
- SQLAlchemy 2.0 async patterns
- Pydantic v2 validation
- Cloudflare R2 S3-compatible API
- Neon PostgreSQL serverless
- JWT authentication patterns

## Stop & Report

**Phase 0 Complete**: Research.md generated with all technical decisions resolved.

**Phase 1 Complete**: Data model, API contracts, and quickstart guide created.

**Next Steps**:
1. Review plan.md and confirm technical approach
2. Run `/sp.tasks` to generate implementation tasks
3. Begin Phase 1 implementation following tasks.md order

**Artifacts Created**:
- `specs/1-zero-backend-api/plan.md` (this file)
- `specs/1-zero-backend-api/spec.md` (feature specification)
- `specs/1-zero-backend-api/checklists/requirements.md` (validation checklist)

**Ready for**: `/sp.tasks` command to generate task breakdown.

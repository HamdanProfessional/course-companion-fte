# Course Companion FTE Backend

Zero-Backend-LLM Course Companion API for Panaversity Agent Factory Hackathon IV.

## Architecture

**Zero-Backend-LLM**: Backend serves content verbatim, NO LLM API calls. All AI intelligence happens in ChatGPT using the Course Companion FTE agent.

```
Student → ChatGPT App → Course Companion FTE Agent → Deterministic Backend
         (interface)     (All AI reasoning)    (Content APIs only)
```

## Features

1. **Content Delivery** - Serve course chapters from PostgreSQL/Cloudflare R2
2. **Navigation** - Next/previous chapter sequencing
3. **Search** - Keyword-based search (pre-computed, no real-time embeddings)
4. **Quizzes** - Rule-based grading with answer keys
5. **Progress Tracking** - Store completion, streaks, last activity
6. **Access Control** - Freemium enforcement (free = chapters 1-3, premium = all)

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL (Neon serverless) with asyncpg driver
- **ORM**: SQLAlchemy 2.0+ (async)
- **Storage**: Cloudflare R2 (S3-compatible)
- **Validation**: Pydantic v2
- **Security**: JWT (python-jose), bcrypt (passlib)
- **Rate Limiting**: SlowAPI
- **Testing**: pytest, pytest-asyncio, httpx

## Project Structure

```
backend/
├── src/
│   ├── api/                    # FastAPI endpoints
│   │   ├── main.py            # App entry point
│   │   ├── content.py         # Content endpoints
│   │   ├── quiz.py            # Quiz endpoints
│   │   ├── progress.py        # Progress endpoints
│   │   └── access.py          # Access control endpoints
│   ├── models/
│   │   ├── database.py        # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── content_service.py
│   │   ├── quiz_service.py
│   │   ├── progress_service.py
│   │   └── access_service.py
│   ├── storage/
│   │   ├── r2_client.py       # Cloudflare R2 client
│   │   └── cache.py           # In-memory cache
│   └── core/
│       ├── config.py          # Settings
│       ├── database.py        # DB connection
│       └── security.py        # JWT, password hashing
├── tests/                     # Tests
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── fly.toml
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (Neon recommended for serverless)
- Cloudflare R2 account (optional, for content storage)

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment variables
cp .env.example .env

# 4. Edit .env with your configuration
# DATABASE_URL - PostgreSQL connection string
# R2_* - Cloudflare R2 credentials
# JWT_SECRET - JWT signing secret

# 5. Initialize database (create tables)
python scripts/init_db.py

# 6. Run development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# Cloudflare R2 (optional, for content storage)
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=course-content
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com

# JWT Security
JWT_SECRET=change-this-secret-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Application
DEBUG=True
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Content
- `GET /api/v1/chapters` - List all chapters
- `GET /api/v1/chapters/{id}` - Get chapter content
- `GET /api/v1/chapters/{id}/next` - Get next chapter
- `GET /api/v1/chapters/{id}/previous` - Get previous chapter
- `GET /api/v1/search?q={query}` - Search content

#### Quiz
- `GET /api/v1/quizzes` - List all quizzes
- `GET /api/v1/quizzes/{id}` - Get quiz with questions
- `POST /api/v1/quizzes/{id}/submit` - Submit quiz answers (rule-based grading)
- `GET /api/v1/quizzes/{id}/results` - Get attempt history

#### Progress
- `GET /api/v1/progress/{user_id}` - Get user progress
- `PUT /api/v1/progress/{user_id}` - Update progress (mark chapter complete)
- `GET /api/v1/streaks/{user_id}` - Get streak info
- `POST /api/v1/streaks/{user_id}/checkin` - Record daily activity

#### Access Control
- `POST /api/v1/access/check` - Check access to resource
- `GET /api/v1/user/{user_id}/tier` - Get user tier
- `POST /api/v1/access/upgrade` - Upgrade user tier

## Zero-LLM Compliance

**Critical**: Phase 1 backend MUST have ZERO LLM API calls.

### What's Allowed
- ✅ Content serving from PostgreSQL/R2
- ✅ Database queries (SQLAlchemy)
- ✅ Rule-based quiz grading (answer key matching)
- ✅ Deterministic calculations (progress, streaks)
- ✅ HTTP requests to storage/database

### What's Forbidden
- ❌ OpenAI API calls (GPT-4, etc.)
- ❌ Anthropic API calls (Claude, etc.)
- ❌ LLM content summarization
- ❌ Prompt orchestration in backend
- ❌ Agent loops in backend

### Verification

```bash
# Audit for LLM API calls
cd backend/src
grep -ri "openai\|anthropic\|claude\|chatgpt\|gpt\|llm" --include="*.py" .

# Expected: NO RESULTS
```

## Deployment

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd backend
fly launch
fly deploy

# Set environment variables
fly secrets set DATABASE_URL="your-database-url"
fly secrets set JWT_SECRET="your-jwt-secret"
fly secrets set R2_ACCOUNT_ID="your-r2-account"
# ... etc
```

## Testing

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

## Cost Efficiency

**Target**: $0.002-0.004 per user per month

| Resource | Cost/Month | Users | Cost/User |
|----------|------------|-------|-----------|
| Fly.io VMs | $25-250 | 10K-100K | $0.0025 |
| Neon DB | $0-97 | 10K-100K | $0.0010 |
| R2 Storage | $1-15 | 10K-100K | $0.00015 |
| **Total** | | | **$0.0036** ✅ |

## License

MIT License - Hackathon IV Project

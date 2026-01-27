# Quickstart Guide: Zero-Backend-LLM Course Companion API

**Feature**: 1-zero-backend-api
**Prerequisites**: Python 3.11+, Git, Docker (optional)
**Estimated Setup Time**: 15 minutes

---

## Overview

This guide will get you up and running with the Course Companion FTE backend API locally. By the end, you'll have:
- FastAPI server running locally
- PostgreSQL database connected (Neon)
- Cloudflare R2 storage configured
- API documentation accessible at `/docs`

---

## 1. Prerequisites

### Required Software
- **Python 3.11+**: [Download here](https://www.python.org/downloads/)
- **Git**: [Download here](https://git-scm.com/downloads)
- **Docker Desktop** (optional, for containerization): [Download here](https://www.docker.com/products/docker-desktop/)

### Required Accounts
- **GitHub**: For code repository
- **Neon** (PostgreSQL): [Sign up free](https://neon.tech/)
- **Cloudflare** (R2 Storage): [Sign up free](https://www.cloudflare.com/products/zero-trust/r2/)

---

## 2. Repository Setup

```bash
# Clone the repository
git clone https://github.com/your-org/course-companion-fte.git
cd course-companion-fte

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Navigate to backend directory
cd backend
```

---

## 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
# Should output: 0.104.0 or higher
```

**requirements.txt contents**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
boto3==1.29.0
python-multipart==0.0.6
slowapi==0.1.9
```

---

## 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
```

**`.env` file**:
```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-region.aws.neon.tech/neondb?sslmode=require

# JWT Secret (generate random string)
JWT_SECRET=your-super-secret-jwt-key-change-this

# Cloudflare R2 Storage
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=course-content
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com

# CORS (allowed origins for frontend)
CORS_ORIGINS=["http://localhost:3000","https://your-app.vercel.app"]

# Application
APP_NAME=Course Companion FTE API
APP_VERSION=1.0.0
DEBUG=true
```

### Generate JWT Secret
```bash
# Generate secure random string
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 5. Database Setup (Neon)

### Option A: Use Neon Console (Recommended)

1. Go to [Neon Console](https://console.neon.tech/)
2. Create a new project
3. Copy the connection string
4. Paste in `.env` as `DATABASE_URL`

### Option B: Use Neon CLI

```bash
# Install Neon CLI
npm install -g neonctl

# Login to Neon
neonctl auth

# Create project
neonctl projects create --name course-companion-fte

# Get connection string
neonctl connection-string --project-id <your-project-id>
```

---

## 6. Cloudflare R2 Setup

### Create R2 Bucket

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create R2 bucket
wrangler r2 bucket create course-content

# Get API credentials
# Visit: https://dash.cloudflare.com/?to=/:account/r2/api/create-token
# Generate token with "Edit R2" permissions
```

**Add credentials to `.env`**:
```bash
R2_ACCOUNT_ID=<from-cloudflare-dashboard>
R2_ACCESS_KEY_ID=<from-api-token>
R2_SECRET_ACCESS_KEY=<from-api-token>
```

### Upload Sample Content

```bash
# Create sample chapter
echo "# Chapter 1: Introduction

This is the first chapter of the course." > chapter1.md

# Upload to R2 (using AWS CLI)
aws s3 cp chapter1.md s3://course-content/chapters/chapter1.md \
    --endpoint-url https://<account-id>.r2.cloudflarestorage.com
```

---

## 7. Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Run migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: chapters, users, quizzes, questions, progress, streaks, quiz_attempts
```

---

## 8. Run Development Server

```bash
# Start FastAPI server with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at: http://localhost:8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 9. Access API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Try the API

```bash
# List all chapters
curl http://localhost:8000/api/v1/chapters

# Get specific chapter
curl http://localhost:8000/api/v1/chapters/<chapter-id>

# Search content
curl http://localhost:8000/api/v1/search?q=neural+networks
```

---

## 10. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

---

## 11. Docker Setup (Optional)

### Build Docker Image

```bash
# Build image
docker build -t course-companion-api .

# Run container
docker run -d \
  --name course-api \
  -p 8000:8000 \
  --env-file .env \
  course-companion-api
```

### Docker Compose (Recommended)

```bash
# Start all services (API + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 12. Verify Setup

Run this health check:

```bash
# Health check endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","storage":"connected"}
```

---

## Troubleshooting

### Issue: Module not found
```bash
# Solution: Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Issue: Database connection failed
```bash
# Solution: Verify DATABASE_URL is correct
echo $DATABASE_URL

# Test connection directly
psql $DATABASE_URL
```

### Issue: R2 authentication failed
```bash
# Solution: Verify credentials are correct
# Check R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
```

### Issue: Port 8000 already in use
```bash
# Solution: Use different port
uvicorn src.api.main:app --reload --port 8001
```

---

## Next Steps

1. **Create sample data**: Use the provided seed script to populate the database
2. **Build frontend**: Set up Next.js web app (see `specs/3-web-app/quickstart.md`)
3. **Configure ChatGPT App**: Set up ChatGPT App manifest (see `specs/2-chatgpt-app/quickstart.md`)
4. **Deploy to production**: Follow deployment guide in `plan.md`

---

## Useful Commands

```bash
# Start development server
uvicorn src.api.main:app --reload

# Run tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/

# Database migration
alembic revision --autogenerate -m "description"
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Production Deployment

For production deployment to Fly.io, see the **Deployment** section in `plan.md`. Quick reference:

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
fly auth login

# Deploy
fly launch
fly deploy
```

---

**Need Help?**
- Check the `plan.md` for architecture decisions
- Review `data-model.md` for database schema
- See `contracts/` for API specifications
- Open an issue on GitHub

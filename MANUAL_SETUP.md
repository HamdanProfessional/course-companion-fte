# Manual Setup & Deployment Guide

**Course Companion FTE - Hackathon IV**
**Date**: 2026-01-28

---

## Overview

This document provides step-by-step instructions for all manual tasks required to deploy and run the Course Companion FTE application. The automated code implementation is complete, but you need to manually configure external services, API keys, and deployment platforms.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Backend Setup](#phase-1-backend-setup)
3. [Phase 2: ChatGPT App Submission](#phase-2-chatgpt-app-submission)
4. [Phase 3: Web App Deployment](#phase-3-web-app-deployment)
5. [Verification Steps](#verification-steps)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

Before starting, create accounts for these services:

- [ ] **GitHub** - For code hosting (if not already have)
- [ ] **Fly.io** - For backend deployment
- [ ] **Neon** - For PostgreSQL database
- [ ] **Cloudflare** - For R2 storage (optional, can use database for content)
- [ ] **OpenAI** - For ChatGPT App Store submission
- [ ] **Vercel** (optional) - For web app deployment

### Local Development Tools

Ensure you have installed:

- [ ] **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
- [ ] **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
- [ ] **Git** - Download from [git-scm.com](https://git-scm.com/)
- [ ] **VS Code** (recommended) - Download from [code.visualstudio.com](https://code.visualstudio.com/)

---

## Phase 1: Backend Setup

### 1.1 Database Setup (Neon PostgreSQL)

**Why**: Serverless PostgreSQL database for storing all application data.

#### Step 1: Create Neon Account

1. Go to https://neon.tech/
2. Click **Sign Up**
3. Choose one of:
   - Continue with GitHub (recommended)
   - Sign up with Email
   - Sign up with Google

#### Step 2: Create Project

1. After signup, you'll be redirected to the dashboard
2. Click **"Create a project"**
3. Enter project details:
   - **Name**: `course-companion-fte`
   - **Region**: Choose closest to your users (e.g., AWS us-east-1)
   - **PostgreSQL Version**: 16 (default)
4. Click **"Create Project"**

#### Step 3: Get Connection String

1. On the project dashboard, locate **Connection Details**
2. Copy the **Connection String** (format: `postgresql+asyncpg://...`)
3. **Save this** - you'll need it for the backend configuration

**Example Connection String**:
```
postgresql+asyncpg://course-companion-fte-owner:random-password@ep-cool-darkness-123456.us-east-1.aws.neon.tech/course-companion-fte?sslmode=require
```

#### Step 4: Create Tables (Automated via init_db.py)

The database tables will be created automatically when you run the initialization script.

---

### 1.2 Backend Deployment (Fly.io)

**Why**: Deploy the FastAPI backend to production.

#### Step 1: Install Fly CLI

**Windows**:
```powershell
# Run PowerShell as Administrator
iwr https://fly.io/install.ps1 | iex
```

**Linux/Mac**:
```bash
curl -L https://fly.io/install.sh | sh
```

#### Step 2: Login to Fly.io

```bash
fly auth login
```

A browser window will open. Log in or sign up for Fly.io.

#### Step 3: Create Backend Directory

```bash
# Navigate to project
cd C:\Users\User\Desktop\PIAIC_HACKATHON_1\Hackathon_4\backend

# Install dependencies
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file and add:
```bash
# Database Configuration (from Neon)
DATABASE_URL=postgresql+asyncpg://<your-neon-connection-string>

# JWT Secret (generate a secure random string)
JWT_SECRET=<generate-a-random-secret-key>

# CORS Origins (comma-separated)
CORS_ORIGINS=["http://localhost:3000","https://your-web-app.vercel.app"]

# Cloudflare R2 (optional - for content storage)
R2_ACCOUNT_ID=<your-cloudflare-account-id>
R2_ACCESS_KEY_ID=<your-r2-access-key-id>
R2_SECRET_ACCESS_KEY=<your-r2-secret-access-key>
R2_BUCKET_NAME=course-content
R2_ENDPOINT_URL=https://<your-account-id>.r2.cloudflarestorage.com

# Application Settings
APP_NAME=Course Companion FTE
APP_VERSION=1.0.0
DEBUG=False

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**To generate a secure JWT_SECRET**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 5: Initialize Database

```bash
python init_db.py
```

Expected output:
```
✓ Database initialized
✓ Created user: student@example.com
✓ Created chapters: 4
✓ Created quizzes with 11 questions
✓ Sample data created successfully!
```

#### Step 6: Test Locally

```bash
uvicorn src.api.main:app --reload
```

Backend will run on http://localhost:8000

Test it:
```bash
# Health check
curl http://localhost:8000/health

# List chapters
curl http://localhost:8000/api/v1/chapters

# Search content
curl "http://localhost:8000/api/v1/search?q=AI"
```

#### Step 7: Deploy to Fly.io

```bash
# From backend directory
fly launch

# Follow the prompts:
# - App name: course-companion-fte-backend (or your choice)
# - Region: choose closest to your users
# - Deploy with existing config? No (first time)

# Set environment variables
fly secrets set DATABASE_URL="postgresql+asyncpg://<your-neon-connection-string>"
fly secrets set JWT_SECRET="<your-jwt-secret>"
fly secrets set R2_ACCOUNT_ID="<your-r2-account-id>"
fly secrets set R2_ACCESS_KEY_ID="<your-r2-access-key>"
fly secrets set R2_SECRET_ACCESS_KEY="<your-r2-secret>"
fly secrets set R2_ENDPOINT_URL="https://<your-account-id>.r2.cloudflarestorage.com"
```

#### Step 8: Deploy Application

```bash
fly deploy
```

This will:
- Build Docker image
- Push to Fly.io registry
- Deploy to Fly.io infrastructure
- Health checks will automatically start

#### Step 9: Verify Deployment

```bash
# Get your app URL
fly apps list

# Test health endpoint
curl https://your-backend-app.fly.dev/health

# Should return:
# {"status":"healthy","version":"1.0.0","timestamp":"2026-01-28T..."}
```

**Save your backend URL**: `https://course-companion-fte-backend.fly.dev`

---

### 1.3 Cloudflare R2 Setup (Optional but Recommended)

**Why**: Store course content files (markdown chapters) in S3-compatible storage.

#### Step 1: Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with email
3. Verify email address

#### Step 2: Create R2 Bucket

1. In Cloudflare dashboard, navigate to **R2** (under **Storage**)
2. Click **Create Bucket**
3. Enter bucket details:
   - **Bucket Name**: `course-companion-fte-content`
4. Click **Create Bucket**

#### Step 3: Create API Token

1. Go to **R2 Overview**
2. Click **Manage R2 API Tokens**
3. Click **Create API Token**
4. Enter token details:
   - **Name**: `course-companion-fte-backend`
5. Permissions:
   - ✅ **Read** - Enable
   - ✅ **Write** - Enable
   - ✅ **List** - Enable
6. Click **Create API Token**

**IMPORTANT**: Save the credentials securely - you won't see them again!
```
Account ID: <your-account-id>
Access Key ID: <your-access-key-id>
Secret Access Key: <your-secret-access-key>
```

#### Step 4: Update Backend Secrets

```bash
fly secrets set R2_ACCOUNT_ID="<your-account-id>"
fly secrets set R2_ACCESS_KEY_ID="<your-access-key-id>"
fly secrets set R2_SECRET_ACCESS_KEY="<your-secret-access-key>"
fly secrets set R2_ENDPOINT_URL="https://<your-account-id>.r2.cloudflarestorage.com"
fly secrets set R2_BUCKET_NAME="course-companion-fte-content"
```

#### Step 5: Deploy with New Configuration

```bash
fly deploy
```

---

## Phase 2: ChatGPT App Submission

### 2.1 Prepare ChatGPT App

**Why**: Make the course companion available to 800M+ ChatGPT users.

#### Step 1: Update Backend URL in Manifest

Edit `chatgpt-app/manifest.yaml`:

```yaml
env:
  BACKEND_URL: "https://course-companion-fte-backend.fly.dev"  # Replace with your deployed backend URL
```

#### Step 2: Test Backend Integration

```bash
cd chatgpt-app
python -c "
from api.backend_client import get_backend_client
import asyncio

async def test():
    client = get_backend_client()
    chapters = await client.list_chapters()
    print(f'Connected! Found {len(chapters)} chapters')

asyncio.run(test())
"
```

Expected output:
```
Connected! Found 4 chapters
```

#### Step 3: Test Intent Detection

```bash
python lib/intent_detector.py
```

Expected output:
```
Message: 'Explain what MCP is'
  Intent: explain
  Skill: concept-explainer
  Confidence: 0.90
  Keywords: ['explain']
```

---

### 2.2 Submit to ChatGPT App Store

#### Step 1: Access ChatGPT App Store

1. Go to https://chat.openai.com/apps
2. Click **"Create New App"**
3. Sign in with your OpenAI account (or create one)

#### Step 2: Create App Configuration

You'll need to provide:

**App Information**:
- **Name**: `Course Companion FTE`
- **Description**: `Your AI-powered tutor for mastering AI Agent Development`
- **Instructions**: (See below)

**Instructions** (paste this):

```markdown
You are the Course Companion FTE, a digital full-time equivalent tutor.

Your role is to help students master AI Agent Development through personalized, conversational learning.

Core Principles:
1. Zero-LLM Backend: All AI intelligence happens here in ChatGPT. The backend serves content verbatim only.
2. Intent Detection: Detect what the student needs (explain, quiz, help, progress).
3. Skill Loading: Load appropriate educational skill for the task.
4. Backend Integration: Fetch content from backend when needed.

Intent Detection Priority:
1. Quiz - "quiz me", "test me", "practice" → quiz-master skill
2. Explain - "explain", "what is", "how does" → concept-explainer skill
3. Socratic - "stuck", "help me think", "give me a hint" → socratic-tutor skill
4. Progress - "progress", "streak", "how am I doing" → progress-motivator skill
5. General - Fallback to helpful tutoring

When a student asks a question:
1. Detect their intent
2. Load the appropriate skill
3. Fetch relevant content from backend if needed
4. Provide a helpful, encouraging response

Always maintain a supportive, encouraging tone. Celebrate achievements and provide constructive feedback.
```

#### Step 3: Configure Backend Tools

In the app configuration, add HTTP tools:

**Tool 1: Content API**
- Name: `content_api`
- Endpoint: `${BACKEND_URL}/api/v1`
- Operations:
  - GET `/chapters`
  - GET `/chapters/{chapter_id}`
  - GET `/chapters/{chapter_id}/next`
  - GET `/chapters/{chapter_id}/previous`
  - GET `/search`

**Tool 2: Quiz API**
- Name: `quiz_api`
- Endpoint: `${BACKEND_URL}/api/v1`
- Operations:
  - GET `/quizzes`
  - GET `/quizzes/{quiz_id}`
  - POST `/quizzes/{quiz_id}/submit`

**Tool 3: Progress API**
- Name: `progress_api`
- Endpoint: `${BACKEND_URL}/api/v1`
- Operations:
  - GET `/progress/{user_id}`
  - PUT `/progress/{user_id}`
  - GET `/streaks/{user_id}`
  - POST `/streaks/{user_id}/checkin`

**Tool 4: Access API**
- Name: `access_api`
- Endpoint: `${BACKEND_URL}/api/v1`
- Operations:
  - POST `/access/check`
  - GET `/user/{user_id}/tier`
  - POST `/access/upgrade`

#### Step 4: Configure Environment Variables

Add environment variable:
```
BACKEND_URL = https://course-companion-fte-backend.fly.dev
```

Replace with your actual backend URL.

#### Step 5: Configure Pricing

**Pricing Model**: Freemium

**Free Tier**:
- First 3 chapters of course content
- Basic quizzes for free chapters
- Progress tracking
- Streak gamification
- Concept explanations

**Premium Tier** ($9.99/month recommended):
- All 10 chapters of course content
- Advanced quizzes with detailed feedback
- Priority support
- Certificates of completion

#### Step 6: Test in Development Environment

1. ChatGPT provides a development environment for testing
2. Test with sample queries:
   - "Explain what MCP is"
   - "Quiz me on MCP"
   - "How am I doing?"
   - "I'm stuck on understanding agents"

#### Step 7: Submit for Review

1. Click **"Submit for Review"**
2. Fill in any remaining metadata
3. Wait for OpenAI review process

**Note**: Review typically takes 3-7 business days.

---

## Phase 3: Web App Deployment

### 3.1 Deploy Web Application (Vercel)

**Why**: Deploy the Next.js web application to production.

#### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

#### Step 2: Login to Vercel

```bash
vercel login
```

A browser window will open. Log in or sign up.

#### Step 3: Configure Environment

```bash
cd web-app

# Install dependencies
npm install
```

Create `.env.local`:
```bash
NEXT_PUBLIC_BACKEND_URL=https://course-companion-fte-backend.fly.dev
```

#### Step 4: Test Locally

```bash
npm run dev
```

Web app will run on http://localhost:3000

Test:
- Navigate to http://localhost:3000
- Should redirect to /dashboard
- Test chapters, quizzes, progress pages

#### Step 5: Deploy to Vercel

```bash
vercel
```

Follow the prompts:
- **Scope**: Root directory
- **Framework**: Next.js (auto-detected)
- **Root directory**: `./`
- **Project name**: `course-companion-fte-web` (or your choice)

#### Step 6: Set Environment Variables in Vercel Dashboard

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add:
   - `NEXT_PUBLIC_BACKEND_URL`: `https://course-companion-fte-backend.fly.dev`

#### Step 7: Verify Deployment

Visit your deployed web app (e.g., https://course-companion-fte-web.vercel.app)

Test:
- Dashboard loads with progress
- Can navigate chapters
- Quiz interface works
- Progress page displays correctly

---

### Alternative Deployment Platforms

#### Netlify

```bash
cd web-app
npm run build
npx netlify deploy
```

#### Railway

1. Connect your GitHub repository to Railway
2. Select `web-app` directory as root
3. Configure build command: `npm run build`
4. Configure start command: `npm start`
5. Add environment variable: `NEXT_PUBLIC_BACKEND_URL`
6. Deploy

#### Render

1. Connect your GitHub repository to Render
2. Select "Web Service"
3. Configure:
   - Build Command: `npm run build`
   - Start Command: `npm start`
   - Environment: `NEXT_PUBLIC_BACKEND_URL`
4. Deploy

---

## Verification Steps

### 4.1 Backend Verification

#### Test Health Endpoint

```bash
curl https://course-companion-fte-backend.fly.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-28T..."
}
```

#### Test Content API

```bash
curl https://course-companion-fte-backend.fly.dev/api/v1/chapters
```

Expected response:
```json
[
  {
    "id": "...",
    "title": "Introduction to AI Agents",
    "order": 1,
    "difficulty_level": "beginner",
    "estimated_time": 30
  }
  ]
}
```

#### Test Search API

```bash
curl "https://course-companion-fte-backend.fly.dev/api/v1/search?q=MCP"
```

#### Zero-LLM Compliance Test

```bash
cd backend
python tests/test_zero_llm_compliance.py
```

Expected output:
```
[OK] Zero-LLM compliance verified: No LLM imports found
[OK] Zero-LLM compliance verified: No LLM API calls found
[OK] ALL ZERO-LLM COMPLIANCE TESTS PASSED!
```

### 4.2 ChatGPT App Verification

#### Test Intent Detection

```bash
cd chatgpt-app
python lib/intent_detector.py
```

Expected: All tests pass with correct intent routing.

#### Test Backend Client

```bash
python -c "
from api.backend_client import get_backend_client
import asyncio

async def test():
    client = get_backend_client()

    # Test content API
    chapters = await client.list_chapters()
    assert len(chapters) > 0, 'No chapters found'
    print(f'✓ Chapters: {len(chapters)}')

    # Test quiz API
    quizzes = await client.list_quizzes()
    assert len(quizzes) > 0, 'No quizzes found'
    print(f'✓ Quizzes: {len(quizzes)}')

    print('✓ Backend client tests passed!')

asyncio.run(test())
"
```

### 4.3 Web App Verification

#### Test All Pages

1. **Dashboard**: `/dashboard` - Should show progress, streak, course outline
2. **Chapters**: `/chapters` - Should list all chapters with completion status
3. **Chapter Detail**: `/chapters/1` - Should show chapter content with navigation
4. **Progress**: `/progress` - Should show visual progress tracking
5. **Profile**: `/profile` - Should show account info and tier

#### Test Browser Console

Open browser DevTools (F12) and check for:
- No console errors
- API calls succeed (Network tab)
- Pages load within 3 seconds

---

## Post-Deployment Configuration

### 5.1 Domain Configuration (Optional)

#### Custom Domain for Backend (Fly.io)

```bash
# Add custom domain
fly certs add yourdomain.com
```

Update `BACKEND_URL` in ChatGPT App and Web App.

#### Custom Domain for Web App (Vercel)

1. Go to Vercel project dashboard
2. Navigate to **Domains**
3. Add custom domain
4. Configure DNS records as instructed

---

### 5.2 Monitoring Setup

#### Fly.io Monitoring

1. Go to your app dashboard on Fly.io
2. **Metrics** tab shows:
   - CPU usage
   - Memory usage
   - Response times
   - Request counts

#### Vercel Analytics

1. Go to your project dashboard on Vercel
2. **Analytics** tab shows:
   - Page views
   - Unique visitors
   - Top pages
   - Geographic distribution

---

## Security Checklist

### Before Going to Production

- [ ] **JWT_SECRET** is a strong random string (32+ characters)
- [ ] **DATABASE_URL** uses SSL (sslmode=require)
- [ ] **CORS_ORIGINS** only includes trusted domains
- [ ] **RATE_LIMIT_PER_MINUTE** is set (60 recommended)
- [ ] **DEBUG=False** in production
- [ ] All secrets set via `fly secrets set` (not hardcoded)
- [ ] HTTPS enabled for all endpoints
- [ ] API keys not committed to Git
- [ ] `.env` files in `.gitignore`

### API Key Security

**Never commit these files**:
- `.env`
- `.env.local`
- Any file containing actual API keys
- `backend/.env` (if created)
- `chatgpt-app/.env` (if created)
- `web-app/.env.local` (if created)

---

## Troubleshooting

### Issue 1: Backend Won't Start

**Symptom**: `uvicorn src.api.main:app` fails

**Solutions**:
1. Check Python version: `python --version` (should be 3.11+)
2. Activate virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Check `.env` file exists and is configured
5. Check database is accessible

### Issue 2: Database Connection Errors

**Symptom**: `connection refused` or `authentication failed`

**Solutions**:
1. Verify Neon database is running
2. Check connection string format: `postgresql+asyncpg://...`
3. Ensure SSL is enabled: `sslmode=require`
4. Test connection string in Neon dashboard
5. Check firewall allows outbound PostgreSQL connections

### Issue 3: Fly.io Deployment Fails

**Symptom**: `fly deploy` errors

**Solutions**:
1. Check Fly CLI is authenticated: `fly auth whoami`
2. Check app is created: `fly apps list`
3. Check logs: `fly logs`
4. Ensure all secrets are set: `fly secrets list`
5. Check Dockerfile is present and valid
6. Try `fly deploy --ha-only` for HA deployment

### Issue 4: ChatGPT App Test Fails

**Symptom**: Backend client connection timeout

**Solutions**:
1. Verify backend is deployed and accessible
2. Test backend URL in browser: `curl https://your-backend.fly.dev/health`
3. Check CORS configuration on backend
4. Verify NEXT_PUBLIC_BACKEND_URL is correct
5. Check Fly.io firewall allows connections

### Issue 5: Web App Shows Errors

**Symptom**: Pages don't load or console errors

**Solutions**:
1. Check browser console (F12) for errors
2. Check Network tab for failed API calls
3. Verify backend is accessible
4. Check environment variables in Vercel dashboard
5. Try clearing browser cache
6. Check build logs in Vercel dashboard

### Issue 6: Quiz Grading Not Working

**Symptom**: Quiz submission fails or scores incorrect

**Solutions**:
1. Check backend `/api/v1/quizzes/{id}/submit` endpoint works
2. Verify answer keys in database are correct
3. Check request body format matches schema
4. Review backend logs for errors
5. Test with curl:

```bash
curl -X POST https://your-backend.fly.dev/api/v1/quizzes/{quiz_id}/submit \
  -H "Content-Type: application/json" \
  -d '{"answers":{"question_id":"A"}}'
```

### Issue 7: Progress Not Saving

**Symptom**: Chapter completion not recorded

**Solutions**:
1. Check `/api/v1/progress/{user_id}` endpoint
2. Verify request format includes `chapter_id`
3. Check database `progress` table has rows
4. Review backend logs for errors
5. Test with curl:

```bash
curl -X PUT https://your-backend.fly.dev/api/v1/progress/00000000-0000-0000-0000-000000000001 \
  -H "Content-Type: application/json" \
  -d '{"chapter_id":"chapter-id"}'
```

---

## Cost Monitoring

### Track Your Monthly Costs

**Backend (Fly.io)**:
1. Go to https://fly.io/dashboard
2. Select your app
3. **Metrics** tab shows costs
4. **Budgets**: Set up budget alerts

**Database (Neon)**:
1. Go to https://console.neon.tech/
2. Select your project
3. **Usage** tab shows costs

**Storage (Cloudflare R2)**:
1. Go to https://dash.cloudflare.com/
2. Navigate to **R2** → **Your Bucket**
3. **Metrics** shows usage and costs

**Web App (Vercel)**:
1. Go to https://vercel.com/dashboard
2. Select your project
3. **Usage** tab shows bandwidth and functions
4. **Settings** → **Billing** shows costs

### Expected Monthly Costs (at 10K users)

| Service | Cost/Month | Notes |
|---------|-----------|-------|
| Fly.io (Backend) | $25-250 | Scales with usage |
| Neon (Database) | $0-97 | Serverless pricing |
| Cloudflare R2 | $1-15 | For content storage |
| Vercel (Web App) | $0-20 | Hobby plan |
| **Total** | **$26-382** | **$0.0036/user** ✅ |

---

## Access URLs Summary

After completing all steps, you'll have:

| Component | URL Format | Example |
|-----------|------------|--------|
| **Backend API** | `https://<app-name>.fly.dev` | `https://course-companion-fte-backend.fly.dev` |
| **ChatGPT App** | Via ChatGPT interface | Available in ChatGPT App Store |
| **Web Application** | `https://<app-name>.vercel.app` | `https://course-companion-fte-web.vercel.app` |

---

## Getting Help

### Documentation

- Backend: `backend/README.md`
- ChatGPT App: `chatgpt-app/README.md`
- Web App: `web-app/README.md`
- Implementation Status: `IMPLEMENTATION_STATUS.md`
- Main Project: `README.md`

### Troubleshooting Guides

Each phase README includes troubleshooting section:
- Backend API → `backend/README.md`#troubleshooting
- ChatGPT App → `chatgpt-app/README.md#troubleshooting
- Web App → `web-app/README.md#troubleshooting

### Community Resources

- **Fly.io Docs**: https://fly.io/docs/
- **Neon Docs**: https://neon.tech/docs
- **Cloudflare R2**: https://developers.cloudflare.com/r2/
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs

---

## Quick Reference

### Environment Variables Summary

**Backend (.env)**:
```bash
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=<random-32-char-string>
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=course-companion-fte-content
CORS_ORIGINS=["http://localhost:3000","https://your-web-app.vercel.app"]
```

**ChatGPT App (manifest.yaml env)**:
```yaml
env:
  BACKEND_URL: "https://your-backend.fly.dev"
```

**Web App (.env.local)**:
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend.fly.dev
```

### Common Commands

**Backend**:
```bash
cd backend
source venv/Scripts/activate  # Windows
# source venv/bin/activate  # Linux/Mac
uvicorn src.api.main:app --reload  # Dev server
python init_db.py                   # Initialize database
pytest                               # Run tests
```

**Fly.io**:
```bash
fly launch                           # Create app
fly deploy                           # Deploy
fly secrets set KEY=value           # Set secret
fly logs                              # View logs
fly apps list                        # List apps
```

**Web App**:
```bash
cd web-app
npm install                          # Install deps
npm run dev                          # Dev server
npm run build                        # Build for prod
npm start                            # Start production
vercel deploy                        # Deploy to Vercel
```

---

## Next Actions After Manual Setup

1. ✅ Complete all steps in this guide
2. ✅ Verify all deployments are working
3. ✅ Test end-to-end user flows
4. ✅ Monitor costs for first week
5. ✅ Collect user feedback
6. ✅ Iterate and improve features

---

## Completion Checklist

Use this checklist to track your manual setup progress:

### Phase 1: Backend Setup
- [ ] Neon PostgreSQL account created
- [ ] Project created in Neon
- [ ] Connection string obtained
- [ ] Fly.io CLI installed
- [ ] Logged into Fly.io
- [ ] Backend dependencies installed
- [ ] .env file configured
- [ ] Database initialized with `init_db.py`
- [ ] Backend runs locally
- [ ] Backend deployed to Fly.io
- [ ] Backend health check passes
- [ ] Zero-LLM compliance test passes

### Phase 2: ChatGPT App
- [ ] OpenAI account created
- [ ] Backend URL configured in manifest.yaml
- [ ] Backend client tested successfully
- [ ] Intent detector tested
- [ ] ChatGPT App Store account created
- [ ] App configuration completed
- [ ] App submitted for review
- [ ] Development environment tested

### Phase 3: Web Application
- [ ] Vercel CLI installed
- [ ] Logged into Vercel
- [ ] Node.js dependencies installed
- [ ] Environment variables configured
- [ ] Web app runs locally
- [ ] Web app deployed to Vercel
- [ ] Environment variables set in Vercel
- [ ] All pages tested
- [ ] Backend integration works

### Verification
- [ ] All health checks pass
- [ ] Zero-LLM compliance verified
- [ ] End-to-end user flows work
- [ ] Costs within budget ($0.0036/user/month)
- [ ] Documentation reviewed

---

**Last Updated**: 2026-01-28
**Version**: 1.0.0
**Project**: Course Companion FTE (Hackathon IV)

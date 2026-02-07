# Gamification Features Deployment Guide

## Overview

This guide covers deploying the 3 new gamification features to production:
1. **Random Tips** - Educational tips displayed on dashboard
2. **Global Leaderboard** - XP-based leaderboard with privacy controls
3. **Certificate Verification** - Public certificate verification for recruiters

**Commit:** `fa478d2` - feat: implement gamification features (tips, leaderboard, certificates)

---

## Pre-Deployment Checklist

- [x] All code committed to git
- [x] Database migration created (003_add_gamification_tables.py)
- [x] Tips data seeded (16 tips across 4 categories)
- [ ] Backend server access credentials
- [ ] Frontend deployment access (Vercel)
- [ ] Database backup created

---

## Step 1: Database Migration (Already Complete ✓)

The database migration has already been run locally:

```bash
cd backend
alembic upgrade head
```

**Status:** Migration `003_add_gamification` completed successfully

**Tables Created:**
- `tips` - Educational tips content
- `leaderboard_opt_in` - Student leaderboard preferences
- `certificates` - Course completion certificates

---

## Step 2: Backend Deployment

### 2.1 Push Code to Production

Push the committed changes to the remote repository:

```bash
git push origin master
```

### 2.2 SSH into Production Server

Connect to the production server:

```bash
ssh user@92.113.147.250
```

### 2.3 Pull Latest Code

Navigate to the backend directory and pull:

```bash
cd /path/to/backend
git pull origin master
```

### 2.4 Run Database Migration on Production

```bash
cd backend
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade 002_add_llm_costs_table -> 003_add_gamification
```

### 2.5 Seed Tips Data

```bash
python scripts/seed_tips.py
```

**Expected output:**
```
Starting tips seed...
Successfully added 16 tips to the database!

Tip breakdown:
  - study_habits: 4 tips
  - quiz_strategy: 4 tips
  - motivation: 4 tips
  - course_tips: 4 tips
```

### 2.6 Restart Backend Server

```bash
pm2 restart course-companion-backend
```

Or if using systemd:

```bash
sudo systemctl restart course-companion-backend
```

### 2.7 Verify Backend Endpoints

Test the new endpoints:

```bash
# Test tips endpoint
curl http://92.113.147.250:3505/api/v3/tutor/tips/random

# Test leaderboard endpoint
curl http://92.113.147.250:3505/api/v3/tutor/leaderboard

# Check API docs
open http://92.113.147.250:3505/docs
```

**Expected response from `/tips/random`:**
```json
{
  "id": "uuid",
  "content": "Tip content here...",
  "category": "study_habits",
  "difficulty_level": null,
  "active": true
}
```

---

## Step 3: Frontend Deployment

### 3.1 Build Frontend

```bash
cd web-app
npm run build
```

### 3.2 Deploy to Vercel

If using Vercel CLI:

```bash
vercel --prod
```

Or push to trigger automatic deployment (if configured).

### 3.3 Verify Frontend Pages

Visit the following URLs:

- **Dashboard:** http://92.113.147.250:3225/dashboard
  - Should show "Tip of the Day" card

- **Leaderboard:** http://92.113.147.250:3225/leaderboard
  - Should show top 10 students by XP

- **Profile:** http://92.113.147.250:3225/profile
  - Should have "Certificates" section

- **Certificate Verification:** http://92.113.147.250:3225/certificate/verify/CERT-XXXXXX
  - Should show certificate details (after generating one)

---

## Step 4: Post-Deployment Testing

### 4.1 Test Tips Feature

1. Visit dashboard
2. Verify tip card appears
3. Dismiss tip and refresh to see a new one
4. Test category filtering (if implemented)

### 4.2 Test Leaderboard Feature

1. Visit `/leaderboard`
2. Verify top 10 students displayed
3. Check XP calculation is correct
4. Test opt-in functionality:
   - User not on leaderboard: Show opt-in form
   - Submit display name
   - Verify appears on leaderboard
5. Test opt-out:
   - Toggle "Show on leaderboard" off
   - Verify name disappears

### 4.3 Test Certificate Feature

1. Visit `/profile`
2. Check if student meets requirements:
   - 100% course completion
   - Average quiz score >= 70%
3. Generate certificate (if eligible)
4. Click verification link
5. Verify certificate page shows correctly
6. Test with invalid certificate ID

### 4.4 Test Public Verification

Share a certificate verification URL with someone else:
- Should work without login
- Shows student name, grade, score, date
- Has verification badge

---

## Step 5: Monitor and Troubleshoot

### 5.1 Check Backend Logs

```bash
pm2 logs course-companion-backend
```

Look for errors related to:
- Database connection issues
- Missing tables
- Import errors

### 5.2 Common Issues

**Issue: Tips endpoint returns 404**
- Solution: Verify tips router is included in `__init__.py`
- Solution: Check database has tips in `tips` table

**Issue: Leaderboard shows empty array**
- Solution: Students need to opt-in first
- Solution: Verify XP calculation in leaderboard_service.py

**Issue: Certificate generation fails**
- Solution: Check student completion percentage
- Solution: Verify average quiz score is >= 70%
- Solution: Check certificate_id uniqueness constraint

**Issue: Database migration fails**
- Solution: Check current migration state: `alembic current`
- Solution: Stamp if needed: `alembic stamp 002_add_llm_costs_table`

---

## API Endpoints Reference

### Tips API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v3/tutor/tips/random` | Get random tip |
| GET | `/api/v3/tutor/tips` | Get all tips |
| GET | `/api/v3/tutor/tips/{id}` | Get tip by ID |
| POST | `/api/v3/tutor/tips` | Create tip (admin) |

### Leaderboard API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v3/tutor/leaderboard` | Get top 10 leaderboard |
| POST | `/api/v3/tutor/leaderboard/opt-in` | Opt into leaderboard |
| PATCH | `/api/v3/tutor/leaderboard/preferences` | Update preferences |
| GET | `/api/v3/tutor/leaderboard/status` | Get opt-in status |
| GET | `/api/v3/tutor/leaderboard/xp/{user_id}` | Get user XP |

### Certificates API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v3/tutor/certificates/generate` | Generate certificate |
| GET | `/api/v3/tutor/certificates` | Get user certificates |
| GET | `/api/v3/certificate/verify/{id}` | **Public** verification |

---

## Frontend Components

### New Components

- `TipOfTheDay.tsx` - Displays random educational tip
- `leaderboard/page.tsx` - Full leaderboard page
- `certificate/verify/[id]/page.tsx` - Public verification page

### Modified Components

- `dashboard/page.tsx` - Added TipOfTheDay component
- `profile/page.tsx` - Added certificates section
- `lib/api-v3.ts` - Added 20+ new API methods

---

## Database Schema

### Tips Table

```sql
CREATE TABLE tips (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(20),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    display_count INTEGER DEFAULT 0
);
```

### Leaderboard Opt-In Table

```sql
CREATE TABLE leaderboard_opt_in (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users(id),
    display_name VARCHAR(50) NOT NULL,
    show_on_leaderboard BOOLEAN DEFAULT TRUE,
    opted_in_at TIMESTAMP DEFAULT NOW()
);
```

### Certificates Table

```sql
CREATE TABLE certificates (
    id UUID PRIMARY KEY,
    certificate_id VARCHAR(16) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    student_name VARCHAR(255) NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    completion_date TIMESTAMP NOT NULL,
    final_grade VARCHAR(2) NOT NULL,
    final_score INTEGER NOT NULL,
    total_xp INTEGER NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verification_count INTEGER DEFAULT 0
);
```

---

## XP Calculation Formula

```python
total_xp = quiz_total + (completed_chapters * 10) + (current_streak * 5)
```

- **quiz_total**: Sum of all quiz scores
- **completed_chapters**: Number of completed chapters × 10
- **current_streak**: Current streak days × 5

---

## Certificate Requirements

To generate a certificate, students must:

1. ✅ Complete 100% of course content
2. ✅ Pass all quizzes (score >= 70%)
3. ✅ Average quiz score >= 70%

**Grading Scale:**
- A: 90% and above
- B: 80-89%
- C: 70-79%
- D: Below 70% (still passes but lowest grade)

---

## Privacy Features

### Leaderboard Privacy

- **Opt-in only**: Students must explicitly opt-in
- **Anonymous names**: Can use display name instead of real name
- **Easy opt-out**: Toggle to hide from leaderboard
- **No personal info**: Only shows XP, score, streak, chapters

### Certificate Privacy

- **Public verification**: Recruiters can verify without login
- **Minimal data**: Shows only name, grade, score, date
- **No sensitive info**: No email, phone, or address exposed

---

## Rollback Plan

If issues occur after deployment:

### 1. Backend Rollback

```bash
git checkout previous-commit
pm2 restart course-companion-backend
```

### 2. Database Rollback

```bash
alembic downgrade 002_add_llm_costs_table
```

### 3. Frontend Rollback

```bash
vercel rollback [deployment-url]
```

---

## Success Criteria

Deployment is successful when:

- ✅ All 19 API endpoints respond with 200 status
- ✅ Tips display on dashboard
- ✅ Leaderboard shows top 10 students
- ✅ Students can opt-in/opt-out of leaderboard
- ✅ Certificates can be generated (for eligible students)
- ✅ Certificate verification works publicly
- ✅ No errors in backend logs
- ✅ Frontend pages load without errors

---

## Performance Monitoring

After deployment, monitor:

- **API response times**: Should be <2 seconds for all endpoints
- **Database query performance**: Check for slow queries
- **Error rates**: Should be <1%
- **User engagement**: Track opt-in rates, certificate generations

---

## Next Steps

After successful deployment:

1. **Announce features** to students
2. **Monitor usage** for first week
3. **Gather feedback** on gamification features
4. **Iterate** based on user suggestions
5. **Consider additional features**:
   - Achievement badges
   - Daily streak bonuses
   - Monthly challenges
   - Leaderboard categories (by chapter, by quiz)

---

## Contact

For issues or questions:
- Backend Repository: [GitHub URL]
- Frontend Repository: [GitHub URL]
- Production Server: http://92.113.147.250:3505 (backend)
- Production Frontend: http://92.113.147.250:3225 (web-app)

---

**Deployment Date:** 2026-02-07
**Commit:** fa478d2
**Version:** 3.1.0 (Gamification Release)

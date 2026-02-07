# Gamification Features - Quick Reference Card

## 🎮 Features Overview

| Feature | Endpoint | Description |
|---------|----------|-------------|
| **Tip of the Day** | `/dashboard` | Random learning tips on dashboard |
| **Global Leaderboard** | `/leaderboard` | XP-based rankings with privacy controls |
| **Certificates** | `/profile` + `/certificate/verify/{id}` | Completion certificates with public verification |

## 📊 XP Formula

```
XP = quiz_score + (10 × chapters) + (5 × streak_days)
```

**Example:** 85% quiz avg + 5 chapters + 7 day streak = **170 XP**

## 🎯 Certificate Requirements

| Requirement | Threshold |
|-------------|-----------|
| Course Completion | 100% |
| Average Quiz Score | 70%+ |

**Certificate ID Format:** `CERT-XXXXXX` (6 random alphanumeric characters)

## 🚀 Quick Setup

```bash
cd backend
python scripts/setup_gamification.py
```

## 📡 API Endpoints

### Tips
```
GET  /api/v3/tutor/tips/random          ← Get random tip for dashboard
```

### Leaderboard
```
GET  /api/v3/tutor/leaderboard/         ← Get top 10 students
POST /api/v3/tutor/leaderboard/opt-in   ← Join leaderboard
POST /api/v3/tutor/leaderboard/opt-out  ← Leave leaderboard
```

### Certificates
```
POST /api/v3/tutor/certificates/generate              ← Generate certificate
GET  /api/v3/tutor/certificates/check-eligibility     ← Check eligibility
GET  /api/v3/certificate/verify/{cert_id}             ← Public verify (no auth)
```

## 🎨 Frontend Components

| Component | Location | Props |
|-----------|----------|-------|
| `TipOfTheDay` | `components/TipOfTheDay.tsx` | `className?` |
| Leaderboard Page | `app/leaderboard/page.tsx` | - |
| Certificate Verify | `app/certificate/verify/[id]/page.tsx` | - |

## 🔒 Privacy Controls

### Leaderboard Opt-In Settings
- ✅ `display_name` - Anonymous name (max 50 chars)
- ✅ `show_rank` - Show/hide rank
- ✅ `show_score` - Show/hide average score
- ✅ `show_streak` - Show/hide streak days

## 📝 Database Tables

```sql
tips              -- 16 pre-written tips
leaderboard_opt_in -- Privacy controls
certificates       -- Completion records
```

## ✅ Zero-Backend-LLM Check

| Feature | LLM Used? | Implementation |
|---------|-----------|----------------|
| Tips | ❌ No | Pre-written content |
| Leaderboard | ❌ No | Formula: quiz + 10*chapters + 5*streak |
| Certificates | ❌ No | Rule-based eligibility check |

## 🧪 Testing URLs

After setup:
1. **Tips:** Navigate to `http://localhost:3000/dashboard`
2. **Leaderboard:** Navigate to `http://localhost:3000/leaderboard`
3. **Certificates:** Navigate to `http://localhost:3000/profile`
4. **Public Verify:** `http://localhost:3000/certificate/verify/CERT-ABC123`

## 📚 Documentation Files

- `GAMIFICATION_IMPLEMENTATION_GUIDE.md` - Full setup guide
- `GAMIFICATION_IMPLEMENTATION_SUMMARY.md` - Technical summary
- `backend/scripts/setup_gamification.py` - Setup script
- `backend/scripts/seed_tips.py` - Tips seed script

---

**Status:** ✅ All features implemented and ready to use!

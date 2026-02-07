"""
Unified Tutor API Router - Phase 3

Consolidates all content, quiz, progress, LLM, and gamification features
into a single, coherent API structure.

Base Path: /api/v3/tutor

Sub-routers:
- /content: Chapter and course content
- /quizzes: Quiz taking and grading
- /progress: Learning progress tracking
- /ai: AI-powered features (adaptive, mentor, LLM grading)
- /access: Subscription and access control
- /teacher: Teacher dashboard
- /tips: Random learning tips
- /leaderboard: Global leaderboard with privacy controls
- /certificates: Course completion certificates
"""

from fastapi import APIRouter
from .content import router as content_router
from .quizzes import router as quizzes_router
from .progress import router as progress_router
from .ai import router as ai_router
from .access import router as access_router
from .teacher import router as teacher_router
from .tips import router as tips_router
from .leaderboard import router as leaderboard_router
from .certificates import router as certificates_router

# Create main tutor router
router = APIRouter()

# Include sub-routers
router.include_router(
    content_router,
    prefix="/content",
    tags=["Content"]
)

router.include_router(
    quizzes_router,
    prefix="/quizzes",
    tags=["Quizzes"]
)

router.include_router(
    progress_router,
    prefix="/progress",
    tags=["Progress"]
)

router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI Features (Phase 3)"]
)

router.include_router(
    access_router,
    prefix="/access",
    tags=["Access & Subscription"]
)

router.include_router(
    teacher_router,
    prefix="/teacher",
    tags=["Teacher Dashboard"]
)

router.include_router(
    tips_router,
    prefix="/tips",
    tags=["Tips"]
)

router.include_router(
    leaderboard_router,
    prefix="/leaderboard",
    tags=["Leaderboard"]
)

router.include_router(
    certificates_router,
    prefix="/certificates",
    tags=["Certificates"]
)


@router.get("/", tags=["Root"])
async def tutor_root():
    """Tutor API root - available endpoints."""
    return {
        "name": "Course Companion FTE - Unified Tutor API",
        "version": "3.0.0",
        "phase": "Phase 3 - Full LLM Integration + Gamification",
        "description": "Unified API combining content, quizzes, progress, AI, teacher features, and gamification",
        "endpoints": {
            "content": "/api/v3/tutor/content",
            "quizzes": "/api/v3/tutor/quizzes",
            "progress": "/api/v3/tutor/progress",
            "ai": "/api/v3/tutor/ai",
            "access": "/api/v3/tutor/access",
            "teacher": "/api/v3/tutor/teacher",
            "tips": "/api/v3/tutor/tips",
            "leaderboard": "/api/v3/tutor/leaderboard",
            "certificates": "/api/v3/tutor/certificates"
        },
        "features": {
            "content_delivery": "Chapters, navigation, search",
            "quiz_grading": "Rule-based + LLM grading",
            "progress_tracking": "Completion, streaks, achievements",
            "ai_features": "Adaptive learning, AI mentor, personalized content",
            "subscription": "Tier-based access control",
            "teacher_dashboard": "Analytics, student management, engagement metrics",
            "gamification": "Tips, global leaderboard, certificates"
        }
    }

"""
Teacher Dashboard API Router.
Provides analytics, student management, and engagement metrics for teachers.
All endpoints require teacher role authentication.
Zero-LLM compliance: All data from deterministic database queries.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger

from src.core.database import get_db
from src.api.dependencies import require_teacher
from src.services.teacher_service import TeacherService
from src.models.teacher_schemas import (
    TeacherStats,
    TeacherStudent,
    QuizStats,
    QuizPerformance,
    QuestionAnalysis,
    EngagementMetrics,
    AtRiskStudent,
    RecentActivity
)


# Initialize logger
logger = getLogger(__name__)

# Create router
router = APIRouter()


# =============================================================================
# Analytics Endpoints
# =============================================================================

@router.get("/analytics", response_model=TeacherStats, tags=["Teacher Dashboard"])
async def get_dashboard_analytics(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teacher dashboard statistics.

    Returns overall metrics including:
    - Total and active student counts
    - Average quiz scores
    - Completion rates
    - At-risk student counts

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        stats = await service.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dashboard analytics"
        )


@router.get("/students", response_model=List[TeacherStudent], tags=["Teacher Dashboard"])
async def get_all_students(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all students with progress information.

    Returns detailed student data including:
    - Progress percentages
    - Current streaks
    - Last activity timestamps
    - Recent quiz scores
    - Subscription tier

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        students = await service.get_all_students()
        return students
    except Exception as e:
        logger.error(f"Error fetching student list: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve student list"
        )


@router.get("/analytics/quiz-stats", response_model=QuizStats, tags=["Teacher Dashboard"])
async def get_quiz_statistics(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall quiz statistics.

    Returns aggregate quiz metrics:
    - Total quiz attempts
    - Average score across all attempts
    - Pass rate (score >= 70%)
    - Student completion rate

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        stats = await service.get_quiz_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching quiz statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve quiz statistics"
        )


@router.get("/analytics/quiz-performance", response_model=List[QuizPerformance], tags=["Teacher Dashboard"])
async def get_quiz_performance_data(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get per-quiz performance breakdown.

    Returns detailed statistics for each quiz:
    - Total attempts
    - Average, highest, and lowest scores
    - Pass rates
    - Quiz titles and IDs

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        performance = await service.get_quiz_performance()
        return performance
    except Exception as e:
        logger.error(f"Error fetching quiz performance: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve quiz performance data"
        )


@router.get("/analytics/question-analysis", response_model=List[QuestionAnalysis], tags=["Teacher Dashboard"])
async def get_question_analytics(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get question-level analytics for difficulty assessment.

    Returns per-question metrics:
    - Total attempts
    - Correct answer rates
    - Difficulty classification (easy/medium/hard)
    - Question text

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        analysis = await service.get_question_analysis()
        return analysis
    except Exception as e:
        logger.error(f"Error fetching question analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve question analysis"
        )


# =============================================================================
# Engagement Endpoints
# =============================================================================

@router.get("/engagement/metrics", response_model=EngagementMetrics, tags=["Teacher Dashboard"])
async def get_engagement_data(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get student engagement metrics.

    Returns engagement data including:
    - Active student count (last 7 days)
    - Average completion rate
    - Weekly activity breakdown (last 7 days)

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        metrics = await service.get_engagement_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching engagement metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve engagement metrics"
        )


@router.get("/engagement/at-risk", response_model=List[AtRiskStudent], tags=["Teacher Dashboard"])
async def get_at_risk_students_data(
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of at-risk students with identified risk factors.

    Returns students needing attention, with:
    - Risk level (high/medium/low)
    - Specific risk factors (activity, progress, quiz scores)
    - Last activity and progress data

    Sorted by risk priority (high first).

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        at_risk = await service.get_at_risk_students()
        return at_risk
    except Exception as e:
        logger.error(f"Error fetching at-risk students: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve at-risk student data"
        )


@router.get("/engagement/activity-feed", response_model=List[RecentActivity], tags=["Teacher Dashboard"])
async def get_activity_feed(
    limit: int = Query(50, ge=1, le=200, description="Number of recent activities to return"),
    current_user = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent student activity feed.

    Returns chronological activity log including:
    - Quiz completions with scores
    - Student logins
    - Chapter completions

    Sorted by most recent first.

    Requires teacher role authentication.
    """
    try:
        service = TeacherService(db)
        activities = await service.get_recent_activity(limit=limit)
        return activities
    except Exception as e:
        logger.error(f"Error fetching activity feed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve activity feed"
        )


# =============================================================================
# Root Endpoint
# =============================================================================

@router.get("/", tags=["Teacher Dashboard"])
async def teacher_root():
    """Teacher API root - available endpoints."""
    return {
        "name": "Teacher Dashboard API",
        "version": "1.0.0",
        "description": "Analytics and student management for teachers",
        "endpoints": {
            "analytics": "/api/v3/tutor/teacher/analytics",
            "students": "/api/v3/tutor/teacher/students",
            "quiz_stats": "/api/v3/tutor/teacher/analytics/quiz-stats",
            "quiz_performance": "/api/v3/tutor/teacher/analytics/quiz-performance",
            "question_analysis": "/api/v3/tutor/teacher/analytics/question-analysis",
            "engagement_metrics": "/api/v3/tutor/teacher/engagement/metrics",
            "at_risk_students": "/api/v3/tutor/teacher/engagement/at-risk",
            "activity_feed": "/api/v3/tutor/teacher/engagement/activity-feed"
        },
        "features": {
            "dashboard_analytics": "Overall statistics and metrics",
            "student_management": "Detailed student progress and performance",
            "quiz_analytics": "Quiz and question-level analysis",
            "engagement_tracking": "Activity monitoring and at-risk identification"
        },
        "authorization": "All endpoints require teacher role authentication"
    }

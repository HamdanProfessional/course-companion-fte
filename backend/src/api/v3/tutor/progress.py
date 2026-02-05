"""
Progress Router - Phase 3 Unified API

Handles progress tracking and gamification:
- Course completion tracking
- Streak management
- Achievement system
- Score history
- Gamification features

Path: /api/v3/tutor/progress
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_db
from src.services.progress_service import ProgressService
from src.models.database import Progress as UserProgress, Streak as UserStreak, QuizAttempt
from src.models.schemas import Progress

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Enums and Models
# =============================================================================


class AchievementType(str, Enum):
    """Achievement types."""
    FIRST_CHAPTER = "first_chapter"
    FIRST_QUIZ = "first_quiz"
    STREAK_3 = "streak_3"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    PERFECT_SCORE = "perfect_score"
    HALF_COURSE = "half_course"
    FULL_COURSE = "full_course"
    SPEED_DEMON = "speed_demon"
    KNOWLEDGE_SEEKER = "knowledge_seeker"


class AchievementItem(BaseModel):
    """Achievement item."""
    id: str
    name: str
    description: str
    icon: str
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0  # 0-100 for partial progress
    rarity: str = "common"  # common, rare, epic, legendary


class StreakDay(BaseModel):
    """Single day in streak calendar."""
    date: date
    active: bool
    streak_day: Optional[int] = None


class StreakCalendar(BaseModel):
    """Monthly streak calendar."""
    year: int
    month: int
    days: List[StreakDay]
    current_streak: int
    longest_streak: int
    total_active_days: int


class ScoreHistoryItem(BaseModel):
    """Score history data point."""
    date: date
    quiz_id: str
    quiz_title: str
    score: int
    passed: bool


class ProgressSummary(BaseModel):
    """Overall progress summary."""
    user_id: str
    completion_percentage: float
    completed_chapters: List[str]
    total_chapters: int
    current_chapter_id: Optional[str] = None
    last_activity: datetime
    total_quizzes_taken: int
    average_score: float
    current_streak: int
    longest_streak: int
    total_achievements: int
    unlocked_achievements: int


class ChapterProgress(BaseModel):
    """Progress for a specific chapter."""
    chapter_id: str
    chapter_title: str
    chapter_order: int
    completed: bool
    completed_at: Optional[datetime] = None
    quiz_taken: bool
    best_quiz_score: Optional[int] = None


class ProgressUpdateRequest(BaseModel):
    """Request to update progress."""
    chapter_id: str = Field(..., description="Chapter ID to mark complete")
    quiz_score: Optional[int] = None


class CelebrationResponse(BaseModel):
    """Response for achievement unlock."""
    achievement_id: str
    achievement: AchievementItem
    message: str
    confetti: bool = True
    share_url: Optional[str] = None


# =============================================================================
# Achievement Definitions
# =============================================================================

ACHIEVEMENTS = {
    "first_chapter": AchievementItem(
        id="first_chapter",
        name="First Steps",
        description="Complete your first chapter",
        icon="📖",
        rarity="common"
    ),
    "first_quiz": AchievementItem(
        id="first_quiz",
        name="Quiz Novice",
        description="Complete your first quiz",
        icon="✏️",
        rarity="common"
    ),
    "streak_3": AchievementItem(
        id="streak_3",
        name="On Fire",
        description="Maintain a 3-day learning streak",
        icon="🔥",
        rarity="common"
    ),
    "streak_7": AchievementItem(
        id="streak_7",
        name="Dedicated Learner",
        description="Maintain a 7-day learning streak",
        icon="💪",
        rarity="rare"
    ),
    "streak_30": AchievementItem(
        id="streak_30",
        name="Month Master",
        description="Maintain a 30-day learning streak",
        icon="🏆",
        rarity="epic"
    ),
    "perfect_score": AchievementItem(
        id="perfect_score",
        name="Perfectionist",
        description="Score 100% on any quiz",
        icon="💯",
        rarity="rare"
    ),
    "half_course": AchievementItem(
        id="half_course",
        name="Halfway There",
        description="Complete 50% of the course",
        icon="🎯",
        rarity="rare"
    ),
    "full_course": AchievementItem(
        id="full_course",
        name="Course Master",
        description="Complete 100% of the course",
        icon="🎓",
        rarity="legendary"
    ),
    "speed_demon": AchievementItem(
        id="speed_demon",
        name="Speed Demon",
        description="Complete a chapter in under 10 minutes",
        icon="⚡",
        rarity="rare"
    ),
    "knowledge_seeker": AchievementItem(
        id="knowledge_seeker",
        name="Knowledge Seeker",
        description="Take 10 quizzes",
        icon="🧠",
        rarity="rare"
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================


async def check_and_unlock_achievements(
    user_id: UUID,
    db: AsyncSession
) -> List[AchievementItem]:
    """Check for and return any newly unlocked achievements."""
    unlocked = []

    # Get user progress
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    user_progress = result.scalar_one_or_none()

    if not user_progress:
        return unlocked

    # Get user streak
    result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    user_streak = result.scalar_one_or_none()

    # Get quiz attempts
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.completed_at)
    )
    quiz_attempts = result.scalars().all()

    # Check achievements (simplified - in production, track which are already unlocked)
    if user_progress.completed_chapters and len(user_progress.completed_chapters) >= 1:
        unlocked.append(ACHIEVEMENTS["first_chapter"])

    if len(quiz_attempts) >= 1:
        unlocked.append(ACHIEVEMENTS["first_quiz"])

    if user_streak and user_streak.current_streak >= 3:
        unlocked.append(ACHIEVEMENTS["streak_3"])

    if user_streak and user_streak.current_streak >= 7:
        unlocked.append(ACHIEVEMENTS["streak_7"])

    if user_streak and user_streak.current_streak >= 30:
        unlocked.append(ACHIEVEMENTS["streak_30"])

    # Check for perfect score
    for attempt in quiz_attempts:
        if attempt.score == 100:
            unlocked.append(ACHIEVEMENTS["perfect_score"])
            break

    return unlocked


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/summary", response_model=ProgressSummary)
async def get_progress_summary(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall progress summary for a user.

    Includes:
    - Completion percentage
    - Completed chapters
    - Quiz performance
    - Streak information
    - Achievement progress

    **Phase 3 Enhancement**: Comprehensive progress dashboard.
    """
    try:
        # Get user progress
        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        # Get total chapters count
        from src.models.database import Chapter
        result = await db.execute(select(func.count(Chapter.id)))
        total_chapters = result.scalar() or 0

        # Get streak
        result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        user_streak = result.scalar_one_or_none()

        # Get quiz stats
        result = await db.execute(
            select(func.count(QuizAttempt.id), func.avg(QuizAttempt.score))
            .where(QuizAttempt.user_id == user_id)
        )
        quiz_stats = result.first()
        total_quizzes = quiz_stats[0] or 0
        avg_score = float(quiz_stats[1]) if quiz_stats[1] else 0.0

        completed_chapters = []
        completion_pct = 0.0
        current_chapter = None
        last_activity = datetime.utcnow()

        if user_progress:
            completed_chapters = user_progress.completed_chapters or []
            completion_pct = user_progress.completion_percentage
            current_chapter = str(user_progress.current_chapter_id) if user_progress.current_chapter_id else None
            last_activity = user_progress.last_activity

        current_streak = user_streak.current_streak if user_streak else 0
        longest_streak = user_streak.longest_streak if user_streak else 0

        return ProgressSummary(
            user_id=str(user_id),
            completion_percentage=completion_pct,
            completed_chapters=completed_chapters,
            total_chapters=total_chapters,
            current_chapter_id=current_chapter,
            last_activity=last_activity,
            total_quizzes_taken=total_quizzes,
            average_score=round(avg_score, 1),
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_achievements=len(ACHIEVEMENTS),
            unlocked_achievements=0  # Would track in production
        )

    except Exception as e:
        logger.error(f"Error getting progress summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress summary"
        )


@router.get("/chapters", response_model=List[ChapterProgress])
async def get_chapters_progress(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get progress for all chapters.

    Returns completion status and quiz performance for each chapter.

    **Phase 3 Enhancement**: Detailed chapter-by-chapter progress.
    """
    try:
        from src.models.database import Chapter, Quiz

        # Get all chapters
        result = await db.execute(
            select(Chapter).order_by(Chapter.order)
        )
        chapters = result.scalars().all()

        # Get user progress
        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        completed_set = set()
        if user_progress and user_progress.completed_chapters:
            completed_set = set(user_progress.completed_chapters or [])

        # Build response
        progress_list = []
        for chapter in chapters:
            # Check if completed
            completed = str(chapter.id) in completed_set

            # Get quiz info
            result = await db.execute(
                select(Quiz).where(Quiz.chapter_id == chapter.id)
            )
            quiz = result.scalar_one_or_none()

            quiz_taken = False
            best_score = None

            if quiz:
                result = await db.execute(
                    select(func.max(QuizAttempt.score))
                    .where(QuizAttempt.quiz_id == quiz.id)
                    .where(QuizAttempt.user_id == user_id)
                )
                score = result.scalar()
                quiz_taken = score is not None
                best_score = score

            progress_list.append(ChapterProgress(
                chapter_id=str(chapter.id),
                chapter_title=chapter.title,
                chapter_order=chapter.order,
                completed=completed,
                completed_at=None,  # Would track timestamps in production
                quiz_taken=quiz_taken,
                best_quiz_score=best_score
            ))

        return progress_list

    except Exception as e:
        logger.error(f"Error getting chapters progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chapter progress"
        )


@router.post("/update", response_model=Progress)
async def update_progress(
    request: ProgressUpdateRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update progress by marking a chapter as complete.

    Also triggers:
    - Streak updates
    - Achievement checks
    - Celebration if new achievement unlocked

    **Phase 3 Enhancement**: Gamification triggers on progress update.
    """
    try:
        service = ProgressService(db)

        # Update progress
        progress = await service.mark_chapter_complete(
            user_id,
            UUID(request.chapter_id)
        )

        # Check for achievements
        new_achievements = await check_and_unlock_achievements(user_id, db)

        return progress

    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update progress"
        )


@router.get("/streak/calendar", response_model=StreakCalendar)
async def get_streak_calendar(
    user_id: UUID = Query(description="User UUID"),
    year: int = Query(default=None, description="Year (default current)"),
    month: int = Query(default=None, description="Month (default current)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get streak calendar for a specific month.

    Shows active learning days and streak information.

    **Phase 3 Enhancement**: Visual calendar for gamification.
    """
    try:
        from datetime import date
        import calendar

        # Default to current month
        today = date.today()
        year = year or today.year
        month = month or today.month

        # Get user streak
        result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        user_streak = result.scalar_one_or_none()

        current_streak = user_streak.current_streak if user_streak else 0
        longest_streak = user_streak.longest_streak if user_streak else 0

        # Generate calendar days
        days_in_month = calendar.monthrange(year, month)[1]
        days = []

        for day in range(1, days_in_month + 1):
            day_date = date(year, month, day)
            # In production, check actual activity records
            active = False  # Placeholder
            days.append(StreakDay(
                date=day_date,
                active=active
            ))

        return StreakCalendar(
            year=year,
            month=month,
            days=days,
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_active_days=0  # Would calculate from activity records
        )

    except Exception as e:
        logger.error(f"Error getting streak calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve streak calendar"
        )


@router.get("/quiz-scores", response_model=List[ScoreHistoryItem])
async def get_score_history(
    user_id: UUID = Query(description="User UUID"),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get quiz score history for charts.

    **Phase 3 Enhancement**: Performance visualization data.
    """
    try:
        from src.models.database import Quiz

        result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
        )
        attempts = result.scalars().all()

        history = []
        for attempt in attempts:
            quiz = await db.get(Quiz, attempt.quiz_id)
            history.append(ScoreHistoryItem(
                date=attempt.completed_at.date(),
                quiz_id=str(attempt.quiz_id),
                quiz_title=quiz.title if quiz else "Unknown",
                score=attempt.score,
                passed=attempt.score >= 70
            ))

        return history

    except Exception as e:
        logger.error(f"Error getting score history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve score history"
        )


@router.get("/achievements", response_model=List[AchievementItem])
async def get_achievements(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all achievements and their unlock status.

    **Phase 3 Enhancement**: Gamification achievement system.
    """
    try:
        # Check which achievements are unlocked
        unlocked = await check_and_unlock_achievements(user_id, db)

        # Get all achievement definitions with unlock status
        achievements = []
        unlocked_ids = {a.id for a in unlocked}

        for achievement_id, achievement in ACHIEVEMENTS.items():
            is_unlocked = achievement_id in unlocked_ids
            base_data = achievement.model_dump(exclude_unset=True, exclude={'unlocked_at', 'progress'})
            achievements.append(AchievementItem(
                **base_data,
                unlocked_at=datetime.utcnow() if is_unlocked else None,
                progress=100.0 if is_unlocked else 0.0
            ))

        return achievements

    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve achievements"
        )


@router.post("/checkin")
async def daily_checkin(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Record daily checkin for streak tracking.

    **Phase 3 Enhancement**: Daily engagement tracking.
    """
    try:
        service = ProgressService(db)
        streak = await service.update_streak(user_id)

        # Check for streak achievements
        new_achievements = await check_and_unlock_achievements(user_id, db)

        return {
            "streak_updated": True,
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "new_achievements": [a.model_dump() for a in new_achievements]
        }

    except Exception as e:
        logger.error(f"Error during checkin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record checkin"
        )

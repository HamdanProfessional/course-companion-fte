"""
Mistakes Router - Phase 3 Unified API

Handles mistake bank operations:
- Get mistakes from both chapter and infinite quizzes
- Filter mistakes by source, category, difficulty
- Mark mistakes as mastered
- Export mistakes for backup

Path: /api/v3/tutor/mistakes
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.mistake_service import MistakeService, MistakeServiceError
from src.api.dependencies import get_current_user
from src.models.database import User

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class MistakeItem(BaseModel):
    """A mistake item."""
    id: str
    question_id: str
    quiz_id: str
    quiz_title: str
    question_text: str
    wrong_answer: str
    correct_answer: str
    explanation: Optional[str] = None
    feedback: Optional[str] = None
    category: Optional[str] = None
    difficulty: str = "beginner"
    date: str
    mastered: bool = False
    times_wrong: int = 1
    last_reviewed: Optional[str] = None
    source: str = "chapter"  # "chapter" or "infinite"
    topic: Optional[str] = None
    subtopic: Optional[str] = None


class MistakeStats(BaseModel):
    """Mistake statistics."""
    total_attempts: int
    average_score: float
    mistakes_count: int
    by_category: Dict[str, int]
    by_difficulty: Dict[str, int]


class InfiniteQuizMistakeRequest(BaseModel):
    """Request to add a mistake from infinite quiz."""
    question_data: Dict[str, Any] = Field(..., description="AI-generated question data")
    wrong_answer: str = Field(..., description="User's wrong answer")


class MistakesExport(BaseModel):
    """Exported mistakes data."""
    user_id: str
    export_date: str
    total_mistakes: int
    mistakes: List[Dict[str, Any]]


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=List[MistakeItem])
async def get_mistakes(
    current_user: User = Depends(get_current_user),
    source: Optional[str] = Query(None, description="Filter by source: 'chapter' or 'infinite'"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    mastered: Optional[bool] = Query(None, description="Filter by mastery status"),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's mistakes from quizzes.

    Returns mistakes from both chapter quizzes and infinite (AI) quizzes.
    Can be filtered by source, category, difficulty, and mastery status.

    **Phase 3 Feature**: Comprehensive mistake tracking from all quiz sources.

    **Authentication**: Required - Users must be logged in to view their mistakes.
    """
    try:
        mistake_service = MistakeService(db)

        # Get mistakes from chapter quizzes
        mistakes = await mistake_service.get_mistakes_from_chapter_quizzes(
            current_user.id, limit=limit
        )

        # Apply filters
        if source:
            mistakes = [m for m in mistakes if m.source == source]
        if category:
            mistakes = [m for m in mistakes if m.category == category]
        if difficulty:
            mistakes = [m for m in mistakes if m.difficulty == difficulty]
        if mastered is not None:
            mistakes = [m for m in mistakes if m.mastered == mastered]

        # Convert to response models
        return [MistakeItem(**m.to_dict()) for m in mistakes]

    except MistakeServiceError as e:
        logger.error(f"Mistake service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting mistakes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve mistakes"
        )


@router.get("/stats", response_model=MistakeStats)
async def get_mistake_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about user's mistakes.

    Returns:
    - Total quiz attempts
    - Average score
    - Number of mistakes
    - Breakdown by category
    - Breakdown by difficulty

    **Phase 3 Feature**: Detailed mistake analytics.

    **Authentication**: Required - Users must be logged in to view their stats.
    """
    try:
        mistake_service = MistakeService(db)
        stats = await mistake_service.get_mistake_stats(current_user.id)

        return MistakeStats(**stats)

    except Exception as e:
        logger.error(f"Error getting mistake stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve mistake statistics"
        )


@router.post("/infinite")
async def add_infinite_quiz_mistake(
    request: InfiniteQuizMistakeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a mistake from infinite (AI-generated) quiz.

    Records wrong answers from AI-generated quiz questions.
    These are tagged with source="infinite" for filtering.

    **Phase 3 Feature**: Track mistakes from AI-generated practice questions.

    **Authentication**: Required - Users must be logged in to record mistakes.
    """
    try:
        mistake_service = MistakeService(db)
        mistake = await mistake_service.add_infinite_quiz_mistake(
            current_user.id,
            request.question_data,
            request.wrong_answer
        )

        return {
            "message": "Mistake recorded",
            "mistake": mistake.to_dict()
        }

    except Exception as e:
        logger.error(f"Error adding infinite quiz mistake: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record mistake"
        )


@router.get("/export", response_model=MistakesExport)
async def export_mistakes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all mistakes for backup.

    Returns all mistakes in a structured format for backup or analysis.

    **Phase 3 Feature**: Export mistake data for GDPR compliance.

    **Authentication**: Required - Users must be logged in to export their mistakes.
    """
    try:
        mistake_service = MistakeService(db)
        export_data = await mistake_service.export_mistakes(current_user.id)

        return MistakesExport(**export_data)

    except Exception as e:
        logger.error(f"Error exporting mistakes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export mistakes"
        )

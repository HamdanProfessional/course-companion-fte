"""
Progress API endpoints.
Zero-LLM compliance: Deterministic tracking, no AI services.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.progress_service import ProgressService, StreakService
from src.models.schemas import (
    Progress as ProgressSchema,
    ProgressUpdate,
    Streak as StreakSchema,
)

router = APIRouter()


@router.get("/progress/{user_id}", response_model=ProgressSchema, tags=["Progress"])
async def get_progress(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's learning progress.
    Zero-LLM: Returns verbatim progress data with calculated completion percentage.
    """
    progress_service = ProgressService(db)
    progress = await progress_service.get_user_progress(user_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress for user {user_id} not found"
        )

    return progress


@router.put("/progress/{user_id}", response_model=ProgressSchema, tags=["Progress"])
async def update_progress(
    user_id: str,
    update: ProgressUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark chapter as complete and update progress.
    Zero-LLM: Adds chapter to completed list and recalculates percentage.
    """
    progress_service = ProgressService(db)
    progress = await progress_service.update_progress(user_id, str(update.chapter_id))

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} or chapter {update.chapter_id} not found"
        )

    return progress


@router.get("/streaks/{user_id}", response_model=StreakSchema, tags=["Progress"])
async def get_streak(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's streak information.
    Zero-LLM: Returns verbatim streak data from database.
    """
    streak_service = StreakService(db)
    streak = await streak_service.get_user_streak(user_id)

    if not streak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Streak for user {user_id} not found"
        )

    return streak


@router.post("/streaks/{user_id}/checkin", response_model=StreakSchema, tags=["Progress"])
async def record_checkin(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Record daily activity checkin.
    Zero-LLM: Deterministic calculation based on last checkin date.
    - Same day: No change
    - Consecutive day: Increment streak
    - Gap > 1 day: Reset streak
    """
    streak_service = StreakService(db)
    streak = await streak_service.record_checkin(user_id)

    if not streak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    return streak

"""
Leaderboard API Router - Global leaderboard with privacy controls.
Zero-Backend-LLM: XP calculated using deterministic formula.
Formula: total_quiz_score + (10 × completed_chapters) + (5 × streak_days)
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.leaderboard_service import LeaderboardService
from src.models.schemas import (
    LeaderboardOptInCreate, LeaderboardOptInUpdate,
    LeaderboardOptIn, Leaderboard
)

router = APIRouter()


@router.get("/", response_model=Leaderboard)
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Maximum entries to return"),
    user_id: Optional[UUID] = Query(None, description="Current user ID to find their rank"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get global leaderboard with top students.

    Zero-LLM compliance: XP calculated using formula only, no LLM.

    XP Formula:
        total_quiz_score + (10 × completed_chapters) + (5 × streak_days)

    Args:
        limit: Maximum entries to return (default: 10, max: 100)
        user_id: Current user's ID to find their rank

    Returns:
        Leaderboard with entries and optional user rank
    """
    service = LeaderboardService(db)
    leaderboard = await service.get_leaderboard(limit=limit, current_user_id=user_id)
    return leaderboard


@router.get("/opt-in-status", response_model=Optional[LeaderboardOptIn])
async def get_opt_in_status(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's leaderboard opt-in status.

    Zero-LLM compliance: Simple database query.

    Args:
        user_id: User UUID

    Returns:
        Opt-in status or None if not opted in
    """
    service = LeaderboardService(db)
    opt_in = await service.get_opt_in_status(user_id)
    return opt_in


@router.post("/opt-in", response_model=LeaderboardOptIn)
async def opt_in_to_leaderboard(
    user_id: UUID,
    opt_in_data: LeaderboardOptInCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Opt in to the global leaderboard.

    Zero-LLM compliance: Creates opt-in record with display name.

    Privacy: User chooses anonymous display name and what to show.

    Args:
        user_id: User UUID
        opt_in_data: Display name and privacy settings

    Returns:
        Created/updated opt-in record
    """
    service = LeaderboardService(db)
    opt_in = await service.opt_in(user_id, opt_in_data)
    return opt_in


@router.post("/opt-out")
async def opt_out_from_leaderboard(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Opt out from the global leaderboard.

    Zero-LLM compliance: Updates boolean flag.

    Privacy: User can leave leaderboard at any time.

    Args:
        user_id: User UUID

    Returns:
        Success message
    """
    service = LeaderboardService(db)
    success = await service.opt_out(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in leaderboard"
        )

    return {"message": "Successfully opted out from leaderboard"}


@router.put("/opt-in-settings", response_model=LeaderboardOptIn)
async def update_opt_in_settings(
    user_id: UUID,
    update_data: LeaderboardOptInUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update leaderboard opt-in privacy settings.

    Zero-LLM compliance: Updates privacy control fields.

    Args:
        user_id: User UUID
        update_data: Fields to update

    Returns:
        Updated opt-in record

    Raises:
        HTTPException 404: If opt-in record not found
    """
    service = LeaderboardService(db)
    opt_in = await service.update_opt_in(user_id, update_data)

    if not opt_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opt-in record not found. Please opt in first."
        )

    return opt_in


@router.get("/rank/{user_id}")
async def get_user_rank(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current rank on the leaderboard.

    Zero-LLM compliance: Simple rank lookup.

    Args:
        user_id: User UUID

    Returns:
        User's rank or null if not opted in

    Raises:
        HTTPException 404: If user not eligible for leaderboard
    """
    service = LeaderboardService(db)
    rank = await service.get_user_rank(user_id)

    if rank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not opted in to leaderboard"
        )

    return {"user_id": str(user_id), "rank": rank}


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's stats for leaderboard calculation.

    Zero-LLM compliance: Returns raw stats data.

    Stats breakdown:
        - average_score: From all quiz attempts
        - completed_chapters: From progress record
        - current_streak: From streak record
        - xp: Calculated using formula

    Args:
        user_id: User UUID

    Returns:
        User stats with XP breakdown
    """
    service = LeaderboardService(db)
    stats = await service.get_user_stats(user_id)
    return stats

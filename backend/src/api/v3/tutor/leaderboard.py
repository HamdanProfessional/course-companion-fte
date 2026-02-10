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
from src.api.dependencies import get_current_user, get_optional_user
from src.models.database import User

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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's leaderboard opt-in status.

    Zero-LLM compliance: Simple database query.

    Returns:
        Opt-in status or None if not opted in

    **Authentication**: Required - Users must be logged in to check their opt-in status.
    """
    service = LeaderboardService(db)
    opt_in = await service.get_opt_in_status(current_user.id)
    return opt_in


@router.post("/opt-in", response_model=LeaderboardOptIn)
async def opt_in_to_leaderboard(
    opt_in_data: LeaderboardOptInCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Opt in to the global leaderboard.

    Zero-LLM compliance: Creates opt-in record with display name.

    Privacy: User chooses anonymous display name and what to show.

    Returns:
        Created/updated opt-in record

    **Authentication**: Required - Users must be logged in to opt in.
    """
    service = LeaderboardService(db)
    opt_in = await service.opt_in(current_user.id, opt_in_data)
    return opt_in


@router.post("/opt-out")
async def opt_out_from_leaderboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Opt out from the global leaderboard.

    Zero-LLM compliance: Updates boolean flag.

    Privacy: User can leave leaderboard at any time.

    Returns:
        Success message

    **Authentication**: Required - Users must be logged in to opt out.
    """
    service = LeaderboardService(db)
    success = await service.opt_out(current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in leaderboard"
        )

    return {"message": "Successfully opted out from leaderboard"}


@router.put("/opt-in-settings", response_model=LeaderboardOptIn)
async def update_opt_in_settings(
    update_data: LeaderboardOptInUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update leaderboard opt-in privacy settings.

    Zero-LLM compliance: Updates privacy control fields.

    Returns:
        Updated opt-in record

    Raises:
        HTTPException 404: If opt-in record not found

    **Authentication**: Required - Users must be logged in to update their settings.
    """
    service = LeaderboardService(db)
    opt_in = await service.update_opt_in(current_user.id, update_data)

    if not opt_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opt-in record not found. Please opt in first."
        )

    return opt_in


@router.get("/rank/me")
async def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's rank on the leaderboard.

    Zero-LLM compliance: Simple rank lookup.

    Returns:
        User's rank or null if not opted in

    **Authentication**: Required - Users must be logged in to check their rank.
    """
    service = LeaderboardService(db)
    rank = await service.get_user_rank(current_user.id)

    if rank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not opted in to leaderboard"
        )

    return {"user_id": str(current_user.id), "rank": rank}


@router.get("/stats/me")
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's stats for leaderboard calculation.

    Zero-LLM compliance: Returns raw stats data.

    Stats breakdown:
        - average_score: From all quiz attempts
        - completed_chapters: From progress record
        - current_streak: From streak record
        - xp: Calculated using formula

    Returns:
        User stats with XP breakdown

    **Authentication**: Required - Users must be logged in to view their stats.
    """
    service = LeaderboardService(db)
    stats = await service.get_user_stats(current_user.id)
    return stats

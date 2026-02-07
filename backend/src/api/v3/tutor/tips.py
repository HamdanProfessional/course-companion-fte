"""
Tips API Router - Random tip feature for dashboard.
Zero-Backend-LLM: All tips are pre-written content.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.tip_service import TipService
from src.models.schemas import Tip, TipCreate, TipList

router = APIRouter()


@router.get("/", response_model=TipList)
async def get_all_tips(
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tips with optional filtering.

    Zero-LLM compliance: Returns pre-written tips only.

    Args:
        category: Filter by category (study_habits, quiz_strategy, motivation, course_tips)
        difficulty_level: Filter by difficulty (beginner, intermediate, advanced)
        active_only: Only return active tips (default: true)

    Returns:
        List of tips matching filters
    """
    service = TipService(db)
    tips = await service.get_all_tips(
        category=category,
        difficulty_level=difficulty_level,
        active_only=active_only
    )

    return TipList(tips=tips, total=len(tips))


@router.get("/random", response_model=Tip)
async def get_random_tip(
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a random active tip.

    Zero-LLM compliance: Returns randomly selected pre-written tip.

    Args:
        category: Optional category filter
        difficulty_level: Optional difficulty filter

    Returns:
        Random tip

    Raises:
        HTTPException 404: If no tips available
    """
    service = TipService(db)
    tip = await service.get_random_tip(
        category=category,
        difficulty_level=difficulty_level
    )

    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tips available matching the criteria"
        )

    return tip


@router.get("/{tip_id}", response_model=Tip)
async def get_tip_by_id(
    tip_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific tip by ID.

    Zero-LLM compliance: Returns pre-written tip only.

    Args:
        tip_id: Tip UUID

    Returns:
        Tip details

    Raises:
        HTTPException 404: If tip not found
    """
    service = TipService(db)
    tip = await service.get_tip_by_id(tip_id)

    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tip not found"
        )

    return tip


@router.post("/", response_model=Tip, status_code=status.HTTP_201_CREATED)
async def create_tip(
    tip_data: TipCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tip.

    Zero-LLM compliance: Creates pre-written tip, no LLM generation.

    Args:
        tip_data: Tip data to create

    Returns:
        Created tip
    """
    service = TipService(db)
    tip = await service.create_tip(tip_data)
    return tip


@router.put("/{tip_id}", response_model=Tip)
async def update_tip(
    tip_id: UUID,
    tip_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing tip.

    Zero-LLM compliance: Updates pre-written tip content.

    Args:
        tip_id: Tip UUID
        tip_data: Fields to update

    Returns:
        Updated tip

    Raises:
        HTTPException 404: If tip not found
    """
    service = TipService(db)
    tip = await service.update_tip(tip_id, tip_data)

    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tip not found"
        )

    return tip


@router.delete("/{tip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tip(
    tip_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a tip.

    Zero-LLM compliance: Deletes pre-written tip.

    Args:
        tip_id: Tip UUID

    Raises:
        HTTPException 404: If tip not found
    """
    service = TipService(db)
    deleted = await service.delete_tip(tip_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tip not found"
        )

    return None


@router.get("/stats/count")
async def get_tip_count(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get count of tips.

    Zero-LLM compliance: Simple count query.

    Args:
        active_only: Only count active tips (default: true)

    Returns:
        Count of tips
    """
    service = TipService(db)
    count = await service.get_tip_count(active_only=active_only)
    return {"count": count}

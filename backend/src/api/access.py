"""
Access Control API endpoints.
Zero-LLM compliance: Rule-based enforcement, no AI evaluation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.access_service import AccessService
from src.models.schemas import (
    AccessCheck,
    AccessResponse,
    UserTierUpdate,
    TierUpdateResponse,
)

router = APIRouter()


@router.post("/access/check", response_model=AccessResponse, tags=["Access"])
async def check_access(
    check: AccessCheck,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user has access to resource.
    Zero-LLM: Rule-based enforcement (free tier = chapters 1-3 only).
    """
    service = AccessService(db)
    result = await service.check_access(check.user_id, check.resource)

    return result


@router.get("/user/{user_id}/tier", tags=["Access"])
async def get_user_tier(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current subscription tier.
    Zero-LLM: Returns verbatim tier from database.
    """
    service = AccessService(db)
    result = await service.get_user_tier(user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    return result


@router.post("/access/upgrade", response_model=TierUpdateResponse, tags=["Access"])
async def upgrade_tier(
    user_id: str,
    update: UserTierUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Upgrade user to new subscription tier.
    Zero-LLM: Simple database update (payment integration would be separate).
    """
    service = AccessService(db)
    result = await service.upgrade_user_tier(user_id, update.new_tier)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    return result

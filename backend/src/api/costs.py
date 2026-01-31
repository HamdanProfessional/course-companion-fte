"""
Cost Tracking API Endpoints - Phase 2.

Admin and user-facing endpoints for monitoring LLM API costs.
Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.config import settings
from src.services.cost_tracking_service import (
    get_user_costs,
    get_total_costs,
    get_top_users,
    CostTrackingError
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================


class FeatureCostBreakdown(BaseModel):
    """Cost breakdown for a specific feature."""

    cost_usd: float = Field(description="Total cost in USD")
    tokens: int = Field(description="Total tokens used")
    calls: int = Field(description="Number of API calls")


class UserCostResponse(BaseModel):
    """User cost summary."""

    user_id: str = Field(description="User UUID")
    period_days: int = Field(description="Period covered (days)")
    total_cost_usd: float = Field(description="Total cost in USD")
    total_tokens: int = Field(description="Total tokens used")
    total_calls: int = Field(description="Total API calls")
    feature_breakdown: dict = Field(description="Breakdown by feature")


class TotalCostResponse(BaseModel):
    """Total cost summary (admin)."""

    period_days: int = Field(description="Period covered (days)")
    total_cost_usd: float = Field(description="Total cost in USD")
    total_tokens: int = Field(description="Total tokens used")
    total_calls: int = Field(description="Total API calls")
    unique_users: int = Field(description="Number of unique users")
    average_cost_per_user: float = Field(description="Average cost per user")
    feature_breakdown: dict = Field(description="Breakdown by feature")


class TopUserItem(BaseModel):
    """Single top user entry."""

    user_id: str = Field(description="User UUID")
    total_cost_usd: float = Field(description="Total cost in USD")
    total_tokens: int = Field(description="Total tokens used")
    call_count: int = Field(description="Number of API calls")


class TopUsersResponse(BaseModel):
    """Top users by cost."""

    period_days: int = Field(description="Period covered (days)")
    top_users: list = Field(description="List of top users")


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str = Field(description="Error message")
    phase_2_enabled: bool = Field(
        description="Whether Phase 2 LLM features are enabled",
        default=False
    )


# =============================================================================
# API Endpoints
# =============================================================================


@router.get(
    "/costs/{user_id}",
    response_model=UserCostResponse,
    tags=["Cost Tracking (Phase 2)"],
    summary="Get user's LLM costs",
    description="Retrieve LLM API costs for a specific user"
)
async def get_user_cost_endpoint(
    user_id: UUID,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get LLM costs for a specific user.

    Returns:
    - Total cost in USD
    - Total tokens used
    - Number of API calls
    - Breakdown by feature (adaptive, quiz_llm, mentor)

    **Access**: Users can view their own costs. Admins can view all users.

    **Phase 2 Feature**: Only available when ENABLE_PHASE_2_LLM=true
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Phase 2 LLM features are not enabled",
                "phase_2_enabled": False
            }
        )

    try:
        costs = await get_user_costs(str(user_id), db, days)
        return UserCostResponse(**costs)

    except CostTrackingError as e:
        logger.error(f"Cost tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_user_costs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user costs"
        )


@router.get(
    "/costs/summary/total",
    response_model=TotalCostResponse,
    tags=["Cost Tracking (Phase 2)"],
    summary="Get total LLM costs (admin)",
    description="Retrieve total LLM API costs across all users"
)
async def get_total_cost_endpoint(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get total LLM costs across all users.

    Returns:
    - Total cost in USD
    - Total tokens used
    - Number of API calls
    - Number of unique users
    - Average cost per user
    - Breakdown by feature

    **Access**: Admin only (implement authentication check)

    **Use Cases**:
    - Monitor overall LLM spending
    - Calculate cost per user
    - Track feature usage patterns
    - Budget planning

    **Phase 2 Feature**: Only available when ENABLE_PHASE_2_LLM=true
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Phase 2 LLM features are not enabled",
                "phase_2_enabled": False
            }
        )

    try:
        costs = await get_total_costs(db, days)
        return TotalCostResponse(**costs)

    except CostTrackingError as e:
        logger.error(f"Cost tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_total_costs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve total costs"
        )


@router.get(
    "/costs/top-users",
    response_model=TopUsersResponse,
    tags=["Cost Tracking (Phase 2)"],
    summary="Get top users by LLM usage (admin)",
    description="Retrieve users with highest LLM costs"
)
async def get_top_users_endpoint(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum users to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top users by LLM usage.

    Returns users sorted by total cost (highest first).

    **Access**: Admin only (implement authentication check)

    **Use Cases**:
    - Identify power users
    - Detect unusual usage patterns
    - Resource planning
    - Fair use policy enforcement

    **Phase 2 Feature**: Only available when ENABLE_PHASE_2_LLM=true
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Phase 2 LLM features are not enabled",
                "phase_2_enabled": False
            }
        )

    try:
        top_users = await get_top_users(db, days, limit)
        return TopUsersResponse(
            period_days=days,
            top_users=top_users
        )

    except CostTrackingError as e:
        logger.error(f"Cost tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_top_users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve top users"
        )


@router.get(
    "/costs/status",
    tags=["Cost Tracking (Phase 2)"],
    summary="Check cost tracking status"
)
async def get_cost_tracking_status():
    """
    Check if cost tracking is enabled.

    Returns configuration information.
    """
    return {
        "phase_2_enabled": settings.enable_phase_2_llm,
        "cost_tracking_enabled": settings.enable_phase_2_llm,
        "llm_provider": settings.llm_provider if settings.enable_phase_2_llm else None,
        "model": settings.openai_model if settings.llm_provider == "openai" else settings.anthropic_model,
    }

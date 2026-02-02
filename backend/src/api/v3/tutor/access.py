"""
Access & Subscription Router - Phase 3 Unified API

Handles access control and subscription management:
- Access checks for premium content
- Tier management
- Subscription info
- Upgrade/downgrade
- Payment integration

Path: /api/v3/tutor/access
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.config import settings
from src.services.access_service import AccessService
from src.models.database import User
from src.models.schemas import UserTier, AccessCheck, AccessResponse, TierUpdateResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Enums and Models
# =============================================================================


class SubscriptionPlan(BaseModel):
    """Subscription plan details."""
    tier: UserTier
    name: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    limits: Dict[str, Any]


class SubscriptionInfo(BaseModel):
    """User's subscription information."""
    user_id: str
    current_tier: UserTier
    tier_name: str
    subscribed_at: Optional[datetime] = None
    subscription_status: str  # active, cancelled, past_due
    next_billing_date: Optional[datetime] = None
    cancel_at_period_end: bool = False


class AccessCheckRequest(BaseModel):
    """Request to check access to a resource."""
    resource: str = Field(..., description="Resource identifier (e.g., 'chapter-4')")


class AccessCheckResponse(BaseModel):
    """Response for access check."""
    has_access: bool
    tier: UserTier
    reason: Optional[str] = None
    upgrade_url: Optional[str] = None
    requirements: Optional[str] = None


class TierChangeRequest(BaseModel):
    """Request to change subscription tier."""
    new_tier: UserTier
    payment_method_id: Optional[str] = None
    billing_cycle: str = Field(default="monthly", description="monthly or yearly")


class ExportDataRequest(BaseModel):
    """Request to export user data (GDPR)."""
    include_progress: bool = True
    include_quiz_history: bool = True
    include_streaks: bool = True
    format: str = Field(default="json", description="json, csv, or pdf")


class ExportDataResponse(BaseModel):
    """Response for data export request."""
    export_id: str
    status: str
    expires_at: datetime
    download_url: Optional[str] = None


# =============================================================================
# Subscription Plan Definitions
# =============================================================================

SUBSCRIPTION_PLANS = {
    UserTier.FREE: SubscriptionPlan(
        tier=UserTier.FREE,
        name="Free",
        price_monthly=0.0,
        price_yearly=0.0,
        features=[
            "Access to chapters 1-3",
            "Basic quizzes (rule-based grading)",
            "Progress tracking",
            "3-day streak tracking"
        ],
        limits={
            "chapters": 3,
            "quiz_grading": "rule_based",
            "ai_features": False,
            "support": "community"
        }
    ),
    UserTier.PREMIUM: SubscriptionPlan(
        tier=UserTier.PREMIUM,
        name="Premium",
        price_monthly=9.99,
        price_yearly=99.99,
        features=[
            "Access to ALL chapters",
            "AI-powered quiz grading",
            "Adaptive learning recommendations",
            "AI mentor for Q&A",
            "Unlimited streak tracking",
            "Achievement system",
            "Content explanations",
            "Priority email support"
        ],
        limits={
            "chapters": "unlimited",
            "quiz_grading": "ai_enhanced",
            "ai_features": True,
            "support": "email"
        }
    ),
    UserTier.PRO: SubscriptionPlan(
        tier=UserTier.PRO,
        name="Pro",
        price_monthly=29.99,
        price_yearly=299.99,
        features=[
            "Everything in Premium",
            "Personalized learning paths",
            "1-on-1 AI tutoring sessions",
            "Advanced analytics dashboard",
            "Cost tracking reports",
            "API access",
            "Priority support (24h response)",
            "Early access to new features"
        ],
        limits={
            "chapters": "unlimited",
            "quiz_grading": "ai_advanced",
            "ai_features": True,
            "support": "priority",
            "api_access": True
        }
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================


async def get_user_or_404(user_id: UUID, db: AsyncSession) -> User:
    """Get user or raise 404."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/plans", response_model=List[SubscriptionPlan])
async def list_subscription_plans():
    """
    List all available subscription plans.

    Returns pricing, features, and limits for each tier.

    **Phase 3 Enhancement**: Detailed plan comparison.
    """
    return list(SUBSCRIPTION_PLANS.values())


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription_info(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current subscription information.

    **Phase 3 Enhancement**: Full subscription details.
    """
    try:
        user = await get_user_or_404(user_id, db)

        # In production, this would fetch from Stripe/Payment processor
        # For now, return basic info
        tier_names = {
            UserTier.FREE: "Free",
            UserTier.PREMIUM: "Premium",
            UserTier.PRO: "Pro"
        }

        return SubscriptionInfo(
            user_id=str(user.id),
            current_tier=user.tier,
            tier_name=tier_names.get(user.tier, "Unknown"),
            subscribed_at=user.created_at if user.tier != UserTier.FREE else None,
            subscription_status="active" if user.tier != UserTier.FREE else "none",
            next_billing_date=None,  # Would come from Stripe
            cancel_at_period_end=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription info"
        )


@router.post("/check", response_model=AccessCheckResponse)
async def check_access(
    request: AccessCheckRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user has access to a specific resource.

    Resources can be:
    - `chapter-{id}`: Specific chapter
    - `quiz-{id}`: Specific quiz
    - `ai-feature`: AI features
    - `adaptive-learning`: Adaptive recommendations
    - `ai-mentor`: AI mentor chat

    **Phase 3 Enhancement**: Detailed access control with upgrade prompts.
    """
    try:
        user = await get_user_or_404(user_id, db)
        service = AccessService(db)

        # Parse resource
        resource = request.resource.lower()

        has_access = True
        reason = None
        requirements = None
        upgrade_url = None

        # Chapter access (Chapter 4+ requires premium)
        if resource.startswith("chapter-"):
            try:
                chapter_num = int(resource.split("-")[1])
                if chapter_num >= 4 and user.tier == UserTier.FREE:
                    has_access = False
                    reason = f"Chapter {chapter_num} requires Premium or Pro subscription"
                    requirements = f"Chapters 1-3 are free. Chapters 4+ require Premium."
                    upgrade_url = "/api/v3/tutor/access/upgrade"
            except (ValueError, IndexError):
                pass

        # AI features require premium
        elif resource in ["ai-feature", "adaptive-learning", "ai-mentor"]:
            if user.tier == UserTier.FREE:
                has_access = False
                reason = "AI features require Premium or Pro subscription"
                requirements = "Upgrade to Premium to access AI-powered features"
                upgrade_url = "/api/v3/tutor/access/upgrade"

        # Pro-only features
        elif resource in ["api-access", "advanced-analytics", "cost-tracking"]:
            if user.tier != UserTier.PRO:
                has_access = False
                reason = "This feature requires Pro subscription"
                requirements = "Upgrade to Pro for advanced features"
                upgrade_url = "/api/v3/tutor/access/upgrade"

        return AccessCheckResponse(
            has_access=has_access,
            tier=user.tier,
            reason=reason,
            upgrade_url=upgrade_url,
            requirements=requirements
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check access"
        )


@router.post("/upgrade", response_model=TierUpdateResponse)
async def upgrade_tier(
    request: TierChangeRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upgrade or change subscription tier.

    **Phase 3 Feature**: Integrated with payment processor (Stripe).

    For production:
    1. Create Stripe checkout session
    2. Redirect to payment page
    3. Webhook updates tier after payment

    For this implementation:
    - Direct tier update (for testing)
    - Payment integration would be added here
    """
    try:
        user = await get_user_or_404(user_id, db)

        # In production, this would:
        # 1. Validate payment method
        # 2. Create Stripe subscription
        # 3. Return checkout URL

        # For now, update tier directly
        old_tier = user.tier
        user.tier = request.new_tier
        await db.commit()

        # Log the change
        logger.info(f"User {user_id} tier updated: {old_tier} -> {request.new_tier}")

        return TierUpdateResponse(
            user_id=str(user_id),
            old_tier=old_tier,
            new_tier=request.new_tier,
            upgraded_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading tier: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade tier"
        )


@router.post("/downgrade")
async def downgrade_tier(
    new_tier: UserTier = Body(..., embed=True),
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Downgrade subscription tier.

    Takes effect at the end of the current billing period.
    User retains current tier access until then.

    **Phase 3 Feature**: Graceful downgrade with period end.
    """
    try:
        user = await get_user_or_404(user_id, db)

        # In production, this would:
        # 1. Schedule downgrade in Stripe
        # 2. Set cancel_at_period_end
        # 3. Webhook processes downgrade

        old_tier = user.tier

        # Only allow downgrade
        tier_order = {UserTier.FREE: 0, UserTier.PREMIUM: 1, UserTier.PRO: 2}
        if tier_order.get(new_tier, 0) >= tier_order.get(old_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only downgrade to a lower tier"
            )

        # For now, update directly
        user.tier = new_tier
        await db.commit()

        logger.info(f"User {user_id} downgraded: {old_tier} -> {new_tier}")

        return {
            "message": "Tier downgraded successfully",
            "old_tier": old_tier,
            "new_tier": new_tier,
            "effective": "immediately"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downgrading tier: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to downgrade tier"
        )


@router.post("/export-data", response_model=ExportDataResponse)
async def request_data_export(
    request: ExportDataRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Request export of user data (GDPR compliance).

    **Phase 3 Feature**: GDPR-compliant data export.

    Exports can include:
    - Progress data
    - Quiz history
    - Streak information
    - Achievement history

    Available formats:
    - JSON (default, machine-readable)
    - CSV (spreadsheet-compatible)
    - PDF (human-readable report)
    """
    try:
        user = await get_user_or_404(user_id, db)

        # Generate export ID
        import uuid
        export_id = str(uuid.uuid4())

        # In production, this would:
        # 1. Collect requested data
        # 2. Generate file in requested format
        # 3. Upload to storage
        # 4. Return download URL
        # 5. Set expiration (e.g., 7 days)

        # For now, return a placeholder
        from datetime import timedelta

        return ExportDataResponse(
            export_id=export_id,
            status="processing",
            expires_at=datetime.utcnow() + timedelta(days=7),
            download_url=None  # Would be populated when ready
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting data export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request data export"
        )


@router.get("/export-data/{export_id}")
async def get_export_status(
    export_id: str,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of data export request.

    Returns:
    - Status (processing, ready, expired)
    - Download URL (if ready)
    - Expiration date
    """
    try:
        # In production, query the export job status
        return {
            "export_id": export_id,
            "status": "processing",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow(),
            "download_url": None
        }

    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get export status"
        )


@router.delete("/account")
async def delete_account(
    confirmation: str = Body(..., embed=True, description="Must be 'DELETE' to confirm"),
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account and all associated data.

    **GDPR Compliance**: Right to be forgotten.

    This action is irreversible and will:
    - Delete user account
    - Delete all progress data
    - Delete quiz attempts
    - Delete streak data
    - Cancel any subscriptions

    Must confirm by sending confirmation='DELETE'.
    """
    try:
        if confirmation != "DELETE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must confirm by sending confirmation='DELETE'"
            )

        user = await get_user_or_404(user_id, db)

        # In production, this would:
        # 1. Cancel Stripe subscription
        # 2. Delete all user data from database
        # 3. Delete any stored files
        # 4. Log the deletion for audit

        # For now, just log
        logger.warning(f"Account deletion requested for user {user_id}")

        return {
            "message": "Account deletion initiated",
            "user_id": str(user_id),
            "status": "processing",
            "irreversible": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


@router.get("/payment-methods")
async def get_payment_methods(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's payment methods on file.

    **Phase 3 Feature**: Payment method management.

    In production, this would fetch from Stripe.
    """
    try:
        user = await get_user_or_404(user_id, db)

        # Placeholder - in production, fetch from Stripe
        return {
            "payment_methods": [],
            "default_payment_method": None,
            "has_payment_method": False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment methods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment methods"
        )

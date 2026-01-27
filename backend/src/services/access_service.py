"""
Access control service business logic.
Zero-LLM compliance: Rule-based enforcement only, no LLM evaluation.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.database import User, Chapter
from src.models.schemas import (
    UserTier,
    AccessResponse,
    TierUpdateResponse
)


class AccessService:
    """Business logic for freemium access control and tier enforcement."""

    # Free tier access limit (first N chapters)
    FREE_TIER_CHAPTER_LIMIT = 3

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_access(
        self,
        user_id: str,
        resource: str
    ) -> AccessResponse:
        """
        Check if user has access to resource.
        Zero-LLM: Deterministic rule-based enforcement.

        Args:
            user_id: User UUID
            resource: Resource identifier (e.g., "chapter-4")

        Returns:
            Access response with granted/denied status
        """
        # Get user tier
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return AccessResponse(
                access_granted=False,
                tier=UserTier.FREE,
                reason="User not found",
                upgrade_url="/api/v1/access/upgrade"
            )

        tier = user.tier

        # Parse resource type (e.g., "chapter-4" -> chapter_number = 4)
        if resource.startswith("chapter-"):
            try:
                chapter_number = int(resource.split("-")[1])

                # Free tier: access to first 3 chapters only
                if tier == UserTier.FREE and chapter_number > self.FREE_TIER_CHAPTER_LIMIT:
                    return AccessResponse(
                        access_granted=False,
                        tier=tier.value,
                        reason=f"Chapter {chapter_number} is premium content. Free tier includes chapters 1-{self.FREE_TIER_CHAPTER_LIMIT}.",
                        upgrade_url="/api/v1/access/upgrade"
                    )

                # Premium and Pro: all chapters
                return AccessResponse(
                    access_granted=True,
                    tier=tier.value,
                    reason=None,
                    upgrade_url=None
                )
            except (ValueError, IndexError):
                return AccessResponse(
                    access_granted=False,
                    tier=tier.value,
                    reason="Invalid resource format",
                    upgrade_url=None
                )

        # Default: deny access for unknown resource types
        return AccessResponse(
            access_granted=False,
            tier=tier.value,
            reason="Unknown resource type",
            upgrade_url=None
        )

    async def get_user_tier(self, user_id: str) -> Optional[dict]:
        """
        Get user's current subscription tier.

        Args:
            user_id: User UUID

        Returns:
            User tier information
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        return {
            "user_id": str(user.id),
            "tier": user.tier.value,
            "created_at": user.created_at.isoformat(),
        }

    async def upgrade_user_tier(
        self,
        user_id: str,
        new_tier: UserTier
    ) -> TierUpdateResponse:
        """
        Upgrade user to new subscription tier.
        Zero-LLM: Simple database update, no payment processing.

        Args:
            user_id: User UUID
            new_tier: New tier (premium or pro)

        Returns:
            Tier update confirmation
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        old_tier = user.tier
        user.tier = new_tier

        await self.db.commit()

        return TierUpdateResponse(
            user_id=str(user.id),
            old_tier=old_tier.value,
            new_tier=new_tier.value,
            upgraded_at=user.created_at  # Using created_at as timestamp placeholder
        )

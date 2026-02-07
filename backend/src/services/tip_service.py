"""
Tip Service - Manages learning tips for students.
Zero-Backend-LLM: All tips are pre-written content, no LLM generation.
"""

import uuid
import random
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Tip
from src.models.schemas import TipCreate, Tip


class TipService:
    """Service for managing learning tips."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_tips(
        self,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        active_only: bool = True
    ) -> List[Tip]:
        """
        Get all tips with optional filtering.

        Args:
            category: Filter by category
            difficulty_level: Filter by difficulty level
            active_only: Only return active tips

        Returns:
            List of tips matching filters
        """
        query = select(Tip)

        conditions = []
        if active_only:
            conditions.append(Tip.active == True)
        if category:
            conditions.append(Tip.category == category)
        if difficulty_level:
            # Match tips with specific difficulty OR no difficulty (general tips)
            conditions.append(
                or_(
                    Tip.difficulty_level == difficulty_level,
                    Tip.difficulty_level == None  # noqa: E711
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Tip.created_at.desc())

        result = await self.db.execute(query)
        tips = result.scalars().all()
        return list(tips)

    async def get_tip_by_id(self, tip_id: uuid.UUID) -> Optional[Tip]:
        """
        Get a specific tip by ID.

        Args:
            tip_id: Tip UUID

        Returns:
            Tip or None if not found
        """
        query = select(Tip).where(Tip.id == tip_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_random_tip(
        self,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None
    ) -> Optional[Tip]:
        """
        Get a random active tip.

        Args:
            category: Optional category filter
            difficulty_level: Optional difficulty filter

        Returns:
            Random tip or None if no tips available
        """
        tips = await self.get_all_tips(
            category=category,
            difficulty_level=difficulty_level,
            active_only=True
        )

        if not tips:
            return None

        return random.choice(tips)

    async def create_tip(self, tip_data: TipCreate) -> Tip:
        """
        Create a new tip.

        Args:
            tip_data: Tip data to create

        Returns:
            Created tip
        """
        tip = Tip(**tip_data.model_dump())
        self.db.add(tip)
        await self.db.commit()
        await self.db.refresh(tip)
        return tip

    async def update_tip(
        self,
        tip_id: uuid.UUID,
        tip_data: dict
    ) -> Optional[Tip]:
        """
        Update an existing tip.

        Args:
            tip_id: Tip UUID
            tip_data: Fields to update

        Returns:
            Updated tip or None if not found
        """
        query = select(Tip).where(Tip.id == tip_id)
        result = await self.db.execute(query)
        tip = result.scalar_one_or_none()

        if not tip:
            return None

        for key, value in tip_data.items():
            if hasattr(tip, key):
                setattr(tip, key, value)

        await self.db.commit()
        await self.db.refresh(tip)
        return tip

    async def delete_tip(self, tip_id: uuid.UUID) -> bool:
        """
        Delete a tip.

        Args:
            tip_id: Tip UUID

        Returns:
            True if deleted, False if not found
        """
        query = select(Tip).where(Tip.id == tip_id)
        result = await self.db.execute(query)
        tip = result.scalar_one_or_none()

        if not tip:
            return False

        await self.db.delete(tip)
        await self.db.commit()
        return True

    async def get_tip_count(self, active_only: bool = True) -> int:
        """
        Get count of tips.

        Args:
            active_only: Only count active tips

        Returns:
            Number of tips
        """
        from sqlalchemy import func

        query = select(func.count(Tip.id))
        if active_only:
            query = query.where(Tip.active == True)

        result = await self.db.execute(query)
        return result.scalar() or 0

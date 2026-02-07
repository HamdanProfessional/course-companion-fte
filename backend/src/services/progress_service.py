"""
Progress service business logic.
Zero-LLM compliance: Deterministic calculations only, no LLM services.
"""

from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.database import Progress, Chapter, Streak
from src.models.schemas import Progress as ProgressSchema, Streak as StreakSchema


class ProgressService:
    """Business logic for progress tracking and streak calculation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_progress(self, user_id: str) -> Optional[ProgressSchema]:
        """
        Get user's learning progress.

        Args:
            user_id: User UUID

        Returns:
            User progress with completion percentage
        """
        # Get progress record
        result = await self.db.execute(
            select(Progress)
            .options(selectinload(Progress.current_chapter))
            .where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        if not progress:
            # Create initial progress record
            progress = Progress(
                user_id=user_id,
                completed_chapters=[],
                current_chapter_id=None,
                last_activity=datetime.utcnow(),
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)

        # Get total chapter count
        total_chapters_result = await self.db.execute(
            select(Chapter).order_by(Chapter.order)
        )
        total_chapters = len(total_chapters_result.scalars().all())

        # Calculate completion percentage
        completed_count = len(progress.completed_chapters) if progress.completed_chapters else 0
        completion_percentage = (
            (completed_count / total_chapters * 100) if total_chapters > 0 else 0.0
        )

        return ProgressSchema(
            id=str(progress.id),
            user_id=str(progress.user_id),
            completed_chapters=progress.completed_chapters or [],
            current_chapter_id=str(progress.current_chapter_id) if progress.current_chapter_id else None,
            completion_percentage=round(completion_percentage, 2),
            last_activity=progress.last_activity,
        )

    async def update_progress(
        self,
        user_id: str,
        chapter_id: str
    ) -> Optional[ProgressSchema]:
        """
        Mark chapter as complete and update progress.

        Args:
            user_id: User UUID
            chapter_id: Chapter UUID to mark complete

        Returns:
            Updated progress
        """
        # Get existing progress
        result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = Progress(
                user_id=user_id,
                completed_chapters=[],
                current_chapter_id=None,
                last_activity=datetime.utcnow(),
            )
            self.db.add(progress)

        # Add chapter to completed if not already there
        if chapter_id not in (progress.completed_chapters or []):
            if not progress.completed_chapters:
                progress.completed_chapters = []
            progress.completed_chapters.append(chapter_id)

        # Update current chapter to next in sequence
        chapter_result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = chapter_result.scalar_one_or_none()
        if chapter and chapter.next_chapter_id:
            progress.current_chapter_id = chapter.next_chapter_id

        # Update last activity
        progress.last_activity = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(progress)

        return await self.get_user_progress(user_id)

    async def mark_chapter_complete(
        self,
        user_id: str,
        chapter_id: str
    ) -> Optional[ProgressSchema]:
        """
        Alias for update_progress - marks chapter as complete.

        Args:
            user_id: User UUID
            chapter_id: Chapter UUID to mark complete

        Returns:
            Updated progress
        """
        return await self.update_progress(user_id, chapter_id)


class StreakService:
    """Business logic for streak tracking and gamification."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_streak(self, user_id: str) -> StreakSchema:
        """
        Get user's current streak information.

        Args:
            user_id: User UUID

        Returns:
            User streak data
        """
        result = await self.db.execute(
            select(Streak).where(Streak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()

        if not streak:
            # Create initial streak record
            streak = Streak(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                last_checkin=None,
            )
            self.db.add(streak)
            await self.db.commit()
            await self.db.refresh(streak)

        return StreakSchema(
            id=str(streak.id),
            user_id=str(streak.user_id),
            current_streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            last_checkin=streak.last_checkin,
        )

    async def record_checkin(self, user_id: str) -> StreakSchema:
        """
        Record daily activity checkin and update streak.
        Zero-LLM: Deterministic calculation based on dates.

        Args:
            user_id: User UUID

        Returns:
            Updated streak
        """
        # Get existing streak
        result = await self.db.execute(
            select(Streak).where(Streak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()

        if not streak:
            streak = Streak(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                last_checkin=None,
            )
            self.db.add(streak)

        today = date.today()

        # Streak calculation logic
        if streak.last_checkin is None:
            # First checkin
            streak.current_streak = 1
            streak.longest_streak = 1
            streak.last_checkin = today
        elif streak.last_checkin == today:
            # Already checked in today, no change
            pass
        elif streak.last_checkin == today - timedelta(days=1):
            # Consecutive day, increment streak
            streak.current_streak += 1
            streak.last_checkin = today
            # Update longest streak
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        elif streak.last_checkin < today - timedelta(days=1):
            # Streak broken (gap > 1 day), reset
            streak.current_streak = 1
            streak.last_checkin = today

        await self.db.commit()
        await self.db.refresh(streak)

        return StreakSchema(
            id=str(streak.id),
            user_id=str(streak.user_id),
            current_streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            last_checkin=streak.last_checkin,
        )

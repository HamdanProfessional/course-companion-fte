"""
Leaderboard Service - Manages global leaderboard with XP calculation.
Zero-Backend-LLM: All calculations are deterministic formulas.
XP Formula: total_quiz_score + (10 × completed_chapters) + (5 × streak_days)
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import (
    User, LeaderboardOptIn, Progress, Streak, QuizAttempt
)
from src.models.schemas import (
    LeaderboardOptInCreate, LeaderboardOptInUpdate,
    LeaderboardEntry, Leaderboard
)


class LeaderboardService:
    """Service for managing leaderboard with privacy controls."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_xp(self, user_id: uuid.UUID) -> int:
        """
        Calculate XP for a user.
        XP = total_quiz_score + (10 × completed_chapters) + (5 × streak_days)

        Args:
            user_id: User UUID

        Returns:
            Total XP points
        """
        # Get average quiz score
        quiz_query = select(func.avg(QuizAttempt.score)).where(
            QuizAttempt.user_id == user_id
        )
        quiz_result = await self.db.execute(quiz_query)
        avg_quiz_score = quiz_result.scalar() or 0

        # Get completed chapters count
        progress_query = select(Progress).where(Progress.user_id == user_id)
        progress_result = await self.db.execute(progress_query)
        progress = progress_result.scalar_one_or_none()

        completed_chapters = 0
        if progress and progress.completed_chapters:
            completed_chapters = len(progress.completed_chapters)

        # Get current streak
        streak_query = select(Streak).where(Streak.user_id == user_id)
        streak_result = await self.db.execute(streak_query)
        streak = streak_result.scalar_one_or_none()

        streak_days = streak.current_streak if streak else 0

        # Calculate XP
        xp = int(avg_quiz_score) + (10 * completed_chapters) + (5 * streak_days)
        return xp

    async def get_user_stats(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive stats for a user.

        Args:
            user_id: User UUID

        Returns:
            Dictionary with user stats
        """
        # Get average quiz score
        quiz_query = select(func.avg(QuizAttempt.score)).where(
            QuizAttempt.user_id == user_id
        )
        quiz_result = await self.db.execute(quiz_query)
        avg_quiz_score = quiz_result.scalar() or 0

        # Get progress
        progress_query = select(Progress).where(Progress.user_id == user_id)
        progress_result = await self.db.execute(progress_query)
        progress = progress_result.scalar_one_or_none()

        completed_chapters = 0
        if progress and progress.completed_chapters:
            completed_chapters = len(progress.completed_chapters)

        # Get streak
        streak_query = select(Streak).where(Streak.user_id == user_id)
        streak_result = await self.db.execute(streak_query)
        streak = streak_result.scalar_one_or_none()

        current_streak = streak.current_streak if streak else 0

        return {
            "average_score": float(avg_quiz_score),
            "completed_chapters": completed_chapters,
            "current_streak": current_streak,
            "xp": int(avg_quiz_score) + (10 * completed_chapters) + (5 * current_streak)
        }

    async def get_leaderboard(
        self,
        limit: int = 10,
        current_user_id: Optional[uuid.UUID] = None
    ) -> Leaderboard:
        """
        Get global leaderboard with opt-in users.

        Args:
            limit: Maximum number of entries to return
            current_user_id: Current user's ID to find their rank

        Returns:
            Leaderboard with entries and optional user rank
        """
        # Get all opted-in users
        opt_in_query = select(LeaderboardOptIn).where(
            LeaderboardOptIn.is_opted_in == True
        )
        opt_in_result = await self.db.execute(opt_in_query)
        opted_in_users = opt_in_result.scalars().all()

        # Calculate XP for each user and build entries
        entries = []
        for opt_in in opted_in_users:
            stats = await self.get_user_stats(opt_in.user_id)
            entry = LeaderboardEntry(
                rank=0,  # Will be set after sorting
                user_id=opt_in.user_id,
                display_name=opt_in.display_name,
                xp=stats["xp"],
                average_score=stats["average_score"],
                current_streak=stats["current_streak"],
                completed_chapters=stats["completed_chapters"]
            )
            entries.append(entry)

        # Sort by XP descending
        entries.sort(key=lambda e: e.xp, reverse=True)

        # Assign ranks
        for i, entry in enumerate(entries, start=1):
            entry.rank = i

        # Get user's rank if provided
        user_rank = None
        user_xp = None
        if current_user_id:
            for entry in entries:
                if entry.user_id == current_user_id:
                    user_rank = entry.rank
                    user_xp = entry.xp
                    break

        return Leaderboard(
            leaderboard=entries[:limit],
            total_entries=len(entries),
            user_rank=user_rank,
            user_xp=user_xp
        )

    async def get_opt_in_status(self, user_id: uuid.UUID) -> Optional[LeaderboardOptIn]:
        """
        Get user's opt-in status.

        Args:
            user_id: User UUID

        Returns:
            Opt-in record or None
        """
        query = select(LeaderboardOptIn).where(
            LeaderboardOptIn.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def opt_in(
        self,
        user_id: uuid.UUID,
        opt_in_data: LeaderboardOptInCreate
    ) -> LeaderboardOptIn:
        """
        Create or update opt-in status.

        Args:
            user_id: User UUID
            opt_in_data: Opt-in data

        Returns:
            Created/updated opt-in record
        """
        # Check if existing
        existing = await self.get_opt_in_status(user_id)

        if existing:
            # Update existing
            existing.display_name = opt_in_data.display_name
            existing.is_opted_in = True
            existing.show_rank = opt_in_data.show_rank
            existing.show_score = opt_in_data.show_score
            existing.show_streak = opt_in_data.show_streak
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new
            opt_in = LeaderboardOptIn(
                user_id=user_id,
                display_name=opt_in_data.display_name,
                is_opted_in=True,
                show_rank=opt_in_data.show_rank,
                show_score=opt_in_data.show_score,
                show_streak=opt_in_data.show_streak
            )
            self.db.add(opt_in)
            await self.db.commit()
            await self.db.refresh(opt_in)
            return opt_in

    async def opt_out(self, user_id: uuid.UUID) -> bool:
        """
        Opt out from leaderboard.

        Args:
            user_id: User UUID

        Returns:
            True if opted out, False if not found
        """
        opt_in = await self.get_opt_in_status(user_id)

        if not opt_in:
            return False

        opt_in.is_opted_in = False
        await self.db.commit()
        return True

    async def update_opt_in(
        self,
        user_id: uuid.UUID,
        update_data: LeaderboardOptInUpdate
    ) -> Optional[LeaderboardOptIn]:
        """
        Update opt-in settings.

        Args:
            user_id: User UUID
            update_data: Fields to update

        Returns:
            Updated opt-in or None if not found
        """
        opt_in = await self.get_opt_in_status(user_id)

        if not opt_in:
            return None

        for key, value in update_data.model_dump(exclude_unset=True).items():
            if hasattr(opt_in, key):
                setattr(opt_in, key, value)

        await self.db.commit()
        await self.db.refresh(opt_in)
        return opt_in

    async def get_user_rank(self, user_id: uuid.UUID) -> Optional[int]:
        """
        Get user's current rank on leaderboard.

        Args:
            user_id: User UUID

        Returns:
            User's rank or None if not opted in
        """
        opt_in = await self.get_opt_in_status(user_id)

        if not opt_in or not opt_in.is_opted_in:
            return None

        leaderboard = await self.get_leaderboard(limit=1000)  # Get all to find rank

        for entry in leaderboard.leaderboard:
            if entry.user_id == user_id:
                return entry.rank

        return None

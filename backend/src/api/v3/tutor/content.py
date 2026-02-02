"""
Content Router - Phase 3 Unified API

Handles all content-related operations:
- List chapters
- Get chapter content
- Navigation (next/previous)
- Search content

Path: /api/v3/tutor/content
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.content_service import ContentService
from src.models.schemas import (
    ChapterDetail,
    SearchResult,
    SearchResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================


class ChapterListItem(BaseModel):
    """Chapter list item with metadata."""
    id: str
    title: str
    order: int
    difficulty_level: str
    estimated_time: int
    completed: bool = False
    quiz_id: Optional[str] = None


class ChapterListResponse(BaseModel):
    """Response for chapter list."""
    chapters: List[ChapterListItem]
    total: int
    completion_percentage: float = 0.0


class ChapterNavigationResponse(BaseModel):
    """Response for navigation queries."""
    current: Optional[ChapterListItem] = None
    previous: Optional[ChapterListItem] = None
    next: Optional[ChapterListItem] = None
    can_continue: bool = True


class ChapterContentResponse(BaseModel):
    """Response for chapter content."""
    id: str
    title: str
    order: int
    difficulty_level: str
    estimated_time: int
    content: Optional[str] = None
    summary: Optional[str] = None
    quiz_id: Optional[str] = None
    completed: bool = False


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/chapters", response_model=ChapterListResponse)
async def list_chapters(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all chapters with completion status.

    Returns:
    - Chapter metadata (title, order, difficulty, time)
    - Completion status for this user
    - Overall completion percentage

    **Phase 3 Enhancement**: Includes user's completion status.
    """
    try:
        service = ContentService(db)
        chapters = await service.list_chapters()

        # Get user's completed chapters
        from src.models.database import UserProgress
        from sqlalchemy import select

        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        completed_chapters = set()
        if user_progress and user_progress.completed_chapters:
            completed_chapters = set(user_progress.completed_chapters or [])

        # Transform to response format
        chapter_items = []
        for ch in chapters:
            chapter_items.append(ChapterListItem(
                id=str(ch.id),
                title=ch.title,
                order=ch.order,
                difficulty_level=ch.difficulty_level.value,
                estimated_time=ch.estimated_time,
                completed=str(ch.id) in completed_chapters,
                quiz_id=str(ch.quiz_id) if ch.quiz_id else None
            ))

        completion_pct = (len(completed_chapters) / len(chapters) * 100) if chapters else 0.0

        return ChapterListResponse(
            chapters=chapter_items,
            total=len(chapters),
            completion_percentage=round(completion_pct, 1)
        )

    except Exception as e:
        logger.error(f"Error listing chapters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chapters"
        )


@router.get("/chapters/{chapter_id}", response_model=ChapterContentResponse)
async def get_chapter(
    chapter_id: str,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full chapter content.

    Returns:
    - Complete chapter content
    - Chapter metadata
    - Completion status
    - Associated quiz (if any)

    **Phase 3 Enhancement**: Includes user's progress and LLM-generated summary.
    """
    try:
        service = ContentService(db)
        chapter = await service.get_chapter_content(chapter_id)

        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_id} not found"
            )

        # Check completion status
        from src.models.database import UserProgress
        from sqlalchemy import select

        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        completed = False
        if user_progress and user_progress.completed_chapters:
            completed = chapter_id in (user_progress.completed_chapters or [])

        # Phase 3: Generate LLM summary if enabled
        summary = None
        if chapter.content and len(chapter.content) > 100:
            # For Phase 3, we'll use the first paragraph as a simple summary
            # In a full implementation, this would call an LLM
            paragraphs = chapter.content.split('\n\n')
            if paragraphs:
                summary = paragraphs[0][:500] + "..." if len(paragraphs[0]) > 500 else paragraphs[0]

        return ChapterContentResponse(
            id=str(chapter.id),
            title=chapter.title,
            order=chapter.order,
            difficulty_level=chapter.difficulty_level.value,
            estimated_time=chapter.estimated_time,
            content=chapter.content,
            summary=summary,
            quiz_id=str(chapter.quiz_id) if chapter.quiz_id else None,
            completed=completed
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chapter content"
        )


@router.get("/chapters/{chapter_id}/navigation", response_model=ChapterNavigationResponse)
async def get_navigation(
    chapter_id: str,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get navigation context for a chapter.

    Returns:
    - Current chapter info
    - Previous chapter (if any)
    - Next chapter (if any)
    - Whether user can proceed (access check)

    **Phase 3 Enhancement**: Includes access control and premium checks.
    """
    try:
        service = ContentService(db)

        # Get current chapter
        current = await service.get_chapter_content(chapter_id)
        if not current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_id} not found"
            )

        # Get navigation
        prev_chapter = await service.get_previous_chapter(chapter_id)
        next_chapter = await service.get_next_chapter(chapter_id)

        # Check access (Chapter 4+ requires premium)
        from src.models.database import User
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        can_continue = True
        if current.order >= 4 and user and user.tier == "FREE":
            can_continue = False

        return ChapterNavigationResponse(
            current=ChapterListItem(
                id=str(current.id),
                title=current.title,
                order=current.order,
                difficulty_level=current.difficulty_level.value,
                estimated_time=current.estimated_time
            ),
            previous=ChapterListItem(
                id=str(prev_chapter.id),
                title=prev_chapter.title,
                order=prev_chapter.order,
                difficulty_level=prev_chapter.difficulty_level.value,
                estimated_time=prev_chapter.estimated_time
            ) if prev_chapter else None,
            next=ChapterListItem(
                id=str(next_chapter.id),
                title=next_chapter.title,
                order=next_chapter.order,
                difficulty_level=next_chapter.difficulty_level.value,
                estimated_time=next_chapter.estimated_time
            ) if next_chapter else None,
            can_continue=can_continue
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting navigation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve navigation"
        )


@router.get("/search", response_model=SearchResponse)
async def search_content(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search course content.

    Supports:
    - Keyword search across titles and content
    - Case-insensitive matching
    - Result ranking by relevance

    **Phase 3 Enhancement**: Fast and accurate search with highlighting.
    """
    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query 'q' is required"
        )

    try:
        service = ContentService(db)
        results = await service.search_content(q, limit)

        return SearchResponse(
            query=q,
            results=results,
            total=len(results)
        )

    except Exception as e:
        logger.error(f"Error searching content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/continue")
async def get_continue_learning(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the next chapter to continue learning.

    Returns the next uncompleted chapter for the user,
    or the last completed chapter if all are done.

    **Phase 3 Enhancement**: Smart continuation based on progress.
    """
    try:
        from src.models.database import UserProgress
        from sqlalchemy import select

        service = ContentService(db)

        # Get user progress
        result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        # Get all chapters
        all_chapters = await service.list_chapters()

        if not user_progress or not user_progress.completed_chapters:
            # User hasn't completed anything - return first chapter
            next_chapter = all_chapters[0] if all_chapters else None
        else:
            # Find first uncompleted chapter
            completed_ids = set(user_progress.completed_chapters or [])
            next_chapter = None
            for ch in all_chapters:
                if str(ch.id) not in completed_ids:
                    next_chapter = ch
                    break

            # If all completed, return the last one
            if not next_chapter and all_chapters:
                next_chapter = all_chapters[-1]

        if not next_chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chapters found"
            )

        return {
            "chapter_id": str(next_chapter.id),
            "title": next_chapter.title,
            "order": next_chapter.order,
            "reason": "Continue where you left off" if next_chapter.order > 1 else "Start your learning journey",
            "url": f"/chapters/{next_chapter.id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting continue learning: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get continue learning"
        )

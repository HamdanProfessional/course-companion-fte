"""
Content service business logic.
Zero-LLM compliance: Content retrieval only, no LLM generation.
"""

import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.database import Chapter
from src.models.schemas import ChapterDetail, SearchResult
from src.storage.r2_client import r2_client
from src.storage.cache import cache


class ContentService:
    """Business logic for content delivery and search."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_chapter_content(self, chapter_id: str) -> Optional[ChapterDetail]:
        """
        Get full chapter content from database or R2.

        Args:
            chapter_id: Chapter UUID

        Returns:
            ChapterDetail with content, or None if not found
        """
        # Check cache first
        cache_key = f"chapter:{chapter_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Query database
        result = await self.db.execute(
            select(Chapter)
            .options(selectinload(Chapter.quiz))
            .where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one_or_none()

        if not chapter:
            return None

        # If content is in R2, fetch it
        content = chapter.content
        if chapter.r2_content_key:
            r2_content = r2_client.get_object(chapter.r2_content_key)
            if r2_content:
                content = r2_content

        # Build response
        chapter_detail = ChapterDetail(
            id=str(chapter.id),
            title=chapter.title,
            content=content,
            order=chapter.order,
            difficulty_level=chapter.difficulty_level.upper(),  # Normalize to uppercase
            estimated_time=chapter.estimated_time,
            r2_content_key=chapter.r2_content_key,
            quiz_id=str(chapter.quiz.id) if chapter.quiz else None,
        )

        # Cache for 5 minutes
        cache.set(cache_key, chapter_detail, ttl=300)

        return chapter_detail

    async def list_chapters(self) -> List[ChapterDetail]:
        """
        List all chapters (metadata only, no full content).

        Returns:
            List of chapters
        """
        cache_key = "chapters:all"
        cached = cache.get(cache_key)
        if cached:
            return cached

        result = await self.db.execute(
            select(Chapter)
            .order_by(Chapter.order)
        )
        chapters = result.scalars().all()

        chapter_list = []
        for chapter in chapters:
            # Debug print to stdout
            print(f"DEBUG: Processing chapter '{chapter.title}'")
            print(f"DEBUG: chapter.difficulty_level = {repr(chapter.difficulty_level)}")
            print(f"DEBUG: type = {type(chapter.difficulty_level)}")
            print(f"DEBUG: .upper() = {repr(chapter.difficulty_level.upper())}")
            import sys
            sys.stdout.flush()

            chapter_list.append(ChapterDetail(
                id=str(chapter.id),
                title=chapter.title,
                content=None,  # Exclude content from list view
                order=chapter.order,
                difficulty_level=chapter.difficulty_level.upper(),  # Normalize to uppercase
                estimated_time=chapter.estimated_time,
                r2_content_key=chapter.r2_content_key,
            ))

        # Cache for 5 minutes
        cache.set(cache_key, chapter_list, ttl=300)

        return chapter_list

    async def get_next_chapter(self, chapter_id: str) -> Optional[ChapterDetail]:
        """
        Get next chapter in sequence.

        Args:
            chapter_id: Current chapter UUID

        Returns:
            Next chapter or None if last chapter
        """
        # Get current chapter
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        current = result.scalar_one_or_none()
        if not current or not current.next_chapter_id:
            return None

        # Return next chapter (metadata only)
        return await self.get_chapter_content(str(current.next_chapter_id))

    async def get_previous_chapter(self, chapter_id: str) -> Optional[ChapterDetail]:
        """
        Get previous chapter in sequence.

        Args:
            chapter_id: Current chapter UUID

        Returns:
            Previous chapter or None if first chapter
        """
        # Get current chapter
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        current = result.scalar_one_or_none()
        if not current or not current.previous_chapter_id:
            return None

        # Return previous chapter (metadata only)
        return await self.get_chapter_content(str(current.previous_chapter_id))

    async def search_content(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search course content using keyword matching.
        Zero-LLM: Pre-computed search only, no real-time embedding generation.

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of search results with relevance scores
        """
        # Normalize query
        query_lower = query.lower().strip()
        if not query_lower:
            return []

        # Get all chapters with content
        chapters = await self.list_chapters()
        results = []

        for chapter in chapters:
            # Get full content for searching
            chapter_detail = await self.get_chapter_content(str(chapter.id))
            if not chapter_detail or not chapter_detail.content:
                continue

            content_lower = chapter_detail.content.lower()
            title_lower = chapter_detail.title.lower()

            # Keyword matching (simple algorithm, no LLM)
            relevance_score = 0.0

            # Exact phrase match in title
            if query_lower in title_lower:
                relevance_score = 1.0
            # Exact phrase match in content
            elif query_lower in content_lower:
                # Count occurrences for scoring
                count = content_lower.count(query_lower)
                relevance_score = min(0.8, 0.3 + (count * 0.1))
            # Word-level matching
            else:
                query_words = set(query_lower.split())
                content_words = set(content_lower.split())
                matches = query_words & content_words
                if matches:
                    relevance_score = min(0.5, len(matches) / len(query_words) * 0.4)

            # Extract snippet (first occurrence)
            snippet = ""
            if query_lower in content_lower:
                idx = content_lower.find(query_lower)
                start = max(0, idx - 100)
                end = min(len(content_lower), idx + len(query_lower) + 100)
                snippet = "..." + content_lower[start:end] + "..."
                # Highlight the match
                snippet = snippet.replace(query_lower, f"**{query}**")

            if relevance_score > 0:
                results.append(SearchResult(
                    chapter_id=chapter_detail.id,
                    title=chapter_detail.title,
                    snippet=snippet,
                    relevance_score=relevance_score
                ))

        # Sort by relevance and limit
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:limit]

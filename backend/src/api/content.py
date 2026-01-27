"""
Content API endpoints.
Zero-LLM compliance: Serve content verbatim, no generation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.content_service import ContentService
from src.models.schemas import (
    ChapterDetail,
    ChapterList,
    SearchResult,
    SearchResponse,
)

router = APIRouter()


@router.get("/chapters", response_model=List[ChapterDetail], tags=["Content"])
async def list_chapters(
    db: AsyncSession = Depends(get_db)
):
    """
    List all chapters (metadata only).
    Zero-LLM: Returns verbatim chapter list from database.
    """
    service = ContentService(db)
    chapters = await service.list_chapters()
    return chapters


@router.get("/chapters/{chapter_id}", response_model=ChapterDetail, tags=["Content"])
async def get_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get full chapter content.
    Zero-LLM: Returns verbatim content from database or R2.
    """
    service = ContentService(db)
    chapter = await service.get_chapter_content(chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )

    return chapter


@router.get("/chapters/{chapter_id}/next", response_model=ChapterDetail, tags=["Content"])
async def get_next_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get next chapter in sequence.
    Zero-LLM: Returns next chapter or null if last chapter.
    """
    service = ContentService(db)
    next_chapter = await service.get_next_chapter(chapter_id)

    if not next_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No next chapter (end of course)"
        )

    return next_chapter


@router.get("/chapters/{chapter_id}/previous", response_model=ChapterDetail, tags=["Content"])
async def get_previous_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get previous chapter in sequence.
    Zero-LLM: Returns previous chapter or null if first chapter.
    """
    service = ContentService(db)
    previous_chapter = await service.get_previous_chapter(chapter_id)

    if not previous_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No previous chapter (start of course)"
        )

    return previous_chapter


@router.get("/search", response_model=SearchResponse, tags=["Content"])
async def search_content(
    q: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Search course content.
    Zero-LLM: Keyword-based search with pre-computed relevance scores.
    No real-time embedding generation or LLM processing.
    """
    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query 'q' is required"
        )

    service = ContentService(db)
    results = await service.search_content(q, limit)

    return SearchResponse(
        query=q,
        results=results,
        total=len(results)
    )

"""
Q&A API endpoints - Phase 1 Requirement
Zero-LLM compliance: Returns content verbatim, no AI generation.

Provides grounded Q&A by searching and returning relevant content sections.
All AI reasoning happens in ChatGPT; this API only serves content.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.content_service import ContentService
from src.models.schemas import SearchResult

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================


class QAContentSection(BaseModel):
    """Single relevant content section."""
    chapter_id: str
    chapter_title: str
    section_title: Optional[str] = None
    content: str
    relevance_score: float
    context_window: int  # Characters shown before/after match


class QAResponse(BaseModel):
    """Response model for Q&A request."""
    question: str
    answer_type: str = "grounded_content"
    relevant_sections: List[QAContentSection]
    total_sections: int
    did_you_mean: Optional[str] = None


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/ask", response_model=QAResponse, tags=["Q&A"])
async def ask_question(
    question: str = Query(..., description="Question to answer", min_length=2),
    chapter_id: Optional[str] = Query(None, description="Optional: restrict to chapter"),
    max_results: int = Query(5, ge=1, le=10, description="Maximum content sections to return"),
    context_size: int = Query(500, ge=100, le=2000, description="Characters around match"),
    db: AsyncSession = Depends(get_db)
):
    """
    Answer a question by returning relevant content sections.

    **Phase 1 Requirement - Grounded Q&A**
    This endpoint performs a deterministic search and returns content verbatim.
    NO LLM is used - ChatGPT provides the AI reasoning.

    Flow:
    1. Search content using keyword matching (zero-LLM)
    2. Extract relevant sections with context windows
    3. Return content chunks for ChatGPT to synthesize

    Example:
        GET /api/v1/qa/ask?question=what+is+a+neural+network
        GET /api/v1/qa/ask?question=gradient+descent&chapter_id=abc123&max_results=3

    Args:
        question: The student's question
        chapter_id: Optional chapter to search within
        max_results: Maximum number of content sections
        context_size: Characters of context around matches

    Returns:
        QAResponse with relevant content sections
    """
    try:
        service = ContentService(db)

        # Search for relevant content
        if chapter_id:
            # Search within specific chapter
            results = await _search_in_chapter(
                service, chapter_id, question, context_size
            )
        else:
            # Search all chapters
            results = await service.search_content(question, limit=max_results)

        if not results:
            # No results - try spelling suggestions
            suggestion = await _generate_search_suggestion(service, question)
            return QAResponse(
                question=question,
                answer_type="grounded_content",
                relevant_sections=[],
                total_sections=0,
                did_you_mean=suggestion
            )

        # Extract full content sections with context
        sections = []
        for result in results[:max_results]:
            section = await _extract_content_section(
                service, result, context_size
            )
            if section:
                sections.append(section)

        return QAResponse(
            question=question,
            answer_type="grounded_content",
            relevant_sections=sections,
            total_sections=len(sections)
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question"
        )


@router.get("/ask/batch", response_model=List[QAResponse], tags=["Q&A"])
async def ask_questions_batch(
    questions: List[str] = Query(..., description="List of questions"),
    max_results: int = Query(3, ge=1, le=5),
    db: AsyncSession = Depends(get_db)
):
    """
    Answer multiple questions in one request.

    Optimized for ChatGPT apps that need to answer multiple related questions.
    Returns grounded content for each question.

    **Phase 1 Requirement** - Batch processing for efficiency.

    Example:
        GET /api/v1/qa/ask/batch?questions=what+is+ML&questions=how+does+DL+differ

    Args:
        questions: List of questions to answer
        max_results: Results per question

    Returns:
        List of QAResponse, one per question
    """
    try:
        service = ContentService(db)
        responses = []

        for question in questions:
            # Search content
            results = await service.search_content(question, limit=max_results)

            # Extract sections
            sections = []
            for result in results:
                section = await _extract_content_section(service, result, 500)
                if section:
                    sections.append(section)

            responses.append(QAResponse(
                question=question,
                answer_type="grounded_content",
                relevant_sections=sections,
                total_sections=len(sections)
            ))

        return responses

    except Exception as e:
        logger.error(f"Error in batch Q&A: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch questions"
        )


# =============================================================================
# Helper Functions
# =============================================================================


async def _search_in_chapter(
    service: ContentService,
    chapter_id: str,
    question: str,
    context_size: int
) -> List[SearchResult]:
    """Search within a specific chapter."""
    # Get full chapter content
    chapter = await service.get_chapter_content(chapter_id)
    if not chapter or not chapter.content:
        return []

    # Simple keyword search in chapter content
    query_lower = question.lower()
    content_lower = chapter.content.lower()

    # Find best match positions
    positions = []
    pos = 0
    while True:
        pos = content_lower.find(query_lower, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1

    if not positions:
        return []

    # Create search result with highest relevance
    best_pos = positions[0]
    snippet_start = max(0, best_pos - context_size // 2)
    snippet_end = min(len(chapter.content), best_pos + len(question) + context_size // 2)
    snippet = chapter.content[snippet_start:snippet_end]

    return [SearchResult(
        chapter_id=chapter.id,
        title=chapter.title,
        snippet=snippet,
        relevance_score=1.0
    )]


async def _extract_content_section(
    service: ContentService,
    result: SearchResult,
    context_size: int
) -> Optional[QAContentSection]:
    """Extract full content section from search result."""
    try:
        # Get full chapter
        chapter = await service.get_chapter_content(str(result.chapter_id))
        if not chapter or not chapter.content:
            return None

        # Find snippet in full content
        snippet_lower = result.snippet.lower()
        content_lower = chapter.content.lower()

        # Find position of snippet
        pos = content_lower.find(snippet_lower[:100])  # Use first 100 chars to locate
        if pos == -1:
            # Can't find exact position, return snippet as-is
            content = result.snippet
        else:
            # Extract with context window
            start = max(0, pos - context_size)
            end = min(len(chapter.content), pos + len(result.snippet) + context_size)
            content = chapter.content[start:end]

        return QAContentSection(
            chapter_id=str(result.chapter_id),
            chapter_title=result.title,
            section_title=None,  # Could extract section headers if content has them
            content=content,
            relevance_score=result.relevance_score,
            context_window=context_size
        )

    except Exception as e:
        logger.error(f"Error extracting content section: {e}")
        return None


async def _generate_search_suggestion(
    service: ContentService,
    query: str
) -> Optional[str]:
    """Generate search suggestions for misspelled queries."""
    # Simple implementation: suggest alternative keywords
    # In production, could use edit distance or fuzzy matching

    # Get all chapter titles
    chapters = await service.list_chapters()
    titles = [c.title.lower() for c in chapters]

    # Check if query partially matches any title
    query_words = query.lower().split()
    for word in query_words:
        for title in titles:
            if word in title and len(word) > 3:
                return f"Try searching for: {title}"

    return None

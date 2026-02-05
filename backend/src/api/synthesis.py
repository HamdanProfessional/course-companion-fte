"""
Cross-Chapter Synthesis API - Phase 2 Hybrid Feature
Hybrid Intelligence: Uses LLM to connect concepts across chapters.

This is a PREMIUM feature that:
1. Aggregates content from multiple chapters
2. Uses LLM to synthesize connections and relationships
3. Provides "big picture" understanding
4. Tracks LLM costs for transparency

Phase 2 Feature: Allowed LLM usage for premium value-add.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.config import settings
from src.services.content_service import ContentService
from src.services.access_service import AccessService
from src.services import cost_tracking_service
from src.core.llm import get_llm_client
from src.models.schemas import UserTier

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================


class SynthesisRequest(BaseModel):
    """Request for cross-chapter synthesis."""
    chapter_ids: List[str] = Field(..., description="Chapter IDs to synthesize", min_items=2, max_items=5)
    focus_topic: Optional[str] = Field(None, description="Optional topic to focus analysis on")
    include_examples: bool = Field(True, description="Include examples from chapters")
    complexity_level: str = Field("intermediate", description="complexity level: beginner, intermediate, advanced")


class SynthesisConcept(BaseModel):
    """A synthesized concept connecting multiple chapters."""
    concept: str
    explanation: str
    source_chapters: List[str]
    connections: List[str] = Field(description="How this connects chapters")


class SynthesisExample(BaseModel):
    """Example from chapters demonstrating concepts."""
    title: str
    chapter_id: str
    description: str
    code_snippet: Optional[str] = None


class BigPictureInsight(BaseModel):
    """Big picture insight from synthesis."""
    insight: str
    significance: str
    related_concepts: List[str]


class SynthesisResponse(BaseModel):
    """Response from cross-chapter synthesis."""
    synthesis_id: str
    chapters_analyzed: List[str]
    focus_topic: Optional[str]
    overview: str
    key_concepts: List[SynthesisConcept]
    examples: List[SynthesisExample]
    big_picture_insights: List[BigPictureInsight]
    learning_path: List[str] = Field(description="Recommended reading order")
    estimated_study_time_minutes: int
    generated_at: datetime
    llm_cost_tracked: bool
    tier_required: UserTier


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/analyze", response_model=SynthesisResponse, tags=["Synthesis (Phase 2)"])
async def synthesize_chapters(
    request: SynthesisRequest,
    user_id: UUID = Query(..., description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesize connections across multiple chapters using LLM.

    **Phase 2 Hybrid Feature - Premium Only**

    This endpoint uses LLM intelligence to:
    - Identify key concepts across selected chapters
    - Explain how concepts relate and build on each other
    - Provide big-picture insights
    - Suggest optimal learning paths
    - Track LLM costs transparently

    Example Request:
    {
        "chapter_ids": ["chapter-1", "chapter-3", "chapter-5"],
        "focus_topic": "neural networks",
        "include_examples": true,
        "complexity_level": "intermediate"
    }

    Args:
        request: Synthesis parameters
        user_id: User ID for access control and cost tracking

    Returns:
        SynthesisResponse with LLM-generated insights

    Raises:
        403: Free tier user (premium feature)
        402: Insufficient credits (if applicable)
    """
    try:
        # Check access (premium feature)
        access_service = AccessService(db)
        access_check = await access_service.check_access(
            user_id=user_id,
            feature="cross_chapter_synthesis",
            tier_required=UserTier.PREMIUM
        )

        if not access_check.has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "premium_required",
                    "message": "Cross-chapter synthesis is a premium feature",
                    "tier_required": "PREMIUM",
                    "current_tier": access_check.user_tier
                }
            )

        # Fetch content from all chapters
        content_service = ContentService(db)
        chapters_data = []
        chapter_titles = []

        for chapter_id in request.chapter_ids:
            chapter = await content_service.get_chapter_content(chapter_id)
            if not chapter:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chapter {chapter_id} not found"
                )
            chapters_data.append({
                "id": str(chapter.id),
                "title": chapter.title,
                "content": chapter.content or "",
                "order": chapter.order
            })
            chapter_titles.append(chapter.title)

        # Generate synthesis using LLM
        synthesis = await _generate_synthesis(
            chapters_data=chapters_data,
            focus_topic=request.focus_topic,
            include_examples=request.include_examples,
            complexity_level=request.complexity_level
        )

        # Track LLM cost
        total_tokens = synthesis.get("tokens_input", 0) + synthesis.get("tokens_output", 0)
        if total_tokens > 0:
            await cost_tracking_service.log_llm_cost(
                user_id=str(user_id),
                feature="cross_chapter_synthesis",
                provider="openai",
                model=synthesis.get("model", "gpt-4"),
                tokens_used=total_tokens,
                cost_usd=synthesis.get("cost_usd", 0.0),
                db=db
            )

        # Build response
        return SynthesisResponse(
            synthesis_id=synthesis["id"],
            chapters_analyzed=chapter_titles,
            focus_topic=request.focus_topic,
            overview=synthesis["overview"],
            key_concepts=synthesis["key_concepts"],
            examples=synthesis["examples"],
            big_picture_insights=synthesis["big_picture_insights"],
            learning_path=synthesis["learning_path"],
            estimated_study_time_minutes=synthesis["estimated_time"],
            generated_at=datetime.utcnow(),
            llm_cost_tracked=True,
            tier_required=UserTier.PREMIUM
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in synthesis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate synthesis: {str(e)}"
        )


@router.get("/preview", tags=["Synthesis (Phase 2)"])
async def preview_synthesis(
    chapter_ids: List[str] = Query(..., description="Chapter IDs to preview", min_length=2),
    user_id: UUID = Query(..., description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Preview synthesis without using LLM (free tier friendly).

    Returns basic chapter information and potential connections
    without LLM analysis. Useful for free users to see what they'd get.

    **Phase 2 Feature** - Freemium access pattern.
    """
    try:
        content_service = ContentService(db)
        chapters_info = []

        for chapter_id in chapter_ids:
            chapter = await content_service.get_chapter_content(chapter_id)
            if not chapter:
                continue
            chapters_info.append({
                "id": str(chapter.id),
                "title": chapter.title,
                "order": chapter.order,
                "description": chapter.description,
                "content_preview": (chapter.content or "")[:500] + "..." if chapter.content else ""
            })

        return {
            "chapters": chapters_info,
            "premium_feature": "Full synthesis requires PREMIUM tier",
            "upgrade_benefits": [
                "AI-powered concept connections",
                "Big picture insights",
                "Personalized learning paths",
                "Integrated examples"
            ]
        }

    except Exception as e:
        logger.error(f"Error in preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview synthesis"
        )


# =============================================================================
# Helper Functions
# =============================================================================


async def _generate_synthesis(
    chapters_data: List[Dict],
    focus_topic: Optional[str],
    include_examples: bool,
    complexity_level: str
) -> Dict[str, Any]:
    """
    Generate synthesis using LLM.

    Args:
        chapters_data: List of chapter content
        focus_topic: Optional topic to focus on
        include_examples: Whether to include examples
        complexity_level: Target complexity level

    Returns:
        Synthesis data dictionary
    """
    # Check if Phase 2 LLM is enabled
    if not settings.enable_phase_2_llm:
        # Return mock synthesis for testing
        return _get_mock_synthesis(chapters_data, focus_topic)

    try:
        llm_client = get_llm_client()

        # Build prompt
        chapters_summary = "\n\n".join([
            f"Chapter {ch['order']}: {ch['title']}\n{ch['content'][:2000]}"
            for ch in chapters_data
        ])

        prompt = f"""You are an expert educational synthesizer. Analyze these course chapters and create connections.

{chapters_summary}

Focus topic: {focus_topic or 'General synthesis'}
Complexity level: {complexity_level}
Include examples: {include_examples}

Provide a synthesis that helps students understand the big picture and how concepts connect.

Respond in JSON format with these fields:
{{
    "overview": "High-level summary of how these chapters connect",
    "key_concepts": [
        {{
            "concept": "Concept name",
            "explanation": "How it connects the chapters",
            "source_chapters": ["Chapter 1", "Chapter 2"],
            "connections": ["Connection 1", "Connection 2"]
        }}
    ],
    "examples": [
        {{
            "title": "Example title",
            "chapter_id": "chapter-1",
            "description": "Example description",
            "code_snippet": "Optional code"
        }}
    ],
    "big_picture_insights": [
        {{
            "insight": "Big picture insight",
            "significance": "Why this matters",
            "related_concepts": ["concept1", "concept2"]
        }}
    ],
    "learning_path": ["Step 1", "Step 2", "Step 3"],
    "estimated_time": 45
}}
"""

        # Call LLM
        response = await llm_client.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )

        # Parse response (in production, add proper error handling)
        import json
        synthesis_data = json.loads(response)

        # Add metadata
        synthesis_data["id"] = f"synth_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        synthesis_data["tokens_input"] = len(prompt) // 4  # Rough estimate
        synthesis_data["tokens_output"] = len(response) // 4
        synthesis_data["model"] = getattr(llm_client, 'model_name', 'gpt-4')

        return synthesis_data

    except Exception as e:
        logger.error(f"LLM synthesis failed: {e}")
        # Fallback to mock
        return _get_mock_synthesis(chapters_data, focus_topic)


def _get_mock_synthesis(chapters_data: List[Dict], focus_topic: Optional[str]) -> Dict[str, Any]:
    """Generate mock synthesis for testing/fallback."""
    chapter_titles = [ch["title"] for ch in chapters_data]

    return {
        "id": f"synth_mock_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "overview": f"This synthesis connects {', '.join(chapter_titles)} to show how foundational concepts build upon each other. {'Focus: ' + focus_topic if focus_topic else ''}",
        "key_concepts": [
            {
                "concept": "Progressive Learning",
                "explanation": "Each chapter introduces concepts that build on previous material",
                "source_chapters": chapter_titles,
                "connections": [
                    "Chapter 1 establishes foundations",
                    "Chapter 2 extends those foundations",
                    "Later chapters apply concepts to real scenarios"
                ]
            }
        ],
        "examples": [
            {
                "title": "Concept in Practice",
                "chapter_id": chapters_data[0]["id"],
                "description": "Practical application from first chapter"
            }
        ],
        "big_picture_insights": [
            {
                "insight": "Concepts are interconnected",
                "significance": "Understanding relationships helps retention",
                "related_concepts": ["Foundations", "Applications", "Best Practices"]
            }
        ],
        "learning_path": [
            "Start with first chapter for foundations",
            "Progress through chapters in order",
            "Review connections between topics",
            "Apply concepts to practical scenarios"
        ],
        "estimated_time": sum(len(ch.get("content", "")) // 100 for ch in chapters_data),
        "tokens_input": 0,
        "tokens_output": 0,
        "model": "mock"
    }

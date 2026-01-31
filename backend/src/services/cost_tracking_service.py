"""
Cost Tracking Service - Phase 2 LLM Features.

Tracks all LLM API costs for Phase 2 features.
Logs every LLM call with user_id, feature, tokens_used, and cost_usd.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.database import LLMCost, User
from src.core.config import settings
from src.core.llm import get_llm_client, LLMClient

logger = logging.getLogger(__name__)


class CostTrackingError(Exception):
    """Base exception for cost tracking errors."""
    pass


class LLMProviderPricing:
    """Pricing information for LLM providers (per 1M tokens)."""

    # OpenAI pricing (as of 2026)
    OPENAI_PRICING = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},  # $ per 1M tokens
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    # Anthropic pricing (as of 2026)
    ANTHROPIC_PRICING = {
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    }


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate LLM API cost in USD.

    Args:
        provider: LLM provider ("openai" or "anthropic")
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD

    Raises:
        CostTrackingError: If pricing not found
    """
    if provider == "openai":
        pricing = LLMProviderPricing.OPENAI_PRICING.get(model)
    elif provider == "anthropic":
        pricing = LLMProviderPricing.ANTHROPIC_PRICING.get(model)
    else:
        raise CostTrackingError(f"Unknown provider: {provider}")

    if not pricing:
        raise CostTrackingError(f"Pricing not found for {provider}/{model}")

    # Calculate cost (pricing is per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return round(total_cost, 6)  # Round to 6 decimal places (~microdollars)


async def log_llm_cost(
    user_id: str,
    feature: str,
    provider: str,
    model: str,
    tokens_used: int,
    cost_usd: float,
    db: AsyncSession
) -> LLMCost:
    """
    Log an LLM API call to the database.

    Args:
        user_id: User UUID
        feature: Feature name ("adaptive", "quiz_llm", "mentor")
        provider: LLM provider ("openai" or "anthropic")
        model: Model name
        tokens_used: Total tokens used
        cost_usd: Cost in USD
        db: Database session

    Returns:
        Created LLMCost record
    """
    try:
        cost_record = LLMCost(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            feature=feature,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            timestamp=datetime.utcnow()
        )

        db.add(cost_record)
        await db.commit()

        logger.info(
            f"Logged LLM cost: user={user_id}, feature={feature}, "
            f"model={model}, tokens={tokens_used}, cost=${cost_usd:.6f}"
        )

        return cost_record

    except Exception as e:
        logger.error(f"Failed to log LLM cost: {e}")
        await db.rollback()
        raise CostTrackingError(f"Failed to log cost: {e}")


async def get_user_costs(
    user_id: str,
    db: AsyncSession,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get LLM costs for a specific user.

    Args:
        user_id: User UUID
        db: Database session
        days: Number of days to look back (default: 30)

    Returns:
        Cost summary with breakdown by feature
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(LLMCost)
            .where(LLMCost.user_id == uuid.UUID(user_id))
            .where(LLMCost.timestamp >= since_date)
            .order_by(LLMCost.timestamp.desc())
        )
        costs = result.scalars().all()

        # Calculate totals
        total_cost = sum(c.cost_usd for c in costs)
        total_tokens = sum(c.tokens_used for c in costs)
        call_count = len(costs)

        # Break down by feature
        feature_breakdown = {}
        for cost in costs:
            if cost.feature not in feature_breakdown:
                feature_breakdown[cost.feature] = {
                    "cost": 0.0,
                    "tokens": 0,
                    "calls": 0
                }
            feature_breakdown[cost.feature]["cost"] += cost.cost_usd
            feature_breakdown[cost.feature]["tokens"] += cost.tokens_used
            feature_breakdown[cost.feature]["calls"] += 1

        return {
            "user_id": user_id,
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_calls": call_count,
            "feature_breakdown": {
                k: {
                    "cost_usd": round(v["cost"], 4),
                    "tokens": v["tokens"],
                    "calls": v["calls"]
                }
                for k, v in feature_breakdown.items()
            }
        }

    except Exception as e:
        logger.error(f"Failed to get user costs: {e}")
        raise CostTrackingError(f"Failed to retrieve costs: {e}")


async def get_total_costs(
    db: AsyncSession,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get total LLM costs across all users.

    Args:
        db: Database session
        days: Number of days to look back (default: 30)

    Returns:
        Total cost summary
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(LLMCost)
            .where(LLMCost.timestamp >= since_date)
        )
        costs = result.scalars().all()

        total_cost = sum(c.cost_usd for c in costs)
        total_tokens = sum(c.tokens_used for c in costs)
        call_count = len(costs)

        # Count unique users
        unique_users = len(set(c.user_id for c in costs))

        # Break down by feature
        feature_breakdown = {}
        for cost in costs:
            if cost.feature not in feature_breakdown:
                feature_breakdown[cost.feature] = {
                    "cost": 0.0,
                    "tokens": 0,
                    "calls": 0
                }
            feature_breakdown[cost.feature]["cost"] += cost.cost_usd
            feature_breakdown[cost.feature]["tokens"] += cost.tokens_used
            feature_breakdown[cost.feature]["calls"] += 1

        return {
            "period_days": days,
            "total_cost_usd": round(total_cost, 2),
            "total_tokens": total_tokens,
            "total_calls": call_count,
            "unique_users": unique_users,
            "average_cost_per_user": round(total_cost / unique_users, 4) if unique_users > 0 else 0,
            "feature_breakdown": {
                k: {
                    "cost_usd": round(v["cost"], 2),
                    "tokens": v["tokens"],
                    "calls": v["calls"]
                }
                for k, v in feature_breakdown.items()
            }
        }

    except Exception as e:
        logger.error(f"Failed to get total costs: {e}")
        raise CostTrackingError(f"Failed to retrieve total costs: {e}")


async def get_top_users(
    db: AsyncSession,
    days: int = 30,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get top users by LLM usage.

    Args:
        db: Database session
        days: Number of days to look back (default: 30)
        limit: Maximum number of users to return (default: 10)

    Returns:
        List of top users with cost summaries
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)

        # Query costs grouped by user
        result = await db.execute(
            select(
                LLMCost.user_id,
                func.sum(LLMCost.cost_usd).label("total_cost"),
                func.sum(LLMCost.tokens_used).label("total_tokens"),
                func.count(LLMCost.id).label("call_count")
            )
            .where(LLMCost.timestamp >= since_date)
            .group_by(LLMCost.user_id)
            .order_by(func.sum(LLMCost.cost_usd).desc())
            .limit(limit)
        )

        top_users = []
        for row in result:
            top_users.append({
                "user_id": str(row.user_id),
                "total_cost_usd": round(row.total_cost, 4),
                "total_tokens": row.total_tokens,
                "call_count": row.call_count
            })

        return top_users

    except Exception as e:
        logger.error(f"Failed to get top users: {e}")
        raise CostTrackingError(f"Failed to retrieve top users: {e}")


class CostTrackingLLMClient:
    """
    Wrapper around LLMClient that automatically tracks costs.

    Usage:
        client = CostTrackingLLMClient(user_id, "adaptive", db)
        response = await client.generate("...")
        # Cost is automatically logged
    """

    def __init__(
        self,
        user_id: str,
        feature: str,
        db: AsyncSession,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize cost-tracking LLM client wrapper.

        Args:
            user_id: User UUID
            feature: Feature name ("adaptive", "quiz_llm", "mentor")
            db: Database session
            llm_client: Optional pre-configured LLM client
        """
        self.user_id = user_id
        self.feature = feature
        self.db = db
        self.llm_client = llm_client or get_llm_client()

        if not self.llm_client:
            raise CostTrackingError("LLM client not available. Phase 2 may be disabled.")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion and automatically track cost.

        Note: This is an estimated cost based on token count.
        Actual API cost may vary slightly.
        """
        # Generate response
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Estimate tokens (rough approximation: ~4 chars per token)
        input_tokens = len(prompt) // 4
        if system_prompt:
            input_tokens += len(system_prompt) // 4
        output_tokens = len(response) // 4
        total_tokens = input_tokens + output_tokens

        # Calculate cost
        provider = self.llm_client.provider.value
        model = self.llm_client.model
        cost = calculate_cost(provider, model, input_tokens, output_tokens)

        # Log cost
        await log_llm_cost(
            user_id=self.user_id,
            feature=self.feature,
            provider=provider,
            model=model,
            tokens_used=total_tokens,
            cost_usd=cost,
            db=self.db
        )

        return response


def get_cost_tracking_client(
    user_id: str,
    feature: str,
    db: AsyncSession
) -> Optional[CostTrackingLLMClient]:
    """
    Get or create a cost-tracking LLM client.

    Returns None if Phase 2 LLM features are disabled.

    Args:
        user_id: User UUID
        feature: Feature name ("adaptive", "quiz_llm", "mentor")
        db: Database session

    Returns:
        CostTrackingLLMClient or None
    """
    if not settings.enable_phase_2_llm:
        return None

    try:
        return CostTrackingLLMClient(user_id, feature, db)
    except CostTrackingError:
        return None

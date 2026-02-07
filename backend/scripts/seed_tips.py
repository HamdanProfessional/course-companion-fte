"""
Seed Tips Database - Pre-written learning tips.

Zero-Backend-LLM: All tips are pre-written content.
Run this script to populate the tips table.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Tip
from src.core.config import settings

# Pre-written tips organized by category
TIPS_DATA = [
    # Study Habits (4 tips)
    {
        "content": "Study in focused 25-minute sessions with 5-minute breaks (Pomodoro Technique) to maintain peak concentration and avoid burnout.",
        "category": "study_habits",
        "difficulty_level": None
    },
    {
        "content": "Review previous chapters before starting new ones. Spaced repetition helps transfer knowledge from short-term to long-term memory.",
        "category": "study_habits",
        "difficulty_level": None
    },
    {
        "content": "Take handwritten notes while reading chapters. The physical act of writing helps your brain process and retain information better.",
        "category": "study_habits",
        "difficulty_level": None
    },
    {
        "content": "Set a consistent study schedule. Learning at the same time each day trains your brain to be focused during those hours.",
        "category": "study_habits",
        "difficulty_level": None
    },

    # Quiz Strategy (4 tips)
    {
        "content": "Read each question carefully twice before answering. Many mistakes come from misreading rather than not knowing the answer.",
        "category": "quiz_strategy",
        "difficulty_level": None
    },
    {
        "content": "If you're unsure, eliminate obviously wrong answers first. This increases your chances even if you have to guess.",
        "category": "quiz_strategy",
        "difficulty_level": None
    },
    {
        "content": "Review quiz explanations after submission, even for correct answers. Understanding WHY an answer is correct deepens your learning.",
        "category": "quiz_strategy",
        "difficulty_level": None
    },
    {
        "content": "Take practice quizzes without time pressure first to build understanding, then add time limits to simulate real conditions.",
        "category": "quiz_strategy",
        "difficulty_level": None
    },

    # Motivation (4 tips)
    {
        "content": "Remember: Every expert was once a beginner. Your current struggle is just a stepping stone to mastery.",
        "category": "motivation",
        "difficulty_level": None
    },
    {
        "content": "Consistency beats intensity. Studying 30 minutes daily is more effective than cramming for 5 hours once a week.",
        "category": "motivation",
        "difficulty_level": None
    },
    {
        "content": "Celebrate small wins! Completing a chapter or improving your quiz score by 5% are real achievements worth acknowledging.",
        "category": "motivation",
        "difficulty_level": None
    },
    {
        "content": "Your learning journey is unique. Don't compare your pace to others—focus on your own progress and growth.",
        "category": "motivation",
        "difficulty_level": None
    },

    # Course Tips (4 tips)
    {
        "content": "AI Agents are all about defining clear tasks and tools. When building an agent, start by defining what problem it solves.",
        "category": "course_tips",
        "difficulty_level": "beginner"
    },
    {
        "content": "MCP (Model Context Protocol) enables agents to access external tools. Think of it as a universal adapter for AI capabilities.",
        "category": "course_tips",
        "difficulty_level": "beginner"
    },
    {
        "content": "Skills are reusable capabilities. Design your skills to be modular—they can be combined and reused across different agents.",
        "category": "course_tips",
        "difficulty_level": "intermediate"
    },
    {
        "content": "Error handling in agents is crucial. Always include fallback behavior when tools fail or return unexpected results.",
        "category": "course_tips",
        "difficulty_level": "advanced"
    }
]


async def seed_tips():
    """Seed the tips table with pre-written learning tips."""

    # Create async engine
    engine = create_async_engine(settings.database_url)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("Starting tips seed...")

        # Clear existing tips (optional, comment out if you want to keep existing)
        # from sqlalchemy import delete
        # await session.execute(delete(Tip))
        # await session.commit()
        # print("Cleared existing tips")

        # Add tips
        added_count = 0
        for tip_data in TIPS_DATA:
            tip = Tip(**tip_data)
            session.add(tip)
            added_count += 1

        # Commit
        await session.commit()

        print(f"Successfully added {added_count} tips to the database!")
        print("\nTip breakdown:")
        from collections import Counter
        categories = [t["category"] for t in TIPS_DATA]
        for category, count in Counter(categories).items():
            print(f"  - {category}: {count} tips")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_tips())

"""
Course Companion FTE - MCP Server for ChatGPT
Uses FastMCP to provide tools and resources to ChatGPT Apps
"""

import logging
import os
from typing import Dict, List, Any, Optional
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8180")

# Server instructions for ChatGPT
server_instructions = """
This MCP server provides course content, quizzes, and progress tracking for the Course Companion FTE AI Agent Development course.

Available tools:
- search: Search course content by keywords
- fetch: Get full chapter content by ID
- list_chapters: Get all available chapters
- get_quiz: Get quiz questions
- submit_quiz: Submit quiz answers for grading
- get_progress: Get user learning progress
- update_progress: Mark chapter as complete
- get_streak: Get user streak information
- check_access: Check content access (freemium model)

Use search to find relevant content, then fetch to get complete details.
"""

# Import backend services
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.services.content_service import ContentService
from src.services.quiz_service import QuizService
from src.services.progress_service import ProgressService
from src.services.access_service import AccessService
from src.core.database import async_session_maker


def create_mcp_server():
    """Create and configure the FastMCP server with course companion tools."""

    # Initialize the FastMCP server
    mcp = FastMCP(
        name="Course Companion FTE",
        instructions=server_instructions
    )

    # Helper function to get services with fresh session
    async def get_services():
        """Create services with a fresh database session."""
        async with async_session_maker() as db:
            content_service = ContentService(db)
            quiz_service = QuizService(db)
            progress_service = ProgressService(db)
            access_service = AccessService(db)
            return content_service, quiz_service, progress_service, access_service, db

    @mcp.tool()
    async def search(query: str) -> Dict[str, Any]:
        """
        Search course content for relevant topics.

        Use this tool to find chapters and content related to specific keywords.
        Returns a list of matching chapters with their IDs and titles.

        Args:
            query: Search query string (keywords, topics, concepts)

        Returns:
            Dictionary with 'results' key containing list of matching chapters.
            Each result includes id, title, difficulty_level, and order.
        """
        if not query or not query.strip():
            return {"results": []}

        logger.info(f"Searching course content for: '{query}'")

        try:
            # Get services with fresh session
            content_service, _, _, _, db = await get_services()

            # Search content using backend service
            results = await content_service.search_content(query, limit=10)

            formatted_results = []
            for chapter in results:
                result = {
                    "id": str(chapter.id),
                    "title": chapter.title,
                    "difficulty_level": chapter.difficulty_level,
                    "order": chapter.order,
                    "estimated_time": chapter.estimated_time
                }
                formatted_results.append(result)

            return {"results": formatted_results}

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {"results": []}

    @mcp.tool()
    async def fetch(id: str) -> Dict[str, Any]:
        """
        Retrieve complete chapter content by ID.

        Use this tool after finding relevant chapters with the search tool.
        Returns full chapter content including text and metadata.

        Args:
            id: Chapter ID from search results

        Returns:
            Complete chapter with id, title, content, difficulty, order, and metadata

        Raises:
            ValueError: If the specified chapter ID is not found
        """
        if not id:
            raise ValueError("Chapter ID is required")

        logger.info(f"Fetching chapter content for ID: {id}")

        try:
            # Get chapter content from backend service
            chapter = content_service.get_chapter_by_id(id)

            if not chapter:
                raise ValueError(f"Chapter not found: {id}")

            result = {
                "id": str(chapter.id),
                "title": chapter.title,
                "content": chapter.content,
                "difficulty_level": chapter.difficulty_level,
                "order": chapter.order,
                "estimated_time": chapter.estimated_time,
                "quiz_id": str(chapter.quiz_id) if chapter.quiz_id else None,
                "url": f"{BACKEND_API_URL}/api/v1/chapters/{id}"
            }

            return result

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Fetch error: {str(e)}")
            raise ValueError(f"Error fetching chapter: {str(e)}")

    @mcp.tool()
    async def list_chapters() -> Dict[str, Any]:
        """
        Get all available course chapters.

        Returns a complete list of all chapters in the course with their IDs,
        titles, difficulty levels, and order. Use this to get an overview
        of the entire course structure.

        Returns:
            Dictionary with 'results' key containing list of all chapters.
        """
        logger.info("Listing all chapters")

        try:
            chapters = content_service.get_all_chapters()

            formatted_results = []
            for chapter in chapters:
                result = {
                    "id": str(chapter.id),
                    "title": chapter.title,
                    "difficulty_level": chapter.difficulty_level,
                    "order": chapter.order,
                    "estimated_time": chapter.estimated_time,
                    "has_quiz": bool(chapter.quiz_id)
                }
                formatted_results.append(result)

            return {"results": formatted_results}

        except Exception as e:
            logger.error(f"List chapters error: {str(e)}")
            return {"results": []}

    @mcp.tool()
    async def get_quiz(quiz_id: str) -> Dict[str, Any]:
        """
        Get quiz questions by quiz ID.

        Retrieves all questions for a specific quiz along with answer options.

        Args:
            quiz_id: The ID of the quiz to retrieve

        Returns:
            Quiz object with id, questions, and answer options
        """
        if not quiz_id:
            raise ValueError("Quiz ID is required")

        logger.info(f"Getting quiz: {quiz_id}")

        try:
            quiz = quiz_service.get_quiz(quiz_id)

            if not quiz:
                raise ValueError(f"Quiz not found: {quiz_id}")

            return {
                "id": str(quiz.id),
                "chapter_id": str(quiz.chapter_id),
                "questions": quiz.questions
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Get quiz error: {str(e)}")
            raise ValueError(f"Error retrieving quiz: {str(e)}")

    @mcp.tool()
    async def submit_quiz(quiz_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit quiz answers for grading.

        Submits answers for a quiz and returns the graded results with
        correct answers and feedback.

        Args:
            quiz_id: The ID of the quiz
            answers: Dictionary mapping question IDs to selected answers

        Returns:
            Graded quiz with score, correct answers, and feedback
        """
        if not quiz_id:
            raise ValueError("Quiz ID is required")
        if not answers:
            raise ValueError("Answers dictionary is required")

        logger.info(f"Submitting quiz: {quiz_id}")

        try:
            result = quiz_service.submit_quiz_attempt(quiz_id, answers)
            return result

        except Exception as e:
            logger.error(f"Submit quiz error: {str(e)}")
            raise ValueError(f"Error submitting quiz: {str(e)}")

    @mcp.tool()
    async def get_progress(user_id: str) -> Dict[str, Any]:
        """
        Get user learning progress.

        Retrieves completion status, quiz scores, and overall progress
        for a specific user.

        Args:
            user_id: The user's ID

        Returns:
            Progress data including completed chapters, quiz scores, and statistics
        """
        if not user_id:
            raise ValueError("User ID is required")

        logger.info(f"Getting progress for user: {user_id}")

        try:
            progress = progress_service.get_user_progress(user_id)

            return {
                "user_id": user_id,
                "completed_chapters": progress.completed_chapters,
                "quiz_scores": progress.quiz_scores,
                "total_chapters": len(content_service.get_all_chapters())
            }

        except Exception as e:
            logger.error(f"Get progress error: {str(e)}")
            return {"user_id": user_id, "completed_chapters": [], "quiz_scores": {}}

    @mcp.tool()
    async def update_progress(user_id: str, chapter_id: str) -> Dict[str, Any]:
        """
        Mark a chapter as complete for a user.

        Updates the user's progress to mark a specific chapter as completed.

        Args:
            user_id: The user's ID
            chapter_id: The chapter ID to mark as complete

        Returns:
            Updated progress information
        """
        if not user_id:
            raise ValueError("User ID is required")
        if not chapter_id:
            raise ValueError("Chapter ID is required")

        logger.info(f"Updating progress for user {user_id}, chapter {chapter_id}")

        try:
            progress_service.update_progress(user_id, chapter_id)
            return await get_progress(user_id)

        except Exception as e:
            logger.error(f"Update progress error: {str(e)}")
            raise ValueError(f"Error updating progress: {str(e)}")

    @mcp.tool()
    async def get_streak(user_id: str) -> Dict[str, Any]:
        """
        Get user learning streak information.

        Retrieves the user's current streak, consecutive days of learning,
        and streak history.

        Args:
            user_id: The user's ID

        Returns:
            Streak information including current streak and last activity date
        """
        if not user_id:
            raise ValueError("User ID is required")

        logger.info(f"Getting streak for user: {user_id}")

        try:
            streak = progress_service.get_streak(user_id)

            return {
                "user_id": user_id,
                "current_streak": streak.current_streak,
                "last_activity_date": str(streak.last_activity_date) if streak.last_activity_date else None
            }

        except Exception as e:
            logger.error(f"Get streak error: {str(e)}")
            return {"user_id": user_id, "current_streak": 0, "last_activity_date": None}

    @mcp.tool()
    async def check_access(user_id: str, resource: str) -> Dict[str, Any]:
        """
        Check if user can access a specific resource (freemium model).

        Determines if the user has access to premium content based on
        their subscription tier.

        Args:
            user_id: The user's ID
            resource: The resource to check (e.g., 'chapter-4')

        Returns:
            Access information including has_access boolean and tier information
        """
        if not user_id:
            raise ValueError("User ID is required")
        if not resource:
            raise ValueError("Resource identifier is required")

        logger.info(f"Checking access for user {user_id}, resource {resource}")

        try:
            has_access = access_service.check_access(user_id, resource)

            return {
                "user_id": user_id,
                "resource": resource,
                "has_access": has_access
            }

        except Exception as e:
            logger.error(f"Check access error: {str(e)}")
            return {"user_id": user_id, "resource": resource, "has_access": False}

    return mcp


def main():
    """Main function to start the MCP server with SSE transport."""
    logger.info("Starting Course Companion FTE MCP Server")

    # Create the MCP server
    server = create_mcp_server()

    # Configure and start the server
    mcp_port = int(os.environ.get("MCP_PORT", "8000"))
    mcp_host = os.environ.get("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting MCP server on {mcp_host}:{mcp_port}")
    logger.info("Server will be accessible via SSE transport")

    try:
        # Use FastMCP's built-in run method with SSE transport
        server.run(transport="sse", host=mcp_host, port=mcp_port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()

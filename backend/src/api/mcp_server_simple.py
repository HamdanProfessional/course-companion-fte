"""
Course Companion FTE - MCP Server for ChatGPT
Uses FastMCP to provide tools and resources to ChatGPT Apps
Calls existing backend API endpoints (HTTP wrapper approach)
"""

import logging
import os
from typing import Dict, List, Any
import httpx
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


def create_mcp_server():
    """Create and configure the FastMCP server with course companion tools."""

    # Initialize the FastMCP server
    mcp = FastMCP(
        name="Course Companion FTE",
        instructions=server_instructions
    )

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
        """
        if not query or not query.strip():
            return {"results": []}

        logger.info(f"Searching course content for: '{query}'")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/v1/search",
                    params={"query": query, "limit": 10},
                    timeout=10.0
                )
                response.raise_for_status()
                results = response.json()

                formatted_results = []
                for chapter in results:
                    result = {
                        "id": chapter["id"],
                        "title": chapter["title"],
                        "difficulty_level": chapter.get("difficulty_level", "BEGINNER"),
                        "order": chapter.get("order", 0),
                        "estimated_time": chapter.get("estimated_time", 30)
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
        """
        if not id:
            raise ValueError("Chapter ID is required")

        logger.info(f"Fetching chapter content for ID: {id}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/v1/chapters/{id}",
                    timeout=10.0
                )
                response.raise_for_status()
                chapter = response.json()

                return {
                    "id": chapter["id"],
                    "title": chapter["title"],
                    "content": chapter.get("content", ""),
                    "difficulty_level": chapter.get("difficulty_level", "BEGINNER"),
                    "order": chapter.get("order", 0),
                    "estimated_time": chapter.get("estimated_time", 30),
                    "quiz_id": chapter.get("quiz_id"),
                    "url": f"{BACKEND_API_URL}/api/v1/chapters/{id}"
                }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Chapter not found: {id}")
            raise ValueError(f"Error fetching chapter: {str(e)}")
        except Exception as e:
            logger.error(f"Fetch error: {str(e)}")
            raise ValueError(f"Error fetching chapter: {str(e)}")

    @mcp.tool()
    async def list_chapters() -> Dict[str, Any]:
        """
        Get all available course chapters.

        Returns a complete list of all chapters in the course with their IDs,
        titles, difficulty levels, and order.

        Returns:
            Dictionary with 'results' key containing list of all chapters.
        """
        logger.info("Listing all chapters")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/v1/chapters",
                    timeout=10.0
                )
                response.raise_for_status()
                chapters = response.json()

                formatted_results = []
                for chapter in chapters:
                    result = {
                        "id": chapter["id"],
                        "title": chapter["title"],
                        "difficulty_level": chapter.get("difficulty_level", "BEGINNER"),
                        "order": chapter.get("order", 0),
                        "estimated_time": chapter.get("estimated_time", 30),
                        "has_quiz": bool(chapter.get("quiz_id"))
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
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                quiz = response.json()

                return {
                    "id": quiz["id"],
                    "chapter_id": quiz.get("chapter_id"),
                    "questions": quiz.get("questions", [])
                }

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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/submit",
                    json={"answers": answers},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

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
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/v1/progress/{user_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                progress = response.json()

                return {
                    "user_id": user_id,
                    "completed_chapters": progress.get("completed_chapters", []),
                    "quiz_scores": progress.get("quiz_attempts", {})
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
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{BACKEND_API_URL}/api/v1/progress/{user_id}",
                    json={"chapter_id": chapter_id},
                    timeout=10.0
                )
                response.raise_for_status()
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
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_API_URL}/api/v1/streaks/{user_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                streak = response.json()

                return {
                    "user_id": user_id,
                    "current_streak": streak.get("current_streak", 0),
                    "last_activity_date": streak.get("last_activity_date")
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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_API_URL}/api/v1/access/check",
                    json={"user_id": user_id, "resource": resource},
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "user_id": user_id,
                    "resource": resource,
                    "has_access": result.get("has_access", False)
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

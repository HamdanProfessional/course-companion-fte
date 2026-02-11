#!/usr/bin/env python3
"""
Course Companion FTE - MCP Server with SSE Transport
For hosting on web servers (e.g., sse.testservers.online/mcp)

This version uses Server-Sent Events (SSE) transport instead of stdio,
allowing ChatGPT to connect remotely via HTTP.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://92.113.147.250:3505")
WIDGET_DOMAIN = os.getenv("WIDGET_DOMAIN", "92.113.147.250")
WIDGET_FULL_URL = os.getenv("WIDGET_URL", f"http://{WIDGET_DOMAIN}:3505/ui")

# Skill definitions
SKILLS_DIR = Path(".claude/skills")
SKILL_INSTRUCTIONS = {
    "concept-explainer": {
        "name": "Concept Explainer",
        "description": "Explains concepts at learner's level using analogies and examples. Use this when the student asks to 'explain', 'what is', 'how does', 'help me understand'. Breaks down complex topics using:
        - Simple analogies from real-world scenarios
        - Progressive complexity (start simple, add detail)
        - Concrete examples before abstract concepts
        - Check for understanding with simple questions
        - If confused, simplify and try a different analogy",
        "file": "concept-explainer/SKILL.md"
    },
    "quiz-master": {
        "name": "Quiz Master",
        "description": "Conducts quizzes with encouragement and immediate feedback. Use this when students request 'quiz', 'test me', 'practice', 'check my knowledge'. Presents questions, validates answers, provides feedback, and maintains motivation. Always end with positive reinforcement.",
        "file": "quiz-master/SKILL.md"
    },
    "socratic-tutor": {
        "name": "Socratic Tutor",
        "description": "Guides learning through questioning rather than direct answers. Use this when students say 'help me think', 'I'm stuck', 'give me a hint'. Facilitates discovery by asking targeted questions that lead to insight. Never give the answer directly.",
        "file": "socratic-tutor/SKILL.md"
    },
    "progress-motivator": {
        "name": "Progress Motivator",
        "description": "Tracks progress, celebrates achievements, and maintains motivation. Use this when students ask about 'my progress', 'streak', 'how am I doing'. Monitors completion, encourages consistency, and provides positive reinforcement. Highlight specific achievements.",
        "file": "progress-motivator/SKILL.md"
    }
}

# Intent to skill mapping
INTENT_TO_SKILL = {
    "explain": "concept-explainer",
    "what is": "concept-explainer",
    "how does": "concept-explainer",
    "help me understand": "concept-explainer",
    "quiz": "quiz-master",
    "test me": "quiz-master",
    "practice": "quiz-master",
    "check my knowledge": "quiz-master",
    "help me think": "socratic-tutor",
    "i'm stuck": "socratic-tutor",
    "give me a hint": "socratic-tutor",
    "my progress": "progress-motivator",
    "streak": "progress-motivator",
    "how am i doing": "progress-motivator",
}

# Create FastAPI app for SSE endpoint
app = FastAPI(title="Course Companion FTE MCP Server")

# Create MCP server instance
mcp_server = Server("course-companion-fte")


class BackendClient:
    """HTTP client for the remote backend API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get_chapters(self) -> list[Dict[str, Any]]:
        """Get all chapters from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/chapters")
        response.raise_for_status()
        return response.json()

    async def get_chapter(self, chapter_id: str) -> Dict[str, Any]:
        """Get chapter by ID from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/chapters/{chapter_id}")
        response.raise_for_status()
        return response.json()

    async def get_quiz_by_id(self, quiz_id: str) -> Dict[str, Any]:
        """Get quiz by ID from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/quizzes/by-chapter/{quiz_id}")
        response.raise_for_status()
        return response.json()

    async def list_all_quizzes(self) -> list[Dict[str, Any]]:
        """List all available chapters with quizzes (v3 API)."""
        # First get all chapters
        chapters = await self.get_chapters()

        # Filter chapters that have quizzes
        quizzes = []
        for chapter in chapters:
            if chapter.get("has_quiz"):
                quizzes.append({
                    "id": chapter["id"],
                    "title": chapter["title"],
                    "difficulty": chapter.get("difficulty_level", "intermediate"),
                    "order": chapter.get("order", 0)
                })
        return quizzes

    async def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user progress from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/progress/{user_id}")
        response.raise_for_status()
        return response.json()

    async def search_content(self, query: str, limit: int = 5) -> list[Dict[str, Any]]:
        """Search chapters and content by keywords."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/search",
            params={"q": query, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    async def search_content(self, query: str, limit: int = 5) -> list[Dict[str, Any]]:
        """Search course content."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/search",
            params={"q": query, "limit": limit}
        )
        response.raise_for_status()
        return response.json()


def create_widget_response(content: str) -> Dict[str, Any]:
    """
    Create a tool response with widget metadata for ChatGPT.
    """
    return {
        "content": [
            {"type": "text", "text": content}
        ],
        "_meta": {
            "openai/widgetDomain": WIDGET_DOMAIN,
            "openai/widgetUrl": WIDGET_FULL_URL,
            "openai/widgetCSP": {
                "connect_domains": ["https://chatgpt.com", "http://*.testservers.online"],
                "resource_domains": [
                    "https://*.oaistatic.com",
                    f"http://{WIDGET_DOMAIN}:*",
                    "https://*.testservers.online"
                ]
            }
        }
    }


def get_skill_for_intent(user_message: str) -> Optional[str]:
    """
    Detect intent from user message and return appropriate skill.
    """
    user_message_lower = user_message.lower()
    for trigger, skill in INTENT_TO_SKILL.items():
        if trigger in user_message_lower:
            return skill
    return None


async def load_skill_instruction(skill_name: str) -> Dict[str, Any]:
    """
    Load skill instruction from SKILL.md file.
    """
    if skill_name not in SKILL_INSTRUCTIONS:
        return {
            "content": [{"type": "text", "text": f"Skill {skill_name} not found"}],
            "skill_name": skill_name,
            "available_skills": list(SKILL_INSTRUCTIONS.keys())
        }

    skill_info = SKILL_INSTRUCTIONS[skill_name]
    skill_file = SKILLS_DIR / skill_info["file"]

    if not skill_file.exists():
        logger.warning(f"Skill file not found: {skill_file}")

    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "content": [{"type": "text", "text": content}],
            "skill_name": skill_name,
            "skill_description": skill_info["description"],
            "available_skills": list(SKILL_INSTRUCTIONS.keys()),
            "skill_file": str(skill_file)
        }
    except IOError as e:
        logger.error(f"Failed to load skill {skill_name}: {e}")
        return {
            "content": [{"type": "text", "text": f"Failed to load skill {skill_name}: {str(e)}"}],
            "skill_name": skill_name,
            "available_skills": list(SKILL_INSTRUCTIONS.keys())
        }


async def get_skill_for_message(message: str) -> Dict[str, Any]:
    """
    Detect intent from message and return appropriate skill instructions.
    """
    skill_name = get_skill_for_intent(message)

    if not skill_name:
        return {
            "content": [{"type": "text", "text": """
I can help you with several types of educational support:

1. **Concept Explanations** - Explain complex topics using analogies and examples
2. **Quizzes** - Test your knowledge with practice questions
3. **Guided Thinking** - Help you solve problems step-by-step
4. **Progress Tracking** - Show your learning progress and achievements

What would you like to work on?
""" }],
            "available_skills": list(SKILL_INSTRUCTIONS.keys())
        }

    return await load_skill_instruction(skill_name)


async def get_chapter_tool(chapter_id: str) -> Dict[str, Any]:
    """Get chapter content."""
    if not chapter_id:
        raise ValueError("chapter_id is required")

    logger.info(f"Fetching chapter: {chapter_id}")

    async with BackendClient(BACKEND_URL) as backend:
        chapter_data = await backend.get_chapter(chapter_id)
        content = json.dumps(chapter_data, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def list_chapters_tool() -> Dict[str, Any]:
    """List all available chapters."""
    logger.info("Listing chapters")

    async with BackendClient(BACKEND_URL) as backend:
        chapters = await backend.get_chapters()

        result = {
            "chapters": [
                {
                    "id": c.get("id"),
                    "title": c.get("title"),
                    "order": c.get("order"),
                    "difficulty": c.get("difficulty_level", "intermediate"),
                    "has_quiz": c.get("has_quiz", False),
                    "estimated_time": c.get("estimated_time", 30)
                }
                for c in chapters
            ],
            "total": len(chapters)
        }

        content = json.dumps(result, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def get_quiz_tool(chapter_id: str) -> Dict[str, Any]:
    """Get quiz for a chapter and return with widget metadata."""
    if not chapter_id:
        raise ValueError("chapter_id is required")

    logger.info(f"Fetching quiz for chapter: {chapter_id}")

    async with BackendClient(BACKEND_URL) as backend:
        quiz_data = await backend.get_quiz_by_id(chapter_id)
        content = json.dumps(quiz_data, indent=2)
        return create_widget_response(content)


async def list_quizzes_tool() -> Dict[str, Any]:
    """List all available quizzes (by chapter)."""
    logger.info("Listing quizzes")

    async with BackendClient(BACKEND_URL) as backend:
        quizzes = await backend.list_all_quizzes()

        result = {
            "quizzes": quizzes,
            "total": len(quizzes),
            "note": "Each quiz is associated with a chapter. Use the chapter ID to get the full quiz."
        }

        content = json.dumps(result, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def get_progress_tool(user_id: str) -> Dict[str, Any]:
    """Get user progress."""
    if not user_id:
        raise ValueError("user_id is required")

    logger.info(f"Fetching progress for user: {user_id}")

    async with BackendClient(BACKEND_URL) as backend:
        progress_data = await backend.get_progress(user_id)
        content = json.dumps(progress_data, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def search_content_tool(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search course content."""
    logger.info(f"Searching: {query}")

    async with BackendClient(BACKEND_URL) as backend:
        results = await backend.search_content(query, limit)
        content = json.dumps(results, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def get_skill_tool(message: str) -> Dict[str, Any]:
    """
    Get educational skill instructions based on user's message.
    Detects intent and loads the appropriate skill (concept-explainer, quiz-master, socratic-tutor, progress-motivator).
    """
    logger.info(f"Getting skill for message: {message}")

    return await get_skill_for_message(message)


async def list_skills_tool() -> Dict[str, Any]:
    """List all available educational skills."""
    logger.info("Listing available skills")

    skills_info = []
    for skill_name, skill_data in SKILL_INSTRUCTIONS.items():
        skill_file = SKILLS_DIR / skill_data["file"]
        skills_info.append({
            "name": skill_data["name"],
            "description": skill_data["description"],
            "available": skill_file.exists()
        })

    content = json.dumps({
        "skills": skills_info,
        "total": len(skills_info),
        "message": "Use get_skill with your message to activate the appropriate educational support."
    }, indent=2)

    return {"content": [{"type": "text", "text": content}]}


# Register MCP tools
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="list_chapters",
            description="Use this when the student asks to browse course content, see available chapters, or find learning materials. Returns chapter IDs, titles, difficulty levels, and estimated time.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_chapter",
            description="Use this when the student asks to read a chapter, view content, or access learning materials for a specific topic. Returns full chapter content with text, examples, and key concepts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "string",
                        "description": "Chapter ID to get content for (obtained from list_chapters)"
                    }
                },
                "required": ["chapter_id"]
            }
        ),
        Tool(
            name="get_quiz",
            description="Use this when the student asks to take a quiz, practice questions, or test their knowledge. Loads an interactive quiz widget in ChatGPT for immediate practice.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "string",
                        "description": "Chapter ID to get quiz for (obtained from list_chapters or list_quizzes)"
                    }
                },
                "required": ["chapter_id"]
            }
        ),
        Tool(
            name="list_quizzes",
            description="Use this when the student asks what quizzes are available or wants to see practice options. Returns chapter IDs with associated quizzes.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_progress",
            description="Use this when the student asks about their progress, learning stats, completion status, or streak information. Requires user ID from authenticated session.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (UUID format, obtained from authentication)"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="search_content",
            description="Use this when the student asks to find information about a specific topic across all course materials. Searches chapters, examples, and key concepts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query topic (e.g., 'MCP', 'neural networks', 'FastAPI')"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_skill",
            description="Use this when the student needs educational support. Detects intent and loads the appropriate skill (concept-explainer, quiz-master, socratic-tutor, or progress-motivator) to guide the interaction. Pass the student's message to activate the right educational behavior.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Student's message to detect intent and load appropriate skill"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="list_skills",
            description="List all available educational skills and their descriptions. Shows what types of support are available (concept explanations, quizzes, guided thinking, progress tracking).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Any:
    """Handle tool calls."""
    try:
        if name == "list_chapters":
            return await list_chapters_tool()
        elif name == "get_chapter":
            return await get_chapter_tool(**arguments)
        elif name == "get_quiz":
            return await get_quiz_tool(**arguments)
        elif name == "list_quizzes":
            return await list_quizzes_tool()
        elif name == "get_progress":
            return await get_progress_tool(**arguments)
        elif name == "search_content":
            return await search_content_tool(**arguments)
        elif name == "get_skill":
            # Get skill from message
            message = arguments.get("message", "")
            return await get_skill_tool(message)
        elif name == "list_skills":
            return await list_skills_tool()
        else:
            raise ValueError(f"Unknown tool: {name}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return {"content": [{"type": "text", "text": f"API Error: {e.response.status_code} - {str(e)}"}]}
    except Exception as e:
        logger.error(f"Tool error: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "course-companion-fte",
        "transport": "SSE",
        "backend": BACKEND_URL,
        "widget_url": WIDGET_FULL_URL,
        "timestamp": datetime.utcnow().isoformat()
    }


# SSE endpoint for MCP
@app.get("/mcp")
async def mcp_endpoint():
    """
    SSE endpoint for MCP connections.
    ChatGPT will connect to this endpoint for server-sent events transport.
    """
    async def event_stream():
        """Stream events for MCP protocol."""
        logger.info("New SSE connection established")

        # Create SSE transport
        transport = SseServerTransport("/messages")

        # Handle the connection
        async with transport.connect() as streams:
            await mcp_server.run(
                streams[0],
                streams[1],
                mcp_server.create_initialization_options()
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


# Messages endpoint for POST requests from ChatGPT
@app.post("/messages")
async def messages_endpoint(request: dict):
    """
    Handle POST requests to /messages endpoint.
    This is used by ChatGPT to send messages to the MCP server.
    """
    logger.info(f"Received message: {request.get('method', 'unknown')}")

    # Process the message through MCP server
    # Note: This is a simplified version - full implementation would
    # properly handle all MCP protocol messages

    return {"status": "ok"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "Course Companion FTE MCP Server",
        "version": "1.0.0",
        "transport": "SSE (Server-Sent Events)",
        "endpoints": {
            "mcp": "/mcp",
            "messages": "/messages",
            "health": "/health"
        },
        "usage": {
            "chatgpt_config": {
                "sse": f"sse.testservers.online/mcp",
                "transport": "sse"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    logger.info("=" * 60)
    logger.info("Course Companion FTE MCP Server (SSE Transport)")
    logger.info(f"Starting on port {port}...")
    logger.info(f"SSE Endpoint: http://0.0.0.0:{port}/mcp")
    logger.info(f"Backend: {BACKEND_URL}")
    logger.info(f"Widget: {WIDGET_FULL_URL}")
    logger.info("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

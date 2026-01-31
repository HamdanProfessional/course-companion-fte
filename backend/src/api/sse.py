from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
import json
import asyncio
import httpx
from src.core.config import settings

router = APIRouter(tags=["MCP", "SSE"])

# Backend API URL for tool execution
BACKEND_API_URL = "http://localhost:8180"

@router.post("/sse")
async def mcp_post(request: Request):
    """Handle MCP JSON-RPC POST requests from ChatGPT."""
    try:
        data = await request.json()

        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")

        # Handle initialize - MUST return correct MCP format
        if method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "Course Companion FTE",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                },
                "id": req_id
            })

        # Handle tools/list
        elif method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {
                            "name": "list_chapters",
                            "description": "List all available chapters",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "get_chapter",
                            "description": "Get detailed chapter content by ID",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "chapter_id": {
                                        "type": "string",
                                        "description": "Chapter ID"
                                    }
                                },
                                "required": ["chapter_id"]
                            }
                        },
                        {
                            "name": "search_content",
                            "description": "Search course content",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "get_quiz",
                            "description": "Get quiz with questions",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "quiz_id": {
                                        "type": "string",
                                        "description": "Quiz ID"
                                    }
                                },
                                "required": ["quiz_id"]
                            }
                        },
                        {
                            "name": "submit_quiz",
                            "description": "Submit quiz answers for grading",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "quiz_id": {"type": "string"},
                                    "answers": {"type": "object"}
                                },
                                "required": ["quiz_id", "answers"]
                            }
                        },
                        {
                            "name": "get_progress",
                            "description": "Get user learning progress",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string"}
                                },
                                "required": ["user_id"]
                            }
                        },
                        {
                            "name": "update_progress",
                            "description": "Mark chapter as complete",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string"},
                                    "chapter_id": {"type": "string"}
                                },
                                "required": ["user_id", "chapter_id"]
                            }
                        },
                        {
                            "name": "get_streak",
                            "description": "Get user streak information",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string"}
                                },
                                "required": ["user_id"]
                            }
                        },
                        {
                            "name": "check_access",
                            "description": "Check content access (freemium)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string"},
                                    "resource": {"type": "string"}
                                },
                                "required": ["user_id", "resource"]
                            }
                        },
                        # Phase 2: Adaptive Learning Tools (Premium only)
                        {
                            "name": "get_adaptive_recommendations",
                            "description": "Get personalized chapter recommendations using AI (Premium/Pro only)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {
                                        "type": "string",
                                        "description": "User ID"
                                    }
                                },
                                "required": ["user_id"]
                            }
                        },
                        {
                            "name": "get_knowledge_analysis",
                            "description": "Analyze knowledge gaps from quiz performance (Premium/Pro only)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {
                                        "type": "string",
                                        "description": "User ID"
                                    }
                                },
                                "required": ["user_id"]
                            }
                        },
                        {
                            "name": "submit_open_answer",
                            "description": "Submit open-ended quiz answer for LLM grading (Premium/Pro only)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "quiz_id": {
                                        "type": "string",
                                        "description": "Quiz ID"
                                    },
                                    "user_id": {
                                        "type": "string",
                                        "description": "User ID"
                                    },
                                    "answer": {
                                        "type": "string",
                                        "description": "Open-ended answer text"
                                    }
                                },
                                "required": ["quiz_id", "user_id", "answer"]
                            }
                        }
                    ]
                },
                "id": req_id
            })

        # Handle tools/call - Execute actual tools
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            try:
                # Call the appropriate backend API endpoint
                async with httpx.AsyncClient() as client:
                    # list_chapters
                    if tool_name == "list_chapters":
                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/chapters",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # get_chapter
                    elif tool_name == "get_chapter":
                        chapter_id = arguments.get("chapter_id")
                        if not chapter_id:
                            raise ValueError("chapter_id is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/chapters/{chapter_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # search_content
                    elif tool_name == "search_content":
                        query = arguments.get("query")
                        if not query:
                            raise ValueError("query is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/search",
                            params={"q": query},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # get_quiz
                    elif tool_name == "get_quiz":
                        quiz_id = arguments.get("quiz_id")
                        if not quiz_id:
                            raise ValueError("quiz_id is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # submit_quiz
                    elif tool_name == "submit_quiz":
                        quiz_id = arguments.get("quiz_id")
                        answers = arguments.get("answers")
                        if not quiz_id or not answers:
                            raise ValueError("quiz_id and answers are required")

                        response = await client.post(
                            f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/submit",
                            json={"answers": answers},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # get_progress
                    elif tool_name == "get_progress":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/progress/{user_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # update_progress
                    elif tool_name == "update_progress":
                        user_id = arguments.get("user_id")
                        chapter_id = arguments.get("chapter_id")
                        if not user_id or not chapter_id:
                            raise ValueError("user_id and chapter_id are required")

                        response = await client.put(
                            f"{BACKEND_API_URL}/api/v1/progress/{user_id}",
                            json={"chapter_id": chapter_id},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # get_streak
                    elif tool_name == "get_streak":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/streaks/{user_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # check_access
                    elif tool_name == "check_access":
                        user_id = arguments.get("user_id")
                        resource = arguments.get("resource")
                        if not user_id or not resource:
                            raise ValueError("user_id and resource are required")

                        response = await client.post(
                            f"{BACKEND_API_URL}/api/v1/access/check",
                            json={"user_id": user_id, "resource": resource},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                    # Phase 2: get_adaptive_recommendations
                    elif tool_name == "get_adaptive_recommendations":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        # Check if Phase 2 is enabled
                        if not settings.enable_phase_2_llm:
                            result = {
                                "error": "Phase 2 LLM features are not enabled on this server",
                                "phase_2_enabled": False
                            }
                        else:
                            response = await client.get(
                                f"{BACKEND_API_URL}/api/v1/adaptive/recommendations?user_id={user_id}",
                                timeout=30.0  # Longer timeout for LLM calls
                            )
                            # Handle premium tier requirement
                            if response.status_code == 403:
                                error_data = response.json()
                                result = {
                                    "error": error_data.get("detail", "Premium or Pro subscription required"),
                                    "upgrade_url": error_data.get("upgrade_url", "/api/v1/access/upgrade")
                                }
                            else:
                                response.raise_for_status()
                                result = response.json()

                    # Phase 2: get_knowledge_analysis
                    elif tool_name == "get_knowledge_analysis":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        # Check if Phase 2 is enabled
                        if not settings.enable_phase_2_llm:
                            result = {
                                "error": "Phase 2 LLM features are not enabled on this server",
                                "phase_2_enabled": False
                            }
                        else:
                            response = await client.get(
                                f"{BACKEND_API_URL}/api/v1/adaptive/analysis?user_id={user_id}",
                                timeout=30.0
                            )
                            # Handle premium tier requirement
                            if response.status_code == 403:
                                error_data = response.json()
                                result = {
                                    "error": error_data.get("detail", "Premium or Pro subscription required"),
                                    "upgrade_url": error_data.get("upgrade_url", "/api/v1/access/upgrade")
                                }
                            else:
                                response.raise_for_status()
                                result = response.json()

                    # Phase 2: submit_open_answer
                    elif tool_name == "submit_open_answer":
                        quiz_id = arguments.get("quiz_id")
                        user_id = arguments.get("user_id")
                        answer = arguments.get("answer")
                        if not quiz_id or not user_id or not answer:
                            raise ValueError("quiz_id, user_id, and answer are required")

                        # Check if Phase 2 is enabled
                        if not settings.enable_phase_2_llm:
                            result = {
                                "error": "Phase 2 LLM features are not enabled on this server",
                                "phase_2_enabled": False
                            }
                        else:
                            response = await client.post(
                                f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/grade-llm?user_id={user_id}",
                                json={"answers": {"open_ended": answer}},
                                timeout=60.0  # Longer timeout for LLM grading
                            )
                            # Handle premium tier requirement
                            if response.status_code == 403:
                                error_data = response.json()
                                result = {
                                    "error": error_data.get("detail", "Premium or Pro subscription required"),
                                    "upgrade_url": error_data.get("upgrade_url", "/api/v1/access/upgrade")
                                }
                            else:
                                response.raise_for_status()
                                result = response.json()

                    else:
                        return JSONResponse(content={
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32601,
                                "message": f"Unknown tool: {tool_name}"
                            },
                            "id": req_id
                        })

                # Return result in MCP format
                # Check if this is a quiz - if so, add UI component metadata
                if tool_name == "get_quiz":
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        },
                        "id": req_id,
                        # Metadata for React UI component
                        "metadata": {
                            "openai/widgetDomain": "https://sse.testservers.online",
                            "openai/widgetCSP": {
                                "connect_domains": ["https://chatgpt.com"],
                                "script_domains": ["https://sse.testservers.online"],
                                "resource_domains": ["https://*.oaistatic.com"]
                            },
                            "openai/widgetUrl": "https://sse.testservers.online/ui/index.html"
                        }
                    })
                else:
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        },
                        "id": req_id
                    })

            except Exception as e:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing {tool_name}: {str(e)}"
                            }
                        ],
                        "isError": True
                    },
                    "id": req_id
                })

        # Unknown method
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": req_id
            })

    except Exception as e:
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)


@router.get("/sse")
async def mcp_sse():
    """MCP SSE endpoint for streaming (for backwards compatibility)."""
    async def event_stream():
        try:
            # Send server announcement
            announcement = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "server": "Course Companion FTE Backend",
                    "version": "1.0.0"
                }
            }

            data = json.dumps(announcement)
            yield f"event: message\ndata: {data}\n\n"

            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield ": keep-alive\n\n"

        except asyncio.CancelledError:
            pass
        except Exception as e:
            error_msg = {
                "jsonrpc": "2.0",
                "method": "error",
                "params": {"code": -1, "message": str(e)}
            }
            data = json.dumps(error_msg)
            yield f"event: error\ndata: {data}\n\n"

    return Response(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Chunking": "no",
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )

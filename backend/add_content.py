"""
Populate Course Companion FTE with course content.
Uses async database sessions.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import select
from src.models.database import Chapter, Quiz, Question
from src.core.database import async_session_maker
import json

# Course content for 4 chapters
CHAPTERS_DATA = [
    {
        "order": 1,
        "title": "Introduction to AI Agents",
        "difficulty_level": "beginner",
        "estimated_time": 30,
        "content": """# Chapter 1: Introduction to AI Agents

## What are AI Agents?

AI Agents are autonomous systems that can perceive their environment, reason about it, and take actions to achieve specific goals. Unlike traditional software that follows fixed instructions, AI agents can perceive, reason, act, and learn.

## Key Characteristics

1. **Autonomy**: Operate without constant human intervention
2. **Reactivity**: Respond to changes in their environment
3. **Proactivity**: Take initiative to achieve goals
4. **Social Ability**: Communicate with other agents and humans

## Real-World Examples

- **Personal Assistants**: Siri, Alexa, Google Assistant
- **Autonomous Vehicles**: Self-driving cars
- **Trading Bots**: Automated financial trading systems
- **Game AI**: NPCs in video games

## Why AI Agents Matter

AI Agents represent the next evolution in software development. Instead of writing explicit rules, we build systems that can handle complex environments, make decisions with incomplete information, adapt to new situations, and work collaboratively with humans.

## The Agent Architecture

AI agents have three main components: Sensors to perceive the environment, a processing core to reason and make decisions, and actuators to take actions in the environment.
""",
        "quiz": {
            "questions": [
                {
                    "question": "What are the four key characteristics of AI agents?",
                    "type": "multiple_choice",
                    "options": [
                        "Speed, accuracy, efficiency, and cost",
                        "Autonomy, reactivity, proactivity, and social ability",
                        "Input, processing, output, and storage",
                        "Learning, reasoning, planning, and acting"
                    ],
                    "correct_answer": 1,
                    "explanation": "The four key characteristics of AI agents are autonomy (operate independently), reactivity (respond to environment), proactivity (take initiative), and social ability (communicate with others)."
                },
                {
                    "question": "Which component of an agent architecture is responsible for gathering information from the environment?",
                    "type": "multiple_choice",
                    "options": ["Actuators", "Sensors", "Processor", "Memory"],
                    "correct_answer": 1,
                    "explanation": "Sensors are responsible for perceiving the environment and gathering information, which is then processed by the agent's logic."
                },
                {
                    "question": "What distinguishes AI agents from traditional software?",
                    "type": "multiple_choice",
                    "options": [
                        "AI agents are faster than traditional software",
                        "AI agents can perceive, reason, act, and learn autonomously",
                        "AI agents require more code than traditional software",
                        "AI agents are only used in games"
                    ],
                    "correct_answer": 1,
                    "explanation": "Unlike traditional software that follows fixed instructions, AI agents can perceive their environment, reason about it, take actions, and learn from experience."
                },
                {
                    "question": "Siri and Alexa are examples of what type of AI agents?",
                    "type": "multiple_choice",
                    "options": ["Autonomous vehicles", "Personal assistants", "Trading bots", "Game AI"],
                    "correct_answer": 1,
                    "explanation": "Siri and Alexa are personal assistant agents that can understand natural language, answer questions, and perform tasks for users."
                },
                {
                    "question": "True or False: AI agents can only operate in static, predictable environments.",
                    "type": "multiple_choice",
                    "options": ["True", "False", "", ""],
                    "correct_answer": 1,
                    "explanation": "False. One of the key advantages of AI agents is their ability to operate in dynamic, changing environments and adapt to new situations."
                }
            ]
        }
    },
    {
        "order": 2,
        "title": "Understanding MCP (Model Context Protocol)",
        "difficulty_level": "beginner",
        "estimated_time": 30,
        "content": """# Chapter 2: Understanding MCP (Model Context Protocol)

## What is MCP?

MCP (Model Context Protocol) is an open standard that enables AI applications to connect to external data sources and tools. Think of it as a universal adapter that lets AI assistants like ChatGPT interact with your APIs, databases, and services.

## Why MCP Matters

Before MCP, connecting AI to your data required custom API integrations for each AI platform, complex authentication handling, and no standardization.

With MCP, you get one integration that works across multiple AI platforms, standardized authentication, automatic tool discovery, and type-safe communication.

## How MCP Works

ChatGPT (Client) sends MCP requests to Your Server, which responds with available tools. The communication uses JSON-RPC 2.0 format over HTTP with Server-Sent Events (SSE) for streaming.

## The Connection Flow

1. **Initialization**: ChatGPT sends initialize request
2. **Discovery**: ChatGPT requests available tools via tools/list
3. **Tool Use**: ChatGPT calls tools with tools/call
4. **Response**: Your server executes tools and returns results

## Key Response Format

The initialize response must include: protocolVersion (2024-11-05), serverInfo with name and version, and capabilities with tools object.

## Defining Tools

Tools in MCP are defined with JSON Schema that includes the tool name, description, and inputSchema with properties and required parameters.

## Best Practices

1. Clear descriptions help the AI understand when to use each tool
2. Type safety using proper JSON Schema for validation
3. Error handling with meaningful error messages
4. Idempotency so tools are safe to retry
5. Rate limiting to protect your resources

## Common Pitfalls

Wrong response format (serverInfo vs server), missing protocolVersion, incorrect capabilities structure, no POST handler, or missing inputSchema for tools.
""",
        "quiz": {
            "questions": [
                {
                    "question": "What does MCP stand for?",
                    "type": "multiple_choice",
                    "options": [
                        "Machine Control Protocol",
                        "Model Context Protocol",
                        "Message Communication Protocol",
                        "Multi-Cloud Platform"
                    ],
                    "correct_answer": 1,
                    "explanation": "MCP stands for Model Context Protocol, an open standard for connecting AI applications to external data sources and tools."
                },
                {
                    "question": "What protocol does MCP use for communication?",
                    "type": "multiple_choice",
                    "options": ["REST", "GraphQL", "JSON-RPC 2.0", "gRPC"],
                    "correct_answer": 2,
                    "explanation": "MCP uses JSON-RPC 2.0 for all communication between clients and servers."
                },
                {
                    "question": "What transport mechanism does MCP use for streaming from server to client?",
                    "type": "multiple_choice",
                    "options": ["WebSockets", "Server-Sent Events (SSE)", "Long polling", "WebRTC"],
                    "correct_answer": 1,
                    "explanation": "MCP uses Server-Sent Events (SSE) for streaming responses from the server to the client."
                },
                {
                    "question": "Which field is REQUIRED in the MCP initialize response?",
                    "type": "multiple_choice",
                    "options": ["server", "serverInfo", "serverUrl", "serverName"],
                    "correct_answer": 1,
                    "explanation": "The 'serverInfo' field (not 'server') is required in the MCP initialize response and must contain name and version."
                },
                {
                    "question": "True or False: MCP tools must include an inputSchema field.",
                    "type": "multiple_choice",
                    "options": ["True", "False", "", ""],
                    "correct_answer": 0,
                    "explanation": "True. All MCP tools must include an inputSchema field that defines the parameters using JSON Schema format."
                }
            ]
        }
    },
    {
        "order": 3,
        "title": "Creating Your First Agent",
        "difficulty_level": "beginner",
        "estimated_time": 45,
        "content": """# Chapter 3: Creating Your First Agent

## What You'll Build

A Research Agent that can accept a research topic, search for relevant information, synthesize findings, and provide a comprehensive summary.

## The Agent Loop

The agent follows a continuous loop: Reason (decide what to do), Act (use tools), Observe (get results), and Respond (format answer).

## Basic Agent Structure

An agent needs access to an LLM client (like OpenAI), a dictionary of available tools, and methods to execute those tools and run the main loop.

## Implementing Tool Use

The agent should be able to execute tools by name with given parameters. Common tools include web search, URL fetching, and database queries.

## Adding Reasoning

Use the LLM to decide the next action based on the current context. The LLM can choose which tools to use and with what parameters.

## The Main Loop

The agent should loop through: getting the next action from the LLM, executing any tool calls, appending results to context, and checking if we should continue or stop.

## Best Practices

1. Clear tool descriptions help the LLM understand when to use each tool
2. Error handling prevents failed tool calls from crashing the agent
3. Context management prevents the context from growing too large
4. Stopping conditions prevent infinite loops

## Testing Your Agent

Test each tool individually before testing the full agent. This makes debugging much easier.

## Common Mistakes

No tool descriptions means the LLM doesn't know when to use tools, ignoring errors crashes the agent, infinite loops from no stopping condition, context overflow slows things down, and no validation means parameters aren't checked.
""",
        "quiz": {
            "questions": [
                {
                    "question": "What are the four main steps in the agent loop?",
                    "type": "multiple_choice",
                    "options": [
                        "Input, process, output, store",
                        "Reason, act, observe, respond",
                        "Plan, execute, monitor, learn",
                        "Sense, think, act, learn"
                    ],
                    "correct_answer": 1,
                    "explanation": "The agent loop consists of: Reason (decide what to do), Act (use tools), Observe (get results), and Respond (format answer)."
                },
                {
                    "question": "What is the purpose of tool descriptions in an agent?",
                    "type": "multiple_choice",
                    "options": [
                        "To document the code",
                        "To help the LLM understand when and how to use each tool",
                        "To validate parameters",
                        "To improve performance"
                    ],
                    "correct_answer": 1,
                    "explanation": "Tool descriptions are critical for helping the LLM understand what each tool does, when to use it, and what parameters it requires."
                },
                {
                    "question": "What happens if an agent's context grows too large?",
                    "type": "multiple_choice",
                    "options": [
                        "The agent becomes smarter",
                        "Performance degrades and costs increase",
                        "The agent automatically stops",
                        "Nothing changes"
                    ],
                    "correct_answer": 1,
                    "explanation": "Large contexts slow down processing, increase API costs, and may hit token limits. Context management is essential."
                },
                {
                    "question": "What is a common stopping condition for an agent loop?",
                    "type": "multiple_choice",
                    "options": [
                        "After exactly 10 iterations",
                        "When the LLM stops calling tools",
                        "When a specific time elapses",
                        "All of the above"
                    ],
                    "correct_answer": 3,
                    "explanation": "Common stopping conditions include: reaching max iterations, no more tool calls, time limits, or explicit completion signals."
                },
                {
                    "question": "True or False: You should test each tool individually before testing the full agent.",
                    "type": "multiple_choice",
                    "options": ["True", "False", "", ""],
                    "correct_answer": 0,
                    "explanation": "True. Testing tools in isolation makes debugging much easier and ensures each component works correctly before integration."
                }
            ]
        }
    },
    {
        "order": 4,
        "title": "Building Reusable Skills",
        "difficulty_level": "intermediate",
        "estimated_time": 45,
        "content": """# Chapter 4: Building Reusable Skills

## What Are Skills?

Skills are reusable capabilities that agents can use. Think of them as plugins or extensions that add specific functionality to your agent.

**Skills vs Tools**: Tools are low-level functions (search, fetch, calculate) while Skills are high-level capabilities (explain, quiz, tutor).

## Why Skills Matter

Skills provide modularity (mix and match capabilities), reusability (use across different agents), maintainability (update skills independently), and scalability (add new features without changing core).

## Skill Architecture

The Agent Core contains reasoning, planning, and memory. It connects to a Skill Loader which dynamically loads capabilities like Concept Explainer, Quiz Master, Socratic Tutor, and Progress Motivator.

## Designing a Skill

Every skill should have: Clear purpose, Trigger detection (keywords that activate the skill), and Execution logic (what the skill actually does).

## Skill Template

A base skill class should have a name, description, list of triggers, methods to check if it should activate, and an execute method.

## Example Skills

**Concept Explainer**: Explains concepts at various complexity levels. Triggered by keywords like 'explain', 'what is', 'how does'.

**Quiz Master**: Conducts quizzes with immediate feedback. Triggered by 'quiz', 'test me', 'practice'.

**Socratic Tutor**: Guides learning through questioning. Triggered by 'stuck', 'help me think', 'give me a hint'.

## Skill Loader

The skill loader registers skills, detects which skill should handle a message, and executes skills by name.

## Best Practices

1. Single Responsibility - Each skill should do ONE thing well
2. Clear Triggers - Make it obvious when a skill should activate
3. Graceful Fallbacks - What if the skill can't complete?
4. Progress Indicators - Long-running skills should show progress

## Common Mistakes

One skill doing multiple things, vague triggers that are hard to match, crashing instead of graceful error handling, and no feedback on progress.
""",
        "quiz": {
            "questions": [
                {
                    "question": "What is the main difference between tools and skills?",
                    "type": "multiple_choice",
                    "options": [
                        "Tools are faster than skills",
                        "Tools are low-level functions while skills are high-level capabilities",
                        "Skills are written in Python, tools are not",
                        "There is no difference"
                    ],
                    "correct_answer": 1,
                    "explanation": "Tools are low-level functions (search, fetch, calculate) while skills are high-level capabilities that combine multiple tools and logic (explain, quiz, tutor)."
                },
                {
                    "question": "What is the purpose of trigger detection in skills?",
                    "type": "multiple_choice",
                    "options": [
                        "To improve performance",
                        "To determine when a skill should activate based on user input",
                        "To validate skill parameters",
                        "To log skill usage"
                    ],
                    "correct_answer": 1,
                    "explanation": "Trigger detection analyzes user input to determine which skill is most appropriate to handle the request."
                },
                {
                    "question": "How many responsibilities should each skill have?",
                    "type": "multiple_choice",
                    "options": ["As many as possible", "One", "Two or three", "At least five"],
                    "correct_answer": 1,
                    "explanation": "Each skill should have a single responsibility and do one thing well. This makes skills more maintainable and reusable."
                },
                {
                    "question": "What should a skill do if it cannot complete its task?",
                    "type": "multiple_choice",
                    "options": [
                        "Raise an exception and crash",
                        "Return a helpful error message with suggestions",
                        "Try forever until it works",
                        "Return nothing"
                    ],
                    "correct_answer": 1,
                    "explanation": "Skills should fail gracefully with helpful error messages and suggestions for the user on how to proceed."
                },
                {
                    "question": "True or False: Skills can be packaged and distributed independently of the agent core.",
                    "type": "multiple_choice",
                    "options": ["True", "False", "", ""],
                    "correct_answer": 0,
                    "explanation": "True. Skills can be packaged as Python modules and distributed independently, allowing others to use them in their own agents."
                }
            ]
        }
    }
]


async def populate_database():
    """Populate database with chapters and quizzes."""
    async with async_session_maker() as session:
        for chapter_data in CHAPTERS_DATA:
            # Check if chapter already exists
            result = await session.execute(
                select(Chapter).where(Chapter.order == chapter_data["order"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Updating chapter {chapter_data['order']}: {existing.title}")
                chapter = existing
                chapter.content = chapter_data["content"]
            else:
                # Create new chapter
                chapter = Chapter(
                    title=chapter_data["title"],
                    order=chapter_data["order"],
                    difficulty_level=chapter_data["difficulty_level"],
                    estimated_time=chapter_data["estimated_time"],
                    content=chapter_data["content"]
                )
                session.add(chapter)
                await session.flush()
                print(f"Created chapter: {chapter.title}")

            # Create/update quiz
            quiz_data = chapter_data["quiz"]
            result = await session.execute(
                select(Quiz).where(Quiz.chapter_id == chapter.id)
            )
            existing_quiz = result.scalar_one_or_none()

            if existing_quiz:
                print(f"  Updating quiz")
                quiz = existing_quiz
                # Delete old questions
                result = await session.execute(
                    select(Question).where(Question.quiz_id == quiz.id)
                )
                old_questions = result.scalars().all()
                for q in old_questions:
                    await session.delete(q)
            else:
                quiz = Quiz(
                    chapter_id=chapter.id,
                    title=f"{chapter.title} - Quiz"
                )
                session.add(quiz)
                await session.flush()
                print(f"  Created quiz")

            # Add questions
            for idx, q_data in enumerate(quiz_data["questions"]):
                # Convert correct answer index to letter (0=A, 1=B, 2=C, 3=D)
                answer_idx = q_data["correct_answer"]
                correct_letter = chr(65 + answer_idx)  # 0='A', 1='B', etc.

                # Build options dict - must have exactly 4 keys (A, B, C, D)
                options_list = q_data.get("options", [])
                while len(options_list) < 4:
                    options_list.append("")  # Pad with empty strings

                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data["question"],
                    options={chr(65 + i): opt for i, opt in enumerate(options_list)},
                    correct_answer=correct_letter,
                    explanation=q_data.get("explanation", ""),
                    order=idx + 1  # 1-based order
                )
                session.add(question)
                print(f"    Added question: {q_data['question'][:50]}...")

            # Link quiz to chapter
            chapter.quiz_id = quiz.id

        await session.commit()
        print("\n✅ Database populated successfully!")


if __name__ == "__main__":
    asyncio.run(populate_database())

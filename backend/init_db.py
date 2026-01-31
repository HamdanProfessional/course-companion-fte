"""
Initialize database with sample course content.
Zero-LLM: Static content only, no generation.
"""

import asyncio
import uuid
import bcrypt
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker
from src.models.database import User, Chapter, Quiz, Question, Progress, Streak


# Sample course content: "AI Agent Development"
SAMPLE_CHAPTERS = [
    {
        "title": "Introduction to AI Agents",
        "order": 1,
        "difficulty": "BEGINNER",
        "estimated_time": 30,
        "content": """# Introduction to AI Agents

## What are AI Agents?

AI agents are autonomous systems that can perceive their environment, reason about it, and take actions to achieve specific goals. Unlike traditional chatbots that simply respond to prompts, AI agents can:

- Use tools to interact with external systems
- Maintain context across multiple interactions
- Plan and execute multi-step tasks
- Learn from feedback and adapt their behavior

## Key Components

1. **Perception**: The agent's ability to understand the current state
2. **Reasoning**: Decision-making based on available information
3. **Action**: Executing tasks through tools or APIs
4. **Memory**: Storing and retrieving information across sessions

## The Claude Agent Framework

The Claude Agent Factory provides a powerful framework for building AI agents with:

- **MCP (Model Context Protocol)**: Standardized way to connect agents to external data sources
- **Skills**: Reusable prompt templates for specific tasks
- **Agents**: Specialized AI assistants with defined behaviors
- **Commands**: Structured workflows for common operations

## Next Steps

In this course, you'll learn how to build, deploy, and scale AI agents using the Claude ecosystem.
""",
        "quiz_questions": [
            {
                "question": "What distinguishes AI agents from traditional chatbots?",
                "options": {"A": "They can only respond to prompts", "B": "They can use tools and maintain context", "C": "They are always faster", "D": "They require less training"},
                "correct": "B",
                "explanation": "AI agents can use tools to interact with external systems and maintain context across multiple interactions, unlike simple chatbots.",
            },
            {
                "question": "What does MCP stand for in the context of AI agents?",
                "options": {"A": "Machine Control Protocol", "B": "Model Context Protocol", "C": "Multi-Cloud Platform", "D": "Memory Cache Provider"},
                "correct": "B",
                "explanation": "MCP stands for Model Context Protocol, which standardizes how AI agents connect to external data sources.",
            },
            {
                "question": "Which of the following is NOT a key component of AI agents?",
                "options": {"A": "Perception", "B": "Reasoning", "C": "Emotional Intelligence", "D": "Action"},
                "correct": "C",
                "explanation": "While perception, reasoning, and action are key components, emotional intelligence is not a core requirement for AI agents.",
            },
        ]
    },
    {
        "title": "Understanding MCP (Model Context Protocol)",
        "order": 2,
        "difficulty": "BEGINNER",
        "estimated_time": 35,
        "content": """# Understanding MCP (Model Context Protocol)

## What is MCP?

MCP (Model Context Protocol) is an open standard that enables AI models to connect to external data sources and tools in a standardized way. Think of it as USB for AI applications.

## Why MCP Matters

Before MCP:
- Each AI application needed custom integrations
- No standard way to share tools and data sources
- Vendors were locked into proprietary ecosystems

With MCP:
- Universal compatibility between AI apps and data/tools
-任何人 can build and share MCP servers
- Collaborative ecosystem of reusable components

## MCP Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   AI App    │────▶│ MCP Client  │────▶│ MCP Server  │
│ (Claude)    │     │             │     │ (Database)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## MCP Server Types

1. **File System**: Access local and remote files
2. **Database**: Query PostgreSQL, MySQL, MongoDB, etc.
3. **API**: Connect to REST, GraphQL, and web services
4. **Tools**: Execute code, run commands, perform actions

## Building an MCP Server

An MCP server implements three types of capabilities:

- **Resources**: Read-only data sources (files, database rows)
- **Prompts**: Reusable prompt templates
- **Tools**: Executable functions with parameters

## Example: File System MCP Server

```python
from mcp.server import Server
from mcp.types import Resource

server = Server("filesystem")

@server.read_resource()
async def read_file(uri: str) -> Resource:
    # Read file from disk
    with open(uri, "r") as f:
        return Resource(contents=f.read())
```

## Next Steps

Now that you understand MCP, let's explore how to build AI agents that leverage these connections.
""",
        "quiz_questions": [
            {
                "question": "What does MCP enable AI models to do?",
                "options": {"A": "Generate images faster", "B": "Connect to external data sources and tools", "C": "Train on larger datasets", "D": "Reduce memory usage"},
                "correct": "B",
                "explanation": "MCP provides a standardized way for AI models to connect to external data sources and tools.",
            },
            {
                "question": "Which of the following is NOT an MCP server type?",
                "options": {"A": "File System", "B": "Database", "C": "Neural Network", "D": "API"},
                "correct": "C",
                "explanation": "File System, Database, and API are all MCP server types. Neural Network is not a standard MCP server category.",
            },
        ]
    },
    {
        "title": "Creating Your First Agent",
        "order": 3,
        "difficulty": "INTERMEDIATE",
        "estimated_time": 40,
        "content": """# Creating Your First Agent

## Agent Definition

An agent is a specialized AI assistant with:
- **Specific role**: Clear purpose and expertise
- **Instructions**: Behavior guidelines and constraints
- **Skills**: Prompt templates for common tasks
- **Tools**: MCP connections for data and actions

## Agent File Structure

```markdown
# agent.md
## Role
You are a helpful code review assistant.

## Instructions
- Always provide constructive feedback
- Suggest specific improvements
- Explain your reasoning

## Skills
- review-code: Analyze code for issues
- suggest-refactor: Propose improvements

## Tools
- github: Fetch repository files
- documentation: Search tech docs
```

## Loading an Agent

```python
from anthropic import Anthropic
from pathlib import Path

client = Anthropic()

agent_content = Path("agent.md").read_text()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system=agent_content,
    messages=[{"role": "user", "content": "Review this code..."}]
)
```

## Best Practices

1. **Clear Role**: Define expertise and boundaries
2. **Specific Instructions**: Be explicit about behavior
3. **Modular Skills**: Break tasks into reusable components
4. **Tool Integration**: Use MCP for data access

## Testing Your Agent

Before deploying, test your agent with:
- Expected use cases
- Edge cases and errors
- Performance benchmarks
- Security considerations

## Next Steps

Now let's explore how to add skills to your agent.
""",
        "quiz_questions": [
            {
                "question": "What are the four main components of an agent?",
                "options": {"A": "Role, Instructions, Skills, Tools", "B": "Data, Logic, UI, API", "C": "Input, Output, Process, Store", "D": "Train, Test, Deploy, Monitor"},
                "correct": "A",
                "explanation": "Agents consist of a Role (purpose), Instructions (behavior), Skills (prompt templates), and Tools (MCP connections).",
            },
            {
                "question": "What is the purpose of agent skills?",
                "options": {"A": "To replace the agent's core model", "B": "To provide reusable prompt templates", "C": "To increase token limits", "D": "To reduce API costs"},
                "correct": "B",
                "explanation": "Skills are reusable prompt templates that help agents perform specific tasks consistently.",
            },
        ]
    },
    {
        "title": "Building Reusable Skills",
        "order": 4,
        "difficulty": "INTERMEDIATE",
        "estimated_time": 45,
        "content": """# Building Reusable Skills

## What are Skills?

Skills are prompt templates that agents can load to perform specific tasks. They encapsulate expertise and best practices for common operations.

## Skill Structure

```markdown
# skill.md
## Description
Explain concepts at learner's level

## Instructions
When the user asks you to explain something:
1. Assess their knowledge level
2. Start with simple analogies
3. Gradually increase complexity
4. Provide examples
5. Check understanding

## Examples
User: "Explain neural networks"
You: "Imagine your brain is a network..."
```

## Creating Effective Skills

### 1. Clear Purpose
Define what the skill does and when to use it.

### 2. Step-by-Step Instructions
Break down the task into clear steps.

### 3. Examples
Show sample inputs and outputs.

### 4. Edge Cases
Handle errors and unexpected inputs.

## Skill Categories

1. **Productivity**: Code review, writing assistance, data analysis
2. **Educational**: Explanation, tutoring, quiz creation
3. **Creative**: Storytelling, brainstorming, design
4. **Technical**: Debugging, refactoring, documentation

## Example: Code Explanation Skill

```python
# Using a skill
from anthropic import Anthropic

client = Anthropic()
skill = Path("explain-code.md").read_text()

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system=skill,
    messages=[{
        "role": "user",
        "content": "Explain this function: def fibonacci(n): ..."
    }]
)
```

## Next Steps

Learn how to combine skills with tools for powerful agents.
""",
        "quiz_questions": [
            {
                "question": "What is the primary purpose of a skill?",
                "options": {"A": "To replace the need for agents", "B": "To provide reusable prompt templates", "C": "To generate training data", "D": "To monitor API usage"},
                "correct": "B",
                "explanation": "Skills are reusable prompt templates that encapsulate expertise for specific tasks.",
            },
        ]
    },
]


async def create_sample_data():
    """Create sample course content in database."""

    # NOTE: Database tables are created by Alembic migrations
    # Run: alembic upgrade head

    # Close any existing connections to clear schema cache
    from src.core.database import engine
    await engine.dispose()

    print("OK Using existing database schema from Alembic migrations")

    async with async_session_maker() as session:
        # Create test user
        hashed = bcrypt.hashpw("pass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            email="student@example.com",
            hashed_password=hashed,
            tier="FREE"
        )
        session.add(user)
        await session.flush()
        print(f"OK Created user: {user.email}")

        # Create progress and streak
        progress = Progress(user_id=user.id, completed_chapters=[], current_chapter_id=None)
        streak = Streak(user_id=user.id, current_streak=0, longest_streak=0, last_checkin=None)
        session.add(progress)
        session.add(streak)
        await session.flush()

        # Create chapters and quizzes
        chapters_map = {}
        for i, chapter_data in enumerate(SAMPLE_CHAPTERS):
            # Create chapter
            chapter = Chapter(
                title=chapter_data["title"],
                content=chapter_data["content"],
                order=chapter_data["order"],
                difficulty_level=chapter_data["difficulty"],
                estimated_time=chapter_data["estimated_time"],
            )
            session.add(chapter)
            await session.flush()
            chapters_map[chapter.order] = chapter
            print(f"OK Created chapter: {chapter.title}")

            # Create quiz
            quiz = Quiz(
                chapter_id=chapter.id,
                title=f"{chapter.title} - Quiz",
                difficulty=chapter_data["difficulty"]
            )
            session.add(quiz)
            await session.flush()

            # Create questions
            for j, q_data in enumerate(chapter_data["quiz_questions"]):
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct"],
                    explanation=q_data["explanation"],
                    order=j + 1
                )
                session.add(question)
            print(f"  OK Created quiz with {len(chapter_data['quiz_questions'])} questions")

        # Link chapters (next/previous)
        for order, chapter in chapters_map.items():
            if order + 1 in chapters_map:
                chapter.next_chapter_id = chapters_map[order + 1].id
            if order - 1 in chapters_map:
                chapter.previous_chapter_id = chapters_map[order - 1].id

        await session.commit()
        print("\nOK Sample data created successfully!")
        print(f"  - {len(SAMPLE_CHAPTERS)} chapters")
        print(f"  - {len(SAMPLE_CHAPTERS)} quizzes")
        print(f"  - Total questions: {sum(len(c['quiz_questions']) for c in SAMPLE_CHAPTERS)}")


if __name__ == "__main__":
    asyncio.run(create_sample_data())

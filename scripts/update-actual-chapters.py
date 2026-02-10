#!/usr/bin/env python3
"""
Update chapter content to match actual 4 chapters in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session_maker
from src.models.database import Chapter

# Correct content for the 4 actual chapters
CHAPTERS_CONTENT = {
    "2912d135-f34f-40af-a297-5f8acfdca3f6": r"""# Introduction to AI Agents

## What are AI Agents?

AI agents are software systems that can autonomously perform tasks in pursuit of goals. Unlike traditional programs that follow explicit instructions, AI agents can perceive their environment, reason about it, and take actions to achieve objectives.

> **Key Insight**: AI agents represent a paradigm shift from static, rule-based software to dynamic, adaptive systems.

## Key Characteristics

### 1. Autonomy
AI agents operate without constant human intervention. Once given a goal, they can work independently to achieve it.

### 2. Perception
Agents can sense and interpret their environment through various inputs:
- **Visual**: Image processing, object detection
- **Auditory**: Speech recognition, sound analysis
- **Textual**: Natural language processing
- **Sensor Data**: Temperature, location, movement

### 3. Reasoning
Based on perceived information, agents can make decisions about what actions to take.

### 4. Action
Agents execute actions that affect their environment or change their internal state.

### 5. Learning
Many AI agents can improve their performance over time through experience.

## Types of AI Agents

| Type | Description | Example |
|------|-------------|---------|
| **Reactive Agents** | Respond only to current state | Chess-playing AI |
| **Proactive Agents** | Can take initiative and plan ahead | Personal assistants |
| **Hybrid Agents** | Combine multiple approaches | Autonomous vehicles |

## Real-World Applications

### Virtual Assistants
- Siri, Alexa, Google Assistant
- Understand natural language
- Perform tasks across multiple apps

### Autonomous Vehicles
- Self-driving cars
- Delivery drones
- Warehouse robots

## Summary

AI agents are transforming how we interact with technology. From simple reactive systems to complex multi-agent societies, they represent the future of intelligent automation.
""",

    "4d595b4d-ac38-4a35-9699-265009f430e9": r"""# Understanding MCP (Model Context Protocol)

## Overview

The Model Context Protocol (MCP) is an open standard that enables AI models to securely connect to external data sources and tools. It allows AI assistants to access and manipulate data in a controlled, safe manner.

## What is MCP?

MCP provides a standardized way for AI applications to:
- Connect to data sources (databases, APIs, file systems)
- Execute tools and functions
- Maintain security and access control
- Provide context to AI models

## Key Components

### 1. MCP Client
The application that wants to use AI with external data (e.g., ChatGPT, Claude).

### 2. MCP Server
Exposes data and tools to AI models through a standardized interface.

### 3. MCP Transport
The communication protocol between client and server (stdio, SSE, WebSocket).

## How MCP Works

```
AI App (Client) ← MCP → MCP Server ← Query → Data/Tools (Database)
```

## MCP Server Types

### 1. Filesystem Server
- Read/write files
- List directories
- Search file contents

### 2. Database Server
- Query databases
- Execute transactions
- Access control

### 3. API Servers
- Call external APIs
- Webhooks
- Custom integrations

## MCP in ChatGPT

ChatGPT supports MCP through its Apps feature:
1. Create an MCP manifest
2. Define available tools
3. Connect to ChatGPT
4. AI can use your tools seamlessly

## Summary

MCP enables AI assistants to securely interact with your data and systems, opening up endless possibilities for AI-powered applications.
""",

    "91a1e219-c7ff-4677-8a1a-ace4b58787c5": r"""# Creating Your First Agent

## Overview

Now that you understand AI agents and MCP, let's create your first agent! This chapter will guide you through building a simple but functional AI agent.

## Prerequisites

Before starting, ensure you have:
- Basic understanding of Python or JavaScript
- Node.js or Python installed
- A code editor (VS Code recommended)
- An OpenAI or Anthropic API key

## Your First Agent: A Simple Task Assistant

### Step 1: Define the Goal
Our agent will help users manage tasks by:
- Adding new tasks
- Listing all tasks
- Marking tasks as complete

### Step 2: Choose Your Agent Type

We'll build a **Reactive Agent** - simple, responsive, and easy to understand.

### Step 3: Implement the Agent

```python
class TaskAgent:
    def __init__(self):
        self.tasks = []

    def perceive(self):
        return len(self.tasks)

    def decide(self, state):
        return state > 0

    def act(self, action, data=None):
        if action == 'add':
            self.tasks.append(data)
        elif action == 'list':
            return self.tasks
        elif action == 'complete':
            if self.tasks:
                return self.tasks.pop(0)
```

### Step 4: Test Your Agent

```python
agent = TaskAgent()
agent.run("add Buy groceries")
agent.run("list")
agent.run("complete")
```

## Next Steps

Once your basic agent works:
1. Add more actions (delete, prioritize)
2. Implement memory (save/load tasks)
3. Add AI capabilities (use LLM for understanding)
4. Create an MCP server for your agent

## Summary

You've built your first AI agent! It demonstrates all the key concepts: perception, decision-making, and action.
""",

    "56aa5028-8ddd-4e21-b00a-e935147079cc": r"""# Building Reusable Skills

## Overview

Skills are modular capabilities that agents can use. Building reusable skills makes your agents more powerful and easier to maintain.

## What are Skills?

A **skill** is a self-contained unit of functionality that:
- Performs a specific task
- Has clear inputs and outputs
- Can be reused across different agents
- Is independently testable

## Designing Good Skills

### Principles

1. **Single Responsibility**: Each skill does one thing well
2. **Clear Interface**: Inputs and outputs are well-defined
3. **Stateless**: Skills don't maintain internal state
4. **Idempotent**: Same input always produces same output

### Example Skills

#### Web Search Skill
```python
class WebSearchSkill:
    name = "web_search"

    def execute(self, query: str) -> list:
        results = search(query)
        return results
```

#### File Operations Skill
```python
class FileOperationsSkill:
    name = "file_ops"

    def execute(self, action: str, path: str, content=None):
        if action == "read":
            return read_file(path)
        elif action == "write":
            write_file(path, content)
```

## MCP Skills

When building MCP servers, skills become tools:

```python
@mcp.tool()
async def search_files(query: str) -> list:
    """Search for files matching a query"""
    return search_files(query)

@mcp.tool()
async def read_file(path: str) -> str:
    """Read file contents"""
    with open(path) as f:
        return f.read()
```

## Composing Skills

Agents combine multiple skills to create complex behaviors:

```python
class ComposedAgent:
    def __init__(self):
        self.skills = [
            WebSearchSkill(),
            FileOperationsSkill(),
            DatabaseQuerySkill()
        ]

    def use_skill(self, skill_name, *args, **kwargs):
        for skill in self.skills:
            if skill.name == skill_name:
                return skill.execute(*args, **kwargs)
```

## Summary

Building reusable skills is key to creating powerful, maintainable AI agents. Follow the principles of good design and your agents will be easier to build and extend.
"""
}


async def update_chapters():
    async with async_session_maker() as session:
        result = await session.execute(select(Chapter))
        chapters = result.scalars().all()

        print(f"Found {len(chapters)} chapters in database\n")

        for chapter in chapters:
            if chapter.id in CHAPTERS_CONTENT:
                chapter.content = CHAPTERS_CONTENT[chapter.id]
                print(f"Updated: Chapter {chapter.order} - {chapter.title}")

        await session.commit()
        print(f"\nSuccessfully updated all chapters with correct content!")


if __name__ == "__main__":
    asyncio.run(update_chapters())

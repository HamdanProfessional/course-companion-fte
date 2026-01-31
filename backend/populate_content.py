"""
Populate Course Companion FTE with full course content and quizzes.
Run this on the server: python populate_content.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.models.database import engine, Chapter, Quiz, Question
import uuid

# Course content for all 10 chapters
CHAPTERS_DATA = [
    {
        "order": 1,
        "title": "Introduction to AI Agents",
        "difficulty_level": "BEGINNER",
        "estimated_time": 30,
        "content": """# Chapter 1: Introduction to AI Agents

## What are AI Agents?

AI Agents are autonomous systems that can perceive their environment, reason about it, and take actions to achieve specific goals. Unlike traditional software that follows fixed instructions, AI agents can:

- **Perceive**: Gather information from their environment
- **Reason**: Process information and make decisions
- **Act**: Execute actions to influence their environment
- **Learn**: Improve performance over time

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

## The Agent Architecture

```
┌─────────────┐
│  Sensors    │ ← Perceive environment
└──────┬──────┘
       │
┌──────▼──────┐
│   Agent     │ ← Process & Decide
│   Logic     │
└──────┬──────┘
       │
┌──────▼──────┐
│  Actuators  │ ← Take action
└─────────────┘
```

## Why AI Agents Matter

AI Agents represent the next evolution in software development. Instead of writing explicit rules, we build systems that can:

1. Handle complex, changing environments
2. Make decisions based on incomplete information
3. Adapt to new situations
4. Work collaboratively with humans and other agents

## In This Course

You'll learn how to:
- Build AI agents using modern frameworks
- Implement agent reasoning and decision-making
- Create agents that can use tools and APIs
- Deploy agents at scale
- Follow best practices for production agents
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
                    "type": "true_false",
                    "correct_answer": False,
                    "explanation": "False. One of the key advantages of AI agents is their ability to operate in dynamic, changing environments and adapt to new situations."
                }
            ]
        }
    },
    {
        "order": 2,
        "title": "Understanding MCP (Model Context Protocol)",
        "difficulty_level": "BEGINNER",
        "estimated_time": 30,
        "content": """# Chapter 2: Understanding MCP (Model Context Protocol)

## What is MCP?

MCP (Model Context Protocol) is an open standard that enables AI applications to connect to external data sources and tools. Think of it as a universal adapter that lets AI assistants like ChatGPT interact with your APIs, databases, and services.

## Why MCP Matters

Before MCP, connecting AI to your data required:
- Custom API integrations for each AI platform
- Complex authentication handling
- Limited tool discovery
- No standardization

With MCP:
- ✅ One integration works across multiple AI platforms
- ✅ Standardized authentication
- ✅ Automatic tool discovery
- ✅ Type-safe communication

## How MCP Works

```
┌─────────────┐         MCP         ┌──────────────┐
│   ChatGPT   │ ◄──────────────► │  Your Server  │
│  (Client)   │   JSON-RPC/SSE    │   (Server)    │
└─────────────┘                    └──────────────┘
       │                                  │
       │                                  │
    Sends                              Responds
  Requests                            with Tools
```

### The Connection Flow

1. **Initialization**: ChatGPT sends `initialize` request
2. **Discovery**: ChatGPT requests available tools via `tools/list`
3. **Tool Use**: ChatGPT calls tools with `tools/call`
4. **Response**: Your server executes tools and returns results

## MCP Message Format

All MCP communication uses JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "id": 1
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "Your Server",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {}
    }
  },
  "id": 1
}
```

## Server-Sent Events (SSE)

MCP uses SSE for streaming responses from server to client:

```
event: message
data: {"jsonrpc":"2.0","method":"notifications/initialized",...}

event: message
data: {"jsonrpc":"2.0","method":"tools/list",...}

: keep-alive
```

## Defining Tools

Tools in MCP are defined with JSON Schema:

```json
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
}
```

## Best Practices

1. **Clear Descriptions**: Help the AI understand when to use each tool
2. **Type Safety**: Use proper JSON Schema for validation
3. **Error Handling**: Return meaningful error messages
4. **Idempotency**: Tools should be safe to retry
5. **Rate Limiting**: Protect your resources

## MCP vs Other Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **MCP** | Standard, universal, type-safe | Learning curve |
| **Custom API** | Full control | Platform-specific, maintenance |
| **Function Calling** | Simple | Limited to one platform |

## Real-World Use Cases

- **Data Access**: Connect AI to your database
- **API Integration**: Expose your APIs to AI
- **Tool Execution**: Let AI call your services
- **Content Management**: AI can search and retrieve content
- **Automation**: Trigger workflows from AI

## Building an MCP Server

Key requirements:

1. **HTTP Endpoint**: Accept POST and GET requests
2. **JSON-RPC 2.0**: Standard protocol format
3. **SSE Support**: Stream responses via Server-Sent Events
4. **Tool Definitions**: Declare available tools with schemas
5. **Error Handling**: Graceful failure modes

## Testing Your MCP Server

Always test with curl before connecting to ChatGPT:

```bash
curl -X POST https://your-server.com/mcp \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}'
```

## Common Pitfalls

- ❌ Wrong response format (serverInfo vs server)
- ❌ Missing protocolVersion
- ❌ Incorrect capabilities structure
- ❌ No POST handler
- ❌ Missing inputSchema for tools

## Summary

MCP is the bridge between AI assistants and your data. By implementing an MCP server, you make your functionality accessible to any AI platform that supports the protocol.

In the next chapter, we'll build your first AI agent that uses MCP tools!
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
                    "type": "true_false",
                    "correct_answer": True,
                    "explanation": "True. All MCP tools must include an inputSchema field that defines the parameters using JSON Schema format."
                }
            ]
        }
    },
    {
        "order": 3,
        "title": "Creating Your First Agent",
        "difficulty_level": "BEGINNER",
        "estimated_time": 45,
        "content": """# Chapter 3: Creating Your First Agent

## Getting Started

In this chapter, you'll build your first functional AI agent. We'll use Python and create a simple but powerful agent that can search the web and answer questions.

## What You'll Build

A **Research Agent** that can:
1. Accept a research topic
2. Search for relevant information
3. Synthesize findings
4. Provide a comprehensive summary

## Prerequisites

```bash
# Install required packages
pip install openai httpx python-dotenv

# Set up your environment
export OPENAI_API_KEY="your-key-here"
```

## Basic Agent Structure

```python
import asyncio
from openai import AsyncOpenAI
import httpx

class ResearchAgent:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.tools = {
            "search_web": self.search_web,
            "fetch_url": self.fetch_url
        }

    async def search_web(self, query: str) -> str:
        """Search the web for information."""
        # Implementation here
        pass

    async def fetch_url(self, url: str) -> str:
        """Fetch content from a URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.text

    async def run(self, user_query: str):
        """Main agent loop."""
        # 1. Understand the query
        # 2. Decide which tools to use
        # 3. Execute tools
        # 4. Synthesize results
        pass
```

## The Agent Loop

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Reason  │ ← Decide what to do
    └────┬────┘
         │
    ┌────▼────┐
    │ Act     │ ← Use tools
    └────┬────┘
         │
    ┌────▼────┐
    │ Observe │ ← Get results
    └────┬────┘
         │
    ┌────▼────┐
    │ Respond │ ← Format answer
    └─────────┘
```

## Implementing Tool Use

```python
async def use_tool(self, tool_name: str, **kwargs):
    """Execute a tool by name."""
    if tool_name not in self.tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    return await self.tools[tool_name](**kwargs)
```

## Adding Reasoning

```python
async def decide_next_action(self, query: str, context: list):
    """Use LLM to decide the next action."""

    response = await self.client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a research assistant."},
            *context,
            {"role": "user", "content": query}
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        }]
    )

    return response.choices[0].message
```

## Complete Agent Example

```python
class ResearchAgent:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.context = []

    async def research(self, topic: str, max_iterations: int = 3):
        """Research a topic thoroughly."""

        query = f"Research this topic: {topic}"
        iteration = 0

        while iteration < max_iterations:
            # Get next action from LLM
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=self.context + [
                    {"role": "user", "content": query}
                ],
                tools=self.get_tools()
            )

            message = response.choices[0].message
            self.context.append({"role": "assistant", "content": message.content})

            # Check if tool call needed
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result = await self.execute_tool(tool_call)
                    self.context.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
            else:
                # Done!
                return message.content

            iteration += 1

        return "Max iterations reached"

    async def execute_tool(self, tool_call):
        """Execute a tool call."""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "search_web":
            return await self.search_web(arguments["query"])
        elif function_name == "fetch_url":
            return await self.fetch_url(arguments["url"])
```

## Testing Your Agent

```python
async def main():
    agent = ResearchAgent()
    result = await agent.research("Latest developments in AI agents")
    print(result)

asyncio.run(main())
```

## Best Practices

### 1. Clear Tool Descriptions
```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for current information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, use specific keywords"
                }
            },
            "required": ["query"]
        }
    }
}]
```

### 2. Error Handling
```python
async def execute_tool(self, tool_call):
    try:
        result = await self.tools[function_name](**arguments)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 3. Context Management
```python
def should_continue(self):
    """Check if we should continue."""
    # Don't let context grow too large
    if len(self.context) > 20:
        # Summarize old context
        pass

    # Check for completion signals
    last_message = self.context[-1]
    if "DONE" in last_message.get("content", ""):
        return False

    return True
```

## Debugging Tips

### 1. Log Everything
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Executing tool: {function_name}")
logger.info(f"Result: {result}")
```

### 2. Visualize Flow
```python
def print_state(self):
    """Print current agent state."""
    print(f"Context length: {len(self.context)}")
    print(f"Last message: {self.context[-1]['role']}")
```

### 3. Test Components
```python
# Test tools individually
async def test_search():
    agent = ResearchAgent()
    result = await agent.search_web("AI agents")
    print(result)
```

## Common Mistakes

1. **No Tool Descriptions**: LLM doesn't know when to use tools
2. **Ignoring Errors**: Failed tool calls crash the agent
3. **Infinite Loops**: No stopping condition
4. **Context Overflow**: Too much history slows things down
5. **No Validation**: Tool parameters not checked

## Next Steps

Now that you have a basic agent:
1. ✅ Add more tools (database, APIs)
2. ✅ Improve reasoning with chain-of-thought
3. ✅ Add memory to remember across sessions
4. ✅ Deploy as a web service

In the next chapter, we'll learn how to build reusable skills that your agent can use!
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
                    "type": "true_false",
                    "correct_answer": True,
                    "explanation": "True. Testing tools in isolation makes debugging much easier and ensures each component works correctly before integration."
                }
            ]
        }
    },
    {
        "order": 4,
        "title": "Building Reusable Skills",
        "difficulty_level": "INTERMEDIATE",
        "estimated_time": 45,
        "content": """# Chapter 4: Building Reusable Skills

## What Are Skills?

Skills are reusable capabilities that agents can use. Think of them as plugins or extensions that add specific functionality to your agent.

**Skills vs Tools:**
- **Tools**: Low-level functions (search, fetch, calculate)
- **Skills**: High-level capabilities (explain, quiz, tutor)

## Why Skills Matter

```
Without Skills:
Agent → LLM → Everything hardcoded

With Skills:
Agent → LLM → Load Skills → Dynamic Capabilities
```

Benefits:
- ✅ **Modularity**: Mix and match capabilities
- ✅ **Reusability**: Use across different agents
- ✅ **Maintainability**: Update skills independently
- ✅ **Scalability**: Add new features without changing core

## Skill Architecture

```
┌─────────────────────────────────┐
│          Agent Core             │
│  (Reasoning, Planning, Memory)  │
└─────────────┬───────────────────┘
              │
      ┌───────▼────────┐
      │  Skill Loader  │
      └───────┬────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐      ┌──────▼──┐
│ Concept│      │  Quiz   │
│Explainer│     │ Master  │
└────────┘      └─────────┘
```

## Designing a Skill

Every skill should have:

### 1. Clear Purpose
```python
"""
Concept Explainer Skill

Purpose: Break down complex concepts at learner's level
When to use: User asks "explain", "what is", "how does"
Input: Concept name or description
Output: Simplified explanation with examples
"""
```

### 2. Trigger Detection
```python
TRIGGERS = [
    "explain", "what is", "how does",
    "tell me about", "describe"
]

def should_trigger(message: str) -> bool:
    """Check if this skill should activate."""
    return any(trigger in message.lower() for trigger in TRIGGERS)
```

### 3. Execution Logic
```python
async def execute(self, concept: str, level: str = "beginner"):
    """Execute the skill."""
    # 1. Fetch concept information
    content = await self.fetch_content(concept)

    # 2. Simplify based on level
    simplified = await self.simplify(content, level)

    # 3. Add examples
    examples = await self.generate_examples(concept)

    return {
        "explanation": simplified,
        "examples": examples,
        "level": level
    }
```

## Skill Template

```python
class BaseSkill:
    """Base class for all skills."""

    name: str = "base_skill"
    description: str = "A reusable skill"
    triggers: list[str] = []

    def __init__(self, backend_client):
        self.backend = backend_client

    def should_activate(self, message: str) -> bool:
        """Check if skill should activate."""
        raise NotImplementedError

    async def execute(self, **kwargs):
        """Execute the skill."""
        raise NotImplementedError
```

## Example Skills

### 1. Concept Explainer

```python
class ConceptExplainerSkill(BaseSkill):
    """Explains concepts at learner's level."""

    name = "concept-explainer"
    description = "Explain concepts at various complexity levels"
    triggers = ["explain", "what is", "how does"]

    def should_activate(self, message: str) -> bool:
        return any(t in message.lower() for t in self.triggers)

    async def execute(self, concept: str, complexity: str = "medium"):
        # Search for content
        results = await self.backend.search(concept)

        if not results:
            return self.generate_fallback_explanation(concept)

        # Get full content
        chapter = await self.backend.get_chapter(results[0]["id"])

        # Adjust complexity
        explanation = self.adjust_complexity(
            chapter["content"],
            complexity
        )

        # Add analogies
        analogies = self.generate_analogies(concept)

        return {
            "concept": concept,
            "explanation": explanation,
            "analogies": analogies,
            "complexity": complexity
        }

    def adjust_complexity(self, content: str, level: str) -> str:
        """Simplify or elaborate content based on level."""
        if level == "beginner":
            # Remove jargon, add simple examples
            return self.simplify(content)
        elif level == "advanced":
            # Add technical details
            return self.elaborate(content)
        return content
```

### 2. Quiz Master

```python
class QuizMasterSkill(BaseSkill):
    """Conducts quizzes with immediate feedback."""

    name = "quiz-master"
    description = "Conduct quizzes and track progress"
    triggers = ["quiz", "test me", "practice"]

    def should_activate(self, message: str) -> bool:
        return any(t in message.lower() for t in self.triggers)

    async def execute(self, topic: str = None):
        # Get available quizzes
        quizzes = await self.backend.list_quizzes()

        if topic:
            # Find quiz for topic
            quiz = self.find_quiz(quizzes, topic)
        else:
            # Use first available quiz
            quiz = quizzes[0]

        # Present quiz
        return await self.present_quiz(quiz)

    async def present_quiz(self, quiz):
        """Present quiz one question at a time."""
        questions = quiz["questions"]

        for i, question in enumerate(questions):
            yield {
                "question": i + 1,
                "total": len(questions),
                "text": question["text"],
                "options": question["options"]
            }

            # Wait for answer
            answer = await self.get_answer()

            # Provide feedback
            if answer == question["correct_answer"]:
                yield {"feedback": "✅ Correct!"}
            else:
                yield {
                    "feedback": "❌ Not quite.",
                    "explanation": question["explanation"]
                }
```

### 3. Socratic Tutor

```python
class SocraticTutorSkill(BaseSkill):
    """Guides learning through questioning."""

    name = "socratic-tutor"
    description = "Guide through questioning (don't give direct answers)"
    triggers = ["stuck", "help me think", "give me a hint"]

    def should_activate(self, message: str) -> bool:
        return any(t in message.lower() for t in self.triggers)

    async def execute(self, problem: str):
        """Guide student to solution through questions."""

        context = [{
            "role": "system",
            "content": "You are a Socratic tutor. Never give direct answers. Always ask guiding questions."
        }]

        max_turns = 5
        for turn in range(max_turns):
            # Generate question
            response = await self.llm.chat(context + [
                {"role": "user", "content": f"Student says: {problem}"}
            ])

            question = response["content"]
            yield {"question": question}

            # Get student response
            answer = await self.get_student_input()

            # Check if they got it
            if self.is_correct_insight(answer):
                return {"success": True, "message": "🎉 Exactly! You got it!"}

            # Continue with follow-up question
            context.append({"role": "assistant", "content": question})
            context.append({"role": "user", "content": answer})

        return {"hint": "Here's a small hint..."}
```

## Skill Loader

```python
class SkillLoader:
    """Loads and manages skills."""

    def __init__(self, backend_client):
        self.skills = {}
        self.backend = backend_client

    def register(self, skill_class):
        """Register a skill."""
        skill = skill_class(self.backend)
        self.skills[skill.name] = skill

    def load_all(self):
        """Load all available skills."""
        self.register(ConceptExplainerSkill)
        self.register(QuizMasterSkill)
        self.register(SocraticTutorSkill)
        self.register(ProgressMotivatorSkill)

    def detect_intent(self, message: str) -> str:
        """Detect which skill should handle the message."""
        for name, skill in self.skills.items():
            if skill.should_activate(message):
                return name
        return None

    async def execute(self, skill_name: str, **kwargs):
        """Execute a skill by name."""
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")

        return await self.skills[skill_name].execute(**kwargs)
```

## Using Skills in an Agent

```python
class SmartAgent:
    """Agent with skill system."""

    def __init__(self, backend_client):
        self.skill_loader = SkillLoader(backend_client)
        self.skill_loader.load_all()

    async def process(self, user_message: str):
        """Process user message with appropriate skill."""

        # Detect intent
        skill_name = self.skill_loader.detect_intent(user_message)

        if not skill_name:
            # No specific skill, use general conversation
            return await self.general_response(user_message)

        # Execute skill
        result = await self.skill_loader.execute(
            skill_name,
            message=user_message
        )

        return result
```

## Best Practices

### 1. Single Responsibility
Each skill should do ONE thing well.

❌ Bad: `TeachingSkill` (explains, quizzes, tracks progress)
✅ Good: `ConceptExplainer`, `QuizMaster`, `ProgressTracker`

### 2. Clear Triggers
Make it obvious when a skill should activate.

```python
# Good triggers
triggers = ["quiz", "test me", "practice", "check my knowledge"]

# Bad triggers
triggers = ["learn"]  # Too vague
```

### 3. Graceful Fallbacks
What if the skill can't complete?

```python
async def execute(self, **kwargs):
    try:
        return await self.do_work(**kwargs)
    except Exception as e:
        return {
            "error": f"Skill failed: {str(e)}",
            "suggestion": "Try rephrasing your request"
        }
```

### 4. Progress Indicators
Long-running skills should show progress.

```python
async def execute(self, **kwargs):
    yield {"status": "starting"}

    # Do work
    yield {"status": "processing", "progress": 50}

    # Finish
    yield {"status": "complete", "result": ...}
```

## Testing Skills

```python
# Unit test
async def test_concept_explainer():
    skill = ConceptExplainerSkill(mock_backend)

    assert skill.should_activate("Explain MCP")
    assert not skill.should_activate("Hello")

    result = await skill.execute("MCP", complexity="beginner")
    assert "explanation" in result
    assert "analogies" in result
```

## Distributing Skills

Package skills as Python modules:

```
skills/
├── __init__.py
├── concept_explainer.py
├── quiz_master.py
├── socratic_tutor.py
└── progress_motivator.py
```

Install via pip:
```bash
pip install course-companion-skills
```

## Summary

Skills are the building blocks of capable agents. By designing reusable, composable skills, you can quickly build sophisticated AI systems.

In the next chapter, we'll explore how to connect agents to real-world data sources!
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
                    "type": "true_false",
                    "correct_answer": True,
                    "explanation": "True. Skills can be packaged as Python modules and distributed independently, allowing others to use them in their own agents."
                }
            ]
        }
    }
]

def populate_database():
    """Populate database with chapters and quizzes."""
    with Session(engine) as session:
        for chapter_data in CHAPTERS_DATA:
            # Check if chapter already exists
            existing = session.query(Chapter).filter(
                Chapter.order == chapter_data["order"]
            ).first()

            if existing:
                print(f"✓ Chapter {chapter_data['order']} already exists: {existing.title}")
                chapter = existing
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
                session.flush()
                print(f"✓ Created chapter: {chapter.title}")

            # Create quiz
            quiz_data = chapter_data["quiz"]
            existing_quiz = session.query(Quiz).filter(
                Quiz.chapter_id == chapter.id
            ).first()

            if existing_quiz:
                print(f"  ✓ Quiz already exists")
                quiz = existing_quiz
            else:
                quiz = Quiz(
                    chapter_id=chapter.id,
                    title=f"{chapter.title} - Quiz"
                )
                session.add(quiz)
                session.flush()
                print(f"  ✓ Created quiz")

            # Add questions
            for q_data in quiz_data["questions"]:
                existing_question = session.query(Question).filter(
                    Question.quiz_id == quiz.id,
                    Question.question == q_data["question"]
                ).first()

                if existing_question:
                    print(f"    ✓ Question already exists")
                    continue

                question = Question(
                    quiz_id=quiz.id,
                    question=q_data["question"],
                    question_type=q_data["type"],
                    options=json.dumps(q_data.get("options", [])),
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data.get("explanation", "")
                )
                session.add(question)
                print(f"    ✓ Added question")

            # Link quiz to chapter
            chapter.quiz_id = quiz.id

        session.commit()
        print("\n✅ Database populated successfully!")

if __name__ == "__main__":
    import json
    populate_database()

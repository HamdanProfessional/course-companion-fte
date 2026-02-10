#!/usr/bin/env python3
"""Update Chapter 1 content with comprehensive material."""

import asyncio
from sqlalchemy import update
from src.core.database import async_session_maker
from src.models.database import Chapter

# Comprehensive content for Chapter 1
NEW_CONTENT = """# Introduction to AI Agents

## What are AI Agents?

AI agents are software systems that can autonomously perform tasks in pursuit of goals. Unlike traditional programs that follow fixed instructions, AI agents can perceive their environment, reason about it, make decisions, and take actions to achieve their objectives.

### A Simple Definition

An AI agent is a system that:
- **Perceives** its environment through data, APIs, and user inputs
- **Reasons** about the situation using AI models
- **Acts** to achieve specific goals through tools and APIs
- **Learns** from experience to improve performance

## A Brief History

AI agents have evolved significantly over the decades:

### 1950s-1970s: Symbolic AI Agents
- Early chess-playing agents
- Problem-solving systems like General Problem Solver
- Expert systems that encoded human knowledge

### 1980s-1990s: Reactive Agents
- Rodney Brooks' subsumption architecture
- Behavior-based robots
- Simple rule-based agents

### 2000s-2010s: Learning Agents
- Reinforcement learning agents (AlphaGo)
- Multi-agent systems
- Autonomous vehicles

### 2020s-Present: Large Language Model Agents
- ChatGPT and Claude as conversational agents
- Tool-using agents with function calling
- Multi-step reasoning agents
- Collaborative agent systems

## Key Characteristics of Modern AI Agents

### 1. Autonomy
AI agents operate without constant human intervention. Once given a goal, they can:
- Plan their own actions
- Make decisions based on available information
- Adapt to changing circumstances
- Execute tasks independently

### 2. Perception
Agents gather information through multiple sources:
- **APIs**: Access external services and databases
- **Databases**: Query structured and unstructured data
- **Web Scraping**: Gather real-time information from the internet
- **User Input**: Receive direct commands and feedback
- **Sensors**: Interact with physical environments (for robotics)
- **Tools**: Use specialized utilities and functions

### 3. Reasoning
Using AI models (especially Large Language Models), agents can:
- Analyze complex situations and break down problems
- Generate multiple potential solutions
- Evaluate trade-offs between options
- Chain together multiple reasoning steps
- Handle uncertainty and ambiguity
- Learn from past experiences

### 4. Action
Agents execute actions through various means:
- **Function Calling**: Invoke predefined tools and APIs
- **API Requests**: Make HTTP requests to external services
- **Code Execution**: Write and run programs dynamically
- **User Communication**: Provide natural language responses
- **Tool Composition**: Combine multiple tools together

## Architecture of an AI Agent

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                    AI AGENT                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────┐      ┌────────────┐    ┌─────────┐ │
│  │ Perception│  →   │  Reasoning │  → │  Action │ │
│  │  Layer    │      │    Engine  │    │  Layer  │ │
│  └───────────┘      └────────────┘    └─────────┘ │
│       ↓                   ↓                 ↓        │
│  ┌───────────┐      ┌────────────┐    ┌─────────┐ │
│  │  Sensors  │      │ LLM / AI   │    │  Tools  │ │
│  │   & APIs  │      │   Models   │    │  & APIs │ │
│  └───────────┘      └────────────┘    └─────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │         Memory & Context Management           │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 1. Perception Layer
- Collects data from various sources
- Normalizes and filters information
- Maintains a current view of the environment

### 2. Reasoning Engine
- The "brain" of the agent
- Uses LLMs or other AI models
- Plans and makes decisions
- Handles multi-step reasoning

### 3. Action Layer
- Executes the decisions made by reasoning
- Invokes tools and APIs
- Handles errors and retries
- Returns results to users or systems

### 4. Memory & Context
- Short-term memory (conversation history)
- Long-term memory (knowledge base)
- Context management across sessions
- Learning from past interactions

## Types of AI Agents

### By Capability

**1. Simple Reflex Agents**
- Respond only to current perceptions
- No memory of past states
- Best for: Simple, predictable tasks

**2. Model-Based Reflex Agents**
- Maintain internal model of the world
- Can handle partially observable environments
- Best for: Tasks requiring some context

**3. Goal-Based Agents**
- Have defined goals to achieve
- Can plan sequences of actions
- Best for: Complex planning tasks

**4. Utility-Based Agents**
- Maximize a utility function
- Make trade-offs between competing goals
- Best for: Decision-making under uncertainty

**5. Learning Agents**
- Improve performance over time
- Adapt to new environments
- Best for: Dynamic, changing situations

### By Application Domain

**1. Conversational Agents**
- Chatbots and virtual assistants
- Customer service representatives
- Language tutors and translators

**2. Task Automation Agents**
- Data processing and analysis
- Report generation
- Workflow automation

**3. Creative Agents**
- Content generation (writing, art, music)
- Design assistance
- Brainstorming partners

**4. Research Agents**
- Information gathering and synthesis
- Literature review
- Data analysis and pattern discovery

**5. Collaboration Agents**
- Coordinate team activities
- Schedule and resource management
- Project tracking

## Real-World Examples

### Customer Service Bots
- **What they do**: Handle customer inquiries 24/7
- **Capabilities**: Answer FAQs, process returns, escalate complex issues
- **Benefits**: Reduced wait times, consistent responses, cost savings

### Research Assistants
- **What they do**: Find and analyze information from multiple sources
- **Capabilities**: Web search, paper summarization, citation management
- **Benefits**: Faster research, comprehensive coverage, insight discovery

### Code Review Agents
- **What they do**: Analyze code quality and suggest improvements
- **Capabilities**: Bug detection, style checking, security scanning
- **Benefits**: Higher code quality, fewer bugs, security improvements

### Personal Assistants
- **What they do**: Manage schedules, tasks, and communications
- **Capabilities**: Calendar management, email triage, task prioritization
- **Benefits**: Better time management, reduced stress, increased productivity

### Educational Tutors
- **What they do**: Provide personalized learning experiences
- **Capabilities**: Explain concepts, quiz students, track progress
- **Benefits**: Individualized pacing, immediate feedback, accessible education

## The Rise of LLM-Powered Agents

Large Language Models (like GPT-4, Claude) have revolutionized AI agents:

### Why LLMs Are Game-Changers

**1. Natural Language Understanding**
- Agents can understand complex instructions
- No need for rigid command structures
- Better user experience

**2. Reasoning Capabilities**
- Multi-step problem solving
- Abstract thinking and planning
- Handling of nuance and context

**3. Tool Use**
- Function calling allows agents to use APIs
- Can write and execute code
- Compose multiple tools together

**4. Few-Shot Learning**
- Learn from examples
- Adapt to new tasks quickly
- No extensive training needed

## The AI Agent Ecosystem

### Model Context Protocol (MCP)

MCP is a new standard for connecting AI agents to data sources:

- **Standardized Interface**: Consistent way to access tools and data
- **Server-Client Model**: Agents connect to MCP servers for capabilities
- **Extensible**: Easy to add new tools and data sources
- **Secure**: Fine-grained access control

We'll explore MCP in detail in Chapter 2!

### Agent Frameworks

Popular frameworks for building agents:
- **LangChain**: Composable LLM applications
- **AutoGPT**: Autonomous agent creation
- **CrewAI**: Multi-agent collaboration
- **Claude Code**: Software development agents

## Building Blocks of an Agent

### 1. Tools and Functions
Tools are the capabilities an agent can use:
- Web search
- Database queries
- API calls
- Code execution
- File operations

### 2. Prompts and Instructions
The agent's behavior is guided by:
- System prompts (role and behavior)
- Task instructions (what to do)
- Few-shot examples (how to do it)
- Output format (what to return)

### 3. Memory and Context
Agents need to remember:
- Conversation history
- Task state
- Intermediate results
- User preferences

### 4. Planning and Execution
Agents work through tasks by:
1. Understanding the goal
2. Breaking it into steps
3. Executing each step
4. Evaluating results
5. Adjusting as needed

## The Future of AI Agents

### Emerging Trends

**1. Multi-Agent Systems**
- Specialized agents working together
- Collaborative problem solving
- Agent societies and economies

**2. Autonomous Agents**
- Self-directed goal setting
- Continuous learning
- Environmental exploration

**3. Human-Agent Collaboration**
- Agents as team members
- Augmenting human capabilities
- Shared workspaces

**4. Physical Agents**
- Robotics integration
- Real-world manipulation
- Embodied intelligence

### Challenges to Address

**Safety and Reliability**
- Ensuring agents behave as intended
- Handling edge cases gracefully
- Preventing harmful actions

**Privacy and Security**
- Protecting sensitive data
- Preventing unauthorized access
- Secure tool usage

**Transparency**
- Understanding agent decisions
- Explainable AI
- Accountability

**Performance**
- Reducing latency
- Scaling to complex tasks
- Cost optimization

## What You'll Learn in This Course

By the end of this course, you will:
- ✅ Understand how AI agents work
- ✅ Build your first functional agent
- ✅ Create reusable skills for your agents
- ✅ Connect agents to external data and APIs
- ✅ Deploy agents to production

Let's begin your journey into AI agent development!

---

### Key Takeaways from Chapter 1

1. **AI Agents** are autonomous systems that perceive, reason, and act
2. **Modern agents** are powered by Large Language Models
3. **MCP** provides a standard way to connect agents to tools and data
4. **Agents have four key components**: Perception, Reasoning, Action, Memory
5. **Many types** of agents exist, each suited for different tasks
6. **The future** holds multi-agent systems and greater autonomy

### Discussion Questions

1. What kind of AI agent would be most useful in your daily life?
2. How might AI agents change the way we work in the next 5 years?
3. What are some ethical considerations when building autonomous agents?

---

**Next Chapter:** Understanding MCP (Model Context Protocol) - The standard for connecting AI agents to the world.
"""

async def update_chapter():
    async with async_session_maker() as session:
        result = await session.execute(
            update(Chapter)
            .where(Chapter.order == 1)
            .values(content=NEW_CONTENT)
        )
        await session.commit()
        print('Chapter 1 content updated successfully!')
        print(f'Updated {result.rowcount} row(s)')

if __name__ == "__main__":
    asyncio.run(update_chapter())

#!/usr/bin/env python3
"""Update all chapters with comprehensive content."""

import asyncio
from sqlalchemy import update
from src.core.database import async_session_maker
from src.models.database import Chapter

# Chapter 2: Understanding MCP
CHAPTER_2_CONTENT = """# Understanding MCP (Model Context Protocol)

## Overview

The Model Context Protocol (MCP) is an open standard that enables AI models to securely connect to external data sources and tools, providing a unified interface for AI agents to access diverse systems.

## What is MCP?

MCP bridges the gap between AI models and the real world by providing:

- **Standardized interfaces** - Connect to any data source
- **Security boundaries** - Control what AI can access
- **Type safety** - Predictable, structured interactions
- **Extensibility** - Easy to add new capabilities

## Key Concepts

### 1. Servers

MCP servers expose resources and tools to AI clients.

**What MCP Servers Do:**
- Host data and tools for AI agents to use
- Provide type-safe interfaces through schemas
- Handle authentication and authorization
- Manage access control and permissions

**Server Types:**
- **File System Servers** - Read/write files
- **Database Servers** - Query databases
- **API Servers** - Connect to external services
- **Memory Servers** - Store conversation context
- **Tool Servers** - Execute specific functions

**Server Structure:**
```
MCP Server
├── Capabilities (what it can do)
├── Resources (data it provides)
├── Tools (actions it can perform)
└── Prompts (instruction templates)
```

### 2. Resources

Resources are data sources that AI can read:

**Types of Resources:**
- **Files** - Text, code, documents
- **Database Records** - Structured data
- **API Responses** - Real-time data
- **Memory** - Stored context and state
- **Configurations** - Settings and preferences

**Resource Operations:**
- **list** - Enumerate available resources
- **read** - Get resource contents
- **subscribe** - Watch for changes
- **templates** - Define resource schemas

**Example Resource:**
```python
{
  "uri": "file:///home/user/project/README.md",
  "name": "Project README",
  "description": "Project documentation",
  "mimeType": "text/markdown"
}
```

### 3. Tools

Tools are actions AI can execute:

**Common Tool Types:**
- **File Operations** - Read, write, search files
- **Code Execution** - Run Python, JavaScript, etc.
- **API Calls** - Invoke web services
- **Database Queries** - SQL operations
- **Data Processing** - Transform and analyze

**Tool Definition:**
```python
{
  "name": "read_file",
  "description": "Read a file's contents",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {"type": "string"},
      "encoding": {"type": "string"}
    },
    "required": ["path"]
  }
}
```

### 4. Prompts

Prompts are reusable instruction templates:

**Why Use Prompt Templates?**
- Consistency across agent interactions
- Reduced token usage
- Easier maintenance
- Better agent behavior

**Prompt Template Example:**
```python
{
  "name": "code_review",
  "description": "Review code for issues",
  "arguments": {
    "language": "python",
    "focus": ["security", "style", "performance"]
  }
}
```

## MCP Architecture

### Client-Server Model

```
┌─────────────────────────────────────────────────────────┐
│                     AI Agent                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │              MCP Client                           │    │
│  └─────────────────────────────────────────────────┘    │
│         │                    │                    │         │
└─────────┼────────────────────┼────────────────────┼─────┘
          │                    │                    │
          ▼                    ▼                    ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │   File   │         │Database │         │   API   │
    │  Server │         │ Server  │         │ Server  │
    └─────────┘         └─────────┘         └─────────┘
```

### Communication Flow

1. **Discovery** - Client finds available servers
2. **Connection** - Client establishes connection
3. **Capability Exchange** - Server advertises capabilities
4. **Resource/Tool Access** - Client uses resources and tools
5. **Response** - Server returns results

## MCP Benefits

### For Developers

**Simplified Integration**
- Standard protocol, no custom APIs
- Works with any LLM provider
- Easy to add new data sources

**Security-First Design**
- Fine-grained access control
- Resource-level permissions
- Audit logging

**Type-Safe Interfaces**
- JSON Schema validation
- Clear input/output contracts
- Better developer experience

**Easy Testing**
- Mock servers for testing
- Local development
- Clear error messages

### For Users

**Privacy Control**
- Choose what data to share
- Local-first options available
- Data stays on your device

**Reliable Responses**
- Structured data access
- Error handling built-in
- Consistent behavior

**Provider Flexibility**
- Switch AI providers easily
- Mix and match services
- No vendor lock-in

**Full Transparency**
- See what data is accessed
- Understand AI decisions
- Control agent behavior

## MCP Implementation

### Basic Server Example

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("my-server")

@server.list_resources()
async def list_resources() -> list:
    return [
        {
            "uri": "config:///settings",
            "name": "Settings",
            "description": "Application settings",
            "mimeType": "application/json"
        }
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "config:///settings":
        return '{"theme": "dark"}'
    raise ValueError(f"Unknown resource: {uri}")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "get_time":
        return datetime.now().isoformat()
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as streams:
        await server.run(
            streams[0], streams[1], server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Client Usage

```python
from mcp.client import Client

async def use_mcp_server():
    client = Client()
    await client.connect_to_server(stdio_path)

    # List available resources
    resources = await client.list_resources()
    for resource in resources:
        print(f"Resource: {resource['name']}")

    # Read a resource
    content = await client.read_resource("config:///settings")

    # Call a tool
    result = await client.call_tool("get_time", {})
    print(f"Current time: {result}")
```

## Security Model

### Access Control

**Resource-Level Permissions:**
- Read-only vs read-write
- Path-based restrictions
- Regular expression patterns

**Tool Permissions:**
- Whitelist approach
- Parameter validation
- Rate limiting

**Authentication:**
- Token-based auth
- OAuth 2.0 integration
- API key validation

### Data Privacy

**Local-First Options:**
- Run servers locally
- No data leaves your machine
- Full control over your data

**Encrypted Communication:**
- TLS for transport security
- End-to-end encryption support
- Secure credential storage

## MCP in the Claude Ecosystem

### Claude Code Integration

Claude Code uses MCP to:
- Access your codebase
- Read and write files
- Execute commands
- Run tests

### Custom MCP Servers

You can create MCP servers for:
- **Your proprietary data**
- **Internal tools**
- **Custom integrations**
- **Business logic**

## Getting Started with MCP

### Installation

```bash
# Python SDK
pip install mcp

# JavaScript SDK
npm install @modelcontextprotocol/sdk
```

### Create Your First Server

```bash
# Using the MCP CLI
mcp init my-server
cd my-server
mcp dev
```

### Connect from Your Agent

Your agent automatically discovers and uses MCP servers that are:
1. Running and accessible
2. Properly configured
3. Within security permissions

## Best Practices

### Server Design

**1. Keep Servers Focused**
- One purpose per server
- Clear, specific capabilities
- Easy to understand and maintain

**2. Use Descriptive Names**
- Clear resource names
- Meaningful tool descriptions
- Intuitive prompt templates

**3. Implement Proper Error Handling**
- Validate all inputs
- Return clear error messages
- Log errors appropriately

**4. Document Your Interfaces**
- Schema documentation
- Usage examples
- Security considerations

### Security Considerations

**1. Principle of Least Privilege**
- Only expose necessary resources
- Limit tool capabilities
- Require authentication for sensitive operations

**2. Validate All Inputs**
- Check parameter types
- Validate ranges and formats
- Sanitize file paths

**3. Monitor Usage**
- Log access patterns
- Detect anomalies
- Set up alerts

## Advanced Topics

### Resource Templates

Define reusable resource patterns:

```python
{
  "uri": "git:///{repo}/{file}",
  "name": "{repo} - {file}",
  "type": "git_file"
}
```

### Tool Composition

Chain multiple tools together:

```python
async def analyze_project():
    files = await call_tool("list_files", {"path": "."})
    for file in files:
        content = await call_tool("read_file", {"path": file})
        analysis = await call_tool("analyze_code", {"code": content})
```

### Streaming Resources

Handle large resources efficiently:

```python
async def stream_resource(uri: str):
    async for chunk in server.read_resource_stream(uri):
        yield chunk
```

## Troubleshooting

### Common Issues

**Server Not Discoverable:**
- Check server is running
- Verify transport configuration
- Check firewall settings

**Permission Denied:**
- Verify resource permissions
- Check authentication tokens
- Review access control rules

**Tool Execution Failed:**
- Validate input parameters
- Check tool implementation
- Review server logs

## MCP vs Alternatives

| Feature | MCP | Custom API | LangChain Tools |
|---------|-----|------------|-----------------|
| Standardization | ✅ Yes | ❌ No | ⚠️ Partial |
| Type Safety | ✅ Built-in | ❌ Manual | ⚠️ Optional |
| Security Model | ✅ Integrated | ❌ Manual | ⚠️ Add-on |
| Multi-Language | ✅ Yes | ❌ No | ⚠️ Python-first |
| AI-Native | ✅ Yes | ❌ No | ✅ Yes |

## Real-World MCP Use Cases

### 1. Code Analysis Agent

**MCP Servers:**
- Git server (repository access)
- File system server (code files)
- Linting server (code quality)
- Testing server (run tests)

### 2. Research Assistant

**MCP Servers:**
- ArXiv server (papers)
- Web search server
- Citation database server
- Note-taking server

### 3. Business Intelligence Agent

**MCP Servers:**
- Database server (SQL queries)
- Spreadsheet server (Excel files)
- Dashboard server (metrics)
- Report server (generate PDFs)

## What's Next?

Now that you understand MCP, you're ready to:
- Build your first MCP server
- Connect agents to your data
- Create custom tools
- Implement secure access controls

---

### Key Takeaways

1. **MCP** is an open standard for connecting AI to data and tools
2. **Servers** expose resources and tools through a unified interface
3. **Security** is built-in with granular access control
4. **Type safety** ensures predictable interactions
5. **Local-first** options protect your privacy
6. **Extensible** design makes it easy to add capabilities

---

**Next Chapter:** Creating Your First Agent - Put your knowledge into practice!
"""

# Chapter 3: Creating Your First Agent
CHAPTER_3_CONTENT = """# Creating Your First Agent

## Overview

In this chapter, you'll build your first functional AI agent from scratch. We'll use Python and Claude Code's agent framework to create an agent that can read files, answer questions, and perform tasks.

## Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher installed
- An Anthropic API key for Claude
- Basic understanding of Python
- Text editor or IDE

## Setting Up Your Environment

### Installation

```bash
# Create a project directory
mkdir my-first-agent
cd my-first-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install anthropic mcp python-dotenv
```

### Project Structure

```
my-first-agent/
├── agent.py          # Main agent code
├── tools.py          # Tool definitions
├── prompts.py        # Prompt templates
├── .env              # Environment variables
└── requirements.txt  # Dependencies
```

## Understanding Agent Architecture

### Basic Components

```
┌─────────────────────────────────────┐
│           AI Agent                  │
├─────────────────────────────────────┤
│                                     │
│  1. Perception Layer                │
│     - Receive user input           │
│     - Understand goal               │
│     - Gather context               │
│                                     │
│  2. Reasoning Engine               │
│     - LLM (Claude)                 │
│     - Plan steps                   │
│     - Make decisions               │
│                                     │
│  3. Action Layer                   │
│     - Call tools                   │
│     - Execute functions            │
│     - Return results               │
│                                     │
└─────────────────────────────────────┘
```

### Data Flow

1. **User Request** → Agent receives input
2. **Goal Analysis** → Understand what to do
3. **Planning** → Break down into steps
4. **Tool Selection** → Choose appropriate tools
5. **Execution** → Run tools in sequence
6. **Response** → Return result to user

## Your First Agent: Step by Step

### Step 1: Create the Agent Skeleton

```python
# agent.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class SimpleAgent:
    """A simple AI agent that can read files and answer questions."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tools = {}
        self.context = []

    def register_tool(self, name, func, description):
        """Register a tool that the agent can use."""
        self.tools[name] = {
            "function": func,
            "description": description
        }

    async def chat(self, user_message):
        """Process a user message and return a response."""
        # Add user message to context
        self.context.append({
            "role": "user",
            "content": user_message
        })

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=self.context,
            max_tokens=1024
        )

        assistant_message = response.content[0].text
        self.context.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message
```

### Step 2: Add Tool Capabilities

```python
# tools.py
import os

def read_file(filepath: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {e}"

def list_files(directory: str = ".") -> list:
    """List files in a directory."""
    try:
        return os.listdir(directory)
    except Exception as e:
        return f"Error listing directory: {e}"

def write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"

def search_files(pattern: str, directory: str = ".") -> list:
    """Search for files matching a pattern."""
    import glob
    try:
        return glob.glob(os.path.join(directory, pattern))
    except Exception as e:
        return f"Error searching: {e}"
```

### Step 3: Connect Tools to Your Agent

```python
# agent.py (continued)
from tools import read_file, list_files, write_file, search_files

class SimpleAgent:
    """A simple AI agent that can read files and answer questions."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tools = {
            "read_file": {
                "function": read_file,
                "description": "Read a file and return its contents. Args: filepath (str)"
            },
            "list_files": {
                "function": list_files,
                "description": "List files in a directory. Args: directory (str, optional)"
            },
            "write_file": {
                "function": write_file,
                "description": "Write content to a file. Args: filepath (str), content (str)"
            },
            "search_files": {
                "function": search_files,
                "description": "Search for files matching a pattern. Args: pattern (str), directory (str)"
            }
        }
        self.context = []

    def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool and return the result."""
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"

        tool = self.tools[tool_name]
        try:
            result = tool["function"](**kwargs)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {e}"

    async def chat(self, user_message: str) -> str:
        """Process a user message with tool use."""
        self.context.append({
            "role": "user",
            "content": user_message
        })

        # Check if user wants to use a tool
        available_tools = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])

        # Create system prompt with tool information
        system_prompt = f"""You are a helpful AI assistant with access to tools.

Available tools:
{available_tools}

When the user asks for something that requires a tool, respond with:
TOOL: <tool_name>
ARGS: <json_arguments>

Then wait for the tool result and provide a helpful response based on the result."""

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=self.context,
            max_tokens=1024
        )

        assistant_text = response.content[0].text

        # Check if Claude wants to use a tool
        if assistant_text.startswith("TOOL:"):
            # Parse tool call
            lines = assistant_text.split("\n")
            tool_line = lines[0]
            tool_name = tool_line.replace("TOOL:", "").strip()

            # Parse arguments
            args = {}
            if len(lines) > 1 and lines[1].startswith("ARGS:"):
                import json
                args_str = lines[1].replace("ARGS:", "").strip()
                args = json.loads(args_str)

            # Execute tool
            result = self.execute_tool(tool_name, **args)

            # Add tool result to context
            self.context.append({
                "role": "assistant",
                "content": assistant_text
            })
            self.context.append({
                "role": "user",
                "content": f"Tool result: {result}"
            })

            # Get final response
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=self.context,
                max_tokens=1024
            )

            assistant_text = response.content[0].text

        self.context.append({
            "role": "assistant",
            "content": assistant_text
        })

        return assistant_text
```

### Step 4: Create Your Main Application

```python
# main.py
import asyncio
from agent import SimpleAgent

async def main():
    """Run the interactive agent."""
    agent = SimpleAgent()

    print("🤖 Welcome to Your First AI Agent!")
    print("I can help you with files and answer questions.")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            print("Goodbye! 👋")
            break

        response = await agent.chat(user_input)
        print(f"Agent: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## Running Your Agent

```bash
# Set your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the agent
python main.py
```

### Example Interactions

```
You: What files are in the current directory?
Agent: TOOL: list_files
ARGS: {}
Tool result: ['agent.py', 'tools.py', 'main.py', '.env']
Agent: I can see the following files in the current directory:
- agent.py
- tools.py
- main.py
- .env

You: Read the main.py file
Agent: TOOL: read_file
ARGS: {"filepath": "main.py"}
Tool result: [file contents]
Agent: Here's what's in main.py: [summary]
```

## Improving Your Agent

### 1. Add Better Prompt Engineering

```python
system_prompt = """You are Claude, a helpful AI assistant.

Core Principles:
- Be concise and direct
- Use tools when available
- Explain your reasoning
- Handle errors gracefully

When using tools:
1. Always validate inputs
2. Handle edge cases
3. Provide clear results
4. Suggest next steps"""
```

### 2. Add Memory

```python
class SimpleAgent:
    def __init__(self):
        # ... existing code ...
        self.memory = {}  # Long-term memory

    def remember(self, key: str, value: any):
        """Store information in memory."""
        self.memory[key] = value

    def recall(self, key: str) -> any:
        """Retrieve information from memory."""
        return self.memory.get(key, None)
```

### 3. Add Error Handling

```python
async def chat(self, user_message: str) -> str:
    """Process a user message with robust error handling."""
    try:
        # ... existing logic ...
        pass
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        # Return a user-friendly error message
        return "I'm sorry, something went wrong. Please try again."
```

## Advanced Features

### Multi-Step Planning

```python
async def plan_and_execute(self, goal: str) -> str:
    """Plan and execute a complex goal."""
    # Step 1: Create a plan
    plan = await self.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": f"Create a step-by-step plan to: {goal}\n\nAvailable tools: {list(self.tools.keys())}"
        }],
        max_tokens=1024
    )

    plan_text = plan.content[0].text
    steps = self.parse_steps(plan_text)

    # Step 2: Execute each step
    results = []
    for step in steps:
        result = await self.execute_step(step)
        results.append(result)

    # Step 3: Provide summary
    return self.summarize_results(results)
```

### Parallel Tool Execution

```python
async def execute_tools_parallel(self, tool_calls: list) -> list:
    """Execute multiple tools concurrently."""
    import asyncio

    tasks = [
        self.execute_tool(call["name"], **call.get("args", {}))
        for call in tool_calls
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

## Testing Your Agent

### Unit Tests

```python
# test_agent.py
import pytest
from agent import SimpleAgent

@pytest.mark.asyncio
async def test_tool_registration():
    agent = SimpleAgent()
    assert "read_file" in agent.tools
    assert len(agent.tools) == 4

@pytest.mark.asyncio
async def test_file_reading():
    agent = SimpleAgent()
    result = agent.execute_tool("read_file", filepath="test.txt")
    assert "Error" not in result or "not found" in result
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_conversation():
    agent = SimpleAgent()

    response1 = await agent.chat("List files")
    assert "files" in response1.lower()

    response2 = await agent.chat("Read main.py")
    assert "main.py" in response2
```

## Deploying Your Agent

### Configuration

```python
# config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    max_tokens: int = 1024
    temperature: float = 0.7
    model: str = "claude-3-5-sonnet-20241022"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## Common Patterns

### Research Agent Pattern

```python
async def research_topic(topic: str):
    agent = SimpleAgent()

    # 1. Gather information
    files = agent.execute_tool("search_files", pattern=f"*{topic}*")

    # 2. Read relevant files
    for file in files:
        content = agent.execute_tool("read_file", filepath=file)
        # Process content

    # 3. Synthesize findings
    summary = await agent.chat(f"Summarize findings about: {topic}")
    return summary
```

### Code Assistant Pattern

```python
async def analyze_codebase():
    agent = SimpleAgent()

    # List all Python files
    files = agent.execute_tool("search_files", pattern="*.py", directory=".")

    # Analyze each file
    analyses = []
    for file in files:
        content = agent.execute_tool("read_file", filepath=file)
        analysis = await agent.chat(f"Analyze this code:\\n{content}")
        analyses.append(analysis)

    return analyses
```

## Troubleshooting

### Common Issues

**Agent Not Responding:**
- Check API key is valid
- Verify network connection
- Check rate limits

**Tools Not Working:**
- Verify tool functions are defined
- Check function signatures match
- Test tools independently

**Memory Issues:**
- Clear old context periodically
- Summarize long conversations
- Use memory instead of full context

## Best Practices

### 1. Keep It Simple

Start with basic functionality:
- One tool at a time
- Simple prompts
- Clear error messages

### 2. Iterate Quickly

- Get feedback early
- Test frequently
- Refine gradually

### 3. Monitor Usage

- Log agent interactions
- Track tool usage
- Measure performance

### 4. Handle Errors Gracefully

- Validate all inputs
- Provide clear error messages
- Offer recovery options

## What You Built

Congratulations! You now have:
- ✅ A working AI agent
- ✅ Tool use capabilities
- ✅ File system integration
- ✅ Interactive chat interface
- ✅ Foundation for advanced features

## Next Steps

In the next chapter, you'll learn to:
- Create reusable skills
- Share tools across agents
- Build specialized agents
- Deploy to production

---

### Key Takeaways

1. **Agents** have three layers: Perception, Reasoning, Action
2. **Tools** extend agent capabilities
3. **Context** maintains conversation state
4. **Planning** breaks down complex tasks
5. **Testing** ensures reliability
6. **Iteration** improves performance

---

**Next Chapter:** Building Reusable Skills - Create modular, shareable agent capabilities!
"""

# Chapter 4: Building Reusable Skills
CHAPTER_4_CONTENT = """# Building Reusable Skills

## Overview

Skills are modular, reusable capabilities that you can add to any AI agent. Instead of building monolithic agents, you create small, focused skills that can be mixed and matched like LEGO blocks.

## What are Skills?

A **skill** is a self-contained unit of functionality that:
- Has a specific purpose
- Can be used by any agent
- Handles its own errors
- Has clear inputs and outputs
- Is independently testable

### Skills vs Tools

| Aspect | Tools | Skills |
|--------|-------|--------|
| **Purpose** | Low-level operations | High-level behaviors |
| **Granularity** | Single function | Multi-step workflows |
| **Context** | Stateless | State-aware |
| **Example** | Read file | Analyze code quality |

### Why Build Skills?

**Reusability**
- Write once, use everywhere
- Consistent behavior across agents
- Easy maintenance

**Modularity**
- Clear boundaries
- Independent testing
- Flexible composition

**Collaboration**
- Share with team
- Community contributions
- Standard libraries

## Skill Architecture

### Basic Skill Structure

```python
class Skill:
    """Base class for all skills."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, context: dict) -> dict:
        """Execute the skill."""
        raise NotImplementedError

    def get_schema(self) -> dict:
        """Return the skill's input/output schema."""
        return {
            "name": self.name,
            "description": self.description,
            "inputs": {},
            "outputs": {}
        }
```

### Skill Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    Skill Lifecycle                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Registration → 2. Validation → 3. Execution →    │
│                     4. Result Processing                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Built-in Skills

### 1. FileReader Skill

```python
class FileReader(Skill):
    """Read files from the file system."""

    def __init__(self):
        super().__init__(
            name="file_reader",
            description="Read files from the file system with filtering"
        )

    async def execute(self, context: dict) -> dict:
        filepath = context.get("filepath")
        max_lines = context.get("max_lines", 100)

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()[:max_lines]
                content = "".join(lines)

            return {
                "success": True,
                "content": content,
                "lines_read": len(lines),
                "file_path": filepath
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"File not found: {filepath}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_schema(self) -> dict:
        return {
            **super().get_schema(),
            "inputs": {
                "filepath": {
                    "type": "string",
                    "required": True,
                    "description": "Path to the file to read"
                },
                "max_lines": {
                    "type": "integer",
                    "default": 100,
                    "description": "Maximum lines to read"
                }
            },
            "outputs": {
                "content": "string - File contents",
                "lines_read": "integer - Number of lines read"
            }
        }
```

### 2. CodeAnalyzer Skill

```python
class CodeAnalyzer(Skill):
    """Analyze code for issues and suggestions."""

    def __init__(self):
        super().__init__(
            name="code_analyzer",
            description="Analyze code quality and provide suggestions"
        )
        self.checks = [
            self._check_complexity,
            self._check_naming,
            self._check_documentation
        ]

    async def execute(self, context: dict) -> dict:
        code = context.get("code", "")
        language = context.get("language", "python")

        issues = []
        metrics = {}

        for check in self.checks:
            result = check(code, language)
            if result.get("issues"):
                issues.extend(result["issues"])
            metrics.update(result.get("metrics", {}))

        score = self._calculate_score(issues, metrics)

        return {
            "success": True,
            "score": score,
            "issues": issues,
            "metrics": metrics,
            "suggestions": self._generate_suggestions(issues)
        }

    def _check_complexity(self, code: str, language: str) -> dict:
        """Check code complexity."""
        lines = code.split("\n")
        complexity = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

        issues = []
        if complexity > 50:
            issues.append({
                "severity": "warning",
                "message": f"High complexity: {complexity} lines of code",
                "suggestion": "Consider breaking this into smaller functions"
            })

        return {"issues": issues, "metrics": {"complexity": complexity}}

    def _check_naming(self, code: str, language: str) -> dict:
        """Check naming conventions."""
        # Simplified naming check
        issues = []
        # Implementation would vary by language
        return {"issues": issues, "metrics": {}}

    def _check_documentation(self, code: str, language: str) -> dict:
        """Check for documentation."""
        lines = code.split("\n")
        docstring_lines = [l for l in lines if '"""' in l or "'''" in l]

        issues = []
        if not docstring_lines:
            issues.append({
                "severity": "info",
                "message": "No docstring found",
                "suggestion": "Add a docstring to explain the function's purpose"
            })

        return {"issues": issues, "metrics": {"has_docstring": bool(docstring_lines)}}

    def _calculate_score(self, issues: list, metrics: dict) -> float:
        """Calculate overall code quality score."""
        score = 100.0

        for issue in issues:
            severity = issue.get("severity", "info")
            if severity == "error":
                score -= 10
            elif severity == "warning":
                score -= 5
            elif severity == "info":
                score -= 1

        return max(0.0, score)

    def _generate_suggestions(self, issues: list) -> list:
        """Generate improvement suggestions."""
        return [issue.get("suggestion") for issue in issues if "suggestion" in issue]
```

### 3. WebSearch Skill

```python
class WebSearch(Skill):
    """Search the web for information."""

    def __init__(self, api_key: str = None):
        super().__init__(
            name="web_search",
            description="Search the web and return relevant results"
        )
        self.api_key = api_key

    async def execute(self, context: dict) -> dict:
        query = context.get("query", "")
        max_results = context.get("max_results", 5)

        # Implementation would use a search API
        # This is a simplified example
        results = [
            {
                "title": f"Result for '{query}'",
                "url": f"https://example.com/{query.replace(' ', '-')}",
                "snippet": f"This is a search result for {query}"
            }
            for _ in range(max_results)
        ]

        return {
            "success": True,
            "query": query,
            "results": results,
            "result_count": len(results)
        }
```

## Creating Custom Skills

### Step 1: Define the Skill

```python
class MyCustomSkill(Skill):
    """Your custom skill description."""

    def __init__(self):
        super().__init__(
            name="my_custom_skill",
            description="What this skill does"
        )
        # Initialize any resources
        pass

    async def execute(self, context: dict) -> dict:
        """Execute the skill logic."""
        # 1. Validate inputs
        # 2. Perform the task
        # 3. Return results
        return {
            "success": True,
            "result": "Task completed"
        }
```

### Step 2: Implement Validation

```python
class MyCustomSkill(Skill):
    """Your custom skill description."""

    def validate_input(self, context: dict) -> tuple[bool, str]:
        """Validate input parameters."""
        required_fields = ["param1", "param2"]

        for field in required_fields:
            if field not in context:
                return False, f"Missing required field: {field}"

        return True, ""

    async def execute(self, context: dict) -> dict:
        """Execute the skill logic."""
        # Validate inputs
        valid, error = self.validate_input(context)
        if not valid:
            return {
                "success": False,
                "error": error
            }

        # Execute skill logic
        result = await self._perform_task(context)

        return {
            "success": True,
            "result": result
        }
```

### Step 3: Add Error Handling

```python
class MyCustomSkill(Skill):
    """Your custom skill description."""

    async def execute(self, context: dict) -> dict:
        """Execute the skill logic with error handling."""
        try:
            result = await self._perform_task(context)
            return {
                "success": True,
                "result": result
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Validation error: {e}",
                "error_type": "validation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {e}",
                "error_type": "execution"
            }
```

## Skill Registry

### Managing Skills

```python
class SkillRegistry:
    """Manage available skills."""

    def __init__(self):
        self.skills = {}

    def register(self, skill: Skill):
        """Register a new skill."""
        self.skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        """Get a skill by name."""
        return self.skills.get(name)

    def list_all(self) -> list:
        """List all available skills."""
        return list(self.skills.values())

    def find(self, capability: str) -> list:
        """Find skills that provide a capability."""
        return [
            skill for skill in self.skills.values()
            if capability in skill.description.lower()
        ]
```

## Composing Skills

### Skill Chains

```python
async def execute_skill_chain(skills: list, context: dict) -> dict:
    """Execute multiple skills in sequence."""
    results = []
    current_context = context

    for skill in skills:
        result = await skill.execute(current_context)

        if not result.get("success"):
            return {
                "success": False,
                "failed_at": skill.name,
                "error": result.get("error"),
                "completed_results": results
            }

        results.append({
            "skill": skill.name,
            "result": result
        })

        # Update context for next skill
        current_context.update(result)

    return {
        "success": True,
        "all_results": results
    }
```

### Parallel Skills

```python
async def execute_skills_parallel(skills: list, context: dict) -> dict:
    """Execute multiple skills concurrently."""
    import asyncio

    tasks = [skill.execute(context) for skill in skills]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "success": True,
        "results": [
            {
                "skill": skill.name,
                "result": result
            }
            for skill, result in zip(skills, results)
        ]
    }
```

## Advanced Skill Patterns

### 1. Skills with Memory

```python
class MemorySkill(Skill):
    """Skill that maintains state across invocations."""

    def __init__(self):
        super().__init__(
            name="memory_skill",
            description="Remember and recall information"
        )
        self.memory = {}

    async def execute(self, context: dict) -> dict:
        action = context.get("action", "store")
        key = context.get("key")
        value = context.get("value")

        if action == "store":
            self.memory[key] = value
            return {"success": True, "stored": key}
        elif action == "recall":
            return {
                "success": key in self.memory,
                "value": self.memory.get(key)
            }
```

### 2. Skills with Tools

```python
class ToolUsingSkill(Skill):
    """Skill that uses tools to accomplish tasks."""

    def __init__(self, tools: dict):
        super().__init__(
            name="tool_using_skill",
            description="Uses multiple tools to complete tasks"
        )
        self.tools = tools

    async def execute(self, context: dict) -> dict:
        # Plan tool usage
        plan = self._create_plan(context)

        # Execute tools
        results = []
        for step in plan:
            tool_name = step["tool"]
            tool_args = step["args"]
            result = self.tools[tool_name](**tool_args)
            results.append(result)

        # Aggregate results
        return {
            "success": True,
            "tool_results": results,
            "final_result": self._aggregate(results)
        }
```

### 3. Skills with Validation

```python
class ValidatedSkill(Skill):
    """Skill with input and output validation."""

    def __init__(self):
        super().__init__(
            name="validated_skill",
            description="Validates all inputs and outputs"
        )
        self.input_schema = self._define_input_schema()
        self.output_schema = self._define_output_schema()

    def validate_input(self, data: dict) -> tuple[bool, str]:
        """Validate input against schema."""
        # Implementation
        return True, ""

    def validate_output(self, data: dict) -> tuple[bool, str]:
        """Validate output against schema."""
        # Implementation
        return True, ""

    async def execute(self, context: dict) -> dict:
        # Validate input
        valid, error = self.validate_input(context)
        if not valid:
            return {"success": False, "error": error}

        # Execute logic
        result = await self._perform_task(context)

        # Validate output
        valid, error = self.validate_output(result)
        if not valid:
            return {"success": False, "error": f"Output validation failed: {error}"}

        return {"success": True, "result": result}
```

## Skill Libraries

### Creating a Skill Library

```python
# skills/__init__.py
from .file_skills import FileReader, FileWriter
from .code_skills import CodeAnalyzer, CodeFormatter
from .web_skills import WebSearch, WebScraper
from .analysis_skills import SentimentAnalysis, Summarization

__all__ = [
    "FileReader",
    "FileWriter",
    "CodeAnalyzer",
    "CodeFormatter",
    "WebSearch",
    "WebScraper",
    "SentimentAnalysis",
    "Summarization"
]
```

### Using Skills

```python
from skills import FileReader, CodeAnalyzer
from agent import Agent

# Create agent with skills
agent = Agent()
agent.add_skill(FileReader())
agent.add_skill(CodeAnalyzer())

# Use agent
await agent.chat("Analyze the code in main.py")
```

## Testing Skills

### Unit Testing

```python
import pytest
from skills import CodeAnalyzer

@pytest.mark.asyncio
async def test_code_analyzer():
    skill = CodeAnalyzer()

    context = {
        "code": "def hello():\\n    print('hello')",
        "language": "python"
    }

    result = await skill.execute(context)

    assert result["success"] == True
    assert "score" in result
    assert result["score"] >= 0

@pytest.mark.asyncio
async def test_skill_validation():
    skill = CodeAnalyzer()

    # Missing required fields
    context = {}
    result = await skill.execute(context)

    assert result["success"] == False
    assert "error" in result
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_skill_in_agent():
    from agent import Agent
    from skills import FileReader

    agent = Agent()
    agent.add_skill(FileReader())

    response = await agent.chat("Read the README file")

    assert "README" in response
```

## Publishing Skills

### Package Structure

```
my-skills/
├── README.md
├── setup.py
├── skills/
│   ├── __init__.py
│   └── my_skill.py
├── tests/
│   ├── __init__.py
│   └── test_my_skill.py
└── pyproject.toml
```

### Publishing to PyPI

```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Best Practices

### 1. Keep Skills Focused

Each skill should do one thing well:
- ✅ CodeAnalyzer
- ❌ DevelopmentHelper (too broad)

### 2. Use Clear Names

Names should be descriptive:
- ✅ FileReader
- ❌ FileHandler (ambiguous)

### 3. Document Schemas

Always provide input/output schemas:
- Required fields
- Data types
- Validation rules

### 4. Handle Errors Gracefully

Always return structured errors:
- Error type
- Error message
- Recovery suggestions

### 5. Make Skills Testable

Design for easy testing:
- Pure functions when possible
- Clear inputs and outputs
- No hidden dependencies

## Advanced Topics

### Skill Discovery

```python
class SkillDiscovery:
    """Automatically discover available skills."""

    def __init__(self, skill_directories: list):
        self.skill_directories = skill_directories
        self.skills = {}

    def discover(self):
        """Discover all available skills."""
        for directory in self.skill_directories:
            for module in self._load_modules(directory):
                for skill in self._extract_skills(module):
                    self.skills[skill.name] = skill

    def get_skill(self, name: str):
        """Get a skill by name."""
        return self.skills.get(name)
```

### Skill Dependencies

```python
class DependentSkill(Skill):
    """Skill that depends on other skills."""

    def __init__(self, dependencies: list):
        super().__init__(
            name="dependent_skill",
            description="Requires other skills to function"
        )
        self.dependencies = dependencies

    async def execute(self, context: dict) -> dict:
        # Execute dependencies first
        for dep in self.dependencies:
            dep_result = await dep.execute(context)
            context.update(dep_result)

        # Execute this skill
        return await self._perform_task(context)
```

### Skill Orchestration

```python
class SkillOrchestrator:
    """Coordinate multiple skills."""

    async def orchestrate(self, goal: str, skills: list) -> dict:
        """Orchestrate skills to achieve a goal."""
        # 1. Plan skill usage
        plan = await self._create_plan(goal, skills)

        # 2. Execute plan
        results = []
        for step in plan:
            result = await step["skill"].execute(step["context"])
            results.append(result)

        # 3. Aggregate results
        return self._aggregate_results(results)
```

## What You've Learned

After completing this chapter, you can:
- ✅ Create reusable skills
- ✅ Compose skills together
- ✅ Test skills independently
- ✅ Share skills with others
- ✅ Build skill libraries
- ✅ Deploy skills to production

---

### Key Takeaways

1. **Skills** are modular, reusable capabilities
2. **Composition** allows flexible agent building
3. **Testing** ensures skill reliability
4. **Documentation** makes skills shareable
5. **Validation** prevents errors
6. **Libraries** enable collaboration

---

### Next Steps

You're now ready to:
- Build your own custom skills
- Create skill libraries
- Share skills with the community
- Build production-ready agents

**Congratulations on completing the course!** 🎉

You now have all the knowledge you need to build AI agents with MCP and Claude. Start creating amazing things!
"""

async def update_all_chapters():
    """Update all chapters with comprehensive content."""
    async with async_session_maker() as session:
        # Chapter 2
        result = await session.execute(
            update(Chapter)
            .where(Chapter.order == 2)
            .values(content=CHAPTER_2_CONTENT)
        )
        print(f"Chapter 2 updated: {result.rowcount} row(s)")

        # Chapter 3
        result = await session.execute(
            update(Chapter)
            .where(Chapter.order == 3)
            .values(content=CHAPTER_3_CONTENT)
        )
        print(f"Chapter 3 updated: {result.rowcount} row(s)")

        # Chapter 4
        result = await session.execute(
            update(Chapter)
            .where(Chapter.order == 4)
            .values(content=CHAPTER_4_CONTENT)
        )
        print(f"Chapter 4 updated: {result.rowcount} row(s)")

        await session.commit()
        print("\nAll chapters updated successfully!")

if __name__ == "__main__":
    asyncio.run(update_all_chapters())

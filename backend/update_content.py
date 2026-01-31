"""
Update course chapters with comprehensive content.
"""
import asyncio
import asyncpg
import uuid
import os

# Chapter content
CHAPTERS_CONTENT = {
    "Introduction to AI Agents": """
# Introduction to AI Agents

## What Are AI Agents?

AI Agents are autonomous systems that can:
- **Perceive** their environment through inputs
- **Reason** about what to do using logic or models
- **Act** by executing tasks or calling tools
- **Learn** from feedback to improve over time

Unlike traditional chatbots, agents can:
✓ Use external tools (APIs, databases, file systems)
✓ Maintain context over long conversations
✓ Break down complex goals into steps
✓ Self-correct when things go wrong

## The Agent Architecture

Every AI agent has three core components:

### 1. Planning (The Brain)
Decides what actions to take based on:
- User's goal
- Current context
- Available tools
- Past experience

**Example:** "User wants to book a flight" → Agent breaks this into: search flights → compare prices → present options → handle booking

### 2. Memory (The Context)
Stores and retrieves information:
- **Short-term**: Current conversation, recent actions
- **Long-term**: User preferences, historical data
- **Vector memory**: Semantic search for relevant past info

### 3. Tools (The Hands)
External capabilities the agent can use:
- APIs (weather, maps, email)
- File operations (read, write, search)
- Databases (query, update, delete)
- Custom functions (your code!)

## Why Agents Matter

**Traditional Chatbot:**
- Single interaction
- No memory
- No actions
- Limited to training data

**AI Agent:**
- Multi-step workflows
- Remembers everything
- Takes real actions
- Uses live data
""",
    "Understanding MCP (Model Context Protocol)": """
# Understanding MCP (Model Context Protocol)

## What is MCP?

MCP (Model Context Protocol) is an open standard that connects AI assistants to external data and tools. Think of it as a **universal USB-C for AI agents**.

### The Problem MCP Solves

Before MCP, every AI tool needed custom integration:
- ❌ Different APIs for each tool
- ❌ Custom authentication flows
- ❌ Inconsistent data formats
- ❌ Hard to combine multiple tools

With MCP:
- ✅ Standardized protocol
- ✅ Plug-and-play tools
- ✅ Consistent data handling
- ✅ Easy tool composition

## How MCP Works

### Architecture

```
┌─────────────┐         MCP          ┌──────────────┐
│   AI Agent  │ ←──────────────────→│   MCP Host   │
└─────────────┘                     └──────────────┘
                                            │
                                    ┌───────┴───────┐
                                    ↓               ↓
                              ┌──────────┐    ┌──────────┐
                              │   Server │    │  Client  │
                              │ (Tool)   │    │  (Data)  │
                              └──────────┘    └──────────┘
```

### Key Components

**1. MCP Host**
- Runs the AI assistant
- Manages connections to tools/data
- Claude, ChatGPT, or your own app

**2. MCP Server**
- Exposes tools or data
- Implements MCP protocol
- Can be local or remote

**3. MCP Client**
- Built into the Host
- Communicates with Servers
- Handles protocol messages

### Real-World Example

**Task:** "Search my Google Drive and summarize the last 3 documents about AI"

**Without MCP:**
1. Write Google Drive API integration
2. Handle OAuth authentication
3. Parse file listings
4. Download each file
5. Extract text
6. Send to LLM
→ **Days of work**

**With MCP:**
1. Install Google Drive MCP Server
2. Call `search_files()` tool
3. Call `read_file()` tool
4. LLM summarizes
→ **Minutes of work**

## MCP Server Types

### Filesystem Servers
- Access local files
- Search, read, write
- Example: `@modelcontextprotocol/server-filesystem`

### Database Servers
- Query PostgreSQL, MySQL
- Vector search (pgvector)
- Example: `@modelcontextprotocol/server-postgres`

### API Servers
- GitHub repositories
- Google services
- Slack, Notion, etc.

### Custom Servers
- Your business logic
- Proprietary tools
- Domain-specific data
""",
    "Creating Your First Agent": """
# Creating Your First Agent

## The Agent Development Journey

Building an AI agent follows a clear path:
```
Idea → Prototype → Test → Deploy → Iterate
```

Let's build an agent together!

## Project: Course Companion Agent

Our agent will help students learn by:
1. **Explaining** concepts at their level
2. **Quizzing** them on material
3. **Tracking** their progress
4. **Motivating** them to continue

## Step 1: Define the Agent's Purpose

**Clear Goal Statement:**
```
"Help students master AI Agent Development
through personalized tutoring, practice quizzes,
and progress tracking."
```

**Key Capabilities:**
- Explain any concept from the course
- Generate and grade quizzes
- Track learning progress
- Maintain student motivation

## Step 2: Design the Agent Architecture

### Core Components

**1. Intent Detection**
Understands what the student wants:
```python
 intents = {
     "explain": ["explain", "what is", "how does"],
     "quiz": ["quiz", "test me", "practice"],
     "progress": ["my progress", "how am i doing"],
     "help": ["stuck", "help", "hint"]
 }
```

**2. Skill System**
Modular capabilities for different tasks:
```
skills/
├── concept-explainer/
│   └── SKILL.md
├── quiz-master/
│   └── SKILL.md
├── socratic-tutor/
│   └── SKILL.md
└── progress-motivator/
    └── SKILL.md
```

**3. Backend Integration**
Deterministic content APIs:
```python
GET /api/v1/chapters          # Get course content
GET /api/v1/quizzes/{id}       # Get quiz questions
POST /api/v1/progress          # Update progress
GET /api/v1/user/{id}/tier    # Check access
```

## Step 3: Implement a Skill

Let's build the **Concept Explainer** skill:

**SKILL.md Structure:**
```markdown
# Concept Explainer Skill

## Purpose
Explain concepts at learner's level

## Instructions
1. Detect learner's level (beginner/intermediate/advanced)
2. Use analogies and examples
3. Progressive complexity adjustment

## Examples
Input: "Explain neural networks"
→ Use water flow analogy for beginners
→ Use mathematical notation for advanced
```

## Step 4: Test Your Agent

**Testing Checklist:**
- [ ] Correctly detects user intent
- [ ] Loads appropriate skill
- [ ] Handles edge cases gracefully
- [ ] Provides helpful responses
- [ ] Maintains conversation context

## Step 5: Deploy and Iterate

**Deployment Options:**
1. **ChatGPT Custom GPT** (easiest)
   - Upload manifest
   - Add knowledge base
   - Configure actions

2. **OpenAI Apps SDK** (more control)
   - Python/TypeScript implementation
   - Custom UI integration
   - Advanced routing logic

3. **Full Web App** (maximum control)
   - Next.js frontend
   - Custom backend
   - Complete feature set

## Best Practices

✅ **Start Simple**
- Build one skill first
- Test thoroughly
- Add complexity gradually

✅ **Fail Gracefully**
- Handle API errors
- Provide fallback responses
- Never show raw errors to users

✅ **Measure Success**
- Track user satisfaction
- Monitor completion rates
- A/B test improvements

✅ **Iterate Fast**
- Release early versions
- Gather feedback
- Make incremental improvements
""",
    "Building Reusable Skills": """
# Building Reusable Skills

## What Makes a Skill Reusable?

A good skill is like a LEGO brick:
- **Self-contained** - Works independently
- **Well-documented** - Clear purpose and usage
- **Configurable** - Adapts to different contexts
- **Composable** - Combines with other skills
- **Tested** - Reliable behavior

## The Skill Architecture

### Directory Structure
```
.my-skill/
├── SKILL.md          # Definition
├── skill.py          # Implementation (optional)
├── examples/         # Usage examples
└── tests/           # Test cases
```

### SKILL.md Template

```markdown
# Skill Name

## Purpose
One-line description of what this skill does

## When to Use
Clear criteria for when this skill should be invoked

## Instructions
Step-by-step guide for the AI

## Examples
Input → Output pairs showing expected behavior

## Configuration
Any parameters or settings

## Limitations
What this skill cannot do
```

## Building Four Key Skills

### 1. Concept Explainer

**Purpose:** Explain topics at the learner's comprehension level

**Key Features:**
- Detect learner's level from questions
- Use analogies for beginners
- Add technical depth for advanced users
- Progressive complexity adjustment

**When to Use:**
- "Explain X"
- "What is Y?"
- "How does Z work?"

### 2. Quiz Master

**Purpose:** Test understanding through interactive quizzes

**Key Features:**
- Generate questions from content
- Multiple choice and open-ended
- Immediate feedback
- Encouragement, not just grading
- Celebration of correct answers

**When to Use:**
- "Quiz me"
- "Test my knowledge"
- "Practice questions"

### 3. Socratic Tutor

**Purpose:** Guide learning through questioning

**Key Features:**
- Never gives direct answers
- Asks probing questions
- Hints toward solutions
- Celebrates insights
- Builds critical thinking

**When to Use:**
- "Help me think"
- "I'm stuck"
- "Give me a hint"

### 4. Progress Motivator

**Purpose:** Track and celebrate learning progress

**Key Features:**
- Monitor completion rates
- Calculate streaks
- Celebrate milestones
- Gentle encouragement
- Visual progress tracking

**When to Use:**
- "My progress"
- "How am I doing?"
- After completing lessons

## Making Skills Work Together

### Skill Composition

**Example Learning Session:**
```
Student: "I don't understand neural networks"

→ Socratic Tutor skill activates
→ "What part is confusing?"

Student: "How do they learn?"

→ Concept Explainer skill activates
→ Explains backpropagation with analogy

→ Quiz Master skill activates
→ "Quick check: What's the role of gradients?"

→ Progress Motivator skill activates
→ "Great! You've completed 3 lessons this week!"
```

### Shared State

Skills can share context:
```python
context = {
    "user_level": "intermediate",
    "completed_lessons": ["intro", "mcp"],
    "current_streak": 5,
    "last_topic": "neural_networks"
}
```

## Testing Skills

### Unit Tests
```python
def test_concept_explainer():
    skill = ConceptExplainer()
    result = skill.explain("neural networks", level="beginner")
    assert "analogy" in result.lower()
    assert len(result) < 500  # Keep it simple
```

### Integration Tests
```python
def test_skill_routing():
    agent = CourseCompanionAgent()
    response = agent.process("Quiz me on MCP")
    assert "quiz_master" in response.active_skills
```

## Publishing Your Skills

**Option 1: Open Source**
- GitHub repository
- Clear documentation
- Examples and tests
- License file

**Option 2: Package Manager**
- npm for JavaScript
- PyPI for Python
- Version management
- Dependency tracking

**Option 3: Marketplace**
- OpenAI GPT Store
- Claude Store (future)
- Community sharing

## Advanced: Skill Memory

Give skills access to shared memory:
```python
class Skill:
    def __init__(self, memory_store):
        self.memory = memory_store

    def execute(self, input_data):
        # Read from memory
        user_context = self.memory.get("user_profile")

        # Process using context
        result = self.process(input_data, user_context)

        # Write to memory
        self.memory.set("last_interaction", result)

        return result
```

## Best Practices

✅ **Single Responsibility** - One skill does one thing well
✅ **Clear Interface** - Obvious inputs and outputs
✅ **Error Handling** - Graceful degradation
✅ **Documentation** - Examples clarify usage
✅ **Version Control** - Track changes and improvements
"""
}

async def update_chapters():
    """Update chapter content in database."""
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Convert SQLAlchemy asyncpg URL to asyncpg format if needed
    if database_url.startswith('postgresql+asyncpg://'):
        database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')

    conn = await asyncpg.connect(database_url)

    print("Connected to database")

    # Get all chapters
    chapters = await conn.fetch('SELECT id, title FROM chapters ORDER BY "order"')
    print(f"Found {len(chapters)} chapters")

    # Update each chapter
    for chapter in chapters:
        if chapter['title'] in CHAPTERS_CONTENT:
            content = CHAPTERS_CONTENT[chapter['title']]
            await conn.execute(
                'UPDATE chapters SET content = $1 WHERE id = $2',
                content, chapter['id']
            )
            print(f"✓ Updated: {chapter['title']}")
        else:
            print(f"⚠ No content for: {chapter['title']}")

    # Verify updates
    updated = await conn.fetch('SELECT title, LENGTH(content) as len FROM chapters ORDER BY "order"')
    print("\nUpdated chapters:")
    for chapter in updated:
        print(f"  {chapter['title']}: {chapter['len']:,} characters")

    await conn.close()
    print("\n✅ Chapter content updated successfully!")

if __name__ == "__main__":
    asyncio.run(update_chapters())

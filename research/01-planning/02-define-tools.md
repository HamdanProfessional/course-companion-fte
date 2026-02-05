# Define Tools

**Source:** https://developers.openai.com/apps-sdk/plan/tools
**Phase:** Planning
**Last Updated:** February 2026

---

## Overview

In Apps SDK, tools are the contract between your MCP server and the model. They describe what the connector can do, how to call it, and what data comes back. Good tool design makes discovery accurate, invocation reliable, and downstream UX predictable.

---

## Key Concepts

### The Tool Contract

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Model     │ ──────> │   Tool       │ ──────> │  MCP Server │
│ (ChatGPT)   │ Invoke  │ (Definition) │ Execute  │  (Backend)  │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                        │
                               │<───────────────────────│
                               │    Structured Data     │
                               └────────────────────────┘
```

### Tool Design Goals

- **Discovery accuracy** - Model picks the right tool
- **Invocation reliability** - Model calls it correctly
- **UX predictability** - User gets expected experience

---

## Implementation Details

### 1. One Job Per Tool

Keep each tool focused on a single read or write action.

❌ **Bad (Kitchen Sink):**
```python
tool = {
    "name": "manage_jira_board",
    "description": "Do everything with Jira"
}
```

✅ **Good (Focused Actions):**
```python
tools = [
    {
        "name": "fetch_board",
        "description": "Retrieve a Jira board by ID",
        "inputSchema": {"board_id": "string"}
    },
    {
        "name": "create_ticket",
        "description": "Create a new ticket on a board",
        "inputSchema": {
            "board_id": "string",
            "title": "string",
            "description": "string"
        }
    },
    {
        "name": "move_task",
        "description": "Move a task to a different column",
        "inputSchema": {
            "ticket_id": "string",
            "column_id": "string"
        }
    }
]
```

---

### 2. Explicit Inputs

Define the shape of `inputSchema` with precision:

```yaml
inputSchema:
  type: object
  properties:
    course_id:
      type: string
      description: "Unique identifier for the course"
      enum: ["python-basics", "neural-networks", "sql-fundamentals"]
    chapter_id:
      type: string
      description: "Chapter to retrieve (e.g., 'intro', 'basics', 'advanced')"
      pattern: "^[a-z0-9-]+$"
    include_exercises:
      type: boolean
      description: "Whether to include practice exercises"
      default: false
  required:
    - course_id
```

**Best Practices:**
- Use `enum` for constrained sets
- Provide `default` values
- Use `pattern` for validation
- Document nullable fields
- Use clear, descriptive names

---

### 3. Predictable Outputs

Enumerate structured fields with machine-readable identifiers:

```python
{
    "content": {
        "chapter_id": "neural-networks-01",
        "title": "Introduction to Neural Networks",
        "sections": [...],
        "quiz_ids": ["quiz-01", "quiz-02"]  # Reusable IDs
    },
    "_meta": {
        "openai/outputTemplate": "chapter_viewer"
    }
}
```

---

## Tool Metadata

### Discovery-Driven Metadata

Discovery is driven entirely by metadata. For each tool:

```python
tool = {
    # Name: Action-oriented, unique within connector
    "name": "course_companion.fetch_content",

    # Description: Start with "Use this when..."
    "description": "Use this when the student asks to view course content, " +
                   "read a chapter, or access learning materials. " +
                   "Returns structured chapter data with sections and examples.",

    # Parameter annotations
    "inputSchema": {
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "Course identifier (e.g., 'python-basics', 'neural-networks')",
                "enum": ["python-basics", "neural-networks", "sql-fundamentals"]
            },
            "chapter_id": {
                "type": "string",
                "description": "Chapter to retrieve. If not specified, returns first chapter."
            }
        },
        "required": ["course_id"]
    },

    # Annotations for model behavior
    "annotations": {
        "readOnlyHint": True,      # Tool doesn't mutate state
        "destructiveHint": False,   # Tool doesn't delete data
        "openWorldHint": False     # Tool stays within user account
    }
}
```

### Metadata Best Practices

**Name:**
- Action-oriented: `fetch_content`, `create_quiz`, `submit_answer`
- Namespaced: `course_companion.fetch_content`
- Snake_case for multi-word: `move_task`, `fetch_user_progress`

**Description:**
- Start with "Use this when..." or similar trigger phrase
- Be specific about when to use
- Mention key parameters or constraints
- Keep to 1-2 sentences

**Parameter Descriptions:**
- Call out safe ranges or enumerations
- Note optional vs required
- Provide examples for enums
- Mention validation rules

---

## Model-Side Guardrails

### Prelinked vs. Link-Required

**Anonymous Access (Prelinked):**
```python
tool = {
    "name": "browse_courses",
    "description": "Use this when browsing available courses. No login required.",
    "linkMode": "prelinked"
}
```

**Authenticated Access (Link-Required):**
```python
tool = {
    "name": "fetch_user_progress",
    "description": "Use this when the student asks about their progress. Requires account connection.",
    "linkMode": "link_required"
}
```

### Tool Annotations

```python
"annotations": {
    # Read-only: Cannot mutate state
    "readOnlyHint": True,

    # Destructive: Deletes or overwrites user data
    "destructiveHint": True,

    # Open-world: Publishes content or reaches outside user account
    "openWorldHint": True,

    # Result components: Should render a UI
    "outputTemplate": "chapter_viewer"
}
```

| Annotation | When to Use | Examples |
|------------|-------------|----------|
| `readOnlyHint` | GET requests, queries | `fetch_content`, `get_progress` |
| `destructiveHint` | DELETE, overwrite operations | `reset_progress`, `delete_account` |
| `openWorldHint` | Sharing, publishing | `share_progress`, `post_certificate` |
| `outputTemplate` | Should show UI | All tools with structured content |

---

## Golden Prompt Rehearsal

Before implementation, sanity-check against your prompt set:

### 1. Direct Prompts

For every direct prompt, confirm exactly one tool addresses it:

| Prompt | Expected Tool | Pass? |
|--------|---------------|-------|
| "Show my progress" | `get_progress` | ✅ |
| "Quiz me on Python" | `start_quiz` | ✅ |

### 2. Indirect Prompts

Ensure descriptions give enough context:

| Prompt | Why It Matches | Pass? |
|--------|----------------|-------|
| "How am I doing?" | Description mentions "progress or learning stats" | ✅ |

### 3. Negative Prompts

Verify metadata keeps tool hidden unless opted in:

| Prompt | Should Match? | Pass? |
|--------|---------------|-------|
| "Tell me a joke" | ❌ No | ✅ |

---

## Handoff to Implementation

### Handoff Document Template

```markdown
## Tool: fetch_content

**Purpose:** Retrieve course chapters for student learning

**Input Schema:**
```json
{
  "course_id": "string (required, enum)",
  "chapter_id": "string (optional)"
}
```

**Output Schema:**
```json
{
  "chapter_id": "string",
  "title": "string",
  "sections": [...],
  "quiz_ids": ["string"]
}
```

**Component:** `chapter_viewer`

**Auth Required:** No (public content)

**Rate Limits:** 100 requests/minute per user
```

---

## Best Practices

### Tool Design

1. **Separate reads from writes** - Different tools for fetch vs update
2. **Use enums** - Constrain parameter values when possible
3. **Include IDs** - Machine-readable identifiers in outputs
4. **Default values** - Make common paths frictionless

### Metadata

1. **"Use this when..."** - Start descriptions with trigger phrase
2. **Be specific** - Narrow scope improves accuracy
3. **Mention constraints** - Call out auth, rate limits, prerequisites
4. **Iterate** - Use golden prompts to refine

---

## Common Pitfalls

### Mistake 1: Overly Broad Tools

❌ **Don't:**
```python
{
    "name": "manage_course",
    "description": "Handle all course-related operations"
}
```

✅ **Do:**
```python
[
    {"name": "fetch_content", "description": "Use this when..."},
    {"name": "start_quiz", "description": "Use this when..."}
]
```

---

### Mistake 2: Vague Descriptions

❌ **Don't:**
```python
"Manage student progress"
```

✅ **Do:**
```python
"Use this when the student asks about their progress, learning stats, " +
"completion status, or streak information."
```

---

## Course Companion FTE Tools

| Tool | Description | Read-Only | Destructive | Open-World |
|------|-------------|-----------|-------------|------------|
| `browse_courses` | Catalog of available courses | ✅ | ❌ | ❌ |
| `fetch_content` | Get chapter content | ✅ | ❌ | ❌ |
| `start_quiz` | Begin a quiz session | ✅ | ❌ | ❌ |
| `submit_answer` | Submit quiz answer | ❌ | ❌ | ❌ |
| `get_progress` | Student progress & stats | ✅ | ❌ | ❌ |
| `update_progress` | Mark content complete | ❌ | ❌ | ❌ |
| `reset_progress` | Clear all progress | ❌ | ✅ | ❌ |
| `share_progress` | Share progress to social | ❌ | ❌ | ✅ |

---

## Related Resources

- **Previous:** [Research Use Cases](./01-use-case-research.md)
- **Next:** [Design Components](./03-design-components.md)
- **Implementation:** [Build MCP Server](../../02-build/01-mcp-server.md)

---

## Template: Tool Definition

```python
from typing import Optional, List
from pydantic import BaseModel, Field

class FetchContentInput(BaseModel):
    """Input schema for fetch_content tool"""
    course_id: str = Field(
        description="Course identifier",
        enum=["python-basics", "neural-networks", "sql-fundamentals"]
    )
    chapter_id: Optional[str] = Field(
        default=None,
        description="Chapter to retrieve. If not specified, returns first chapter."
    )

tool_definition = {
    "name": "course_companion.fetch_content",
    "description": (
        "Use this when the student asks to view course content, "
        "read a chapter, or access learning materials."
    ),
    "inputSchema": FetchContentInput.model_json_schema(),
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False
    }
}
```

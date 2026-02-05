# Design Components

**Source:** https://developers.openai.com/apps-sdk/plan/components
**Phase:** Planning
**Last Updated:** February 2026

---

## Overview

UI components are the human-visible half of your connector. They let users view or edit data inline, switch to fullscreen when needed, and keep context synchronized between typed prompts and UI actions. Planning them early ensures your MCP server returns the right structured data and component metadata from day one.

---

## Key Concepts

### Why Components Matter

```
Tool Response → Structured Data → UI Component → User Experience
```

Components transform raw tool outputs into human-friendly interfaces that users can interact with directly within ChatGPT.

---

## Sample Components (Pizzaz Gallery)

OpenAI provides reusable examples in the [pizzaz gallery](https://github.com/openai-apps-sdk-examples/pizzaz):

### 1. List Component

**Purpose:** Renders dynamic collections with empty-state handling

**Use Cases:**
- Task lists
- Course catalogs
- Search results
- Record collections

**Features:**
- Dynamic item rendering
- Empty state messaging
- Selection affordances
- Inline actions

---

### 2. Map Component

**Purpose:** Plots geo data with marker clustering and detail panes

**Use Cases:**
- Location-based services
- Delivery tracking
- Store locators
- Route visualization

**Features:**
- Marker clustering
- Detail panes on click
- Geo-coordinate support
- Responsive layout

---

### 3. Album Component

**Purpose:** Showcases media grids with fullscreen transitions

**Use Cases:**
- Photo galleries
- Video libraries
- Document previews
- Asset management

**Features:**
- Grid layout
- Fullscreen transitions
- Media metadata
- Navigation affordances

---

### 4. Carousel Component

**Purpose:** Highlights featured content with swipe gestures

**Use Cases:**
- Featured courses
- News highlights
- Product showcases
- Step-by-step guides

**Features:**
- Swipe gestures
- Auto-advance options
- Indicator dots
- Navigation arrows

---

### 5. Shop Component

**Purpose:** Product browsing with checkout affordances

**Use Cases:**
- E-commerce catalogs
- Subscription tiers
- Course bundles
- Product listings

**Features:**
- Grid/list view toggle
- Modal product detail
- Price display
- Add to cart affordances

---

## Implementation Details

### 1. Clarify User Interaction

For each use case, decide:

**Viewer vs. Editor**

| Type | Description | Examples |
|------|-------------|----------|
| **Viewer** | Read-only display of data | Charts, dashboards, progress displays |
| **Editor** | Supports editing and writebacks | Forms, kanban boards, text editors |

**Single-Shot vs. Multiturn**

| Type | Description | Examples |
|------|-------------|----------|
| **Single-Shot** | Task accomplished in one invocation | Fetching data, simple queries |
| **Multiturn** | State persists across turns | Multi-step workflows, forms |

**Layout Modes**

| Mode | When to Use | Examples |
|------|-------------|----------|
| **Inline** | Simple, quick interactions | Quick views, confirmations |
| **Fullscreen** | Complex workflows | Full editors, detailed dashboards |
| **PiP (Picture-in-Picture)** | Reference while chatting | Context panels, reference docs |

---

### 2. Map Data Requirements

Components should receive everything they need in the tool response:

**Structured Content**

```python
{
    "content": {
        "items": [
            {
                "id": "item-1",
                "title": "Python Basics",
                "description": "Learn Python fundamentals",
                "thumbnail_url": "https://...",
                "status": "in_progress"
            }
        ]
    },
    "_meta": {
        "openai/outputTemplate": "course_list"
    }
}
```

**Initial Component State**

```python
# Use window.openai.toolOutput as initial render data
tool_output = window.openai.toolOutput

# On subsequent followups, use callTool return value
result = await window.openai.callTool({
    name: "update_progress",
    arguments: { chapter_id: "ch01" }
})

# Cache state for re-rendering
window.openai.setWidgetState({
    selected_chapter: "ch01",
    scroll_position: 150
})
```

**Auth Context**

```python
{
    "content": {...},
    "_meta": {
        "openai/linkedAccount": {
            "account_id": "user-123",
            "account_type": "student"
        }
    }
}
```

---

### 3. Design for Responsive Layouts

Components run inside an iframe on both desktop and mobile.

**Adaptive Breakpoints**

```css
/* Mobile-first approach */
.component-container {
  max-width: 100%;
}

@media (min-width: 768px) {
  .component-container {
    max-width: 600px;
  }
}

@media (min-width: 1024px) {
  .component-container {
    max-width: 800px;
  }
}
```

**Design Considerations:**

| Screen Size | Layout Strategy |
|-------------|-----------------|
| Mobile (< 768px) | Single column, stacked elements |
| Tablet (768-1024px) | Two columns, collapsible sections |
| Desktop (> 1024px) | Multi-column, full features |

**Accessibility:**
- Respect system dark mode (`color-scheme`)
- Provide focus states for keyboard navigation
- Use semantic HTML elements
- Include ARIA labels where needed

**Launcher Transitions:**
- Ensure navigation elements stay visible
- Maintain context when expanding to fullscreen
- Preserve scroll position when collapsing

---

### 4. Define State Contract

Because components and the chat surface share conversation state, be explicit about what is stored where:

**Component State** (`window.openai.setWidgetState`)

```javascript
// Ephemeral UI state
window.openai.setWidgetState({
  selectedRow: "row-42",
  scrollPosition: 250,
  draftFormData: {
    title: "Draft title",
    tags: ["python", "tutorial"]
  }
})
```

**Server State**

```python
# Authoritative data stored on backend
user_progress = {
    "user_id": "user-123",
    "completed_chapters": ["ch01", "ch02"],
    "quiz_scores": {"quiz-01": 85},
    "last_accessed": "2026-02-03T10:00:00Z"
}
```

**Model Messages** (`sendFollowUpMessage`)

```javascript
// Send human-readable updates to transcript
window.openai.sendFollowUpMessage({
  roleId: "user",
  content: {
    type: "text",
    text: "I've completed the Python basics chapter. What's next?"
  }
})
```

**State Diagram**

```
┌─────────────┐     setWidgetState     ┌──────────────┐
│  Component  │ ──────────────────────> │ Widget State │
│  (UI)       │ <────────────────────── │ (Ephemeral) │
└─────────────┘     getWidgetState     └──────────────┘
       │                                     │
       │ callTool                           │
       ↓                                     │
┌─────────────┐                              │
│ MCP Server  │ ──────────────────────────────┘
│ (Backend)   │    Server State (Persistent)
└─────────────┘
```

---

### 5. Plan Telemetry and Debugging

**Analytics Events**

```javascript
// Track component loads
window.openai.analytics?.track({
  event: "component_loaded",
  component: "course_viewer",
  properties: {
    course_id: "python-basics",
    chapter_id: "ch01"
  }
})

// Track button clicks
window.openai.analytics?.track({
  event: "button_clicked",
  component: "course_viewer",
  properties: {
    button: "submit_quiz",
    chapter_id: "ch01"
  }
})

// Track validation errors
window.openai.analytics?.track({
  event: "validation_error",
  component: "quiz_form",
  properties: {
    field: "answer",
    error_type: "required_field_missing"
  }
})
```

**Debugging Hooks**

```javascript
// Log tool-call IDs for traceability
const toolCallId = window.openai.toolOutput?._meta?.toolCallId
console.log('[Component] Tool Call ID:', toolCallId)

// Provide fallback on error
try {
  renderComponent(data)
} catch (error) {
  console.error('[Component] Render error:', error)
  // Show fallback UI
  showFallback({
    message: "Unable to load component. Please try again.",
    rawData: data
  })
}
```

---

## Best Practices

### Component Design

1. **Data-driven** - Component receives all data via tool response
2. **Responsive** - Design for mobile, tablet, and desktop
3. **Accessible** - Keyboard navigation, screen reader support
4. **Graceful degradation** - Fallback UI on errors

### State Management

1. **Widget state** - Ephemeral UI state only
2. **Server state** - Authoritative data source
3. **Avoid localStorage** - Use widget state API instead
4. **Sync carefully** - Merge server changes into widget state

### Performance

1. **Lazy load** - Load large datasets on demand
2. **Cache wisely** - Use widget state for caching
3. **Optimize renders** - Avoid unnecessary re-renders
4. **Bundle size** - Keep JavaScript bundle small

---

## Common Pitfalls

### Mistake 1: Not Planning State Upfront

❌ **Don't:** Figure out state management after building components

✅ **Do:** Map state contracts before implementation

---

### Mistake 2: Ignoring Responsive Design

❌ **Don't:** Design only for desktop

✅ **Do:** Mobile-first, responsive layouts

---

### Mistake 3: No Error Handling

❌ **Don't:** Let components fail silently

✅ **Do:** Provide fallback UI and error messages

---

### Mistake 4: Using localStorage

❌ **Don't:** Store state in browser localStorage

✅ **Do:** Use `window.openai.setWidgetState` for ephemeral state

---

## Course Companion FTE Components

### 1. Course Catalog Viewer

**Type:** Viewer (read-only)
**Layout:** Inline
**Data:** List of available courses with metadata

```python
{
    "courses": [
        {
            "id": "python-basics",
            "title": "Python Basics",
            "description": "Learn Python fundamentals",
            "level": "beginner",
            "duration": "4 hours",
            "thumbnail": "https://..."
        }
    ]
}
```

---

### 2. Chapter Content Viewer

**Type:** Viewer (read-only)
**Layout:** Inline or Fullscreen
**Data:** Chapter sections, code examples, exercises

```python
{
    "chapter": {
        "id": "neural-networks-01",
        "title": "Introduction to Neural Networks",
        "sections": [...],
        "next_chapter_id": "neural-networks-02"
    }
}
```

---

### 3. Quiz Interface

**Type:** Editor (with writeback)
**Layout:** Inline or Fullscreen
**Data:** Quiz questions, answer submission, feedback

```python
{
    "quiz": {
        "id": "quiz-01",
        "questions": [...],
        "current_question": 0,
        "submitted_answers": []
    }
}
```

---

### 4. Progress Dashboard

**Type:** Viewer (read-only)
**Layout:** Inline
**Data:** Completion stats, streak, achievements

```python
{
    "progress": {
        "user_id": "user-123",
        "courses_completed": 3,
        "current_streak": 7,
        "achievements": [...]
    }
}
```

---

## Related Resources

- **Previous:** [Define Tools](./02-define-tools.md)
- **Next:** [Build MCP Server](../../02-build/01-mcp-server.md)
- **Examples:** [Pizzaz Gallery](https://github.com/openai-apps-sdk-examples/pizzaz)
- **Reference:** [ChatGPT UI Guide](../../02-build/02-chatgpt-ui.md)

---

## Template: Component Contract

```markdown
## Component: Chapter Viewer

**Purpose:** Display course chapter content with navigation

**Data Requirements:**
```json
{
  "chapter_id": "string",
  "title": "string",
  "sections": [
    {
      "type": "text|code|exercise",
      "content": "string",
      "language": "string (for code)"
    }
  ],
  "next_chapter_id": "string | null",
  "quiz_ids": ["string"]
}
```

**Layout Modes:**
- Inline: Text content, basic navigation
- Fullscreen: Full content, code highlighting, exercises

**State:**
- Widget: Scroll position, current section
- Server: Progress, completion status

**Actions:**
- `callTool:mark_complete` - Mark chapter complete
- `callTool:start_quiz` - Start chapter quiz
- `sendFollowUpMessage` - Ask follow-up question

**Responsive:**
- Mobile: Single column, stacked sections
- Desktop: Two column, navigation sidebar

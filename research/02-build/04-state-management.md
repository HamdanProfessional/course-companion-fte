# Managing State

**Source:** https://developers.openai.com/apps-sdk/build/state-management
**Phase:** Build
**Last Updated:** February 2026

---

## Overview

State in ChatGPT apps falls into three categories:

| State Type | Owned By | Lifetime | Examples |
|------------|----------|----------|----------|
| **Business Data** (authoritative) | MCP server or backend | Long-lived | Tasks, tickets, documents |
| **UI State** (ephemeral) | Widget instance | Active widget only | Selected row, expanded panel |
| **Cross-session State** (durable) | Your backend or storage | Cross-session | Saved filters, preferences |

```
Server (MCP or backend)
│
├── Authoritative business data (source of truth)
│
▼
ChatGPT Widget
│
├── Ephemeral UI state (visual behavior)
│
└── Rendered view = authoritative data + UI state
```

---

## 1. Business Data (Authoritative)

Business data is the **source of truth**. It lives on your MCP server or backend.

### User Action Flow

```
1. UI calls server tool
2. Server updates data
3. Server returns new authoritative snapshot
4. Widget re-renders using that snapshot
```

### Example: Returning Authoritative State (Node.js)

```javascript
import { Server } from "@modelcontextprotocol/sdk/server";
import { jsonSchema } from "@modelcontextprotocol/sdk/schema";

const tasks = new Map(); // Replace with DB or service
let nextId = 1;

const server = new Server({
  tools: {
    get_tasks: {
      description: "Return all tasks",
      inputSchema: jsonSchema.object({}),
      async run() {
        return {
          structuredContent: {
            type: "taskList",
            tasks: Array.from(tasks.values()),
          }
        };
      }
    },
    add_task: {
      description: "Add a new task",
      inputSchema: jsonSchema.object({ title: jsonSchema.string() }),
      async run({ title }) {
        const id = `task-${nextId++}`;
        tasks.set(id, { id, title, done: false });

        // Always return updated authoritative state
        return this.tools.get_tasks.run({});
      }
    }
  }
});

server.start();
```

---

## 2. UI State (Ephemeral)

UI state describes **how** data is being viewed, not the data itself.

### Storage

- **`window.openai.widgetState`** - Read current state
- **`window.openai.setWidgetState(newState)`** - Write next state (sync, no await)

### React Hook: `useWidgetState`

```typescript
export function useWidgetState<T extends WidgetState>(
  defaultState?: T | (() => T | null)
): readonly [T | null, (state: SetStateAction<T | null>) => void] {
  const widgetStateFromWindow = useOpenAiGlobal("widgetState") as T;

  const [widgetState, _setWidgetState] = useState<T | null>(() => {
    if (widgetStateFromWindow != null) {
      return widgetStateFromWindow;
    }
    return typeof defaultState === "function"
      ? defaultState()
      : (defaultState ?? null);
  });

  useEffect(() => {
    _setWidgetState(widgetStateFromWindow);
  }, [widgetStateFromWindow]);

  const setWidgetState = useCallback(
    (state: SetStateAction<T | null>) => {
      _setWidgetState((prevState) => {
        const newState = typeof state === "function" ? state(prevState) : state;

        if (newState != null) {
          window.openai.setWidgetState(newState);
        }

        return newState;
      });
    },
    [window.openai.setWidgetState]
  );

  return [widgetState, setWidgetState] as const;
}
```

### Example (React Component)

```typescript
import { useWidgetState } from "./use-widget-state";

export function TaskList({ data }) {
  const [widgetState, setWidgetState] = useWidgetState(() => ({
    selectedId: null,
  }));

  const selectTask = (id) => {
    setWidgetState((prev) => ({ ...prev, selectedId: id }));
  };

  return (
    <ul>
      {data.tasks.map((task) => (
        <li
          key={task.id}
          style={{
            fontWeight: widgetState?.selectedId === task.id ? "bold" : "normal",
          }}
          onClick={() => selectTask(task.id)}
        >
          {task.title}
        </li>
      ))}
    </ul>
  );
}
```

### Example (Vanilla JS)

```javascript
const tasks = window.openai.toolOutput?.tasks ?? [];
let widgetState = window.openai.widgetState ?? { selectedId: null };

function selectTask(id) {
  widgetState = { ...widgetState, selectedId: id };
  window.openai.setWidgetState(widgetState);
  renderTasks();
}

function renderTasks() {
  const list = document.querySelector("#task-list");
  list.innerHTML = tasks
    .map(
      (task) => `
        <li
          style="font-weight: ${widgetState.selectedId === task.id ? "bold" : "normal"}"
          onclick="selectTask('${task.id}')"
        >
          ${task.title}
        </li>
      `
    )
    .join("");
}

renderTasks();
```

---

## 3. Cross-Session State

Preferences that persist across conversations, devices, or sessions belong in your backend.

### Bring Your Own Backend

```
┌─────────────┐     OAuth      ┌──────────────┐
│ ChatGPT     │ ──────────────> │ Your Backend │
│ (Widget)    │   Identify user │  (Storage)   │
└─────────────┘                 └──────────────┘
       │                                 │
       │         Fetch/Mutate            │
       └────────────────────────────────>│
                                      Data
```

**Requirements:**
- Authenticate via OAuth (see [Authentication](./03-authentication.md))
- Use your backend's APIs to fetch/mutate data
- Return sufficient structured content for model
- Keep latency low (< 200ms target)

**Plan for:**
- Data residency and compliance
- Rate limits
- Versioning (include schema versions)

### Example: Widget Invokes Tool

```typescript
import { useState } from "react";

export function PreferencesForm({ userId, initialPreferences }) {
  const [formState, setFormState] = useState(initialPreferences);
  const [isSaving, setIsSaving] = useState(false);

  async function savePreferences(next) {
    setIsSaving(true);
    setFormState(next);
    window.openai.setWidgetState(next);

    const result = await window.openai.callTool("set_preferences", {
      userId,
      preferences: next,
    });

    const updated = result?.structuredContent?.preferences ?? next;
    setFormState(updated);
    window.openai.setWidgetState(updated);
    setIsSaving(false);
  }

  return (
    <form>
      {/* form fields */}
      <button
        type="button"
        disabled={isSaving}
        onClick={() => savePreferences(formState)}
      >
        {isSaving ? "Saving…" : "Save preferences"}
      </button>
    </form>
  );
}
```

### Example: Server Handles Tool (Node.js)

```javascript
import { Server } from "@modelcontextprotocol/sdk/server";
import { jsonSchema } from "@modelcontextprotocol/sdk/schema";
import { request } from "undici";

// Helpers that call existing backend API
async function readPreferences(userId) {
  const response = await request(
    `https://api.example.com/users/${userId}/preferences`,
    {
      method: "GET",
      headers: { Authorization: `Bearer ${process.env.API_TOKEN}` }
    }
  );
  if (response.statusCode === 404) return {};
  if (response.statusCode >= 400) throw new Error("Failed to load preferences");
  return await response.body.json();
}

async function writePreferences(userId, preferences) {
  const response = await request(
    `https://api.example.com/users/${userId}/preferences`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${process.env.API_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(preferences)
    }
  );
  if (response.statusCode >= 400) throw new Error("Failed to save preferences");
  return await response.body.json();
}

const server = new Server({
  tools: {
    get_preferences: {
      inputSchema: jsonSchema.object({ userId: jsonSchema.string() }),
      async run({ userId }) {
        const preferences = await readPreferences(userId);
        return { structuredContent: { type: "preferences", preferences } };
      }
    },
    set_preferences: {
      inputSchema: jsonSchema.object({
        userId: jsonSchema.string(),
        preferences: jsonSchema.object({})
      }),
      async run({ userId, preferences }) {
        const updated = await writePreferences(userId, preferences);
        return { structuredContent: { type: "preferences", preferences: updated } };
      }
    }
  }
});
```

---

## Widget Scope Behavior

**Key behavior:**

- **Widgets are message-scoped:** Every response creates a fresh widget instance
- **UI state sticks with the widget:** Reopening same message restores state
- **Server data drives truth:** Widget sees updates when tool call completes

### State Persistence Rules

| Action | Widget State Behavior |
|--------|----------------------|
| Inline follow-up from widget | ✅ State persists |
| PiP composer | ✅ State persists |
| Fullscreen composer | ✅ State persists |
| Main chat composer | ❌ New widget, fresh state |

---

## Summary

| State Type | Where to Store | How to Access |
|------------|----------------|---------------|
| **Business Data** | MCP server or backend | Via tool calls |
| **UI State** | `window.openai.widgetState` | `useWidgetState` hook |
| **Cross-Session** | Your backend storage | Via authenticated APIs |

**Key Guidelines:**
- Store business data on the server
- Store UI state inside the widget
- Store cross-session state in backend storage
- Widget state persists only for specific widget instance
- Avoid `localStorage` for core state

---

## Best Practices

1. **Separate concerns** - Keep business data separate from UI state
2. **Use `useWidgetState` hook** - For React components
3. **Design idempotent tools** - Server should return current state
4. **Avoid localStorage** - Use widget state API instead
5. **Keep state lean** - Under 4k tokens for performance

---

## Common Pitfalls

### Mistake 1: Using localStorage

❌ **Don't:**
```javascript
localStorage.setItem("selectedTask", taskId);
```

✅ **Do:**
```javascript
window.openai.setWidgetState({ selectedTask: taskId });
```

---

### Mistake 2: Not Returning Updated State

❌ **Don't:**
```javascript
async run({ title }) {
  tasks.set(id, { id, title, done: false });
  return { content: "Task added" }; // No updated state
}
```

✅ **Do:**
```javascript
async run({ title }) {
  tasks.set(id, { id, title, done: false });
  return this.tools.get_tasks.run({}); // Return updated state
}
```

---

### Mistake 3: Mixing State Types

❌ **Don't:** Store business data in widget state

✅ **Do:** Keep business data on server, use widget state for UI preferences

---

## Related Resources

- **Previous:** [Authentication](./03-authentication.md)
- **Next:** [Monetization](./05-monetization.md)
- **ChatGPT UI:** [Build Your ChatGPT UI](./02-chatgpt-ui.md)

---

## State Decision Tree

```
Is this business data (tasks, documents)?
├─ Yes → Store on MCP server/backend
│
Is this UI behavior (selection, expansion)?
├─ Yes → Store in widget state
│
Does this need to persist across conversations?
├─ Yes → Store in backend storage
│
No → Store in widget state (ephemeral)
```

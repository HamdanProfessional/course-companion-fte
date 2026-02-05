# Build Your ChatGPT UI

**Source:** https://developers.openai.com/apps-sdk/build/chatgpt-ui
**Phase:** Build
**Last Updated:** February 2026

---

## Overview

UI components turn structured tool results into a human-friendly UI. Components run inside an iframe in ChatGPT, talk to the host via the `window.openai` API, and render inline with the conversation.

### Component Library

Use the optional UI kit at `apps-sdk-ui` for ready-made buttons, cards, input controls, and layout primitives that match ChatGPT's container.

---

## The `window.openai` API

The host injects `window.openai` with UI-related globals and methods.

### Key Capabilities

| Capability | API | Description |
|------------|-----|-------------|
| **State & Data** | `toolInput`, `toolOutput`, `widgetState` | Tool data and persisted UI state |
| **Tools** | `callTool` | Widget invokes tools |
| **Messaging** | `sendFollowUpMessage` | Post user-authored follow-ups |
| **Files** | `uploadFile`, `getFileDownloadUrl` | Image uploads and previews |
| **Layout** | `requestDisplayMode`, `requestModal` | Manage layout and host controls |
| **Context** | `theme`, `locale`, `displayMode` | Adapt UI and copy |

---

## Helper Hooks

### `useOpenAiGlobal`

Keeps components reactive to changes in display mode, theme, and "props" via subsequent tool calls:

```typescript
export function useOpenAiGlobal<K extends keyof OpenAiGlobals>(
  key: K
): OpenAiGlobals[K] {
  return useSyncExternalStore(
    (onChange) => {
      const handleSetGlobal = (event: SetGlobalsEvent) => {
        const value = event.detail.globals[key];
        if (value === undefined) return;
        onChange();
      };

      window.addEventListener(SET_GLOBALS_EVENT_TYPE, handleSetGlobal, {
        passive: true,
      });

      return () => {
        window.removeEventListener(SET_GLOBALS_EVENT_TYPE, handleSetGlobal);
      };
    },
    () => window.openai[key]
  );
}
```

### Derived Hooks

```typescript
export function useToolInput() {
  return useOpenAiGlobal("toolInput");
}

export function useToolOutput() {
  return useOpenAiGlobal("toolOutput");
}

export function useToolResponseMetadata() {
  return useOpenAiGlobal("toolResponseMetadata");
}
```

---

## Widget State

Widget state persists across user sessions and exposes data to ChatGPT:

```typescript
// Read widget state
const state = window.openai.widgetState;

// Write widget state (sync, no await needed)
window.openai.setWidgetState({ selectedId: "item-42" });
```

**Important:** State is scoped to a specific widget instance. Follow-up turns keep the same widget only when submitted through that widget's controls.

### `useWidgetState` Hook

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

---

## API Methods

### Trigger Server Actions

```typescript
async function refreshPlaces(city: string) {
  await window.openai?.callTool("refresh_pizza_list", { city });
}
```

### Send Conversational Follow-ups

```typescript
await window.openai?.sendFollowUpMessage({
  prompt: "Draft a tasting itinerary for the pizzerias I favorited.",
});
```

### Upload Files

```typescript
function FileUploadInput() {
  return (
    <input
      type="file"
      accept="image/png,image/jpeg,image/webp"
      onChange={async (event) => {
        const file = event.currentTarget.files?.[0];
        if (!file || !window.openai?.uploadFile) return;

        const { fileId } = await window.openai.uploadFile(file);
        console.log("Uploaded fileId:", fileId);
      }}
    />
  );
}
```

### Download Files

```typescript
const { downloadUrl } = await window.openai.getFileDownloadUrl({ fileId });
imageElement.src = downloadUrl;
```

### Close Widget

**From UI:**
```typescript
window.openai.requestClose();
```

**From Server:**
```typescript
{
  "metadata": {
    "openai/closeWidget": true,
    "openai/widgetDomain": "https://myapp.example.com",
    "openai/widgetCSP": {
      "connect_domains": ["https://api.myapp.example.com"],
      "resource_domains": ["https://*.oaistatic.com"],
      "redirect_domains": ["https://checkout.example.com"],
      "frame_domains": ["https://*.example.com"]
    }
  }
}
```

### Request Alternate Layouts

```typescript
await window.openai?.requestDisplayMode({ mode: "fullscreen" });
// Note: on mobile, PiP may be coerced to fullscreen
```

### Open Modal

```typescript
await window.openai.requestModal({
  template: "ui://widget/checkout.html",
});
```

---

## Scaffold Component Project

### Project Structure

```
app/
  server/            # MCP server (Python or Node)
  web/               # Component bundle source
    package.json
    tsconfig.json
    src/component.tsx
    dist/component.js   # Build output
```

### Create Project

```bash
cd app/web
npm init -y
npm install react@^18 react-dom@^18
npm install -D typescript esbuild
```

---

## Author the React Component

Entry file mounts component into `root` element and reads initial data:

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

### Pizzaz Component Gallery

Example components from the Apps SDK examples:

| Component | Description |
|-----------|-------------|
| **Pizzaz List** | Ranked card list with favorites and CTA buttons |
| **Pizzaz Carousel** | Horizontal scroller for media-heavy layouts |
| **Pizzaz Map** | Mapbox integration with fullscreen inspector |
| **Pizzaz Album** | Stacked gallery view for deep dives |
| **Pizzaz Video** | Scripted player with overlays and fullscreen controls |

---

## Widget Localization

The host passes `locale` in `window.openai` and mirrors it to `document.documentElement.lang`:

```typescript
import { IntlProvider } from "react-intl";
import en from "./locales/en-US.json";
import es from "./locales/es-ES.json";

const messages: Record<string, Record<string, string>> = {
  "en-US": en,
  "es-ES": es,
};

export function App() {
  const locale = window.openai.locale ?? "en-US";
  return (
    <IntlProvider
      locale={locale}
      messages={messages[locale] ?? messages["en-US"]}
    >
      {/* Render UI */}
    </IntlProvider>
  );
}
```

---

## Bundle for Iframe

Build into a single JavaScript module:

```json
{
  "scripts": {
    "build": "esbuild src/component.tsx --bundle --format=esm --outfile=dist/component.js"
  }
}
```

```bash
npm run build  # produces dist/component.js
```

---

## Host-Backed Navigation

Skybridge mirrors the iframe's history into ChatGPT's UI. Use standard routing APIs:

```typescript
export default function PizzaListRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PizzaListApp />}>
          <Route path="place/:placeId" element={<PizzaListApp />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

Programmatic navigation:
```typescript
const navigate = useNavigate();

function openDetails(placeId: string) {
  navigate(`place/${placeId}`, { replace: false });
}

function closeDetails() {
  navigate("..", { replace: true });
}
```

---

## Best Practices

1. **Use helper hooks** - `useOpenAiGlobal`, `useWidgetState` for reactivity
2. **Keep state lean** - Under 4k tokens for performance
3. **Test with MCP Inspector** - Mirror ChatGPT's widget runtime
4. **Use component library** - `apps-sdk-ui` for consistent styling

---

## Related Resources

- **Previous:** [Build MCP Server](./01-mcp-server.md)
- **Next:** [Authentication](./03-authentication.md)
- **Examples:** [Pizzaz Gallery](https://github.com/openai-apps-sdk-examples/pizzaz)

---

## Vanilla JS Example

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

# Examples

**Source:** https://developers.openai.com/apps-sdk/build/examples
**Phase:** Build
**Last Updated:** February 2026

---

## Overview

The **Pizzaz demo app** bundles UI components showing the full tool surface area end-to-end. Use these examples as blueprints for your own app.

### GitHub Repository

```
https://github.com/openai-apps-sdk-examples/pizzaz
```

---

## Pizzaz Component Gallery

### 1. Pizzaz List

**Purpose:** Ranked card list with favorites and call-to-action buttons

**Use Cases:**
- Restaurant listings
- Product catalogs
- Course directories
- Task lists

**Features:**
- Dynamic card rendering
- Empty state handling
- Favorite/unfavorite actions
- Inline CTA buttons

**Screenshot:**
```
┌─────────────────────────────────────┐
│ 🔍 Search restaurants...            │
├─────────────────────────────────────┤
│ ⭐ Joe's Pizza                     │
│    Italian • $$$ • 0.5 mi          │
│    [♥] [Order Now]                  │
├─────────────────────────────────────┤
│   Tony's Pizzeria                  │
│    Neapolitan • $$ • 1.2 mi        │
│    [♡] [Order Now]                  │
└─────────────────────────────────────┘
```

---

### 2. Pizzaz Map

**Purpose:** Mapbox integration with fullscreen inspector and host state sync

**Use Cases:**
- Location-based services
- Delivery tracking
- Store locators
- Venue maps

**Features:**
- Mapbox integration
- Marker clustering
- Detail panes on click
- Fullscreen inspector
- State synchronization

---

### 3. Pizzaz Album

**Purpose:** Stacked gallery view for deep dives on single items

**Use Cases:**
- Photo galleries
- Product details
- Document previews
- Media collections

**Features:**
- Stacked layout
- Media grid
- Fullscreen transitions
- Navigation affordances

---

### 4. Pizzaz Carousel

**Purpose:** Horizontal scroller for media-heavy layouts

**Use Cases:**
- Featured content
- Image galleries
- Product showcases
- Step-by-step guides

**Features:**
- Embla-powered scroll
- Swipe gestures
- Auto-advance options
- Indicator dots
- Navigation arrows

---

### 5. Pizzaz Shop

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

**Screenshots:**

Grid View:
```
┌─────────────────────────────────────┐
│  Pizza Menu                         │
│  [Grid] [List]                      │
├──────────────┬──────────────┬───────┤
│ 🍕 Margherita│ 🍕 Pepperoni │ 🍕 BBQ│
│   $12.99     │   $14.99     │$13.99 │
│   [Add+]     │   [Add+]     │[Add+] │
└──────────────┴──────────────┴───────┘
```

Modal View:
```
┌─────────────────────────────────────┐
│           [Close]                    │
│  ┌─────────────────────────────┐    │
│  │  🍕 Margherita               │    │
│  │  Fresh basil, mozzarella,    │    │
│  │  tomato sauce                │    │
│  │                              │    │
│  │  $12.99                      │    │
│  │  [Add to Cart]               │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

---

### 6. Pizzaz Video

**Purpose:** Scripted player with overlays and fullscreen controls

**Use Cases:**
- Video tutorials
- Course content
- Product demos
- Trailers

**Features:**
- Video playback
- Overlay controls
- Fullscreen mode
- Progress tracking

---

## How to Use Examples

### Step 1: Clone Repository

```bash
git clone https://github.com/openai-apps-sdk-examples/pizzaz.git
cd pizzaz
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Run Development Server

```bash
npm run dev
```

### Step 4: Explore Components

Navigate through the examples and examine the code structure.

---

## Adapting Examples

### Pattern 1: Choose Closest Component

Find the component closest to your use case:

| Your Need | Use Component |
|-----------|---------------|
| Display list of items | Pizzaz List |
| Map-based display | Pizzaz Map |
| Image gallery | Pizzaz Album |
| Featured content carousel | Pizzaz Carousel |
| Product catalog | Pizzaz Shop |
| Video content | Pizzaz Video |

### Pattern 2: Modify Data Layer

Replace the mock data with your MCP tool outputs:

```typescript
// Before (mock data)
const items = [
  { id: "1", title: "Item 1", ... }
];

// After (tool output)
const items = window.openai.toolOutput?.items ?? [];
```

### Pattern 3: Customize Actions

Change button handlers to call your tools:

```typescript
// Before
const handleClick = () => {
  console.log("Clicked");
};

// After
const handleClick = async () => {
  await window.openai.callTool("your_tool", { id: item.id });
};
```

---

## Example: Course Companion FTE Components

### Course List (Based on Pizzaz List)

```typescript
export function CourseList() {
  const courses = window.openai.toolOutput?.courses ?? [];
  const [widgetState, setWidgetState] = useWidgetState(() => ({
    favorites: [],
  }));

  return (
    <div className="course-list">
      {courses.map((course) => (
        <CourseCard
          key={course.id}
          course={course}
          isFavorite={widgetState.favorites.includes(course.id)}
          onToggleFavorite={() => {
            setWidgetState((prev) => ({
              favorites: prev.favorites.includes(course.id)
                ? prev.favorites.filter((id) => id !== course.id)
                : [...prev.favorites, course.id]
            }));
          }}
          onStartCourse={() => {
            window.openai.callTool("start_course", { courseId: course.id });
          }}
        />
      ))}
    </div>
  );
}
```

### Quiz Interface (Based on Pizzaz Album)

```typescript
export function QuizInterface() {
  const quiz = window.openai.toolOutput?.quiz;
  const [widgetState, setWidgetState] = useWidgetState(() => ({
    currentQuestion: 0,
    answers: {},
  }));

  const question = quiz?.questions[widgetState.currentQuestion];

  if (!question) {
    return <QuizResults answers={widgetState.answers} />;
  }

  return (
    <div className="quiz-container">
      <QuestionCard
        question={question}
        selectedAnswer={widgetState.answers[question.id]}
        onSelectAnswer={(answer) => {
          setWidgetState((prev) => ({
            ...prev,
            answers: { ...prev.answers, [question.id]: answer }
          }));
        }}
        onSubmit={() => {
          window.openai.callTool("submit_answer", {
            quizId: quiz.id,
            questionId: question.id,
            answer: widgetState.answers[question.id]
          });
          setWidgetState((prev) => ({
            ...prev,
            currentQuestion: prev.currentQuestion + 1
          }));
        }}
      />
    </div>
  );
}
```

### Progress Dashboard (Based on Pizzaz List with Stats)

```typescript
export function ProgressDashboard() {
  const progress = window.openai.toolOutput?.progress;

  return (
    <div className="progress-dashboard">
      <StatsCard
        title="Courses Completed"
        value={progress?.courses_completed ?? 0}
        icon="🎓"
      />
      <StatsCard
        title="Current Streak"
        value={`${progress?.current_streak ?? 0} days`}
        icon="🔥"
      />
      <AchievementList achievements={progress?.achievements ?? []} />
    </div>
  );
}
```

---

## Best Practices from Examples

1. **Use `useWidgetState` hook** - For consistent state management
2. **Handle empty states** - Show helpful messages when no data
3. **Provide loading states** - Use spinners or skeletons
4. **Error boundaries** - Catch and handle component errors
5. **Responsive design** - Mobile-first approach
6. **Accessibility** - Keyboard navigation, screen readers
7. **Analytics** - Track component interactions

---

## Project Structure from Examples

```
pizzaz/
├── src/
│   ├── components/
│   │   ├── List/
│   │   │   ├── List.tsx
│   │   │   ├── ListItem.tsx
│   │   │   └── index.ts
│   │   ├── Map/
│   │   ├── Album/
│   │   ├── Carousel/
│   │   ├── Shop/
│   │   └── Video/
│   ├── hooks/
│   │   ├── useWidgetState.ts
│   │   ├── useOpenAiGlobal.ts
│   │   └── index.ts
│   ├── utils/
│   │   ├── analytics.ts
│   │   └── helpers.ts
│   └── styles/
│       ├── global.css
│       └── components.css
├── dist/                     # Build output
├── package.json
└── tsconfig.json
```

---

## Related Resources

- **Previous:** [Monetization](./05-monetization.md)
- **Next:** [Deploy Your App](../../03-deploy/01-deploy-app.md)
- **GitHub:** [openai-apps-sdk-examples](https://github.com/openai-apps-sdk-examples)

---

## Quick Start with Example

```bash
# 1. Clone the repo
git clone https://github.com/openai-apps-sdk-examples/pizzaz.git
cd pizzaz

# 2. Install dependencies
npm install

# 3. Build the components
npm run build

# 4. Copy component structure
# Adapt to your use case
```

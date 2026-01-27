# Data Model: Web Application for Course Companion FTE

**Feature**: 3-web-app
**Phase**: 1 - Design & Contracts
**Date**: 2026-01-28

## Overview

This document defines the frontend state management, data models, and entity relationships for the Next.js 14 web application.

---

## Frontend State Architecture

The web application uses React Query for server state and React Context for client state.

### State Layers

1. **Server State** (React Query): Data from backend API
   - Chapters, quizzes, progress, streaks, user profile
   - Cached, refetched, synchronized with server

2. **Client State** (React Context/Zustand): UI-only state
   - Modal open/closed
   - Selected answer in quiz
   - Sidebar collapsed/expanded
   - Theme (light/dark)

3. **URL State** (Next.js Router): Navigation state
   - Current page, chapter ID, quiz ID
   - Search query parameters

---

## TypeScript Interfaces

### User

```typescript
interface User {
  id: string;
  email: string;
  tier: 'free' | 'premium' | 'pro';
  created_at: string;
  last_login: string | null;
}

interface Session {
  user: User;
  accessToken: string;
  expires: string;
}
```

### Chapter

```typescript
interface Chapter {
  id: string;
  title: string;
  content?: string; // Optional: full content loaded separately
  order: number;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: number; // Minutes
  next_chapter_id?: string;
  previous_chapter_id?: string;
  completed?: boolean; // Derived from progress
}

interface ChapterList extends Chapter {
  // Lightweight version for list view
  content?: never;
}
```

### Quiz

```typescript
interface Question {
  id: string;
  quiz_id: string;
  question_text: string;
  options: Record<string, string>; // { A: "Option A", B: "Option B", ... }
  correct_answer: 'A' | 'B' | 'C' | 'D';
  explanation?: string;
  order: number;
}

interface Quiz {
  id: string;
  chapter_id: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  questions: Question[];
}

interface QuizSubmission {
  quiz_id: string;
  answers: Record<string, string>; // { questionId: answer, ... }
}

interface QuizResult {
  id: string;
  user_id: string;
  quiz_id: string;
  score: number; // 0-100
  passed: boolean;
  answers: Record<string, string>;
  feedback: string;
  completed_at: string;
}
```

### Progress

```typescript
interface Progress {
  id: string;
  user_id: string;
  completed_chapters: string[]; // Array of chapter IDs
  current_chapter_id: string | null;
  last_activity: string;
  completion_percentage: number; // Derived: (completed / total) * 100
}

interface Streak {
  id: string;
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_checkin: string | null; // Date string or null
}
```

### Dashboard State

```typescript
interface DashboardState {
  progress: Progress | null;
  streak: Streak | null;
  recommendedChapter: Chapter | null;
  recentActivity: QuizResult[];
}
```

---

## React Query Keys

```typescript
// Query keys for React Query cache management
const queryKeys = {
  // Chapters
  chapters: ['chapters'] as const,
  chapter: (id: string) => ['chapters', id] as const,

  // Quizzes
  quizzes: ['quizzes'] as const,
  quiz: (id: string) => ['quizzes', id] as const,
  quizResults: (quizId: string) => ['quizzes', quizId, 'results'] as const,

  // Progress
  progress: (userId: string) => ['progress', userId] as const,
  streak: (userId: string) => ['streaks', userId] as const,

  // User
  user: (userId: string) => ['users', userId] as const,
  session: ['session'] as const,
} as const;
```

---

## Custom Hooks

### useProgress

```typescript
function useProgress(userId: string) {
  return useQuery({
    queryKey: queryKeys.progress(userId),
    queryFn: async () => {
      const res = await fetch(`/api/v1/progress/${userId}`);
      if (!res.ok) throw new Error('Failed to fetch progress');
      return res.json() as Promise<Progress>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
  });
}
```

### useChapters

```typescript
function useChapters() {
  return useQuery({
    queryKey: queryKeys.chapters,
    queryFn: async () => {
      const res = await fetch('/api/v1/chapters');
      if (!res.ok) throw new Error('Failed to fetch chapters');
      return res.json() as Promise<Chapter[]>;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

function useChapter(chapterId: string) {
  return useQuery({
    queryKey: queryKeys.chapter(chapterId),
    queryFn: async () => {
      const res = await fetch(`/api/v1/chapters/${chapterId}`);
      if (!res.ok) throw new Error('Failed to fetch chapter');
      return res.json() as Promise<Chapter>;
    },
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
}
```

### useQuiz

```typescript
function useQuiz(quizId: string) {
  return useQuery({
    queryKey: queryKeys.quiz(quizId),
    queryFn: async () => {
      const res = await fetch(`/api/v1/quizzes/${quizId}`);
      if (!res.ok) throw new Error('Failed to fetch quiz');
      return res.json() as Promise<Quiz>;
    },
    staleTime: 10 * 60 * 1000,
  });
}

function useSubmitQuiz() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ quizId, answers }: QuizSubmission) => {
      const res = await fetch(`/api/v1/quizzes/${quizId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      });
      if (!res.ok) throw new Error('Failed to submit quiz');
      return res.json() as Promise<QuizResult>;
    },
    onSuccess: (data, variables) => {
      // Invalidate progress and quiz queries
      queryClient.invalidateQueries({ queryKey: ['progress'] });
      queryClient.invalidateQueries({ queryKey: queryKeys.quiz(variables.quizId) });
    },
  });
}
```

---

## Component State (Client State)

### Quiz Taking State

```typescript
interface QuizState {
  currentQuestionIndex: number;
  answers: Record<string, string>; // { questionId: selectedAnswer }
  isSubmitted: boolean;
  showResults: boolean;
}

function useQuizState(questionCount: number) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  const setAnswer = (questionId: string, answer: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const canSubmit = useMemo(() => {
    return Object.keys(answers).length === questionCount;
  }, [answers, questionCount]);

  const progress = useMemo(() => {
    return ((currentIndex + 1) / questionCount) * 100;
  }, [currentIndex, questionCount]);

  return {
    currentIndex,
    answers,
    isSubmitted,
    setCurrentIndex,
    setAnswer,
    setIsSubmitted,
    canSubmit,
    progress,
  };
}
```

### UI State (Context)

```typescript
interface UIContextType {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

const UIContext = createContext<UIContextType | undefined>(undefined);

export function UIProvider({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);

  return (
    <UIContext.Provider value={{ isSidebarOpen, toggleSidebar, theme, setTheme }}>
      {children}
    </UIContext.Provider>
  );
}

export function useUI() {
  const context = useContext(UIContext);
  if (!context) throw new Error('useUI must be used within UIProvider');
  return context;
}
```

---

## Data Flow Diagrams

### Dashboard Data Flow

```
User visits dashboard
    ↓
useProgress() fetches progress from /api/v1/progress/{userId}
useStreak() fetches streak from /api/v1/streaks/{userId}
useChapters() fetches chapters from /api/v1/chapters
    ↓
React Query caches responses
    ↓
Components render with data:
  - ProgressChart shows completion percentage
  - StreakDisplay shows current streak
  - CourseOutline shows chapters with completion status
    ↓
User clicks "Continue Learning"
    ↓
Router navigates to /chapters/{currentChapterId}
```

### Quiz Data Flow

```
User navigates to /quizzes/{quizId}
    ↓
useQuiz() fetches quiz from /api/v1/quizzes/{quizId}
    ↓
Quiz component renders questions one at a time
    ↓
User selects answers (stored in local state)
    ↓
User clicks "Submit Quiz"
    ↓
useSubmitQuiz() mutation POSTs to /api/v1/quizzes/{quizId}/submit
    ↓
Backend grades quiz and returns results
    ↓
 onSuccess callback:
  - Invalidate progress query (refetches updated progress)
  - Invalidate quiz query (shows updated results)
    ↓
User redirected to /quizzes/{quizId}/results
```

---

## Entity Relationships

```
User (1) ----< (1) Session
User (1) ----< (1) Progress
User (1) ----< (1) Streak
User (1) ----< (N) QuizAttempt

Chapter (1) ----< (1) Quiz
Chapter (N) ----< (N) Question (via Quiz)

Quiz (1) ----< (N) Question
Quiz (1) ----< (N) QuizAttempt

Question (N) ----< (1) Quiz
Question (N) ----< (N) QuizAnswer (in QuizAttempt)

Progress (1) ----< (N) Chapter (via completed_chapters)
```

**Frontend Derivations**:
- `Chapter.completed` = `progress.completed_chapters.includes(chapter.id)`
- `Progress.completion_percentage` = `(completed_chapters.length / total_chapters) * 100`
- `Dashboard.recommendedChapter` = First chapter not in `completed_chapters`

---

## Form State

### Login Form

```typescript
interface LoginFormData {
  email: string;
  password: string;
}

function useLoginForm() {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof LoginFormData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof LoginFormData, string>> = {};

    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await signIn('credentials', formData);
    } catch (error) {
      setErrors({ email: 'Invalid email or password' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    formData,
    errors,
    isSubmitting,
    setFormData,
    handleSubmit,
  };
}
```

### Password Change Form

```typescript
interface PasswordChangeFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

function usePasswordChangeForm() {
  const [formData, setFormData] = useState<PasswordChangeFormData>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof PasswordChangeFormData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof PasswordChangeFormData, string>> = {};

    if (!formData.currentPassword) newErrors.currentPassword = 'Current password is required';
    if (formData.newPassword.length < 8) newErrors.newPassword = 'Password must be at least 8 characters';
    if (formData.newPassword !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await fetch('/api/v1/user/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currentPassword: formData.currentPassword,
          newPassword: formData.newPassword,
        }),
      });
      setSuccess(true);
    } catch (error) {
      setErrors({ currentPassword: 'Failed to update password' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    formData,
    errors,
    isSubmitting,
    success,
    setFormData,
    handleSubmit,
  };
}
```

---

## URL State Management

### Search and Filter State

```typescript
// URL: /chapters?search=neural&difficulty=beginner
function useChapterFilters() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const search = searchParams.get('search') || '';
  const difficulty = searchParams.get('difficulty') || '';

  const setSearch = (value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set('search', value);
    else params.delete('search');
    router.push(`/chapters?${params.toString()}`);
  };

  const setDifficulty = (value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set('difficulty', value);
    else params.delete('difficulty');
    router.push(`/chapters?${params.toString()}`);
  };

  return { search, difficulty, setSearch, setDifficulty };
}
```

---

## Performance Optimizations

### Code Splitting

```typescript
// Lazy load dashboard components
const ProgressChart = dynamic(() => import('@/components/dashboard/ProgressChart'), {
  loading: () => <Skeleton className="h-48 w-48 rounded-full" />,
});

const StreakCalendar = dynamic(() => import('@/components/dashboard/StreakCalendar'), {
  loading: () => <Skeleton className="h-32 w-full" />,
});
```

### Image Optimization

```typescript
import Image from 'next/image';

<Image
  src="/chapter-illustration.png"
  alt="Chapter illustration"
  width={800}
  height={400}
  priority={false} // Lazy load off-screen images
  placeholder="blur" // Show blur placeholder while loading
/>
```

---

**Next Steps**: Create API client contracts and quickstart guide

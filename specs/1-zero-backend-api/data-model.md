# Data Model: Zero-Backend-LLM Course Companion API

**Feature**: 1-zero-backend-api
**Phase**: 1 - Design & Contracts
**Date**: 2026-01-28

## Overview

This document defines the database schema, entities, and relationships for the Course Companion FTE backend API.

---

## Core Entities

### User

Represents a student account with authentication and subscription tier.

```python
class User(Base):
    __tablename__ = "users"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Email = Column(String, unique=True, nullable=False, index=True)
    hashed_password: str = Column(String, nullable=False)
    tier: Enum = Column(Enum(UserTier), default=UserTier.free, nullable=False)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: DateTime = Column(DateTime, nullable=True)

    # Relationships
    progress: Relationship = relationship("Progress", back_populates="user", uselist=False)
    streak: Relationship = relationship("Streak", back_populates="user", uselist=False)
    quiz_attempts: Relationship = relationship("QuizAttempt", back_populates="user")
```

**Fields**:
- `id` (UUID): Primary key, unique identifier
- `email` (Email): Unique login email, indexed for fast lookups
- `hashed_password` (String): bcrypt hash of password (never store plaintext)
- `tier` (Enum): Subscription tier (free, premium, pro)
- `created_at` (DateTime): Account creation timestamp
- `last_login` (DateTime): Last successful login timestamp

**Validation Rules**:
- Email must be valid format and unique
- Password must be 8+ characters with at least one letter and one number
- Tier must be one of: free, premium, pro

**Indexes**:
- Primary index on `id`
- Unique index on `email` for login queries

---

### Chapter

Represents a course chapter with content stored in Cloudflare R2.

```python
class Chapter(Base):
    __tablename__ = "chapters"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: str = Column(String, nullable=False)
    content: Text = Column(Text, nullable=True)  # Optional: content stored in R2
    order: Integer = Column(Integer, unique=True, nullable=False, index=True)
    difficulty_level: Enum = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    estimated_time: Integer = Column(Integer, default=30)  # Minutes
    r2_content_key: str = Column(String, nullable=True)  # R2 object key
    next_chapter_id: UUID = Column(UUID, ForeignKey("chapters.id"), nullable=True)
    previous_chapter_id: UUID = Column(UUID, ForeignKey("chapters.id"), nullable=True)

    # Relationships
    quiz: Relationship = relationship("Quiz", back_populates="chapter", uselist=False)
    next_chapter: Relationship = relationship("Chapter", remote_side=[id], foreign_keys=[next_chapter_id])
    previous_chapter: Relationship = relationship("Chapter", remote_side=[id], foreign_keys=[previous_chapter_id])
```

**Fields**:
- `id` (UUID): Primary key
- `title` (String): Chapter title
- `content` (Text): Markdown content (optional - most content in R2)
- `order` (Integer): Sequential order in course (1, 2, 3...)
- `difficulty_level` (Enum): beginner, intermediate, advanced
- `estimated_time` (Integer): Estimated reading time in minutes
- `r2_content_key` (String): Key for full content in Cloudflare R2
- `next_chapter_id` (UUID): Foreign key to next chapter
- `previous_chapter_id` (UUID): Foreign key to previous chapter

**Validation Rules**:
- `order` must be unique across all chapters
- `difficulty_level` must be one of: beginner, intermediate, advanced
- `estimated_time` must be positive integer

**Indexes**:
- Primary index on `id`
- Unique index on `order` for sequential access

---

### Quiz

Represents a quiz associated with a chapter.

```python
class Quiz(Base):
    __tablename__ = "quizzes"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: UUID = Column(UUID, ForeignKey("chapters.id"), nullable=False)
    title: str = Column(String, nullable=False)
    difficulty: Enum = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chapter: Relationship = relationship("Chapter", back_populates="quiz")
    questions: Relationship = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts: Relationship = relationship("QuizAttempt", back_populates="quiz")
```

**Fields**:
- `id` (UUID): Primary key
- `chapter_id` (UUID): Foreign key to Chapter (one quiz per chapter)
- `title` (String): Quiz title
- `difficulty` (Enum): beginner, intermediate, advanced
- `created_at` (DateTime): Quiz creation timestamp

**Validation Rules**:
- Each chapter can have at most one quiz
- Difficulty must match chapter difficulty (optional constraint)

**Indexes**:
- Primary index on `id`
- Index on `chapter_id` for quiz lookup by chapter

---

### Question

Represents a multiple-choice question within a quiz.

```python
class Question(Base):
    __tablename__ = "questions"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: UUID = Column(UUID, ForeignKey("quizzes.id"), nullable=False)
    question_text: str = Column(Text, nullable=False)
    options: JSON = Column(JSON, nullable=False)  # {"A": "Option A", "B": "Option B", ...}
    correct_answer: Enum = Column(Enum(AnswerChoice), nullable=False)  # "A", "B", "C", "D"
    explanation: Text = Column(Text, nullable=True)
    order: Integer = Column(Integer, nullable=False)

    # Relationships
    quiz: Relationship = relationship("Quiz", back_populates="questions")
```

**Fields**:
- `id` (UUID): Primary key
- `quiz_id` (UUID): Foreign key to Quiz
- `question_text` (String): The question text
- `options` (JSON): Multiple choice options as key-value pairs
- `correct_answer` (Enum): One of "A", "B", "C", "D"
- `explanation` (Text): Explanation for why answer is correct
- `order` (Integer): Order within quiz

**Validation Rules**:
- `options` must contain exactly 4 options (A, B, C, D)
- `correct_answer` must be a valid key in `options`
- `explanation` is required for educational value

**Indexes**:
- Primary index on `id`
- Index on `quiz_id` for question lookup

---

### Progress

Tracks a student's learning progress through the course.

```python
class Progress(Base):
    __tablename__ = "progress"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: UUID = Column(UUID, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    completed_chapters: JSON = Column(JSON, default=list)  # Array of chapter IDs
    current_chapter_id: UUID = Column(UUID, ForeignKey("chapters.id"), nullable=True)
    last_activity: DateTime = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Relationship = relationship("User", back_populates="progress")
    current_chapter: Relationship = relationship("Chapter")
```

**Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User (unique - one progress per user)
- `completed_chapters` (JSON): Array of completed chapter IDs
- `current_chapter_id` (UUID): ID of chapter student is currently on
- `last_activity` (DateTime): Timestamp of last learning activity

**Validation Rules**:
- `user_id` must be unique (one progress record per user)
- `completed_chapters` must be valid chapter IDs

**Indexes**:
- Primary index on `id`
- Unique index on `user_id`

---

### Streak

Tracks a student's learning streak for gamification.

```python
class Streak(Base):
    __tablename__ = "streaks"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: UUID = Column(UUID, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    current_streak: Integer = Column(Integer, default=0, nullable=False)
    longest_streak: Integer = Column(Integer, default=0, nullable=False)
    last_checkin: Date = Column(Date, nullable=True)

    # Relationships
    user: Relationship = relationship("User", back_populates="streak")
```

**Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User (unique)
- `current_streak` (Integer): Current consecutive days of activity
- `longest_streak` (Integer): Historical maximum streak
- `last_checkin` (Date): Date of last activity

**Validation Rules**:
- `current_streak` must be non-negative
- `longest_streak` must be >= `current_streak`
- Streak increments when activity on consecutive days
- Streak resets to 0 when gap > 1 day

**Indexes**:
- Primary index on `id`
- Unique index on `user_id`

---

### QuizAttempt

Records a student's quiz attempt with answers and score.

```python
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: UUID = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id: UUID = Column(UUID, ForeignKey("quizzes.id"), nullable=False, index=True)
    score: Integer = Column(Integer, nullable=False)  # Percentage (0-100)
    answers: JSON = Column(JSON, nullable=False)  # {question_id: answer, ...}
    completed_at: DateTime = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Relationship = relationship("User", back_populates="quiz_attempts")
    quiz: Relationship = relationship("Quiz", back_populates="attempts")
```

**Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `quiz_id` (UUID): Foreign key to Quiz
- `score` (Integer): Score as percentage (0-100)
- `answers` (JSON): Map of question_id to selected answer
- `completed_at` (DateTime): Quiz completion timestamp

**Validation Rules**:
- `score` must be between 0 and 100
- `answers` must contain one answer per question in quiz
- Passing score is >= 70%

**Indexes**:
- Primary index on `id`
- Index on `user_id` for user's attempt history
- Index on `quiz_id` for quiz statistics

---

## Entity Relationships

```
User (1) ----< (1) Progress
User (1) ----< (1) Streak
User (1) ----< (N) QuizAttempt
User (N) ----< (N) Chapter (access via Progress)

Chapter (1) ----< (1) Quiz
Chapter (1) ----< (N) Question
Chapter (N) ----< (N) Question (via Quiz)

Quiz (1) ----< (N) Question
Quiz (1) ----< (N) QuizAttempt

Question (N) ----< (1) Quiz
Question (N) ----< (N) QuizAttempt (via answers JSON)
```

**Key Constraints**:
- One User has one Progress record
- One User has one Streak record
- One Chapter has one Quiz
- One Quiz has many Questions
- One User can have many QuizAttempts
- One Quiz can have many QuizAttempts

---

## Database Schema (SQL)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'free',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Chapters table
CREATE TABLE chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    order INTEGER UNIQUE NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL DEFAULT 'beginner',
    estimated_time INTEGER NOT NULL DEFAULT 30,
    r2_content_key VARCHAR(255),
    next_chapter_id UUID REFERENCES chapters(id),
    previous_chapter_id UUID REFERENCES chapters(id)
);

CREATE INDEX idx_chapters_order ON chapters(order);

-- Quizzes table
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID NOT NULL REFERENCES chapters(id) UNIQUE,
    title VARCHAR(255) NOT NULL,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quizzes_chapter_id ON quizzes(chapter_id);

-- Questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    question_text TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer VARCHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    order INTEGER NOT NULL
);

CREATE INDEX idx_questions_quiz_id ON questions(quiz_id);

-- Progress table
CREATE TABLE progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id),
    completed_chapters JSONB NOT NULL DEFAULT '[]',
    current_chapter_id UUID REFERENCES chapters(id),
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_progress_user_id ON progress(user_id);

-- Streaks table
CREATE TABLE streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id),
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    last_checkin DATE
);

CREATE INDEX idx_streaks_user_id ON streaks(user_id);

-- Quiz attempts table
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    answers JSONB NOT NULL,
    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX idx_quiz_attempts_quiz_id ON quiz_attempts(quiz_id);
```

---

## State Transitions

### User Tier Transitions
```
free → premium (via payment)
premium → pro (via payment)
pro → premium (downgrade)
premium → free (downgrade)
```

### Progress State Machine
```
[No Progress] → [Chapter 1 Started] → [Chapter 1 Complete] → [Chapter 2 Started] → ...
                        ↓                      ↓
                    [Quiz 1 Started] → [Quiz 1 Complete] → [Chapter 2 Complete]
```

### Streak State Machine
```
0 → [Activity Today] → 1 → [Activity Tomorrow] → 2 → ...
          ↓ (miss day)          ↓ (miss day)
          0                     0
```

**Streak Continuity Rule**: If `last_checkin` was yesterday, increment. If `last_checkin` was today, no change. If `last_checkin` was >1 day ago, reset to 0.

---

## Data Access Patterns

### Most Common Queries
1. **Get user by email** (login): `SELECT * FROM users WHERE email = ?`
2. **Get chapter by order** (navigation): `SELECT * FROM chapters WHERE order = ?`
3. **Get quiz by chapter_id**: `SELECT * FROM quizzes WHERE chapter_id = ?`
4. **Get user progress**: `SELECT * FROM progress WHERE user_id = ?`
5. **Get user streak**: `SELECT * FROM streaks WHERE user_id = ?`
6. **List all chapters** (course outline): `SELECT * FROM chapters ORDER BY order`
7. **Get quiz with questions**: `SELECT * FROM quizzes WHERE id = ?; SELECT * FROM questions WHERE quiz_id = ?`

### Optimization Strategies
- Index on `users.email` for fast login
- Index on `chapters.order` for sequential access
- Denormalize `chapter_id` in `quizzes` for one-query quiz lookup
- Use JSONB for `completed_chapters` and `answers` (efficient in PostgreSQL)

---

**Next Steps**: Create API contracts (OpenAPI specs) and quickstart guide

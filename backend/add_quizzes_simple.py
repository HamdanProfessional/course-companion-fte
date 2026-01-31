"""
Add simple multiple-choice quizzes for each chapter.
"""
import asyncio
import asyncpg
import uuid
import json
import os

# Simple multiple choice quizzes (only A, B, C, D answers)
CHAPTER_1_QUIZ = {
    "title": "Introduction to AI Agents - Quiz",
    "difficulty": "BEGINNER",
    "questions": [
        {
            "question": "What are the three core components of an AI agent?",
            "options": {"A": "Planning, Memory, Tools", "B": "Input, Output, Storage", "C": "CPU, RAM, GPU", "D": "Frontend, Backend, Database"},
            "correct_answer": "A",
            "explanation": "AI agents have Planning (decides actions), Memory (stores context), and Tools (takes actions)."
        },
        {
            "question": "True or False: AI agents can use external tools and APIs.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "explanation": "Unlike traditional chatbots, AI agents can use external tools like APIs, databases, and file systems."
        },
        {
            "question": "What is the primary difference between a chatbot and an AI agent?",
            "options": {"A": "Agents are faster", "B": "Agents can take actions and use tools", "C": "Chatbots are smarter", "D": "There is no difference"},
            "correct_answer": "B",
            "explanation": "AI agents can break down goals, use tools, maintain context, and take real actions - chatbots cannot."
        },
        {
            "question": "Which component of an AI agent decides what actions to take?",
            "options": {"A": "Memory", "B": "Tools", "C": "Planning", "D": "Database"},
            "correct_answer": "C",
            "explanation": "The Planning component (the brain) decides what actions to take based on goals, context, and available tools."
        }
    ]
}

CHAPTER_2_QUIZ = {
    "title": "Understanding MCP - Quiz",
    "difficulty": "BEGINNER",
    "questions": [
        {
            "question": "What does MCP stand for?",
            "options": {"A": "Model Context Protocol", "B": "Machine Control Protocol", "C": "Multi-Cloud Platform", "D": "Memory Cache Process"},
            "correct_answer": "A",
            "explanation": "MCP stands for Model Context Protocol, an open standard for connecting AI assistants to external data and tools."
        },
        {
            "question": "What problem does MCP solve?",
            "options": {"A": "Makes AI faster", "B": "Provides standardized way to connect AI to tools/data", "C": "Improves AI accuracy", "D": "Reduces AI costs"},
            "correct_answer": "B",
            "explanation": "MCP provides a universal standard for connecting AI assistants to external tools and data sources, eliminating custom integrations."
        },
        {
            "question": "Which of the following is NOT a type of MCP server?",
            "options": {"A": "Filesystem servers", "B": "Database servers", "C": "API servers", "D": "Graphics rendering servers"},
            "correct_answer": "D",
            "explanation": "MCP servers include filesystem, database, API, and custom servers - but not graphics rendering."
        },
        {
            "question": "True or False: MCP requires custom authentication for each tool.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "B",
            "explanation": "False! MCP standardizes authentication, making it plug-and-play without custom auth flows for each tool."
        }
    ]
}

CHAPTER_3_QUIZ = {
    "title": "Creating Your First Agent - Quiz",
    "difficulty": "INTERMEDIATE",
    "questions": [
        {
            "question": "What is the first step in building an AI agent?",
            "options": {"A": "Write code immediately", "B": "Define the agent's purpose clearly", "C": "Design the UI", "D": "Buy a server"},
            "correct_answer": "B",
            "explanation": "Always start by clearly defining your agent's purpose and goals - this guides all subsequent design decisions."
        },
        {
            "question": "Which file defines how a skill works?",
            "options": {"A": "skill.py", "B": "SKILL.md", "C": "config.json", "D": "README.md"},
            "correct_answer": "B",
            "explanation": "SKILL.md contains the skill's purpose, instructions, examples, and configuration - it's the primary definition file."
        },
        {
            "question": "What is intent detection used for?",
            "options": {"A": "Spelling correction", "B": "Understanding what the user wants to do", "C": "Language translation", "D": "Text formatting"},
            "correct_answer": "B",
            "explanation": "Intent detection determines what the user wants (explain, quiz, help, etc.) so the agent can load the appropriate skill."
        },
        {
            "question": "Which deployment option gives you maximum control?",
            "options": {"A": "ChatGPT Custom GPT", "B": "OpenAI Apps SDK", "C": "Full Web App", "D": "All give equal control"},
            "correct_answer": "C",
            "explanation": "A full web app gives maximum control over UI, backend logic, and features, but requires more development effort."
        }
    ]
}

CHAPTER_4_QUIZ = {
    "title": "Building Reusable Skills - Quiz",
    "difficulty": "INTERMEDIATE",
    "questions": [
        {
            "question": "What makes a skill reusable?",
            "options": {"A": "Complex code", "B": "Self-contained, documented, configurable", "C": "Large file size", "D": "Uses many dependencies"},
            "correct_answer": "B",
            "explanation": "Reusable skills are self-contained, well-documented, configurable, composable, and tested - like LEGO bricks."
        },
        {
            "question": "Which skill should be activated when a student says 'Quiz me'?",
            "options": {"A": "Concept Explainer", "B": "Quiz Master", "C": "Socratic Tutor", "D": "Progress Motivator"},
            "correct_answer": "B",
            "explanation": "The Quiz Master skill handles all quiz-related requests - generating questions, grading answers, and providing feedback."
        },
        {
            "question": "What is the main principle of the Socratic Tutor skill?",
            "options": {"A": "Give direct answers", "B": "Guide learning through questioning", "C": "Grade everything", "D": "Display progress"},
            "correct_answer": "B",
            "explanation": "The Socratic Tutor never gives direct answers - instead, it asks probing questions to guide students toward understanding."
        },
        {
            "question": "True or False: Skills can share context and state.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "explanation": "Skills can share context through shared state/memory, allowing them to work together cohesively in a conversation."
        }
    ]
}

async def add_quizzes():
    """Add quizzes to database."""
    # Get database URL from environment variable (convert asyncpg to asyncpg format for direct connection)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Convert SQLAlchemy asyncpg URL to asyncpg format if needed
    if database_url.startswith('postgresql+asyncpg://'):
        # Remove the +asyncpg for direct asyncpg connection
        database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')

    conn = await asyncpg.connect(database_url)

    print("Connected to database")

    # Delete existing quizzes
    await conn.execute('DELETE FROM quiz_attempts')
    await conn.execute('DELETE FROM questions')
    await conn.execute('DELETE FROM quizzes')
    print("Cleared existing quizzes")

    # Get chapters
    chapters = await conn.fetch('SELECT id, title FROM chapters ORDER BY "order"')
    print(f"Found {len(chapters)} chapters")

    # Map titles to IDs
    chapter_map = {ch['title']: ch['id'] for ch in chapters}

    # Link quizzes to chapters
    quizzes = [
        (CHAPTER_1_QUIZ, chapter_map.get('Introduction to AI Agents')),
        (CHAPTER_2_QUIZ, chapter_map.get('Understanding MCP (Model Context Protocol)')),
        (CHAPTER_3_QUIZ, chapter_map.get('Creating Your First Agent')),
        (CHAPTER_4_QUIZ, chapter_map.get('Building Reusable Skills'))
    ]

    # Add each quiz
    for quiz_data, chapter_id in quizzes:
        if not chapter_id:
            print(f"⚠ Skipping {quiz_data['title']} - chapter not found")
            continue

        # Create quiz
        quiz_id = str(uuid.uuid4())

        await conn.execute("""
            INSERT INTO quizzes (id, title, chapter_id, difficulty)
            VALUES ($1, $2, $3, $4)
        """, quiz_id, quiz_data['title'], chapter_id, quiz_data['difficulty'])

        print(f"✓ Created quiz: {quiz_data['title']}")

        # Add questions
        for i, q in enumerate(quiz_data['questions']):
            question_id = str(uuid.uuid4())

            await conn.execute("""
                INSERT INTO questions (id, quiz_id, question_text,
                                     options, correct_answer, explanation, "order")
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, question_id, quiz_id, q['question'],
                 json.dumps(q['options']), q['correct_answer'], q['explanation'], i)

        print(f"  Added {len(quiz_data['questions'])} questions")

    # Verify
    quiz_count = await conn.fetchval('SELECT COUNT(*) FROM quizzes')
    question_count = await conn.fetchval('SELECT COUNT(*) FROM questions')

    print(f"\n✅ Quiz setup complete!")
    print(f"  Total quizzes: {quiz_count}")
    print(f"  Total questions: {question_count}")

    # Show quiz details
    quizzes_info = await conn.fetch('''
        SELECT q.title, COUNT(qs.id) as question_count
        FROM quizzes q
        LEFT JOIN questions qs ON q.id = qs.quiz_id
        GROUP BY q.id, q.title
        ORDER BY q.title
    ''')

    print("\nQuiz Details:")
    for quiz in quizzes_info:
        print(f"  • {quiz['title']}: {quiz['question_count']} questions")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(add_quizzes())

"""
Add comprehensive quizzes with more questions per chapter.
Expanded from 4 to 6 questions per chapter (24 total).
"""
import asyncio
import asyncpg
import uuid
import json
import os

# Enhanced quizzes with 6 questions each
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
            "options": {"A": "True, agents can use external tools", "B": "False, agents cannot use tools", "C": "True, but only with special permissions", "D": "False, only chatbots can use tools"},
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
        },
        {
            "question": "What does an AI agent use to maintain context over long conversations?",
            "options": {"A": "Planning component", "B": "Memory component", "C": "Tools component", "D": "API layer"},
            "correct_answer": "B",
            "explanation": "The Memory component stores and retrieves information, allowing agents to maintain context, remember preferences, and learn from past interactions."
        },
        {
            "question": "Which of these is NOT an example of an external tool an AI agent might use?",
            "options": {"A": "Weather API", "B": "File system", "C": "AI model", "D": "Database"},
            "correct_answer": "C",
            "explanation": "The AI model itself (like GPT) is NOT an external tool - it's the core intelligence. APIs, file systems, and databases ARE external tools."
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
            "explanation": "MCP servers include filesystem, database, API, and custom servers - but not graphics rendering (yet!)."
        },
        {
            "question": "True or False: MCP requires custom authentication for each tool.",
            "options": {"A": "True, each tool needs custom auth", "B": "False, MCP standardizes auth", "C": "True, but only for paid tools", "D": "False, MCP doesn't use authentication"},
            "correct_answer": "B",
            "explanation": "False! MCP standardizes authentication, making it plug-and-play without custom auth flows for each tool."
        },
        {
            "question": "In the MCP architecture, what component runs the AI assistant?",
            "options": {"A": "MCP Server", "B": "MCP Client", "C": "MCP Host", "D": "MCP Protocol"},
            "correct_answer": "C",
            "explanation": "The MCP Host runs the AI assistant (like Claude or ChatGPT) and manages connections to MCP Servers."
        },
        {
            "question": "What is the main benefit of using MCP for tool integration?",
            "options": {"A": "Faster AI responses", "B": "Universal plug-and-play standard", "C": "Cheaper storage", "D": "Better security"},
            "correct_answer": "B",
            "explanation": "MCP's main benefit is providing a universal standard - any tool that implements MCP can work with any AI assistant that supports MCP."
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
        },
        {
            "question": "What is a 'skill' in the context of AI agents?",
            "options": {"A": "A programming language", "B": "A modular capability the agent can use", "C": "A user interface", "D": "A database table"},
            "correct_answer": "B",
            "explanation": "Skills are modular capabilities like 'concept explainer' or 'quiz master' that an agent can load to accomplish specific tasks."
        },
        {
            "question": "Why is it important to test skills independently before combining them?",
            "options": {"A": "To write more code", "B": "Isolating bugs and ensuring reliability", "C": "To impress investors", "D": "It's not important"},
            "correct_answer": "B",
            "explanation": "Testing skills independently makes debugging easier, ensures reliable behavior, and allows you to verify each skill meets requirements before composing them."
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
            "options": {"A": "True, skills can share context", "B": "False, skills are isolated", "C": "True, but only with special permissions", "D": "False, skills have no memory"},
            "correct_answer": "A",
            "explanation": "Skills can share context through shared state/memory, allowing them to work together cohesively in a conversation."
        },
        {
            "question": "What is 'skill composition'?",
            "options": {"A": "Writing complex code", "B": "Combining multiple skills together", "C": "Deleting unused skills", "D": "Creating one large skill"},
            "correct_answer": "B",
            "explanation": "Skill composition is the practice of combining multiple skills together, allowing them to work collaboratively on complex tasks."
        },
        {
            "question": "Why should skills fail gracefully?",
            "options": {"A": "They shouldn't - always show errors", "B": "To provide fallback responses and maintain user experience", "C": "To confuse users", "D": "No reason"},
            "correct_answer": "B",
            "explanation": "Graceful failure means providing helpful fallback responses when things go wrong, maintaining a good user experience instead of showing raw errors."
        }
    ]
}

async def add_enhanced_quizzes():
    """Add enhanced quizzes with 6 questions each."""
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Convert SQLAlchemy asyncpg URL to asyncpg format if needed
    if database_url.startswith('postgresql+asyncpg://'):
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

    total_questions = 0

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

        total_questions += len(quiz_data['questions'])
        print(f"  Added {len(quiz_data['questions'])} questions")

    # Update chapters with quiz IDs
    for quiz_data, chapter_id in quizzes:
        if chapter_id:
            # Get the quiz ID we just created
            quiz = await conn.fetchrow('SELECT id FROM quizzes WHERE chapter_id = $1', chapter_id)
            if quiz:
                await conn.execute('UPDATE chapters SET quiz_id = $1 WHERE id = $2', quiz['id'], chapter_id)

    # Verify
    quiz_count = await conn.fetchval('SELECT COUNT(*) FROM quizzes')
    question_count = await conn.fetchval('SELECT COUNT(*) FROM questions')

    print(f"\n✅ Enhanced quiz setup complete!")
    print(f"  Total quizzes: {quiz_count}")
    print(f"  Total questions: {question_count}")

    # Show quiz details
    quizzes_info = await conn.fetch('''
        SELECT q.title,
               q.difficulty,
               COUNT(qs.id) as question_count
        FROM quizzes q
        LEFT JOIN questions qs ON q.id = qs.quiz_id
        GROUP BY q.id, q.title, q.difficulty
        ORDER BY q.title
    ''')

    print("\nQuiz Details:")
    for quiz in quizzes_info:
        print(f"  • {quiz['title']}")
        print(f"    Difficulty: {quiz['difficulty']}")
        print(f"    Questions: {quiz['question_count']}")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(add_enhanced_quizzes())

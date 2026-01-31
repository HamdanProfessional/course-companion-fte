"""Simple database initialization script using asyncpg directly."""
import asyncio
import uuid
import bcrypt
import asyncpg
import os

async def main():
    # Connect to database from environment variable
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    conn = await asyncpg.connect(database_url)

    try:
        # Clear existing data first
        print("Clearing existing data...")
        await conn.execute("DELETE FROM quiz_attempts")
        await conn.execute("DELETE FROM questions")
        await conn.execute("DELETE FROM quizzes")
        await conn.execute("DELETE FROM streaks")
        await conn.execute("DELETE FROM progress")
        await conn.execute("DELETE FROM chapters")
        await conn.execute("DELETE FROM users")
        print("OK Data cleared")

        # Create test user
        hashed = bcrypt.hashpw("pass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())

        await conn.execute("""
            INSERT INTO users (id, email, hashed_password, tier)
            VALUES ($1, $2, $3, $4)
        """, user_id, "student@example.com", hashed, "FREE")

        print(f"OK Created user: student@example.com")

        # Create progress and streak
        import json
        await conn.execute("""
            INSERT INTO progress (id, user_id, completed_chapters)
            VALUES ($1, $2, $3)
        """, str(uuid.uuid4()), user_id, json.dumps([]))

        await conn.execute("""
            INSERT INTO streaks (id, user_id, current_streak, longest_streak)
            VALUES ($1, $2, $3, $4)
        """, str(uuid.uuid4()), user_id, 0, 0)

        print("OK Created progress and streak")

        # Create chapters
        chapters = []
        chapter_titles = [
            "Introduction to AI Agents",
            "Understanding MCP (Model Context Protocol)",
            "Creating Your First Agent",
            "Building Reusable Skills"
        ]

        for i, title in enumerate(chapter_titles, 1):
            chapter_id = str(uuid.uuid4())
            content = f"# {title}\n\nThis is the content for chapter {i}..."

            await conn.execute("""
                INSERT INTO chapters (id, title, content, "order", difficulty_level, estimated_time)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, chapter_id, title, content, i, "BEGINNER", 30)

            chapters.append((i, chapter_id, title))
            print(f"OK Created chapter {i}: {title}")

        # Link chapters (next/previous)
        for order, chapter_id, title in chapters:
            if order < len(chapters):
                next_chapter_id = chapters[order][1]
                await conn.execute("""
                    UPDATE chapters SET next_chapter_id = $1 WHERE id = $2
                """, next_chapter_id, chapter_id)

            if order > 1:
                prev_chapter_id = chapters[order-2][1]
                await conn.execute("""
                    UPDATE chapters SET previous_chapter_id = $1 WHERE id = $2
                """, prev_chapter_id, chapter_id)

        print("\nOK Sample data created successfully!")
        print(f"  - {len(chapters)} chapters")
        print(f"  - 1 test user")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())

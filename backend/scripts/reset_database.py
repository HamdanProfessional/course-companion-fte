"""
Reset database by dropping all tables and recreating them.
Use this to ensure the database schema matches the current models.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / ".env")
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from src.core.database import engine, async_session_maker
from src.models.database import Base


async def reset_database():
    """Drop all tables and recreate them from models."""
    print("=" * 70)
    print("Course Companion FTE - Database Reset Script")
    print("=" * 70)
    print("\nWARNING: This will DELETE ALL DATA in the database!")

    async with async_session_maker() as session:
        # Get list of all tables
        result = await session.execute(text("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        tables = [row[0] for row in result.fetchall()]

        if tables:
            print(f"\nFound {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")

            # Drop all tables with CASCADE to handle foreign key dependencies
            print("\nDropping all tables...")
            for table in tables:
                await session.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
                print(f"  - Dropped: {table}")

            await session.commit()
            print("\nAll tables dropped successfully.")

    # Recreate tables from models
    print("\nRecreating tables from models...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("\n" + "=" * 70)
    print("Database reset completed successfully!")
    print("=" * 70)
    print("\nYou can now run the seed script:")
    print("  python scripts/seed_database.py")


if __name__ == "__main__":
    asyncio.run(reset_database())

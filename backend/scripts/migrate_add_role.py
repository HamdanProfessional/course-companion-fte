"""
Migration script to add 'role' column to users table.
Run this after pulling the latest code to update your database schema.
"""

import asyncio
from sqlalchemy import text
from src.core.database import get_db_session


async def migrate_add_role_column():
    """Add role column to users table with default value 'student'."""

    async with get_db_session() as db:
        try:
            # Check if role column already exists
            result = await db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='users' AND column_name='role'
            """))

            if result.first():
                print("✓ Role column already exists in users table")
                return

            # Add role column with default value
            print("Adding role column to users table...")
            await db.execute(text("""
                ALTER TABLE users
                ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student'
            """))

            # Create check constraint for valid roles
            await db.execute(text("""
                ALTER TABLE users
                ADD CONSTRAINT check_valid_role
                CHECK (role IN ('student', 'teacher'))
            """))

            await db.commit()
            print("✓ Successfully added role column to users table")
            print("✓ Added constraint: role must be 'student' or 'teacher'")

        except Exception as e:
            await db.rollback()
            print(f"✗ Migration failed: {e}")
            raise


async def migrate_update_existing_users():
    """Ensure all existing users have the role column set."""

    async with get_db_session() as db:
        try:
            # Update any NULL values to 'student'
            result = await db.execute(text("""
                UPDATE users
                SET role = 'student'
                WHERE role IS NULL
            """))

            await db.commit()
            print(f"✓ Updated existing users to have 'student' role")

        except Exception as e:
            await db.rollback()
            print(f"✗ Migration failed: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add role column to users table")
    print("=" * 60)

    asyncio.run(migrate_add_role_column())
    asyncio.run(migrate_update_existing_users())

    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)

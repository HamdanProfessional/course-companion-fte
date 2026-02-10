#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/home/n00bi2761/course-companion/backend')

from sqlalchemy import select, update
from src.core.database import async_session_maker
from src.models.database import User

async def update_teacher_role():
    async with async_session_maker() as session:
        # Find all users
        result = await session.execute(select(User).order_by(User.email))
        users = result.scalars().all()

        print("All users in database:")
        for user in users:
            print(f"- Email: {user.email}, Role: {user.role}, ID: {user.id}")

        # Find potential teacher accounts (those with 'teacher' in email or username)
        teacher_candidates = [
            u for u in users
            if 'teacher' in u.email.lower() or 'teacher' in (u.email.split('@')[0] if '@' in u.email else '').lower()
        ]

        updated_count = 0
        for user in teacher_candidates:
            if user.role != 'teacher':
                user.role = 'teacher'
                updated_count += 1
                print(f"\nUpdated: {user.email} -> role = teacher")
            else:
                print(f"\nAlready teacher: {user.email}")

        await session.commit()

        if updated_count > 0:
            print(f"\nSuccessfully updated {updated_count} account(s) to teacher role!")
        else:
            print("\nNo accounts found with 'teacher' in email that needed updating.")

        # Also show how to create a teacher account
        print("\n" + "="*60)
        print("To create a new teacher account, register with role='teacher':")
        print("POST http://92.113.147.250:3505/api/v1/auth/register")
        print('{"email": "your@email.com", "password": "yourpassword", "role": "teacher"}')
        print("="*60)

asyncio.run(update_teacher_role())

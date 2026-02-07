"""
Gamification Features Setup Script

This script helps set up the gamification features by:
1. Running the Alembic migration to create the new tables
2. Seeding the tips table with pre-written learning tips

Usage:
    cd backend
    python scripts/setup_gamification.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def run_migration():
    """Run Alembic migration to create gamification tables."""
    import subprocess

    print("=" * 60)
    print("Step 1: Running Database Migration")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Migration successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install it first:")
        print("   pip install alembic")
        return False


async def seed_tips():
    """Seed the tips table with pre-written learning tips."""
    print("\n" + "=" * 60)
    print("Step 2: Seeding Tips Table")
    print("=" * 60)

    try:
        # Import seed function
        from scripts.seed_tips import seed_tips as seed_tips_func

        await seed_tips_func()
        return True
    except Exception as e:
        print(f"❌ Failed to seed tips: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup function."""
    print("\n🎮 Course Companion FTE - Gamification Features Setup")
    print("=" * 60)
    print("\nThis will:")
    print("1. Create 3 new database tables (tips, leaderboard_opt_in, certificates)")
    print("2. Seed the tips table with 16 pre-written learning tips")
    print("\n" + "=" * 60 + "\n")

    # Step 1: Run migration
    migration_success = run_migration()

    if not migration_success:
        print("\n❌ Setup failed at migration step.")
        print("Please check the error messages above and try again.")
        return 1

    # Step 2: Seed tips
    tips_success = asyncio.run(seed_tips())

    if not tips_success:
        print("\n⚠️  Migration completed, but tips seeding failed.")
        print("You can try seeding tips separately:")
        print("   python scripts/seed_tips.py")
        return 1

    # Success!
    print("\n" + "=" * 60)
    print("✅ Gamification Features Setup Complete!")
    print("=" * 60)
    print("\nTables created:")
    print("  • tips - Learning tips for dashboard")
    print("  • leaderboard_opt_in - Privacy controls for leaderboard")
    print("  • certificates - Course completion certificates")
    print("\nTips seeded: 16 tips across 4 categories")
    print("\nNext steps:")
    print("  1. Restart your backend server")
    print("  2. Visit /dashboard to see Tip of the Day")
    print("  3. Visit /leaderboard to join the leaderboard")
    print("  4. Visit /profile to check certificate eligibility")
    print("\n" + "=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

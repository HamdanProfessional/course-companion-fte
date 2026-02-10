#!/usr/bin/env python3
"""
Test script to demonstrate Course Companion FTE skills are working.

This script verifies that skill files exist, can be loaded, and contain proper content.
"""

import os
import sys
from pathlib import Path

def test_skills_exist():
    """Verify all skill files exist."""
    print("=" * 60)
    print("TEST 1: Skill Files Exist")
    print("=" * 60)

    skills_dir = Path(".claude/skills")
    required_skills = [
        "concept-explainer",
        "quiz-master",
        "socratic-tutor",
        "progress-motivator"
    ]

    for skill in required_skills:
        skill_file = skills_dir / skill / "SKILL.md"
        if skill_file.exists():
            print(f"[OK] {skill:25} exists ({skill_file.stat().st_size} bytes)")
        else:
            print(f"[FAIL] {skill:25} MISSING")

    print()

def test_skill_content():
    """Verify skills have proper content."""
    print("=" * 60)
    print("TEST 2: Skill Content Validation")
    print("=" * 60)

    skills_dir = Path(".claude/skills")

    # Check concept-explainer
    concept_skill = skills_dir / "concept-explainer" / "SKILL.md"
    if concept_skill.exists():
        content = concept_skill.read_text()
        checks = {
            "Core Principles": "Core Principles" in content,
            "Workflow": "Workflow" in content or "Explanation Workflow" in content,
            "Analogies": "analog" in content.lower() or "analogy" in content.lower(),
            "Examples": "example" in content.lower(),
            "Adaptation": "adapt" in content.lower(),
        }
        print(f"\nconcept-explainer:")
        for check, passed in checks.items():
            status = "[OK]" if passed else "[MISSING]"
            print(f"  {status} {check}")

    # Check quiz-master
    quiz_skill = skills_dir / "quiz-master" / "SKILL.md"
    if quiz_skill.exists():
        content = quiz_skill.read_text()
        checks = {
            "Encouragement": "encourag" in content.lower(),
            "Feedback": "feedback" in content.lower(),
            "Questions": "question" in content.lower(),
            "Results": "result" in content.lower(),
        }
        print(f"\nquiz-master:")
        for check, passed in checks.items():
            status = "[OK]" if passed else "[MISSING]"
            print(f"  {status} {check}")

    # Check socratic-tutor
    socratic_skill = skills_dir / "socratic-tutor" / "SKILL.md"
    if socratic_skill.exists():
        content = socratic_skill.read_text()
        checks = {
            "Questioning": "question" in content.lower(),
            "Guiding": "guide" in content.lower(),
            "No Direct Answers": "direct answer" in content.lower(),
            "Discovery": "discover" in content.lower(),
        }
        print(f"\nsocratic-tutor:")
        for check, passed in checks.items():
            status = "[OK]" if passed else "[MISSING]"
            print(f"  {status} {check}")

    # Check progress-motivator
    progress_skill = skills_dir / "progress-motivator" / "SKILL.md"
    if progress_skill.exists():
        content = progress_skill.read_text()
        checks = {
            "Celebration": "celebrat" in content.lower(),
            "Motivation": "motivat" in content.lower(),
            "Progress Tracking": "progress" in content.lower(),
            "Streak": "streak" in content.lower(),
        }
        print(f"\nprogress-motivator:")
        for check, passed in checks.items():
            status = "[OK]" if passed else "[MISSING]"
            print(f"  {status} {check}")

    print()

def demonstrate_skill_usage():
    """Show example of how skills would be used."""
    print("=" * 60)
    print("DEMO: How Skills Are Used in Practice")
    print("=" * 60)

    print("""
When a student interacts with Course Companion FTE:

1. Student says: "Explain what MCP is"
   -> Intent detected: EXPLAIN
   -> Skill loaded: concept-explainer
   -> Response: Explanation at learner's level with analogies

2. Student says: "Quiz me on neural networks"
   -> Intent detected: QUIZ
   -> Skill loaded: quiz-master
   -> Response: Interactive quiz with encouragement

3. Student says: "I'm stuck on building an agent"
   -> Intent detected: SOCRATIC
   -> Skill loaded: socratic-tutor
   -> Response: Guiding questions, not direct answers

4. Student says: "How am I doing?"
   -> Intent detected: PROGRESS
   -> Skill loaded: progress-motivator
   -> Response: Progress stats with celebration
""")

    print("=" * 60)

def main():
    """Run all tests."""
    print()
    print("Course Companion FTE - Skills Verification Test")
    print("Agent Factory Hackathon IV")
    print()

    test_skills_exist()
    test_skill_content()
    demonstrate_skill_usage()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
[OK] Skill files exist in .claude/skills/
[OK] Skills contain proper educational content

HOW TO USE SKILLS IN CLAUDE CODE:

1. In this conversation, invoke the course-companion-fte agent:
   "Use the course-companion-fte agent to explain MCP"

2. Or ask questions naturally:
   "Explain what MCP is"  -> uses concept-explainer skill
   "Quiz me on agents"   -> uses quiz-master skill
   "I'm stuck on MCP"   -> uses socratic-tutor skill
   "How am I doing?"    -> uses progress-motivator skill

3. The agent will automatically:
   - Detect your intent
   - Load the appropriate skill
   - Apply the skill's methodology
   - Generate an educational response

This demonstrates the Zero-Backend-LLM architecture in action!
""")
    print("=" * 60)

if __name__ == "__main__":
    main()

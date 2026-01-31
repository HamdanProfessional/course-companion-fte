"""
Skill Loader for Course Companion FTE ChatGPT App.
Dynamically loads educational skills based on detected intent.
Zero-LLM compliance: Skills are loaded from .claude/skills/ and contain procedural knowledge only.
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path

from intent_detector import Intent, IntentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillLoadError(Exception):
    """Base exception for skill loading errors."""
    pass


class SkillNotFoundError(SkillLoadError):
    """Requested skill not found."""
    pass


class SkillLoader:
    """
    Dynamic skill loader for educational skills.
    Loads skill definitions from .claude/skills/ directory.
    """

    # Skill directory relative to project root
    SKILLS_DIR = Path(".claude/skills")

    # Skill metadata mapping
    SKILL_METADATA = {
        "concept-explainer": {
            "name": "Concept Explainer",
            "description": "Explains concepts at learner's level using analogies and examples",
            "file": "concept-explainer/SKILL.md",
        },
        "quiz-master": {
            "name": "Quiz Master",
            "description": "Conducts quizzes with encouragement and immediate feedback",
            "file": "quiz-master/SKILL.md",
        },
        "socratic-tutor": {
            "name": "Socratic Tutor",
            "description": "Guides learning through questioning rather than direct answers",
            "file": "socratic-tutor/SKILL.md",
        },
        "progress-motivator": {
            "name": "Progress Motivator",
            "description": "Tracks progress, celebrates achievements, maintains motivation",
            "file": "progress-motivator/SKILL.md",
        },
    }

    # Intent to skill mapping (consistent with intent detector)
    INTENT_TO_SKILL = {
        IntentType.EXPLAIN: "concept-explainer",
        IntentType.QUIZ: "quiz-master",
        IntentType.SOCRATIC: "socratic-tutor",
        IntentType.PROGRESS: "progress-motivator",
        IntentType.GENERAL: "general-tutoring",  # Fallback
    }

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        Initialize skill loader.

        Args:
            skills_dir: Custom skills directory (defaults to .claude/skills/)
        """
        self.skills_dir = Path(skills_dir) if skills_dir else self.SKILLS_DIR
        self._skill_cache: Dict[str, str] = {}

    def get_skill_path(self, skill_name: str) -> Path:
        """
        Get the file path for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Path to skill file

        Raises:
            SkillNotFoundError: If skill file doesn't exist
        """
        if skill_name not in self.SKILL_METADATA:
            raise SkillNotFoundError(f"Unknown skill: {skill_name}")

        skill_file = self.SKILLS_DIR / self.SKILL_METADATA[skill_name]["file"]

        if not skill_file.exists():
            raise SkillNotFoundError(
                f"Skill file not found: {skill_file}\n"
                f"Ensure skills are checked out from git repository"
            )

        return skill_file

    def load_skill_content(self, skill_name: str) -> str:
        """
        Load skill content from file.

        Args:
            skill_name: Name of the skill

        Returns:
            Skill content as string
        """
        skill_path = self.get_skill_path(skill_name)

        logger.info(f"Loading skill: {skill_name} from {skill_path}")

        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Cache the content
            self._skill_cache[skill_name] = content

            return content
        except IOError as e:
            raise SkillLoadError(f"Failed to load skill {skill_name}: {str(e)}")

    def get_skill_for_intent(self, intent: Intent) -> str:
        """
        Get the appropriate skill for a detected intent.

        Args:
            intent: Detected intent object

        Returns:
            Skill name to load
        """
        return self.INTENT_TO_SKILL.get(intent.type, "general-tutoring")

    def load_skill_for_intent(self, intent: Intent) -> str:
        """
        Load skill content for a detected intent.

        Args:
            intent: Detected intent object

        Returns:
            Skill content
        """
        skill_name = self.get_skill_for_intent(intent)
        return self.load_skill_content(skill_name)

    def get_skill_info(self, skill_name: str) -> Dict[str, str]:
        """
        Get metadata about a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Dictionary with skill metadata
        """
        if skill_name not in self.SKILL_METADATA:
            raise SkillNotFoundError(f"Unknown skill: {skill_name}")

        return self.SKILL_METADATA[skill_name]

    def list_available_skills(self) -> Dict[str, Dict[str, str]]:
        """
        List all available skills with metadata.

        Returns:
            Dictionary mapping skill names to metadata
        """
        return self.SKILL_METADATA.copy()

    def is_skill_available(self, skill_name: str) -> bool:
        """
        Check if a skill is available (file exists).

        Args:
            skill_name: Name of the skill

        Returns:
            True if skill file exists
        """
        if skill_name not in self.SKILL_METADATA:
            return False

        skill_file = self.SKILLS_DIR / self.SKILL_METADATA[skill_name]["file"]
        return skill_file.exists()

    def preload_common_skills(self) -> Dict[str, str]:
        """
        Preload commonly used skills into cache.

        Returns:
            Dictionary of loaded skill contents

        Note:
            This is useful for reducing latency during app initialization.
        """
        logger.info("Preloading common skills...")

        common_skills = ["concept-explainer", "quiz-master", "progress-motivator"]
        loaded = {}

        for skill_name in common_skills:
            try:
                if self.is_skill_available(skill_name):
                    loaded[skill_name] = self.load_skill_content(skill_name)
                    logger.info(f"  ✓ Preloaded: {skill_name}")
            except SkillLoadError as e:
                logger.warning(f"  ✗ Failed to preload {skill_name}: {str(e)}")

        return loaded

    def clear_cache(self):
        """Clear the skill content cache."""
        self._skill_cache.clear()
        logger.info("Skill cache cleared")


# ============================================================================
# Global skill loader instance
# ============================================================================

_global_skill_loader: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """Get global skill loader instance."""
    global _global_skill_loader
    if _global_skill_loader is None:
        _global_skill_loader = SkillLoader()
    return _global_skill_loader


# ============================================================================
# Helper functions for app integration
# ============================================================================

def load_skill_for_message(message: str, intent_detector) -> tuple[str, str]:
    """
    Convenience function: Detect intent and load appropriate skill.

    Args:
        message: User's message
        intent_detector: IntentDetector instance

    Returns:
        Tuple of (skill_name, skill_content)

    Raises:
        SkillLoadError: If skill loading fails
    """
    # Detect intent
    intent = intent_detector.detect(message)

    # Load skill
    skill_loader = get_skill_loader()
    skill_content = skill_loader.load_skill_for_intent(intent)

    return intent.skill, skill_content


def get_all_skills_info() -> Dict[str, Dict[str, str]]:
    """
    Get information about all available skills.

    Returns:
        Dictionary mapping skill names to metadata
    """
    skill_loader = get_skill_loader()
    return skill_loader.list_available_skills()


# ============================================================================
# Example usage and testing
# ============================================================================

if __name__ == "__main__":
    loader = SkillLoader()

    print("Available Skills:")
    print("=" * 60)

    skills = loader.list_available_skills()
    for skill_name, metadata in skills.items():
        print(f"\n{skill_name}:")
        print(f"  Name: {metadata['name']}")
        print(f"  Description: {metadata['description']}")
        print(f"  Available: {loader.is_skill_available(skill_name)}")

        if loader.is_skill_available(skill_name):
            content = loader.load_skill_content(skill_name)
            print(f"  Content length: {len(content)} characters")

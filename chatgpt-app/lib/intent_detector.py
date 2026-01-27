"""
Intent Detection for Course Companion FTE ChatGPT App.
Zero-LLM compliance: Keyword-based pattern matching only, no LLM usage.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Intent types for routing to skills."""
    EXPLAIN = "explain"          # concept-explainer skill
    QUIZ = "quiz"               # quiz-master skill
    SOCRATIC = "socratic"       # socratic-tutor skill
    PROGRESS = "progress"       # progress-motivator skill
    GENERAL = "general"         # Default tutoring mode


@dataclass
class Intent:
    """Intent detection result."""
    type: IntentType
    confidence: float
    skill: str
    keywords: List[str]


class IntentDetector:
    """
    Detect student intent from natural language messages.
    Zero-LLM: Uses keyword matching, no LLM-based classification.
    """

    # Intent keyword patterns (priority order)
    INTENT_PATTERNS = {
        IntentType.QUIZ: [
            "quiz",
            "test me",
            "test",
            "practice",
            "check my knowledge",
            "quiz me",
            "examine",
            "assess",
        ],
        IntentType.EXPLAIN: [
            "explain",
            "what is",
            "what are",
            "how does",
            "how do",
            "describe",
            "tell me about",
            "help me understand",
            "clarify",
            "define",
        ],
        IntentType.SOCRATIC: [
            "stuck",
            "help me think",
            "give me a hint",
            "i'm lost",
            "guide me",
            "don't tell me",
            "walk me through",
            "hint",
        ],
        IntentType.PROGRESS: [
            "progress",
            "streak",
            "how am i doing",
            "my stats",
            "my progress",
            "where am i",
            "what have i completed",
            "my score",
            "how far",
        ],
    }

    # Skill mapping
    INTENT_TO_SKILL = {
        IntentType.EXPLAIN: "concept-explainer",
        IntentType.QUIZ: "quiz-master",
        IntentType.SOCRATIC: "socratic-tutor",
        IntentType.PROGRESS: "progress-motivator",
        IntentType.GENERAL: "general-tutoring",
    }

    # Priority order (higher = more important)
    INTENT_PRIORITY = {
        IntentType.QUIZ: 100,       # Highest - explicit testing request
        IntentType.EXPLAIN: 80,     # High - core learning
        IntentType.SOCRATIC: 60,    # Medium - targeted help
        IntentType.PROGRESS: 40,    # Medium - tracking
        IntentType.GENERAL: 20,     # Lowest - fallback
    }

    def detect(self, message: str) -> Intent:
        """
        Detect intent from student message.
        Zero-LLM: Keyword-based matching with confidence scoring.

        Args:
            message: Student's natural language message

        Returns:
            Detected intent with confidence score
        """
        if not message:
            return Intent(
                type=IntentType.GENERAL,
                confidence=0.5,
                skill="general-tutoring",
                keywords=[],
            )

        message_lower = message.lower().strip()

        # Check for keyword matches for each intent
        detected_intents: List[Intent] = []

        for intent_type, keywords in self.INTENT_PATTERNS.items():
            matched_keywords = [
                kw for kw in keywords
                if kw.lower() in message_lower
            ]

            if matched_keywords:
                # Calculate confidence based on number of matches
                confidence = min(0.95, 0.6 + (len(matched_keywords) * 0.15))

                detected_intents.append(Intent(
                    type=intent_type,
                    confidence=confidence,
                    skill=self.INTENT_TO_SKILL[intent_type],
                    keywords=matched_keywords,
                ))

        # Resolve conflicts using priority order
        if len(detected_intents) == 0:
            # No intent detected - default to general tutoring
            return Intent(
                type=IntentType.GENERAL,
                confidence=0.5,
                skill="general-tutoring",
                keywords=[],
            )
        elif len(detected_intents) == 1:
            # Single intent detected
            return detected_intents[0]
        else:
            # Multiple intents detected - use priority
            detected_intents.sort(
                key=lambda i: self.INTENT_PRIORITY.get(i.type, 0),
                reverse=True
            )
            return detected_intents[0]

    def detect_with_confidence(self, message: str) -> Dict[str, any]:
        """
        Detect intent and return detailed information.
        Useful for debugging and logging.

        Args:
            message: Student's natural language message

        Returns:
            Dict with intent, confidence, skill, and all matches
        """
        if not message:
            return {
                "intent": IntentType.GENERAL,
                "confidence": 0.5,
                "skill": "general-tutoring",
                "all_matches": [],
            }

        message_lower = message.lower().strip()
        all_matches = []

        for intent_type, keywords in self.INTENT_PATTERNS.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    all_matches.append({
                        "intent": intent_type.value,
                        "keyword": keyword,
                        "skill": self.INTENT_TO_SKILL[intent_type],
                    })

        intent = self.detect(message)

        return {
            "intent": intent.type.value,
            "confidence": intent.confidence,
            "skill": intent.skill,
            "matched_keywords": intent.keywords,
            "all_matches": all_matches,
        }

    def get_skill_for_intent(self, message: str) -> str:
        """
        Get the appropriate skill name for a message.
        Convenience method for skill loading.

        Args:
            message: Student's natural language message

        Returns:
            Skill name to load
        """
        intent = self.detect(message)
        return intent.skill


# ============================================================================
# Global detector instance
# ============================================================================

_global_detector: Optional[IntentDetector] = None


def get_intent_detector() -> IntentDetector:
    """Get global intent detector instance."""
    global _global_detector
    if _global_detector is None:
        _global_detector = IntentDetector()
    return _global_detector


# ============================================================================
# Example usage and testing
# ============================================================================

if __name__ == "__main__":
    detector = IntentDetector()

    # Test cases
    test_messages = [
        "Explain what MCP is",
        "Quiz me on neural networks",
        "I'm stuck on this problem",
        "How am I doing with my progress?",
        "What is the meaning of life?",  # Ambiguous
        "",  # Empty
    ]

    print("Intent Detection Test Results:")
    print("=" * 60)

    for msg in test_messages:
        result = detector.detect_with_confidence(msg)
        print(f"\nMessage: '{msg}'")
        print(f"  Intent: {result['intent']}")
        print(f"  Skill: {result['skill']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Keywords: {result['matched_keywords']}")

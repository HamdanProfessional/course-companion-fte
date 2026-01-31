"""
Course Companion FTE - ChatGPT App
Main entry point for the conversational educational interface.

Zero-Backend-LLM Architecture:
- Student → ChatGPT → Course Companion FTE Agent → Backend API (Deterministic)
- All AI intelligence happens in ChatGPT using skills
- Backend serves content verbatim only
"""

import os
import sys
import logging
from typing import Optional

# Add lib directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from intent_detector import IntentDetector, IntentType
from skill_loader import SkillLoader, SkillLoadError
from backend_client import (
    BackendClient,
    BackendClientError,
    BackendConnectionError,
    BackendAccessDeniedError,
    BackendNotFoundError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# App Configuration
# ============================================================================

class AppConfig:
    """Application configuration from environment variables."""

    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "00000000-0000-0000-0000-000000000001")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ============================================================================
# Course Companion FTE App
# ============================================================================

class CourseCompanionFTEApp:
    """
    Main application class for Course Companion FTE ChatGPT App.

    Handles:
    - Intent detection from user messages
    - Skill loading and routing
    - Backend API integration
    - Error handling and graceful degradation
    """

    def __init__(self):
        """Initialize the application."""
        self.intent_detector = IntentDetector()
        self.skill_loader = SkillLoader()
        self.backend_client: Optional[BackendClient] = None

    async def initialize(self):
        """Initialize async resources (backend client)."""
        logger.info("Initializing Course Companion FTE App...")

        # Initialize backend client
        self.backend_client = BackendClient()
        logger.info(f"Backend URL: {AppConfig.BACKEND_URL}")

        # Verify backend connectivity
        try:
            await self.backend_client.list_chapters()
            logger.info("✓ Backend connection verified")
        except BackendConnectionError as e:
            logger.warning(f"⚠ Backend connection failed: {str(e)}")
            logger.warning("App will run in degraded mode with cached/local responses")

        # Preload common skills
        try:
            self.skill_loader.preload_common_skills()
            logger.info("✓ Common skills preloaded")
        except SkillLoadError as e:
            logger.warning(f"⚠ Skill preloading failed: {str(e)}")

    async def shutdown(self):
        """Cleanup resources."""
        if self.backend_client:
            await self.backend_client.close()
        self.skill_loader.clear_cache()

    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        context: Optional[dict] = None
    ) -> str:
        """
        Process a user message and generate a response.

        This is the main entry point for ChatGPT to interact with the app.

        Args:
            message: User's message
            user_id: User identifier (defaults to DEFAULT_USER_ID)
            context: Conversation context (optional)

        Returns:
            Response message to user
        """
        if not message or not message.strip():
            return "Hello! I'm your Course Companion FTE. Ask me to explain concepts, take quizzes, or check your progress!"

        user_id = user_id or AppConfig.DEFAULT_USER_ID
        context = context or {}

        logger.info(f"Processing message from user {user_id}: '{message[:50]}...'")

        try:
            # Step 1: Detect intent
            intent = self.intent_detector.detect(message)
            logger.info(f"Detected intent: {intent.type.value} (confidence: {intent.confidence:.2f})")

            # Step 2: Route to appropriate handler
            response = await self._route_by_intent(intent, message, user_id, context)

            return response

        except BackendAccessDeniedError as e:
            # Handle access denied (premium content)
            return self._handle_access_denied(str(e), user_id)

        except BackendConnectionError as e:
            # Handle backend connection issues
            return self._handle_backend_unavailable(str(e))

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return self._handle_unexpected_error(str(e))

    async def _route_by_intent(
        self,
        intent,
        message: str,
        user_id: str,
        context: dict
    ) -> str:
        """
        Route message to appropriate handler based on intent.

        Args:
            intent: Detected intent
            message: User's message
            user_id: User identifier
            context: Conversation context

        Returns:
            Response message
        """
        intent_type = intent.type

        # Route to appropriate handler
        if intent_type == IntentType.QUIZ:
            return await self._handle_quiz_intent(message, user_id)

        elif intent_type == IntentType.EXPLAIN:
            return await self._handle_explain_intent(message, user_id)

        elif intent_type == IntentType.PROGRESS:
            return await self._handle_progress_intent(message, user_id)

        elif intent_type == IntentType.SOCRATIC:
            return await self._handle_socratic_intent(message, user_id)

        else:  # GENERAL
            return await self._handle_general_intent(message, user_id)

    async def _handle_quiz_intent(self, message: str, user_id: str) -> str:
        """Handle quiz intent - load quiz-master skill and conduct quiz."""
        try:
            # Load quiz-master skill
            skill_content = self.skill_loader.load_skill_for_intent(
                self.intent_detector.detect(message)
            )

            # Get available quiz (try to get first quiz)
            quizzes = await self.backend_client.list_quizzes()

            if not quizzes:
                return "I don't have any quizzes available yet. Check back soon!"

            quiz = quizzes[0]  # Get first quiz
            quiz_detail = await self.backend_client.get_quiz(quiz['id'])

            # Load quiz-master skill content (would be injected into ChatGPT's context)
            # For now, return a conversational quiz introduction
            response = f"""📚 **{quiz_detail['title']}**

I'll test your knowledge with a few questions. Here's the first one:

**Question 1:** {quiz_detail['questions'][0]['question_text']}

Options:
{chr(10).join([f"{key}. {value}" for key, value in quiz_detail['questions'][0]['options'].items()])})

Type your answer (A, B, C, or D)!
"""
            return response

        except BackendConnectionError:
            return "I'm having trouble connecting to the quiz service right now. Try again in a moment!"

    async def _handle_explain_intent(self, message: str, user_id: str) -> str:
        """Handle explain intent - load concept-explainer skill."""
        try:
            # Try to extract what to explain
            # Simple keyword extraction for demo
            message_lower = message.lower()

            # Check if they're asking about a specific topic
            if "mcp" in message_lower:
                # Load concept-explainer skill
                skill_content = self.skill_loader.load_skill_content("concept-explainer")

                # Get relevant chapter content
                search_results = await self.backend_client.search_content("MCP", limit=3)

                if search_results['results']:
                    result = search_results['results'][0]
                    chapter = await self.backend_client.get_chapter(result['chapter_id'])

                    response = f"""**{chapter['title']}**

{chapter.get('content', 'Content not available.')}

Would you like me to explain this in a different way or dive deeper into any aspect?
"""
                else:
                    return """**Model Context Protocol (MCP)**

MCP is like a universal USB cable for AI applications. It lets AI models connect to external data sources and tools in a standardized way.

Think of it this way:
- Before MCP: Every AI app needed custom integrations
- With MCP: Universal compatibility between AI and data/tools

Key benefits:
- Standardized connections
- Tool extensibility
- Data source flexibility

Would you like me to explain how to build an MCP server?
"""
            else:
                # Generic explanation request
                return """I'd be happy to explain that concept! Let me search our course materials for the most relevant information.

Could you tell me which topic you'd like me to explain? For example:
- MCP (Model Context Protocol)
- Neural Networks
- AI Agents
- Or any other topic from the course?

This helps me provide the most accurate explanation from our course materials.
"""

        except BackendConnectionError:
            # Fallback to general explanation without backend
            return """I'm having trouble connecting to the course materials right now.

Based on my knowledge, I can still help! What topic would you like me to explain? (e.g., MCP, Neural Networks, AI Agents, etc.)

Once the connection is restored, I can provide explanations with specific course content.
"""

    async def _handle_progress_intent(self, message: str, user_id: str) -> str:
        """Handle progress intent - load progress-motivator skill."""
        try:
            # Get user progress
            progress = await self.backend_client.get_progress(user_id)
            streak = await self.backend_client.get_streak(user_id)

            completion_pct = progress.get('completion_percentage', 0)
            completed_chapters = progress.get('completed_chapters', [])
            current_streak = streak.get('current_streak', 0)

            response = f"""📊 **Your Learning Progress**

**Course Completion:** {completion_pct}%
**Chapters Completed:** {len(completed_chapters)}/10
**Current Streak:** {current_streak} days 🔥

"""

            if completion_pct >= 100:
                response += """🎉 **Congratulations!** You've completed the entire course!

You've mastered AI Agent Development. Ready for your certificate?
"""
            elif completion_pct >= 50:
                response += f"""You're more than halfway there! Keep up the great work! 💪
"""
            elif current_streak >= 3:
                response += f"""Amazing consistency! {current_streak} days in a row - you're on fire! ⚡
"""
            else:
                response += """You're making progress! Every chapter counts. Keep learning! 📚
"""

            return response

        except BackendConnectionError:
            return "I'm having trouble retrieving your progress right now. Try again in a moment!"

    async def _handle_socratic_intent(self, message: str, user_id: str) -> str:
        """Handle socratic intent - load socratic-tutor skill."""
        # Load socratic-tutor skill
        skill_content = self.skill_loader.load_skill_content("socratic-tutor")

        return """I'll help you work through this step by step!

Let me ask you a guiding question:

**What part of the problem is giving you the most trouble?**

For example:
- Are you unsure about the concept itself?
- Do you understand the concept but get stuck on implementation?
- Is there a specific error or issue you're facing?

Once I understand where you're stuck, I can guide you toward the solution! 🎯
"""

    async def _handle_general_intent(self, message: str, user_id: str) -> str:
        """Handle general/fallback intent - helpful tutoring."""
        return """I'm your Course Companion FTE - here to help you learn AI Agent Development!

Here's what I can help you with:

📚 **Explain Concepts**
- "Explain what MCP is"
- "How do neural networks work?"
- "What is an AI agent?"

🎯 **Take Quizzes**
- "Quiz me on MCP"
- "Test my knowledge"

📊 **Check Progress**
- "How am I doing?"
- "My progress"

💡 **Get Help**
- "I'm stuck on this problem"
- "Help me think through this"

What would you like to work on today?
"""

    def _handle_access_denied(self, error_msg: str, user_id: str) -> str:
        """Handle access denied (premium content)."""
        return f"""🔒 **Premium Content**

This content is part of our Premium tier. Your current tier doesn't include access to this content.

**Free Tier includes:**
- First 3 chapters of course content
- Basic quizzes for free chapters
- Progress tracking
- Streak gamification

**Premium Tier includes:**
- All 10 chapters (unlimited access)
- Advanced quizzes with detailed feedback
- Priority support
- Certificates of completion

Upgrade to Premium to unlock all content and features!

{error_msg}
"""

    def _handle_backend_unavailable(self, error_msg: str) -> str:
        """Handle backend connection errors."""
        return f"""⚠️ **Connection Issues**

I'm having trouble connecting to the course backend right now: {error_msg}

Let me help you with what I know, and we can try again in a moment.

What would you like to explore?
- Course concepts
- General questions about AI/ML
- Study tips and strategies

Or if you'd like, we can try the connection again!
"""

    def _handle_unexpected_error(self, error_msg: str) -> str:
        """Handle unexpected errors."""
        return f"""❌ **Something went wrong**

I encountered an unexpected error: {error_msg}

Let's try a different approach. What would you like to do?
- Ask me to explain a concept
- Take a quiz
- Check your progress
- Or try your request again

I'm here to help!
"""


# ============================================================================
# Global app instance
# ============================================================================

_app_instance: Optional[CourseCompanionFTEApp] = None


async def get_app() -> CourseCompanionFTEApp:
    """Get or initialize global app instance."""
    global _app_instance
    if _app_instance is None:
        _app_instance = CourseCompanionFTEApp()
        await _app_instance.initialize()
    return _app_instance


async def shutdown_app():
    """Shutdown global app instance."""
    global _app_instance
    if _app_instance:
        await _app_instance.shutdown()
        _app_instance = None


# ============================================================================
# Example usage and testing
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_app():
        """Test the Course Companion FTE app."""
        print("Course Companion FTE - ChatGPT App Test")
        print("=" * 60)

        app = CourseCompanionFTEApp()
        await app.initialize()

        # Test messages
        test_messages = [
            ("Explain MCP", "test-user-1"),
            ("Quiz me", "test-user-1"),
            ("How am I doing?", "test-user-1"),
            ("I'm stuck", "test-user-1"),
            ("Hello!", "test-user-1"),
        ]

        for msg, user_id in test_messages:
            print(f"\n📥 User: {msg}")
            response = await app.process_message(msg, user_id)
            print(f"📤 Assistant: {response[:200]}...")

        await app.shutdown()

    # Run test
    asyncio.run(test_app())

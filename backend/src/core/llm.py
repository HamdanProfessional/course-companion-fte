"""
LLM Client Abstraction for Phase 2 Hybrid Features.

Supports OpenAI and Anthropic with unified interface.
Only used when ENABLE_PHASE_2_LLM=true in environment.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

from src.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMTimeoutError(LLMClientError):
    """Exception raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMClientError):
    """Exception raised when LLM rate limit is exceeded."""
    pass


class LLMClient:
    """
    Unified LLM client supporting OpenAI and Anthropic.

    Usage:
        client = LLMClient()  # Auto-detects provider from settings
        response = await client.generate("Explain neural networks")
        analysis = await client.analyze(content, "summarize")
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider (openai/anthropic). Defaults to settings.llm_provider
            api_key: API key. Defaults to settings.{provider}_api_key
            model: Model name. Defaults to settings.{provider}_model
            temperature: Generation temperature. Defaults to settings.llm_temperature
            max_tokens: Max tokens. Defaults to settings.llm_max_tokens
            timeout: Request timeout. Defaults to settings.llm_timeout_seconds
        """
        self.provider = LLMProvider(provider or settings.llm_provider)
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_model()
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens
        self.timeout = timeout if timeout is not None else settings.llm_timeout_seconds

        # Validate API key
        if not self.api_key:
            raise LLMClientError(
                f"API key not found for {self.provider.value}. "
                f"Set {self.provider.value.upper()}_API_KEY environment variable."
            )

        # Lazy import of LLM libraries (only when needed)
        self._openai = None
        self._anthropic = None

        logger.info(
            f"LLM client initialized: provider={self.provider.value}, "
            f"model={self.model}"
        )

    def _get_api_key(self) -> str:
        """Get API key from settings based on provider."""
        if self.provider == LLMProvider.OPENAI:
            return settings.openai_api_key
        elif self.provider == LLMProvider.ANTHROPIC:
            return settings.anthropic_api_key
        else:
            raise LLMClientError(f"Unknown provider: {self.provider}")

    def _get_model(self) -> str:
        """Get model name from settings based on provider."""
        if self.provider == LLMProvider.OPENAI:
            return settings.openai_model
        elif self.provider == LLMProvider.ANTHROPIC:
            return settings.anthropic_model
        else:
            raise LLMClientError(f"Unknown provider: {self.provider}")

    def _get_openai_client(self):
        """Lazy load OpenAI client."""
        if self._openai is None:
            try:
                import openai
                self._openai = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise LLMClientError(
                    "OpenAI library not installed. "
                    "Install with: pip install openai"
                )
        return self._openai

    def _get_anthropic_client(self):
        """Lazy load Anthropic client."""
        if self._anthropic is None:
            try:
                import anthropic
                self._anthropic = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise LLMClientError(
                    "Anthropic library not installed. "
                    "Install with: pip install anthropic"
                )
        return self._anthropic

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        retry_count: int = 3
    ) -> str:
        """
        Generate completion from LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (for instruction/context)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Response format (e.g., {"type": "json_object"})
            retry_count: Number of retries on failure

        Returns:
            Generated text response

        Raises:
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit exceeded
            LLMClientError: For other errors
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        for attempt in range(retry_count):
            try:
                if self.provider == LLMProvider.OPENAI:
                    return await self._generate_openai(
                        prompt, system_prompt, temp, tokens, response_format
                    )
                elif self.provider == LLMProvider.ANTHROPIC:
                    return await self._generate_anthropic(
                        prompt, system_prompt, temp, tokens
                    )

            except asyncio.TimeoutError as e:
                logger.warning(f"LLM request timeout (attempt {attempt + 1}/{retry_count})")
                if attempt == retry_count - 1:
                    raise LLMTimeoutError(f"LLM request timed out after {retry_count} retries")

            except Exception as e:
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    logger.warning(f"LLM rate limit hit (attempt {attempt + 1}/{retry_count})")
                    if attempt == retry_count - 1:
                        raise LLMRateLimitError(f"LLM rate limit exceeded: {e}")
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"LLM request failed: {e}")
                    if attempt == retry_count - 1:
                        raise LLMClientError(f"LLM generation failed: {e}")

        raise LLMClientError("Failed to generate response after retries")

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, str]]
    ) -> str:
        """Generate using OpenAI API."""
        client = self._get_openai_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = await asyncio.wait_for(
            client.chat.completions.create(**kwargs),
            timeout=self.timeout
        )

        return response.choices[0].message.content

    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Anthropic API."""
        client = self._get_anthropic_client()

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = await asyncio.wait_for(
            client.messages.create(**kwargs),
            timeout=self.timeout
        )

        return response.content[0].text

    async def analyze(
        self,
        content: str,
        task: str,
        schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze content and return structured result.

        Args:
            content: Content to analyze
            task: Analysis task description
            schema: Expected output schema (for JSON mode)
            **kwargs: Additional arguments passed to generate()

        Returns:
            Structured analysis result (dict)

        Example:
            result = await client.analyze(
                "Neural networks are computing systems...",
                task="Extract key concepts",
                schema={"concepts": "list", "difficulty": "string"}
            )
        """
        system_prompt = "You are an AI assistant that analyzes educational content."
        prompt = f"""Task: {task}

Content:
{content}

Provide a structured analysis following the specified schema.
"""

        if schema:
            # Request JSON format
            response = await self.generate(
                prompt,
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                **kwargs
            )
        else:
            response = await self.generate(
                prompt,
                system_prompt=system_prompt,
                **kwargs
            )

        # Parse JSON response
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON response, returning as text")
            return {"result": response}

    async def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Generate completions for multiple prompts in parallel.

        Args:
            prompts: List of prompts
            system_prompt: Shared system prompt
            **kwargs: Additional arguments for generate()

        Returns:
            List of generated responses
        """
        tasks = [
            self.generate(prompt, system_prompt, **kwargs)
            for prompt in prompts
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)

    def is_enabled(self) -> bool:
        """Check if Phase 2 LLM features are enabled."""
        return settings.enable_phase_2_llm

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current LLM provider."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "enabled": self.is_enabled()
        }


# Singleton instance for convenience
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> Optional[LLMClient]:
    """
    Get or create LLM client singleton.

    Returns None if Phase 2 LLM features are disabled.
    """
    global _llm_client

    if not settings.enable_phase_2_llm:
        logger.debug("Phase 2 LLM features are disabled")
        return None

    if _llm_client is None:
        try:
            _llm_client = LLMClient()
            logger.info("LLM client initialized successfully")
        except LLMClientError as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return None

    return _llm_client

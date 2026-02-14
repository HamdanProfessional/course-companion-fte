"""
LLM Client Abstraction for Phase 2 Hybrid Features.

Supports OpenAI and Anthropic with unified interface.
Only used when ENABLE_PHASE_2_LLM=true in environment.
"""

import os
import asyncio
import logging
import re
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

from src.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Thinking Tag Stripping (for reasoning models like DeepSeek-R1, DAN, etc.)
# =============================================================================


def strip_thinking_tags(content: str) -> Tuple[str, Optional[str]]:
    """
    Strip thinking tags from model responses.

    Many reasoning models (DeepSeek-R1, DAN-Qwen, etc.) output their thinking
    process in <thinking>...</thinking> tags. This function extracts and removes
    them, returning both the thinking process (if any) and the final answer.

    Args:
        content: Raw model response that may contain <thinking> tags

    Returns:
        Tuple of (cleaned_content, thinking_content)
        - cleaned_content: Response with thinking tags removed
        - thinking_content: The extracted thinking process, or None if not found

    Examples:
        >>> strip_thinking_tags("<thinking>Let me think...</thinking>Answer is 42")
        ("Answer is 42", "Let me think...")
    """
    if not content:
        return content, None

    # Pattern to match <thinking>...</thinking> tags (multiline)
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    matches = re.findall(thinking_pattern, content, re.DOTALL | re.IGNORECASE)

    if matches:
        # Extract all thinking content
        thinking_content = "\n\n".join(matches).strip()

        # Remove all thinking tags from the response
        cleaned_content = re.sub(thinking_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        cleaned_content = cleaned_content.strip()

        logger.debug(f"Stripped {len(matches)} thinking tag(s) from response "
                     f"({len(content)} -> {len(cleaned_content)} chars)")

        return cleaned_content, thinking_content

    return content, None


def extract_thinking_to_extra(content: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Extract thinking content and return it as extra data for API responses.

    This is useful for frontend display of the model's reasoning process.

    Args:
        content: Raw model response

    Returns:
        Tuple of (cleaned_content, extra_data)
        - cleaned_content: Response with thinking tags removed
        - extra_data: Dict with thinking content, or None
    """
    cleaned, thinking = strip_thinking_tags(content)

    extra_data = None
    if thinking:
        extra_data = {
            "thinking": thinking,
            "has_thinking": True
        }

    return cleaned, extra_data


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GLM = "glm"  # Zhipu AI GLM 4.7
    DEEPSEEK = "deepseek"  # DeepSeek AI


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
        timeout: Optional[int] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider (openai/anthropic/glm/deepseek). Defaults to settings.llm_provider
            api_key: API key. Defaults to settings.{provider}_api_key
            model: Model name. Defaults to settings.{provider}_model
            temperature: Generation temperature. Defaults to settings.llm_temperature
            max_tokens: Max tokens. Defaults to settings.llm_max_tokens
            timeout: Request timeout. Defaults to settings.llm_timeout_seconds
            base_url: Custom base URL for GLM/DeepSeek provider
        """
        self.provider = LLMProvider(provider or settings.llm_provider)
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_model()
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens
        self.timeout = timeout if timeout is not None else settings.llm_timeout_seconds
        self.base_url = base_url or self._get_base_url()  # For GLM custom endpoint

        # Validate API key
        if not self.api_key:
            raise LLMClientError(
                f"API key not found for {self.provider.value}. "
                f"Set {self.provider.value.upper()}_API_KEY environment variable."
            )

        # Lazy import of LLM libraries (only when needed)
        self._openai = None
        self._anthropic = None
        self._glm = None
        self._deepseek = None

        logger.info(
            f"LLM client initialized: provider={self.provider.value}, "
            f"model={self.model}, base_url={self.base_url or 'default'}"
        )

    def _get_api_key(self) -> str:
        """Get API key from settings based on provider."""
        if self.provider == LLMProvider.OPENAI:
            return settings.openai_api_key
        elif self.provider == LLMProvider.ANTHROPIC:
            return settings.anthropic_api_key
        elif self.provider == LLMProvider.GLM:
            return settings.glm_api_key
        elif self.provider == LLMProvider.DEEPSEEK:
            return settings.deepseek_api_key
        else:
            raise LLMClientError(f"Unknown provider: {self.provider}")

    def _get_model(self) -> str:
        """Get model name from settings based on provider."""
        if self.provider == LLMProvider.OPENAI:
            return settings.openai_model
        elif self.provider == LLMProvider.ANTHROPIC:
            return settings.anthropic_model
        elif self.provider == LLMProvider.GLM:
            return settings.glm_model
        elif self.provider == LLMProvider.DEEPSEEK:
            return settings.deepseek_model
        else:
            raise LLMClientError(f"Unknown provider: {self.provider}")

    def _get_base_url(self) -> Optional[str]:
        """Get base URL from settings based on provider."""
        if self.provider == LLMProvider.GLM:
            return settings.glm_base_url
        if self.provider == LLMProvider.DEEPSEEK:
            return settings.deepseek_base_url
        return None

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

    def _get_glm_client(self):
        """Lazy load GLM (Zhipu AI) client using OpenAI-compatible API."""
        if self._glm is None:
            try:
                import openai
                # Use OpenAI client with custom base URL for GLM
                self._glm = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise LLMClientError(
                    "OpenAI library not installed. "
                    "Install with: pip install openai"
                )
        return self._glm

    def _get_deepseek_client(self):
        """Lazy load DeepSeek client using OpenAI-compatible API."""
        if self._deepseek is None:
            try:
                import openai
                # Use OpenAI client with custom base URL for DeepSeek
                self._deepseek = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise LLMClientError(
                    "OpenAI library not installed. "
                    "Install with: pip install openai"
                )
        return self._deepseek

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
                elif self.provider == LLMProvider.GLM:
                    return await self._generate_glm(
                        prompt, system_prompt, temp, tokens, response_format
                    )
                elif self.provider == LLMProvider.DEEPSEEK:
                    return await self._generate_deepseek(
                        prompt, system_prompt, temp, tokens, response_format
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

        content = response.choices[0].message.content or ""
        # Strip thinking tags from reasoning models
        cleaned_content, _ = strip_thinking_tags(content)
        return cleaned_content

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

        content = response.content[0].text
        # Strip thinking tags from reasoning models
        cleaned_content, _ = strip_thinking_tags(content)
        return cleaned_content

    async def _generate_glm(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate using GLM (Zhipu AI) API via OpenAI-compatible endpoint.

        Note: GLM API doesn't support response_format parameter, so it's ignored.
        Also strips thinking tags from reasoning models (DAN, DeepSeek-R1, etc.).
        """
        client = self._get_glm_client()

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

        # GLM doesn't support response_format parameter, so we don't pass it
        # The prompt should instruct the model to respond in the desired format
        if response_format:
            logger.warning("GLM provider doesn't support response_format parameter, ignoring it")

        response = await asyncio.wait_for(
            client.chat.completions.create(**kwargs),
            timeout=self.timeout
        )

        content = response.choices[0].message.content or ""

        # Log the raw content for debugging
        logger.debug(f"GLM raw content (first 200 chars): {repr(content[:200])}")

        # Strip thinking tags from reasoning models (DAN-Qwen, DeepSeek-R1, etc.)
        cleaned_content, thinking = strip_thinking_tags(content)

        # Log if thinking was found (for debugging)
        if thinking:
            logger.info(f"GLM response contained thinking tags ({len(thinking)} chars stripped)")

        # Check if the response looks like an error
        if cleaned_content.startswith('\n') and '"answer"' in cleaned_content:
            logger.warning(f"GLM response appears malformed or truncated: {repr(cleaned_content[:200])}")

        return cleaned_content

    async def _generate_deepseek(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, str]]
    ) -> str:
        """Generate using DeepSeek API (OpenAI-compatible)."""
        client = self._get_deepseek_client()

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

        content = response.choices[0].message.content or ""

        # Strip thinking tags from reasoning models (DeepSeek-R1)
        cleaned_content, _ = strip_thinking_tags(content)

        return cleaned_content

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


def get_llm_client() -> Optional["LLMClient"]:
    """
    Get or create LLM client singleton.

    Returns None if Phase 2 LLM features are disabled.
    Returns LLM v2 client with multi-key rotation when LLM_V2=true.
    Returns LLM v1 client when LLM_V2=false or not set.
    """
    global _llm_client

    if not settings.enable_phase_2_llm:
        logger.debug("Phase 2 LLM features are disabled")
        return None

    if _llm_client is None:
        try:
            # Check if LLM v2 is enabled
            if settings.llm_v2:
                logger.info("Initializing LLM v2 client with multi-key rotation")
                from src.core import llm_v2
                _llm_client = llm_v2.LLMClient()
                logger.info("LLM v2 client initialized successfully with multi-key support")
            else:
                logger.info("Initializing LLM v1 client")
                _llm_client = LLMClient()
                logger.info("LLM v1 client initialized successfully")
        except LLMClientError as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error initializing LLM client: {e}")
            return None

    return _llm_client

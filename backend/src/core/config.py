"""
Application configuration using environment variables.
Phase 1: Zero-LLM compliance (default)
Phase 2: Hybrid LLM features (optional, feature-flagged)
"""

import os
from typing import List, Union, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application metadata
    app_name: str = Field(default="Course Companion FTE", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Database configuration (Neon PostgreSQL)
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost/course_companion",
        description="PostgreSQL connection string (asyncpg driver required)"
    )

    # Cloudflare R2 Storage configuration
    r2_account_id: str = Field(default="", description="Cloudflare R2 account ID")
    r2_access_key_id: str = Field(default="", description="R2 access key ID")
    r2_secret_access_key: str = Field(default="", description="R2 secret access key")
    r2_bucket_name: str = Field(default="course-content", description="R2 bucket name")
    r2_endpoint_url: str = Field(
        default="https://your-account-id.r2.cloudflarestorage.com",
        description="R2 endpoint URL"
    )

    # JWT Security configuration
    jwt_secret: str = Field(
        default="change-this-secret-in-production",
        description="JWT signing secret"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=30, description="JWT token expiration in minutes")

    # CORS configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://92.113.147.250:3225",
            "http://92.113.147.250:3000",
            "http://92.113.147.250:3505",
        ],
        description="Allowed CORS origins"
    )

    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")

    # Phase 2: LLM Configuration (Optional)
    # Feature flag to enable Phase 2 hybrid LLM features
    enable_phase_2_llm: bool = Field(
        default=False,
        description="Enable Phase 2 LLM features (default: False for Zero-LLM compliance)"
    )

    # LLM Provider Selection
    llm_provider: str = Field(
        default="openai",
        description="LLM provider: 'openai', 'anthropic', or 'glm'"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key (required if llm_provider=openai)"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use (gpt-4o-mini recommended for cost efficiency)"
    )

    # Anthropic Configuration
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key (required if llm_provider=anthropic)"
    )
    anthropic_model: str = Field(
        default="claude-3-haiku-20240307",
        description="Anthropic model to use (claude-3-haiku recommended for cost efficiency)"
    )

    # GLM (Zhipu AI) Configuration
    glm_api_key: str = Field(
        default="",
        description="GLM API key (required if llm_provider=glm)"
    )
    glm_model: str = Field(
        default="glm-4.7",
        description="GLM model to use (glm-4.7 recommended, also supports glm-4.6, glm-4-plus)"
    )
    glm_base_url: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4",
        description="GLM API base URL"
    )

    # LLM Generation Parameters
    llm_temperature: float = Field(
        default=0.7,
        description="LLM temperature (0.0-1.0, lower = more deterministic)"
    )
    llm_max_tokens: int = Field(
        default=1000,
        description="Maximum tokens per LLM request"
    )
    llm_timeout_seconds: int = Field(
        default=30,
        description="Timeout for LLM API requests"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver: "
                "postgresql+asyncpg://user:password@host/database"
            )
        return v

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider choice."""
        v = v.lower()
        if v not in ["openai", "anthropic", "glm"]:
            raise ValueError("LLM provider must be 'openai', 'anthropic', or 'glm'")
        return v

    @field_validator("llm_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("LLM temperature must be between 0.0 and 1.0")
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret is not default in production."""
        # Check if using default insecure secret
        if v in ["change-this-secret-in-production", "change-this-secret", "secret"]:
            # Allow default only in debug mode
            if not os.getenv("DEBUG", "").lower() in ["true", "1", "yes"]:
                raise ValueError(
                    "Insecure JWT secret detected. Please set a strong JWT_SECRET "
                    "environment variable with at least 32 characters."
                )
        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters long")
        return v


# Global settings instance
settings = Settings()

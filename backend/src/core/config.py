"""
Application configuration using environment variables.
Zero-LLM compliance: No LLM API keys or endpoints.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


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
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")

    @validator("cors_origins", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("database_url")
    def validate_database_url(cls, v):
        """Ensure database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver: "
                "postgresql+asyncpg://user:password@host/database"
            )
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

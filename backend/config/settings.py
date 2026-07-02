"""
Application configuration.

Every other module reads config through the `get_settings()` dependency —
never through `os.environ` directly and never with hardcoded values.
This keeps secrets and environment-specific values in exactly one place.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, validated application settings loaded from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "AI Learning OS"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = Field(
        ...,
        description="Async SQLAlchemy connection string, e.g. postgresql+asyncpg://user:pass@host:5432/db",
    )

    # --- Redis / Celery ---
    REDIS_URL: str = Field(..., description="Redis connection string used as Celery broker/backend")

    # --- JWT ---
    JWT_SECRET_KEY: str = Field(..., description="Secret used to sign JWTs. Must never be committed.")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS as a parsed list, supports comma-separated values in .env."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.

    Use as a FastAPI dependency: `settings: Settings = Depends(get_settings)`.
    lru_cache ensures the .env file is parsed once per process, not per request.
    """
    return Settings()
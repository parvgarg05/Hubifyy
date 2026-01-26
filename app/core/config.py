"""
Application configuration using Pydantic Settings (Pydantic v2).
Loads environment variables from .env safely using SettingsConfigDict.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Required environment variables
    DATABASE_URL: str
    SECRET_KEY: str

    # Defaults
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Optional app metadata (not required by the task but useful)
    APP_NAME: str = "Hubify - College Clubs & Community Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Read from .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Backward-compatible properties for existing code references
    @property
    def database_url(self) -> str:  # pragma: no cover
        return self.DATABASE_URL

    @property
    def secret_key(self) -> str:  # pragma: no cover
        return self.SECRET_KEY

    @property
    def algorithm(self) -> str:  # pragma: no cover
        return self.ALGORITHM

    @property
    def access_token_expire_minutes(self) -> int:  # pragma: no cover
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def app_name(self) -> str:  # pragma: no cover
        return self.APP_NAME

    @property
    def app_version(self) -> str:  # pragma: no cover
        return self.APP_VERSION

    @property
    def debug(self) -> bool:  # pragma: no cover
        return self.DEBUG


# Global settings instance
settings = Settings()

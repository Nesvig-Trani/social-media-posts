from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Social Media API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # CORS settings
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]

    # YouTube API
    YOUTUBE_API_KEY: Optional[str] = None

    # Twitter/X API
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None

    # General settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

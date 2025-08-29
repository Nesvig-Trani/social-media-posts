from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # YouTube API
    YOUTUBE_API_KEY: Optional[str] = None
    
    # Twitter/X API
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None

    # Instagram API (add to your Settings class)
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    
    # General settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"

settings = Settings()
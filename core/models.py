from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"  # For future use
    FACEBOOK = "facebook"  # For future use
    TIKTOK = "tiktok"  # For future use


class SocialMediaPost(BaseModel):
    """Standard model for social media posts across all platforms"""

    id: str
    platform: Platform
    author: str
    author_id: str
    content: str
    created_at: datetime
    url: str
    media_urls: List[str] = Field(default_factory=list)
    engagement: Dict[str, int] = Field(default_factory=dict)
    raw_data: Optional[Dict[str, Any]] = Field(default=None, exclude=True)


class ChannelInfo(BaseModel):
    """Standard model for channel/account information"""

    id: str
    name: str
    username: Optional[str] = None
    platform: Platform
    url: str
    follower_count: Optional[int] = None

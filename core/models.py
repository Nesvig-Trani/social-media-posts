from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class SocialMediaPost(BaseModel):
    """Standard model for social media posts across all platforms"""
    id: str
    platform: str
    author: str
    author_id: str
    content: str
    created_at: datetime
    url: str
    media_urls: list[str] = []
    engagement: Dict[str, int] = {}  # likes, shares, comments, etc.
    raw_data: Optional[Dict[str, Any]] = None

class ChannelInfo(BaseModel):
    """Standard model for channel/account information"""
    id: str
    name: str
    username: Optional[str] = None
    platform: str
    url: str
    follower_count: Optional[int] = None
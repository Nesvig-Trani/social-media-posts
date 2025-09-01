from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

from core.models import ChannelInfo, Platform, SocialMediaPost


# API Response Models
class PostResponse(BaseModel):
    """Response model for post endpoints"""

    success: bool = True
    data: Optional[SocialMediaPost] = None
    message: str = "Post retrieved successfully"


class ChannelResponse(BaseModel):
    """Response model for channel endpoints"""

    success: bool = True
    data: Optional[ChannelInfo] = None
    message: str = "Channel information retrieved successfully"


class MultiPostResponse(BaseModel):
    """Response model for multiple posts"""

    success: bool = True
    data: Dict[str, Optional[SocialMediaPost]] = Field(default_factory=dict)
    message: str = "Posts retrieved successfully"
    errors: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime
    version: str
    available_platforms: List[str]


# Request Models
class MultiChannelRequest(BaseModel):
    """Request model for multiple channels"""

    channels: Dict[Platform, str] = Field()

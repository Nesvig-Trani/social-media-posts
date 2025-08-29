from abc import ABC, abstractmethod
from typing import Optional
from .models import SocialMediaPost, ChannelInfo

class BaseSocialMediaService(ABC):
    """Abstract base class for social media services"""
    
    def __init__(self):
        self.platform_name = self._get_platform_name()
    
    @abstractmethod
    def _get_platform_name(self) -> str:
        """Return the platform name"""
        pass
    
    @abstractmethod
    def get_latest_post(self, channel_identifier: str) -> Optional[SocialMediaPost]:
        """Get the latest post from a channel/account"""
        pass
    
    @abstractmethod
    def get_channel_info(self, channel_identifier: str) -> ChannelInfo:
        """Get information about the channel/account"""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        pass
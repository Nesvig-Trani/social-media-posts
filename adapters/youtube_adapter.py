from services.youtube_service import YouTubeService
from core.base import BaseSocialMediaService


class YouTubeAdapter:
    """Adapter for YouTube service"""

    def __init__(self):
        self._service = YouTubeService()

    @property
    def service(self) -> BaseSocialMediaService:
        return self._service

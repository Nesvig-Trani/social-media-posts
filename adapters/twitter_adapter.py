from services.twitter_service import TwitterService
from core.base import BaseSocialMediaService


class TwitterAdapter:
    """Adapter for Twitter service"""

    def __init__(self):
        self._service = TwitterService()

    @property
    def service(self) -> BaseSocialMediaService:
        return self._service

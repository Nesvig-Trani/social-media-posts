import asyncio
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor

from adapters.twitter_adapter import TwitterAdapter
from adapters.youtube_adapter import YouTubeAdapter
from core.base import BaseSocialMediaService
from core.exceptions import SocialMediaFetcherError
from core.models import Platform, SocialMediaPost


class SocialMediaFetcher:
    """Async-compatible main class that orchestrates fetching posts from different platforms"""

    def __init__(self):
        self._services: Dict[str, BaseSocialMediaService] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._register_services()

    def _register_services(self):
        """Register available social media services"""
        try:
            youtube_adapter = YouTubeAdapter()
            self._services["youtube"] = youtube_adapter.service
        except Exception as e:
            print(f"Warning: YouTube service not available: {e}")

        try:
            twitter_adapter = TwitterAdapter()
            self._services["twitter"] = twitter_adapter.service
        except Exception as e:
            print(f"Warning: Twitter service not available: {e}")

    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        return list(self._services.keys())

    async def get_latest_post(
        self, platform: Platform, channel_identifier: str
    ) -> Optional[SocialMediaPost]:
        """Get the latest post from specified platform and channel (async)"""
        platform_str = platform.value

        if platform_str not in self._services:
            available = self.get_available_platforms()
            raise ValueError(
                f"Platform '{platform_str}' not supported. "
                f"Available platforms: {available}"
            )

        try:
            service = self._services[platform_str]
            # Run the synchronous service method in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._executor, service.get_latest_post, channel_identifier
            )
        except SocialMediaFetcherError:
            raise
        except Exception as e:
            raise SocialMediaFetcherError(f"Unexpected error: {e}")

    async def get_channel_info(self, platform: Platform, channel_identifier: str):
        """Get channel information (async)"""
        platform_str = platform.value

        if platform_str not in self._services:
            available = self.get_available_platforms()
            raise ValueError(
                f"Platform '{platform_str}' not supported. "
                f"Available platforms: {available}"
            )

        try:
            service = self._services[platform_str]
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._executor, service.get_channel_info, channel_identifier
            )
        except SocialMediaFetcherError:
            raise
        except Exception as e:
            raise SocialMediaFetcherError(f"Unexpected error: {e}")

    async def get_latest_posts_from_multiple_channels(
        self, channels: Dict[Platform, str]
    ) -> Dict[str, Optional[SocialMediaPost]]:
        """Get latest posts from multiple channels concurrently"""
        tasks = []
        platform_names = []

        for platform, channel_identifier in channels.items():
            task = self.get_latest_post(platform, channel_identifier)
            tasks.append(task)
            platform_names.append(platform.value)

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        final_results = {}
        for i, result in enumerate(results):
            platform_name = platform_names[i]
            if isinstance(result, Exception):
                print(f"Error fetching from {platform_name}: {result}")
                final_results[platform_name] = None
            else:
                final_results[platform_name] = result

        return final_results

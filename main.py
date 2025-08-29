from typing import Dict, Optional
from core.base import BaseSocialMediaService
from core.models import SocialMediaPost
from core.exceptions import SocialMediaFetcherError
from adapters.youtube_adapter import YouTubeAdapter
from adapters.twitter_adapter import TwitterAdapter


class SocialMediaFetcher:
    """Main class that orchestrates fetching posts from different platforms"""

    def __init__(self):
        self._services: Dict[str, BaseSocialMediaService] = {}
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

    def get_available_platforms(self) -> list[str]:
        """Get list of available platforms"""
        return list(self._services.keys())

    def get_latest_post(
        self, platform: str, channel_identifier: str
    ) -> Optional[SocialMediaPost]:
        """Get the latest post from specified platform and channel"""
        if platform not in self._services:
            raise ValueError(
                f"Platform '{platform}' not supported. "
                f"Available platforms: {self.get_available_platforms()}"
            )

        try:
            service = self._services[platform]
            return service.get_latest_post(channel_identifier)
        except SocialMediaFetcherError:
            raise
        except Exception as e:
            raise SocialMediaFetcherError(f"Unexpected error: {e}")

    def get_latest_posts_from_multiple_channels(
        self, channels: Dict[str, str]
    ) -> Dict[str, Optional[SocialMediaPost]]:
        """Get latest posts from multiple channels

        Args:
            channels: Dict with platform as key and channel_identifier as value
                     e.g., {'youtube': 'channel_name', 'twitter': 'username'}

        Returns:
            Dict with platform as key and post as value
        """
        results = {}

        for platform, channel_identifier in channels.items():
            try:
                results[platform] = self.get_latest_post(platform, channel_identifier)
            except Exception as e:
                print(f"Error fetching from {platform}: {e}")
                results[platform] = None

        return results


# Example usage
if __name__ == "__main__":
    # Create fetcher instance
    fetcher = SocialMediaFetcher()

    # Check available platforms
    print(f"Available platforms: {fetcher.get_available_platforms()}")

    #Get latest post from YouTube
    try:
        youtube_post = fetcher.get_latest_post("youtube", "@mkbhd")
        if youtube_post:
            print(f"Latest YouTube post: {youtube_post.content}")
            print(f"Posted at: {youtube_post.created_at}")
            print(f"Views: {youtube_post.engagement.get('views', 'N/A')}")
            print(f"Video URL: {youtube_post.url}")
    except Exception as e:
        print(f"Error fetching YouTube post: {e}")

    # Get latest post from Twitter
    try:
        twitter_post = fetcher.get_latest_post("twitter", "josevalim")
        if twitter_post:
            print(f"Latest tweet: {twitter_post.content}")
            print(f"Posted at: {twitter_post.created_at}")
            print(f"Likes: {twitter_post.engagement.get('likes', 'N/A')}")
    except Exception as e:
        print(f"Error fetching Twitter post: {e}")

    # Get posts from multiple channels at once
    # channels = {"youtube": "@mkbhd", "twitter": "elonmusk"}

    # posts = fetcher.get_latest_posts_from_multiple_channels(channels)
    # for platform, post in posts.items():
    #     if post:
    #         print(f"{platform.capitalize()}: {post.content[:100]}...")
    #     else:
    #         print(f"{platform.capitalize()}: No post found or error occurred")

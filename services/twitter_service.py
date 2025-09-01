import tweepy
from typing import Optional
from core.base import BaseSocialMediaService
from core.models import Platform, SocialMediaPost, ChannelInfo
from core.exceptions import APIError, AuthenticationError, ChannelNotFoundError
from config.settings import settings


class TwitterService(BaseSocialMediaService):
    """Twitter/X service implementation"""

    def __init__(self):
        super().__init__()
        if not settings.TWITTER_BEARER_TOKEN:
            raise AuthenticationError("Twitter Bearer token not provided")

        try:
            self.client = tweepy.Client(
                bearer_token=settings.TWITTER_BEARER_TOKEN, wait_on_rate_limit=True
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Twitter client: {e}")

    def _get_platform_name(self) -> Platform:
        return Platform.TWITTER

    def validate_credentials(self) -> bool:
        """Validate Twitter API credentials"""
        try:
            self.client.get_me()
            return True
        except Exception:
            return False

    def get_channel_info(self, channel_identifier: str) -> ChannelInfo:
        """Get Twitter account information"""
        try:
            # Remove @ if present
            username = channel_identifier.lstrip("@")

            user = self.client.get_user(
                username=username, user_fields=["public_metrics", "url", "description"]
            )

            if not user.data:  # type: ignore
                raise ChannelNotFoundError(
                    f"Twitter account not found: {channel_identifier}"
                )

            user_data = user.data  # type: ignore

            return ChannelInfo(
                id=str(user_data.id),
                name=user_data.name,
                username=user_data.username,
                platform=self.platform_name,
                url=f"https://twitter.com/{user_data.username}",
                follower_count=user_data.public_metrics.get("followers_count", 0),
            )

        except tweepy.TweepyException as e:
            raise APIError(f"Twitter API error: {e}")

    def get_latest_post(self, channel_identifier: str) -> Optional[SocialMediaPost]:
        """Get the latest tweet from a Twitter account"""
        try:
            # Get user info first
            channel_info = self.get_channel_info(channel_identifier)

            # Get the latest tweet
            tweets = self.client.get_users_tweets(
                id=channel_info.id,
                max_results=5,
                tweet_fields=["created_at", "public_metrics", "attachments"],
                expansions=["attachments.media_keys"],
                media_fields=["url", "preview_image_url"],
            )

            if not tweets.data:  # type: ignore
                return None

            tweet = tweets.data[0]  # type: ignore
            media_urls = []

            return SocialMediaPost(
                id=str(tweet.id),
                platform=self.platform_name,
                author=channel_info.name,
                author_id=channel_info.id,
                content=tweet.text,
                created_at=tweet.created_at,
                url=f"https://twitter.com/{channel_info.username}/status/{tweet.id}",
                media_urls=media_urls,
                engagement={
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                    "quotes": tweet.public_metrics.get("quote_count", 0),
                },
            )

        except tweepy.TweepyException as e:
            raise APIError(f"Twitter API error: {e}")

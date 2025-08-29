from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional
from datetime import datetime
from core.base import BaseSocialMediaService
from core.models import SocialMediaPost, ChannelInfo
from core.exceptions import APIError, AuthenticationError, ChannelNotFoundError
from config.settings import settings


class InstagramService(BaseSocialMediaService):
    """Instragram service implementation"""

    def __init__(self):
        super().__init__()
        # Instagram Basic Display API endpoints
        self.basic_display_base_url = "https://graph.instagram.com"
        
        # Instagram Graph API endpoints (for business accounts)
        self.graph_api_base_url = "https://graph.facebook.com/v18.0"

        if (
            not settings.YOUTUBE_API_KEY
            or not settings.INSTAGRAM_ACCESS_TOKEN
            or not settings.INSTAGRAM_APP_SECRET
        ):
            raise AuthenticationError("Instagram API credentials not provided")

        try:
            self.youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize YouTube client: {e}")

    def _get_platform_name(self) -> str:
        return "instagram"

    def validate_credentials(self) -> bool:
        """Validate Instagram API credentials"""
        if not self.access_token:
            logger.error("Instagram access token not provided")
            return False
        
        # Test the access token by making a simple request
        test_url = f"{self.basic_display_base_url}/me"
        params = {
            'fields': 'id,username',
            'access_token': self.access_token
        }
        
        response_data = self._make_request(test_url, params)
        
        if response_data and 'id' in response_data:
            return True
        else:
            return False

    def get_channel_info(self, channel_identifier: str) -> ChannelInfo:
        """Get YouTube channel information"""
        try:
            # Try by channel ID first
            response = (
                self.youtube.channels()
                .list(part="snippet,statistics", id=channel_identifier)
                .execute()
            )

            if "items" not in response.keys():
                # Try by username
                response = (
                    self.youtube.channels()
                    .list(part="snippet,statistics", forUsername=channel_identifier)
                    .execute()
                )

            if "items" not in response.keys():
                # Try by custom URL (handle)
                response = (
                    self.youtube.search()
                    .list(
                        part="snippet",
                        q=channel_identifier,
                        type="channel",
                        maxResults=1,
                    )
                    .execute()
                )

                if response["items"]:
                    channel_id = response["items"][0]["id"]["channelId"]
                    response = (
                        self.youtube.channels()
                        .list(part="snippet,statistics", id=channel_id)
                        .execute()
                    )

            if not response["items"]:
                raise ChannelNotFoundError(
                    f"YouTube channel not found: {channel_identifier}"
                )

            channel_data = response["items"][0]
            snippet = channel_data["snippet"]
            statistics = channel_data.get("statistics", {})

            channel_info = ChannelInfo(
                id=channel_data["id"],
                name=snippet["title"],
                username=snippet.get("customUrl"),
                platform=self.platform_name,
                url=f"https://www.youtube.com/channel/{channel_data['id']}",
                follower_count=int(statistics.get("subscriberCount", 0)),
            )

            return channel_info

        except HttpError as e:
            raise APIError(f"YouTube API error: {e}")

    def get_latest_post(self, channel_identifier: str) -> Optional[SocialMediaPost]:
        """Get the latest video from a YouTube channel"""
        try:
            # First get channel info to get the channel ID
            channel_info = self.get_channel_info(channel_identifier)

            # Search for the latest video from this channel
            response = (
                self.youtube.search()
                .list(
                    part="snippet",
                    channelId=channel_info.id,
                    type="video",
                    order="date",
                    maxResults=1,
                )
                .execute()
            )

            if not response["items"]:
                return None

            video = response["items"][0]
            video_id = video["id"]["videoId"]
            snippet = video["snippet"]

            # Get additional video details
            video_details = (
                self.youtube.videos()
                .list(part="statistics,contentDetails", id=video_id)
                .execute()
            )

            stats = (
                video_details["items"][0]["statistics"]
                if video_details["items"]
                else {}
            )

            return SocialMediaPost(
                id=video_id,
                platform=self.platform_name,
                author=snippet["channelTitle"],
                author_id=snippet["channelId"],
                content=snippet["title"],
                created_at=datetime.fromisoformat(
                    snippet["publishedAt"].replace("Z", "+00:00")
                ),
                url=f"https://www.youtube.com/watch?v={video_id}",
                media_urls=[f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"],
                engagement={
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                },
                raw_data=video,
            )

        except HttpError as e:
            raise APIError(f"YouTube API error: {e}")

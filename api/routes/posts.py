from fastapi import APIRouter, Path, Body

from api.dependencies import FetcherDep, validate_platform
from api.exceptions.api_exceptions import map_to_http_exception
from api.response_models.responses import (
    MultiChannelRequest,
    MultiPostResponse,
    PostResponse,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/{platform}/{channel_identifier}/latest", response_model=PostResponse)
async def get_latest_post(
    fetcher: FetcherDep,
    platform: str = Path(..., description="Social media platform"),
    channel_identifier: str = Path(
        ..., description="Channel identifier (username, ID, or handle)"
    ),
):
    """Get the latest post from a specific social media channel"""
    try:
        validated_platform = validate_platform(platform)
        post = await fetcher.get_latest_post(validated_platform, channel_identifier)
        if not post:
            return PostResponse(
                success=True, data=None, message="No posts found for this channel"
            )

        return PostResponse(data=post)

    except Exception as e:
        raise map_to_http_exception(e)


@router.post("/latest/batch", response_model=MultiPostResponse)
async def get_latest_posts_batch(
    fetcher: FetcherDep, request: MultiChannelRequest = Body(...)
):
    """Get latest posts from multiple channels across different platforms"""
    try:
        posts = await fetcher.get_latest_posts_from_multiple_channels(request.channels)

        # Separate successful results from errors
        successful_posts = {}
        errors = {}

        for platform_str, post in posts.items():
            if post is not None:
                successful_posts[platform_str] = post
            else:
                errors[platform_str] = "Failed to fetch post or no posts found"

        return MultiPostResponse(
            data=successful_posts,
            errors=errors,
            message=f"Retrieved posts from {len(successful_posts)} out of {len(request.channels)} platforms",
        )

    except Exception as e:
        raise map_to_http_exception(e)

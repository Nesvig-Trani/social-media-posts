from fastapi import APIRouter, Path

from api.dependencies import FetcherDep, validate_platform
from api.exceptions.api_exceptions import map_to_http_exception
from api.response_models.responses import ChannelResponse

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.get("/{platform}/{channel_identifier}", response_model=ChannelResponse)
async def get_channel_info(
    fetcher: FetcherDep,
    platform: str = Path(..., description="Social media platform"),
    channel_identifier: str = Path(
        ..., description="Channel identifier (username, ID, or handle)"
    ),
):
    """Get information about a social media channel/account"""
    try:
        validated_platform = validate_platform(platform)
        channel_info = await fetcher.get_channel_info(
            validated_platform, channel_identifier
        )

        return ChannelResponse(data=channel_info)

    except Exception as e:
        raise map_to_http_exception(e)

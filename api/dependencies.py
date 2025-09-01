from functools import lru_cache
from fastapi import Depends, HTTPException, status
from typing import Annotated

from core.models import Platform
from services.fetcher_service import SocialMediaFetcher


@lru_cache()
def get_social_media_fetcher() -> SocialMediaFetcher:
    """Dependency to get social media fetcher instance"""
    return SocialMediaFetcher()


def validate_platform(platform: str) -> Platform:
    """Validate platform parameter"""
    try:
        return Platform(platform.lower())
    except ValueError:
        available_platforms = [p.value for p in Platform]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Available platforms: {available_platforms}",
        )


# Type aliases for dependencies
FetcherDep = Annotated[SocialMediaFetcher, Depends(get_social_media_fetcher)]

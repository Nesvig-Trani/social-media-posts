from fastapi import HTTPException, status

from core.exceptions import (
    APIError,
    AuthenticationError,
    ChannelNotFoundError,
    RateLimitError,
)


def map_to_http_exception(error: Exception) -> HTTPException:
    """Map internal exceptions to HTTP exceptions"""
    if isinstance(error, ChannelNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    elif isinstance(error, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        )
    elif isinstance(error, RateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(error)
        )
    elif isinstance(error, APIError):
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error))
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

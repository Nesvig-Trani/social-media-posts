class SocialMediaFetcherError(Exception):
    """Base exception for social media fetcher"""
    pass

class APIError(SocialMediaFetcherError):
    """Exception raised when API returns an error"""
    pass

class AuthenticationError(SocialMediaFetcherError):
    """Exception raised when authentication fails"""
    pass

class RateLimitError(SocialMediaFetcherError):
    """Exception raised when rate limit is exceeded"""
    pass

class ChannelNotFoundError(SocialMediaFetcherError):
    """Exception raised when channel/account is not found"""
    pass
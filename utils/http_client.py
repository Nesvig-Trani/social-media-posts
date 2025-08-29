import requests
from typing import Dict, Any
import time
from ..config.settings import settings
from ..core.exceptions import APIError, RateLimitError


class HTTPClient:
    """HTTP client with retry logic and error handling"""

    def __init__(self, timeout: int = None): # type: ignore
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.session = requests.Session()

    def get(
        self, url: str, headers: Dict[str, str] = None, params: Dict[str, Any] = None # type: ignore
    ) -> Dict[str, Any]:
        """Make GET request with retry logic"""
        return self._make_request("GET", url, headers=headers, params=params)

    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                if response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries:
                        wait_time = 2**attempt
                        time.sleep(wait_time)
                        continue
                    raise RateLimitError("Rate limit exceeded")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue

        raise APIError(
            f"Request failed after {self.max_retries} retries: {last_exception}"
        )

"""Custom exceptions for the SURF Research Cloud API client."""

import httpx


class SurfAPIError(Exception):
    """Base exception for SURF API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: httpx.Response | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(SurfAPIError):
    """Raised when the API token is invalid or expired (HTTP 401/403)."""


class NotFoundError(SurfAPIError):
    """Raised when a requested resource does not exist (HTTP 404)."""


class RateLimitError(SurfAPIError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""


class ServerError(SurfAPIError):
    """Raised when the API returns a 5xx server error."""


def raise_for_status(response: httpx.Response) -> None:
    """Raise an appropriate exception based on the HTTP status code."""
    if response.is_success:
        return

    try:
        detail = response.json()
    except Exception:
        detail = response.text

    message = f"HTTP {response.status_code}: {detail}"

    if response.status_code in (401, 403):
        raise AuthenticationError(message, status_code=response.status_code, response=response)
    if response.status_code == 404:
        raise NotFoundError(message, status_code=response.status_code, response=response)
    if response.status_code == 429:
        raise RateLimitError(message, status_code=response.status_code, response=response)
    if response.status_code >= 500:
        raise ServerError(message, status_code=response.status_code, response=response)

    raise SurfAPIError(message, status_code=response.status_code, response=response)

"""HTTP client for the SURF Research Cloud API."""

import os
import time
from typing import Any, Callable

import httpx

from surf_cli.config import read_token
from surf_cli.exceptions import RateLimitError, ServerError, raise_for_status

API_BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"
TOKEN_ENV_VAR = "SURF_API_TOKEN"

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0


class SurfClient:
    """Thin wrapper around the SURF Research Cloud REST API."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str = API_BASE_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        self._token = token or os.environ.get(TOKEN_ENV_VAR) or read_token()
        if not self._token:
            raise ValueError(
                f"API token not provided. Set the {TOKEN_ENV_VAR} environment variable"
                " or run 'surf config set-token <token>'."
            )
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._http = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Token {self._token}",
                "Accept": "application/json",
            },
            timeout=30,
        )

    def _with_retry(self, fn: Callable[[], Any]) -> Any:
        """Execute fn with exponential backoff retries on transient errors."""
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return fn()
            except (RateLimitError, ServerError) as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    break
                delay = self._backoff_delay(attempt, exc)
                time.sleep(delay)
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    break
                time.sleep(self._retry_delay * (2**attempt))
        raise last_exc  # type: ignore[misc]

    def _backoff_delay(self, attempt: int, exc: Exception) -> float:
        """Return the delay before the next retry, respecting Retry-After if present."""
        if isinstance(exc, RateLimitError) and exc.response is not None:
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        return self._retry_delay * (2**attempt)

    def get(self, path: str, **params: Any) -> Any:
        """Send a GET request and return the parsed JSON body."""
        filtered = {k: v for k, v in params.items() if v is not None}
        return self._with_retry(lambda: self._get(path, filtered))

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        response = self._http.get(path, params=params)
        raise_for_status(response)
        return response.json()

    def post(self, path: str, json: Any) -> Any:
        """Send a POST request with a JSON body and return the parsed JSON response."""
        return self._with_retry(lambda: self._post(path, json))

    def _post(self, path: str, json: Any) -> Any:
        response = self._http.post(path, json=json)
        raise_for_status(response)
        return response.json()

    def patch(self, path: str, json: Any) -> Any:
        """Send a PATCH request with a JSON body and return the parsed JSON response."""
        return self._with_retry(lambda: self._patch(path, json))

    def _patch(self, path: str, json: Any) -> Any:
        response = self._http.patch(path, json=json)
        raise_for_status(response)
        return response.json()

    def delete(self, path: str) -> None:
        """Send a DELETE request."""
        self._with_retry(lambda: self._delete(path))

    def _delete(self, path: str) -> None:
        response = self._http.delete(path)
        raise_for_status(response)

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._http.close()

    def __enter__(self) -> "SurfClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

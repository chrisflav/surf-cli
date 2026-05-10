"""HTTP client for the SURF Research Cloud API."""

import os
from typing import Any

import httpx

from surf_cli.config import read_token
from surf_cli.exceptions import raise_for_status

API_BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"
TOKEN_ENV_VAR = "SURF_API_TOKEN"


class SurfClient:
    """Thin wrapper around the SURF Research Cloud REST API."""

    def __init__(self, token: str | None = None, base_url: str = API_BASE_URL) -> None:
        self._token = token or os.environ.get(TOKEN_ENV_VAR) or read_token()
        if not self._token:
            raise ValueError(
                f"API token not provided. Set the {TOKEN_ENV_VAR} environment variable"
                " or run 'surf config set-token <token>'."
            )
        self._http = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Token {self._token}",
                "Accept": "application/json",
            },
            timeout=30,
        )

    def get(self, path: str, **params: Any) -> Any:
        """Send a GET request and return the parsed JSON body."""
        response = self._http.get(path, params={k: v for k, v in params.items() if v is not None})
        raise_for_status(response)
        return response.json()

    def post(self, path: str, json: Any) -> Any:
        """Send a POST request with a JSON body and return the parsed JSON response."""
        response = self._http.post(path, json=json)
        raise_for_status(response)
        return response.json()

    def patch(self, path: str, json: Any) -> Any:
        """Send a PATCH request with a JSON body and return the parsed JSON response."""
        response = self._http.patch(path, json=json)
        raise_for_status(response)
        return response.json()

    def delete(self, path: str) -> None:
        """Send a DELETE request."""
        response = self._http.delete(path)
        raise_for_status(response)

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._http.close()

    def __enter__(self) -> "SurfClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

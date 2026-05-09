"""HTTP client for the SURF Research Cloud API."""

import os

import httpx

API_BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"
TOKEN_ENV_VAR = "SURF_API_TOKEN"


class SurfClient:
    """Thin wrapper around the SURF Research Cloud REST API."""

    def __init__(self, token: str | None = None, base_url: str = API_BASE_URL) -> None:
        self._token = token or os.environ.get(TOKEN_ENV_VAR)
        if not self._token:
            raise ValueError(
                f"API token not provided. Set the {TOKEN_ENV_VAR} environment variable."
            )
        self._http = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Token {self._token}"},
            timeout=30,
        )

    def get(self, path: str, **params: object) -> object:
        """Send a GET request and return the parsed JSON body."""
        response = self._http.get(path, params={k: v for k, v in params.items() if v is not None})
        response.raise_for_status()
        return response.json()

    def post(self, path: str, json: object) -> object:
        """Send a POST request with a JSON body and return the parsed JSON response."""
        response = self._http.post(path, json=json)
        response.raise_for_status()
        return response.json()

    def patch(self, path: str, json: object) -> object:
        """Send a PATCH request with a JSON body and return the parsed JSON response."""
        response = self._http.patch(path, json=json)
        response.raise_for_status()
        return response.json()

    def delete(self, path: str) -> None:
        """Send a DELETE request."""
        response = self._http.delete(path)
        response.raise_for_status()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SurfClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

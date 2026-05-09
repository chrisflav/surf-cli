"""Tests for the SURF API client."""

import pytest
import httpx
from pytest_httpx import HTTPXMock

from surf_cli.client import SurfClient, TOKEN_ENV_VAR, API_BASE_URL
from surf_cli.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SurfAPIError,
)


def test_client_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match=TOKEN_ENV_VAR):
        SurfClient()


def test_client_reads_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TOKEN_ENV_VAR, "test-token")
    client = SurfClient()
    assert client._token == "test-token"
    client.close()


def test_client_explicit_token() -> None:
    client = SurfClient(token="explicit-token")
    assert client._token == "explicit-token"
    client.close()


def test_client_authorization_header() -> None:
    client = SurfClient(token="mytoken")
    assert client._http.headers["Authorization"] == "Token mytoken"
    client.close()


def test_client_accept_header() -> None:
    client = SurfClient(token="mytoken")
    assert client._http.headers["Accept"] == "application/json"
    client.close()


def test_client_context_manager() -> None:
    with SurfClient(token="tok") as client:
        assert client._token == "tok"


def test_get_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"results": []})
    with SurfClient(token="tok") as client:
        data = client.get("/items")
    assert data == {"results": []}


def test_get_with_params(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items?page=2", json={"results": []})
    with SurfClient(token="tok") as client:
        data = client.get("/items", page=2)
    assert data == {"results": []}


def test_get_ignores_none_params(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={})
    with SurfClient(token="tok") as client:
        client.get("/items", page=None)


def test_post_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"id": 1}, status_code=201)
    with SurfClient(token="tok") as client:
        data = client.post("/items", json={"name": "foo"})
    assert data == {"id": 1}


def test_patch_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/1", json={"id": 1, "name": "bar"})
    with SurfClient(token="tok") as client:
        data = client.patch("/items/1", json={"name": "bar"})
    assert data == {"id": 1, "name": "bar"}


def test_delete_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/1", status_code=204, content=b"")
    with SurfClient(token="tok") as client:
        client.delete("/items/1")


def test_authentication_error_401(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=401, json={"detail": "Invalid token."})
    with SurfClient(token="bad-token") as client:
        with pytest.raises(AuthenticationError) as exc_info:
            client.get("/items")
    assert exc_info.value.status_code == 401


def test_authentication_error_403(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=403, json={"detail": "Forbidden."})
    with SurfClient(token="tok") as client:
        with pytest.raises(AuthenticationError) as exc_info:
            client.get("/items")
    assert exc_info.value.status_code == 403


def test_not_found_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/999", status_code=404, json={"detail": "Not found."})
    with SurfClient(token="tok") as client:
        with pytest.raises(NotFoundError) as exc_info:
            client.get("/items/999")
    assert exc_info.value.status_code == 404


def test_rate_limit_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=429, json={"detail": "Too many requests."})
    with SurfClient(token="tok") as client:
        with pytest.raises(RateLimitError) as exc_info:
            client.get("/items")
    assert exc_info.value.status_code == 429


def test_server_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=500, json={"detail": "Internal server error."})
    with SurfClient(token="tok") as client:
        with pytest.raises(ServerError) as exc_info:
            client.get("/items")
    assert exc_info.value.status_code == 500


def test_generic_api_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=422, json={"detail": "Unprocessable entity."})
    with SurfClient(token="tok") as client:
        with pytest.raises(SurfAPIError) as exc_info:
            client.get("/items")
    assert exc_info.value.status_code == 422


def test_error_includes_response(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=401, json={"detail": "Invalid token."})
    with SurfClient(token="bad") as client:
        with pytest.raises(AuthenticationError) as exc_info:
            client.get("/items")
    assert exc_info.value.response is not None

"""Tests for the SURF API client."""

from unittest.mock import patch

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
    assert client._http.headers["Authorization"] == "mytoken"
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
    with SurfClient(token="tok", max_retries=0) as client:
        with pytest.raises(RateLimitError) as exc_info:
            client.get("/items")
    assert exc_info.value.status_code == 429


def test_server_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=500, json={"detail": "Internal server error."})
    with SurfClient(token="tok", max_retries=0) as client:
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


# ---------------------------------------------------------------------------
# Retry / exponential-backoff tests
# ---------------------------------------------------------------------------


def _no_sleep(_: float) -> None:
    """Replacement for time.sleep that does nothing."""


def test_retry_on_server_error_succeeds(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=500, json={"detail": "err"})
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"results": []})
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            data = client.get("/items")
    assert data == {"results": []}


def test_retry_on_rate_limit_succeeds(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=429, json={"detail": "slow"})
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"ok": True})
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            data = client.get("/items")
    assert data == {"ok": True}


def test_retry_exhausted_raises_last_exception(httpx_mock: HTTPXMock) -> None:
    for _ in range(4):  # 1 initial + 3 retries
        httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=500, json={"detail": "err"})
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            with pytest.raises(ServerError):
                client.get("/items")


def test_no_retry_on_auth_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=401, json={"detail": "bad"})
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            with pytest.raises(AuthenticationError):
                client.get("/items")
    # Only one request was made
    assert len(httpx_mock.get_requests()) == 1


def test_no_retry_on_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/1", status_code=404, json={"detail": "nf"})
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            with pytest.raises(NotFoundError):
                client.get("/items/1")
    assert len(httpx_mock.get_requests()) == 1


def test_retry_respects_retry_after_header(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=f"{API_BASE_URL}/items",
        status_code=429,
        headers={"Retry-After": "5"},
        json={"detail": "slow"},
    )
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"ok": True})
    sleep_calls: list[float] = []
    with patch("surf_cli.client.time.sleep", sleep_calls.append):
        with SurfClient(token="tok", max_retries=3, retry_delay=1.0) as client:
            client.get("/items")
    assert sleep_calls == [5.0]


def test_retry_exponential_backoff_delays(httpx_mock: HTTPXMock) -> None:
    for _ in range(3):
        httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=500, json={"detail": "err"})
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"ok": True})
    sleep_calls: list[float] = []
    with patch("surf_cli.client.time.sleep", sleep_calls.append):
        with SurfClient(token="tok", max_retries=3, retry_delay=1.0) as client:
            client.get("/items")
    assert sleep_calls == [1.0, 2.0, 4.0]


def test_retry_on_transport_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ConnectError("connection refused"))
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"ok": True})
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            data = client.get("/items")
    assert data == {"ok": True}


def test_retry_transport_error_exhausted(httpx_mock: HTTPXMock) -> None:
    for _ in range(4):
        httpx_mock.add_exception(httpx.ConnectError("connection refused"))
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            with pytest.raises(httpx.TransportError):
                client.get("/items")


def test_client_default_retry_params() -> None:
    from surf_cli.client import DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY

    client = SurfClient(token="tok")
    assert client._max_retries == DEFAULT_MAX_RETRIES
    assert client._retry_delay == DEFAULT_RETRY_DELAY
    client.close()


def test_client_custom_retry_params() -> None:
    client = SurfClient(token="tok", max_retries=5, retry_delay=2.0)
    assert client._max_retries == 5
    assert client._retry_delay == 2.0
    client.close()


def test_retry_post_on_server_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", status_code=503, json={"detail": "unavail"})
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"id": 1}, status_code=201)
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            data = client.post("/items", json={"name": "foo"})
    assert data == {"id": 1}


def test_retry_delete_on_server_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/1", status_code=500, json={"detail": "err"})
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/1", status_code=204, content=b"")
    with patch("surf_cli.client.time.sleep", _no_sleep):
        with SurfClient(token="tok", max_retries=3, retry_delay=0) as client:
            client.delete("/items/1")


# ---------------------------------------------------------------------------
# Verbose logging tests
# ---------------------------------------------------------------------------


def test_verbose_get_logs_to_stderr(
    httpx_mock: HTTPXMock, capsys: pytest.CaptureFixture[str]
) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"results": []})
    with SurfClient(token="tok", verbose=True) as client:
        client.get("/items")
    err = capsys.readouterr().err
    assert "GET" in err
    assert "200" in err
    # Auth token should be masked
    assert "tok" not in err
    assert "***" in err


def test_verbose_post_logs_to_stderr(
    httpx_mock: HTTPXMock, capsys: pytest.CaptureFixture[str]
) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"id": 1}, status_code=201)
    with SurfClient(token="tok", verbose=True) as client:
        client.post("/items", json={"name": "foo"})
    err = capsys.readouterr().err
    assert "POST" in err
    assert "201" in err


def test_verbose_delete_logs_to_stderr(
    httpx_mock: HTTPXMock, capsys: pytest.CaptureFixture[str]
) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items/1", status_code=204, content=b"")
    with SurfClient(token="tok", verbose=True) as client:
        client.delete("/items/1")
    err = capsys.readouterr().err
    assert "DELETE" in err
    assert "204" in err


def test_non_verbose_no_stderr(httpx_mock: HTTPXMock, capsys: pytest.CaptureFixture[str]) -> None:
    httpx_mock.add_response(url=f"{API_BASE_URL}/items", json={"results": []})
    with SurfClient(token="tok", verbose=False) as client:
        client.get("/items")
    err = capsys.readouterr().err
    assert err == ""

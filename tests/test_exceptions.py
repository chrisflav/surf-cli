"""Tests for custom exception classes."""

import httpx
import pytest

from surf_cli.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SurfAPIError,
    raise_for_status,
)


def _make_response(status_code: int, body: bytes = b'{"detail": "error"}') -> httpx.Response:
    return httpx.Response(status_code, content=body, headers={"content-type": "application/json"})


def test_raise_for_status_success() -> None:
    response = _make_response(200)
    raise_for_status(response)  # should not raise


def test_raise_for_status_401() -> None:
    with pytest.raises(AuthenticationError) as exc_info:
        raise_for_status(_make_response(401))
    assert exc_info.value.status_code == 401


def test_raise_for_status_403() -> None:
    with pytest.raises(AuthenticationError) as exc_info:
        raise_for_status(_make_response(403))
    assert exc_info.value.status_code == 403


def test_raise_for_status_404() -> None:
    with pytest.raises(NotFoundError) as exc_info:
        raise_for_status(_make_response(404))
    assert exc_info.value.status_code == 404


def test_raise_for_status_429() -> None:
    with pytest.raises(RateLimitError) as exc_info:
        raise_for_status(_make_response(429))
    assert exc_info.value.status_code == 429


def test_raise_for_status_500() -> None:
    with pytest.raises(ServerError) as exc_info:
        raise_for_status(_make_response(500))
    assert exc_info.value.status_code == 500


def test_raise_for_status_503() -> None:
    with pytest.raises(ServerError) as exc_info:
        raise_for_status(_make_response(503))
    assert exc_info.value.status_code == 503


def test_raise_for_status_422() -> None:
    with pytest.raises(SurfAPIError) as exc_info:
        raise_for_status(_make_response(422))
    assert exc_info.value.status_code == 422


def test_surf_api_error_is_base() -> None:
    assert issubclass(AuthenticationError, SurfAPIError)
    assert issubclass(NotFoundError, SurfAPIError)
    assert issubclass(RateLimitError, SurfAPIError)
    assert issubclass(ServerError, SurfAPIError)


def test_error_with_non_json_body() -> None:
    response = httpx.Response(
        500, content=b"Internal Server Error", headers={"content-type": "text/plain"}
    )
    with pytest.raises(ServerError) as exc_info:
        raise_for_status(response)
    assert "Internal Server Error" in str(exc_info.value)

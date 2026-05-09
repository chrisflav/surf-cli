"""Tests for the SURF API client."""

import pytest
import httpx

from surf_cli.client import SurfClient, TOKEN_ENV_VAR


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


def test_client_context_manager() -> None:
    with SurfClient(token="tok") as client:
        assert client._token == "tok"

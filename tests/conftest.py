"""Shared pytest fixtures for the surf-cli test suite."""

import pytest

from surf_cli.client import TOKEN_ENV_VAR


@pytest.fixture(autouse=True)
def set_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TOKEN_ENV_VAR, "test-token")


@pytest.fixture()
def no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove all token sources so SurfClient raises on construction."""
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
    monkeypatch.setattr("surf_cli.config.read_token", lambda: None)

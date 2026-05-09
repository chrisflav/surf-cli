"""Shared pytest fixtures for the surf-cli test suite."""

import pytest

from surf_cli.client import TOKEN_ENV_VAR


@pytest.fixture(autouse=True)
def set_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TOKEN_ENV_VAR, "test-token")

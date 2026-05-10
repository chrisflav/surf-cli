"""Shared pytest fixtures for the surf-cli test suite."""

from pathlib import Path

import pytest

from surf_cli.client import TOKEN_ENV_VAR


@pytest.fixture(autouse=True)
def set_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(TOKEN_ENV_VAR, "test-token")
    # Redirect config paths to a non-existent temp location so the real
    # ~/.config/surf-cli/config.toml is never read during tests.
    fake_config = tmp_path / ".config" / "surf-cli" / "config.toml"
    monkeypatch.setattr("surf_cli.config.CONFIG_DIR", fake_config.parent)
    monkeypatch.setattr("surf_cli.config.CONFIG_FILE", fake_config)
    monkeypatch.setattr("surf_cli.main.CONFIG_FILE", fake_config)


@pytest.fixture()
def no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove all token sources so SurfClient raises on construction."""
    monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)

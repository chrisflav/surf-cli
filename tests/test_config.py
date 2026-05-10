"""Tests for configuration file support."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from surf_cli.config import read_token, write_token
from surf_cli.main import app

runner = CliRunner()


@pytest.fixture()
def tmp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Redirect config paths to a temporary directory."""
    config_dir = tmp_path / ".config" / "surf-cli"
    config_file = config_dir / "config.toml"
    monkeypatch.setattr("surf_cli.config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("surf_cli.config.CONFIG_FILE", config_file)
    monkeypatch.setattr("surf_cli.main.CONFIG_FILE", config_file)
    return config_file


class TestReadToken:
    def test_returns_none_when_file_missing(self, tmp_config: Path) -> None:
        assert read_token() is None

    def test_returns_token_from_file(self, tmp_config: Path) -> None:
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        tmp_config.write_text('token = "my-token"\n')
        assert read_token() == "my-token"

    def test_returns_none_for_empty_token(self, tmp_config: Path) -> None:
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        tmp_config.write_text('token = ""\n')
        assert read_token() is None

    def test_returns_none_for_invalid_toml(self, tmp_config: Path) -> None:
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        tmp_config.write_text("not valid toml [\n")
        assert read_token() is None

    def test_returns_none_when_no_token_key(self, tmp_config: Path) -> None:
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        tmp_config.write_text('other = "value"\n')
        assert read_token() is None


class TestWriteToken:
    def test_creates_file_with_token(self, tmp_config: Path) -> None:
        write_token("my-secret-token")
        assert tmp_config.exists()
        assert read_token() == "my-secret-token"

    def test_creates_parent_directory(self, tmp_config: Path) -> None:
        assert not tmp_config.parent.exists()
        write_token("tok")
        assert tmp_config.parent.exists()

    def test_sets_file_permissions(self, tmp_config: Path) -> None:
        write_token("tok")
        mode = tmp_config.stat().st_mode & 0o777
        assert mode == 0o600

    def test_overwrites_existing_token(self, tmp_config: Path) -> None:
        write_token("first-token")
        write_token("second-token")
        assert read_token() == "second-token"


class TestConfigCommands:
    def test_set_token_saves_and_reports(self, tmp_config: Path) -> None:
        result = runner.invoke(app, ["config", "set-token", "my-token"])
        assert result.exit_code == 0
        assert "Token saved" in result.output
        assert read_token() == "my-token"

    def test_show_with_token(self, tmp_config: Path) -> None:
        write_token("abcdefghij")
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "abcd" in result.output
        assert "****" in result.output

    def test_show_without_token(self, tmp_config: Path) -> None:
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "No token configured" in result.output

    def test_config_help(self) -> None:
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "set-token" in result.output
        assert "show" in result.output


class TestConfigValidateCommand:
    def test_validate_success(self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from unittest.mock import MagicMock, patch

        write_token("valid-token")
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = {"results": []}

        with patch("surf_cli.main.get_client", return_value=mock_client):
            result = runner.invoke(app, ["config", "validate"])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()
        mock_client.get.assert_called_once_with("/workspaces/", limit=1)

    def test_validate_invalid_token(
        self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from unittest.mock import MagicMock, patch

        from surf_cli.exceptions import AuthenticationError

        write_token("bad-token")
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = AuthenticationError(
            "HTTP 401: Unauthorized", status_code=401
        )

        with patch("surf_cli.main.get_client", return_value=mock_client):
            result = runner.invoke(app, ["config", "validate"])

        assert result.exit_code == 1

    def test_validate_no_token(self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SURF_API_TOKEN", raising=False)
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 1

    def test_validate_appears_in_config_help(self) -> None:
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "validate" in result.output


class TestClientFallsBackToConfigFile:
    def test_uses_config_file_token_when_env_unset(
        self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("SURF_API_TOKEN", raising=False)
        write_token("config-file-token")
        from surf_cli.client import SurfClient

        client = SurfClient()
        assert client._token == "config-file-token"
        client.close()

    def test_env_var_takes_precedence_over_config_file(
        self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SURF_API_TOKEN", "env-token")
        write_token("config-file-token")
        from surf_cli.client import SurfClient

        client = SurfClient()
        assert client._token == "env-token"
        client.close()

    def test_error_message_mentions_config_command(
        self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("SURF_API_TOKEN", raising=False)
        from surf_cli.client import SurfClient

        with pytest.raises(ValueError, match="set-token"):
            SurfClient()

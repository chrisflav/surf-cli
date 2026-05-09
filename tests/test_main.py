"""Tests for the CLI entry point."""

from typer.testing import CliRunner

from surf_cli.main import app
from surf_cli import __version__

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "surf" in result.output.lower()

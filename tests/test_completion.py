"""Tests for shell completion support."""

import pytest
from typer.testing import CliRunner

from surf_cli.main import app

runner = CliRunner()


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_show_completion(shell: str) -> None:
    result = runner.invoke(app, ["--show-completion", shell])
    assert result.exit_code == 0
    assert len(result.output) > 0


def test_help_shows_completion_options() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "completion" in result.output.lower()


def test_show_completion_bash_contains_surf() -> None:
    result = runner.invoke(app, ["--show-completion", "bash"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "surf" in output


def test_show_completion_zsh_contains_surf() -> None:
    result = runner.invoke(app, ["--show-completion", "zsh"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "surf" in output


def test_show_completion_fish_contains_surf() -> None:
    result = runner.invoke(app, ["--show-completion", "fish"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "surf" in output

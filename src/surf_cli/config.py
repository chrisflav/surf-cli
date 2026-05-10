"""Configuration file support for surf-cli.

The config file is stored at ~/.config/surf-cli/config.toml and provides
an alternative to the SURF_API_TOKEN environment variable.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "surf-cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def read_token() -> str | None:
    """Return the API token from the config file, or None if absent."""
    if not CONFIG_FILE.exists():
        return None
    try:
        with CONFIG_FILE.open("rb") as f:
            data = tomllib.load(f)
        token = data.get("token")
        return str(token) if token else None
    except (tomllib.TOMLDecodeError, OSError):
        return None


def write_token(token: str) -> None:
    """Write *token* to the config file, creating the directory if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(f'token = "{token}"\n', encoding="utf-8")
    CONFIG_FILE.chmod(0o600)

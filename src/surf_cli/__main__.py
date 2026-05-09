"""Allow running surf-cli as ``python -m surf_cli``."""

from surf_cli.main import app

if __name__ == "__main__":
    app()

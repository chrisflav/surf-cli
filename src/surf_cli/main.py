"""Entry point for the surf CLI."""

import os

import typer

from surf_cli import __version__
from surf_cli.commands import catalog, co, storage, wallets, workspaces
from surf_cli.config import CONFIG_FILE, read_token, write_token
from surf_cli.exceptions import AuthenticationError
from surf_cli.formatting import get_client
from surf_cli.state import state

app = typer.Typer(
    name="surf",
    help="CLI for interacting with SURF Research Cloud (surfresearchcloud.nl).",
    no_args_is_help=True,
)

config_app = typer.Typer(
    name="config",
    help="Manage surf-cli configuration.",
    no_args_is_help=True,
)

app.add_typer(workspaces.app, name="workspace")
app.add_typer(catalog.app, name="catalog")
app.add_typer(storage.app, name="storage")
app.add_typer(co.app, name="co")
app.add_typer(wallets.app, name="wallet")
app.add_typer(config_app, name="config")


@config_app.command("set-token")
def config_set_token(token: str = typer.Argument(..., help="API token to save.")) -> None:
    """Save the API token to the configuration file."""
    write_token(token)
    typer.echo(f"Token saved to {CONFIG_FILE}")


@config_app.command("validate")
def config_validate() -> None:
    """Verify that the configured API token is accepted by the SURF Research Cloud API."""
    token = read_token()
    if not token:
        if not os.environ.get("SURF_API_TOKEN"):
            typer.echo("No token configured. Run 'surf config set-token <token>' first.", err=True)
            raise typer.Exit(1)

    try:
        with get_client() as client:
            client.get("/workspaces/", limit=1)
        typer.echo("Token is valid.")
    except AuthenticationError:
        typer.echo("Token is invalid or expired.", err=True)
        raise typer.Exit(1)
    except Exception as exc:
        typer.echo(f"Validation failed: {exc}", err=True)
        raise typer.Exit(1)


@config_app.command("show")
def config_show() -> None:
    """Show the current configuration."""
    token = read_token()
    if token:
        masked = token[:4] + "*" * (len(token) - 4) if len(token) > 4 else "****"
        typer.echo(f"token: {masked}")
        typer.echo(f"config file: {CONFIG_FILE}")
    else:
        typer.echo("No token configured in config file.")
        typer.echo(f"Expected location: {CONFIG_FILE}")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"surf-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: FBT001
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(  # noqa: FBT001
        False,
        "--verbose",
        help="Show raw HTTP request and response details.",
    ),
) -> None:
    """SURF Research Cloud command-line interface."""
    state.verbose = verbose


if __name__ == "__main__":
    app()

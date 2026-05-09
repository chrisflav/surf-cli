"""Entry point for the surf CLI."""

import typer

from surf_cli import __version__
from surf_cli.commands import catalog, storage, workspaces

app = typer.Typer(
    name="surf",
    help="CLI for interacting with SURF Research Cloud (surfresearchcloud.nl).",
    no_args_is_help=True,
)

app.add_typer(workspaces.app, name="workspace")
app.add_typer(catalog.app, name="catalog")
app.add_typer(storage.app, name="storage")


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
) -> None:
    """SURF Research Cloud command-line interface."""


if __name__ == "__main__":
    app()

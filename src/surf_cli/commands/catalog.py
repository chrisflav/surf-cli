"""Catalog commands for the surf CLI.

Exposes read operations on SURF Research Cloud catalog items via the
/catalog/ API endpoints. Catalog items represent applications and services
available for deployment as workspaces.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

from surf_cli.client import SurfClient

app = typer.Typer(help="Browse the SURF Research Cloud catalog.")


def _get_client() -> SurfClient:
    try:
        return SurfClient()
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _print_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2))


@app.command("list")
def list_catalog(
    co_id: Optional[str] = typer.Option(
        None, "--co-id", help="Filter by collaborative organisation ID."
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Search by catalog item name."
    ),
    offset: Optional[int] = typer.Option(
        None, "--offset", help="Offset for pagination."
    ),
    type_: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by application type. Options: Compute, Storage, IP, Network.",
    ),
) -> None:
    """List catalog items available to the authenticated user."""
    with _get_client() as client:
        data = client.get(
            "/catalog/",
            co_id=co_id,
            limit=limit,
            name=name,
            offset=offset,
            type=type_,
        )
    _print_json(data)


@app.command("get")
def get_catalog_item(
    item_id: str = typer.Argument(..., help="Catalog item ID."),
) -> None:
    """Retrieve a catalog item by ID."""
    with _get_client() as client:
        data = client.get(f"/catalog/{item_id}/")
    _print_json(data)

"""Catalog commands for the surf CLI.

Exposes read operations on SURF Research Cloud catalog items via the
/catalog/ API endpoints. Catalog items represent applications and services
available for deployment as workspaces.
"""

from __future__ import annotations

from typing import Optional

import typer

import surf_cli.api.catalog as catalog_api
from surf_cli.formatting import OutputFormat, get_client, print_output

app = typer.Typer(help="Browse the SURF Research Cloud catalog.")


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
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """List catalog items available to the authenticated user."""
    if limit is not None and limit <= 0:
        typer.echo("--limit must be a positive integer.", err=True)
        raise typer.Exit(1)
    if offset is not None and offset < 0:
        typer.echo("--offset must be a non-negative integer.", err=True)
        raise typer.Exit(1)
    with get_client() as client:
        data = catalog_api.list_catalog(
            client, co_id=co_id, limit=limit, name=name, offset=offset, type_=type_
        )
    print_output(data, fmt)


@app.command("get")
def get_catalog_item(
    item_id: str = typer.Argument(..., help="Catalog item ID."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """Retrieve a catalog item by ID."""
    with get_client() as client:
        data = catalog_api.get_catalog_item(client, item_id)
    print_output(data, fmt)

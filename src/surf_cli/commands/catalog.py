"""Catalog commands for the surf CLI.

Exposes read operations on SURF Research Cloud catalog items via the
/catalog/ API endpoints. Catalog items represent applications and services
available for deployment as workspaces.
"""

from __future__ import annotations

from typing import Optional

import typer

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
    with get_client() as client:
        data = client.get(
            "/catalog/",
            co_id=co_id,
            limit=limit,
            name=name,
            offset=offset,
            type=type_,
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
        data = client.get(f"/catalog/{item_id}/")
    print_output(data, fmt)

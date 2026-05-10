"""Storage commands for the surf CLI.

Exposes CRUD operations on SURF Research Cloud storage volumes via the
/storage/ API endpoints. Storage volumes provide persistent network-attached
storage that can be attached to workspaces.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

from surf_cli.formatting import OutputFormat, get_client, print_json, print_output

app = typer.Typer(help="Manage SURF Research Cloud storage volumes.")


@app.command("list")
def list_storage(
    co_id: Optional[str] = typer.Option(
        None, "--co-id", help="Filter by collaborative organisation ID."
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Search by storage volume name."
    ),
    offset: Optional[int] = typer.Option(
        None, "--offset", help="Offset for pagination."
    ),
    status: Optional[str] = typer.Option(
        None,
        "--status",
        "-s",
        help=(
            "Filter by status. Options: creating, available, in-use, full, updating, "
            "deleting, deleted, failed, unknown."
        ),
    ),
    wallet_id: Optional[str] = typer.Option(
        None, "--wallet-id", "-w", help="Filter by wallet ID."
    ),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """List storage volumes accessible to the authenticated user."""
    if limit is not None and limit <= 0:
        typer.echo("--limit must be a positive integer.", err=True)
        raise typer.Exit(1)
    if offset is not None and offset < 0:
        typer.echo("--offset must be a non-negative integer.", err=True)
        raise typer.Exit(1)
    with get_client() as client:
        data = client.get(
            "/storage/",
            co_id=co_id,
            limit=limit,
            name=name,
            offset=offset,
            status=status,
            wallet_id=wallet_id,
        )
    print_output(data, fmt)


@app.command("get")
def get_storage(
    storage_id: str = typer.Argument(..., help="Storage volume ID."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """Retrieve a storage volume by ID."""
    with get_client() as client:
        data = client.get(f"/storage/{storage_id}/")
    print_output(data, fmt)


@app.command("create")
def create_storage(
    payload: str = typer.Argument(
        ...,
        help=(
            "JSON payload for the storage creation request. "
            'Example: \'{"name": "my-storage", "co_id": "co-1", "wallet_id": "wallet-1"}\''
        ),
    ),
) -> None:
    """Create a new storage volume.

    PAYLOAD must be a JSON string with the required fields for the new storage volume.
    """
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON payload: {exc}", err=True)
        raise typer.Exit(1) from exc

    with get_client() as client:
        data = client.post("/storage/", json=body)
    print_json(data)


@app.command("update")
def update_storage(
    storage_id: str = typer.Argument(..., help="Storage volume ID."),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="New storage volume name."
    ),
    end_time: Optional[str] = typer.Option(
        None,
        "--end-time",
        help="New end time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).",
    ),
) -> None:
    """Partially update a storage volume (name and/or end_time)."""
    body: dict[str, str] = {}
    if name is not None:
        body["name"] = name
    if end_time is not None:
        body["end_time"] = end_time

    if not body:
        typer.echo("Provide at least --name or --end-time.", err=True)
        raise typer.Exit(1)

    with get_client() as client:
        data = client.patch(f"/storage/{storage_id}/", json=body)
    print_json(data)


@app.command("delete")
def delete_storage(
    storage_id: str = typer.Argument(..., help="Storage volume ID."),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt."
    ),
) -> None:
    """Delete a storage volume by ID."""
    if not confirm:
        typer.confirm(f"Delete storage volume {storage_id}?", abort=True)
    with get_client() as client:
        client.delete(f"/storage/{storage_id}/")
    typer.echo(f"Storage volume {storage_id} deleted.")

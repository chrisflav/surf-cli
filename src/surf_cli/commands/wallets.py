"""Wallet commands for the surf CLI.

Exposes CRUD operations on SURF Research Cloud wallets via the /wallets/
API endpoints. Wallets represent budget allocations used to pay for
workspace and storage resources.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

import surf_cli.api.wallets as wallets_api
from surf_cli.formatting import OutputFormat, get_client, print_json, print_output

app = typer.Typer(help="Manage SURF Research Cloud wallets.")


@app.command("list")
def list_wallets(
    co_id: Optional[str] = typer.Option(
        None, "--co-id", help="Filter by collaborative organisation ID."
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Search by wallet name."
    ),
    offset: Optional[int] = typer.Option(
        None, "--offset", help="Offset for pagination."
    ),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """List wallets accessible to the authenticated user."""
    if limit is not None and limit <= 0:
        typer.echo("--limit must be a positive integer.", err=True)
        raise typer.Exit(1)
    if offset is not None and offset < 0:
        typer.echo("--offset must be a non-negative integer.", err=True)
        raise typer.Exit(1)
    with get_client() as client:
        data = wallets_api.list_wallets(client, co_id=co_id, limit=limit, name=name, offset=offset)
    print_output(data, fmt)


@app.command("get")
def get_wallet(
    wallet_id: str = typer.Argument(..., help="Wallet ID."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """Retrieve a wallet by ID."""
    with get_client() as client:
        data = wallets_api.get_wallet(client, wallet_id)
    print_output(data, fmt)


@app.command("create")
def create_wallet(
    payload: str = typer.Argument(
        ...,
        help=(
            "JSON payload for the wallet creation request. "
            'Example: \'{"name": "my-wallet", "co_id": "co-1"}\''
        ),
    ),
) -> None:
    """Create a new wallet.

    PAYLOAD must be a JSON string with the required fields.
    """
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON payload: {exc}", err=True)
        raise typer.Exit(1) from exc

    with get_client() as client:
        data = wallets_api.create_wallet(client, body)
    print_json(data)


@app.command("update")
def update_wallet(
    wallet_id: str = typer.Argument(..., help="Wallet ID."),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="New wallet name."
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="New wallet description."
    ),
) -> None:
    """Partially update a wallet (name and/or description)."""
    body: dict[str, str] = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description

    if not body:
        typer.echo("Provide at least --name or --description.", err=True)
        raise typer.Exit(1)

    with get_client() as client:
        data = wallets_api.update_wallet(client, wallet_id, body)
    print_json(data)


@app.command("delete")
def delete_wallet(
    wallet_id: str = typer.Argument(..., help="Wallet ID."),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt."
    ),
) -> None:
    """Delete a wallet by ID."""
    if not confirm:
        typer.confirm(f"Delete wallet {wallet_id}?", abort=True)
    with get_client() as client:
        wallets_api.delete_wallet(client, wallet_id)
    typer.echo(f"Wallet {wallet_id} deleted.")

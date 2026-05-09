"""Wallet commands for the surf CLI.

Exposes CRUD operations on SURF Research Cloud wallets via the /wallets/
API endpoints. Wallets represent budget allocations used to pay for
workspace and storage resources.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

from surf_cli.client import SurfClient

app = typer.Typer(help="Manage SURF Research Cloud wallets.")


def _get_client() -> SurfClient:
    try:
        return SurfClient()
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _print_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2))


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
) -> None:
    """List wallets accessible to the authenticated user."""
    with _get_client() as client:
        data = client.get("/wallets/", co_id=co_id, limit=limit, name=name, offset=offset)
    _print_json(data)


@app.command("get")
def get_wallet(
    wallet_id: str = typer.Argument(..., help="Wallet ID."),
) -> None:
    """Retrieve a wallet by ID."""
    with _get_client() as client:
        data = client.get(f"/wallets/{wallet_id}/")
    _print_json(data)


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

    with _get_client() as client:
        data = client.post("/wallets/", json=body)
    _print_json(data)


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

    with _get_client() as client:
        data = client.patch(f"/wallets/{wallet_id}/", json=body)
    _print_json(data)


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
    with _get_client() as client:
        client.delete(f"/wallets/{wallet_id}/")
    typer.echo(f"Wallet {wallet_id} deleted.")

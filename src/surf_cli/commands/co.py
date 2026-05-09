"""Collaborative Organisation (CO) commands for the surf CLI.

Exposes CRUD and member management operations on SURF Research Cloud
collaborative organisations via the /co/ API endpoints.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

from surf_cli.client import SurfClient

app = typer.Typer(help="Manage SURF Research Cloud collaborative organisations.")


def _get_client() -> SurfClient:
    try:
        return SurfClient()
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _print_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2))


@app.command("list")
def list_cos(
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Search by collaborative organisation name."
    ),
    offset: Optional[int] = typer.Option(
        None, "--offset", help="Offset for pagination."
    ),
) -> None:
    """List collaborative organisations accessible to the authenticated user."""
    with _get_client() as client:
        data = client.get("/co/", limit=limit, name=name, offset=offset)
    _print_json(data)


@app.command("get")
def get_co(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
) -> None:
    """Retrieve a collaborative organisation by ID."""
    with _get_client() as client:
        data = client.get(f"/co/{co_id}/")
    _print_json(data)


@app.command("create")
def create_co(
    payload: str = typer.Argument(
        ...,
        help=(
            "JSON payload for the CO creation request. "
            'Example: \'{"name": "my-co", "description": "My CO"}\''
        ),
    ),
) -> None:
    """Create a new collaborative organisation.

    PAYLOAD must be a JSON string with the required fields.
    """
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON payload: {exc}", err=True)
        raise typer.Exit(1) from exc

    with _get_client() as client:
        data = client.post("/co/", json=body)
    _print_json(data)


@app.command("update")
def update_co(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="New name for the collaborative organisation."
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="New description."
    ),
) -> None:
    """Partially update a collaborative organisation."""
    body: dict[str, str] = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description

    if not body:
        typer.echo("Provide at least --name or --description.", err=True)
        raise typer.Exit(1)

    with _get_client() as client:
        data = client.patch(f"/co/{co_id}/", json=body)
    _print_json(data)


@app.command("delete")
def delete_co(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt."
    ),
) -> None:
    """Delete a collaborative organisation by ID."""
    if not confirm:
        typer.confirm(f"Delete collaborative organisation {co_id}?", abort=True)
    with _get_client() as client:
        client.delete(f"/co/{co_id}/")
    typer.echo(f"Collaborative organisation {co_id} deleted.")


@app.command("members")
def list_members(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    offset: Optional[int] = typer.Option(
        None, "--offset", help="Offset for pagination."
    ),
) -> None:
    """List members of a collaborative organisation."""
    with _get_client() as client:
        data = client.get(f"/co/{co_id}/members/", limit=limit, offset=offset)
    _print_json(data)


@app.command("add-member")
def add_member(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    user_id: str = typer.Option(..., "--user-id", "-u", help="User ID to add."),
    role: Optional[str] = typer.Option(
        None,
        "--role",
        "-r",
        help="Role to assign. Options: member, admin.",
    ),
) -> None:
    """Add a member to a collaborative organisation."""
    body: dict[str, str] = {"user_id": user_id}
    if role is not None:
        body["role"] = role

    with _get_client() as client:
        data = client.post(f"/co/{co_id}/members/", json=body)
    _print_json(data)


@app.command("remove-member")
def remove_member(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    user_id: str = typer.Argument(..., help="User ID to remove."),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt."
    ),
) -> None:
    """Remove a member from a collaborative organisation."""
    if not confirm:
        typer.confirm(
            f"Remove user {user_id} from collaborative organisation {co_id}?",
            abort=True,
        )
    with _get_client() as client:
        client.delete(f"/co/{co_id}/members/{user_id}/")
    typer.echo(f"User {user_id} removed from collaborative organisation {co_id}.")

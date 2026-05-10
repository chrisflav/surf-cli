"""Collaborative Organisation (CO) commands for the surf CLI.

Exposes CRUD and member management operations on SURF Research Cloud
collaborative organisations via the /co/ API endpoints.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

import surf_cli.api.co as co_api
from surf_cli.formatting import OutputFormat, get_client, print_json, print_output

app = typer.Typer(help="Manage SURF Research Cloud collaborative organisations.")


@app.command("list")
def list_cos(
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Search by collaborative organisation name."
    ),
    offset: Optional[int] = typer.Option(None, "--offset", help="Offset for pagination."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """List collaborative organisations accessible to the authenticated user."""
    if limit is not None and limit <= 0:
        typer.echo("--limit must be a positive integer.", err=True)
        raise typer.Exit(1)
    if offset is not None and offset < 0:
        typer.echo("--offset must be a non-negative integer.", err=True)
        raise typer.Exit(1)
    with get_client() as client:
        data = co_api.list_cos(client, limit=limit, name=name, offset=offset)
    print_output(data, fmt)


@app.command("get")
def get_co(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """Retrieve a collaborative organisation by ID."""
    with get_client() as client:
        data = co_api.get_co(client, co_id)
    print_output(data, fmt)


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

    with get_client() as client:
        data = co_api.create_co(client, body)
    print_json(data)


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

    with get_client() as client:
        data = co_api.update_co(client, co_id, body)
    print_json(data)


@app.command("delete")
def delete_co(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Delete a collaborative organisation by ID."""
    if not confirm:
        typer.confirm(f"Delete collaborative organisation {co_id}?", abort=True)
    with get_client() as client:
        co_api.delete_co(client, co_id)
    typer.echo(f"Collaborative organisation {co_id} deleted.")


@app.command("members")
def list_members(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
    offset: Optional[int] = typer.Option(None, "--offset", help="Offset for pagination."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
) -> None:
    """List members of a collaborative organisation."""
    if limit is not None and limit <= 0:
        typer.echo("--limit must be a positive integer.", err=True)
        raise typer.Exit(1)
    if offset is not None and offset < 0:
        typer.echo("--offset must be a non-negative integer.", err=True)
        raise typer.Exit(1)
    with get_client() as client:
        data = co_api.list_members(client, co_id, limit=limit, offset=offset)
    print_output(data, fmt)


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

    with get_client() as client:
        data = co_api.add_member(client, co_id, body)
    print_json(data)


@app.command("remove-member")
def remove_member(
    co_id: str = typer.Argument(..., help="Collaborative organisation ID."),
    user_id: str = typer.Argument(..., help="User ID to remove."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Remove a member from a collaborative organisation."""
    if not confirm:
        typer.confirm(
            f"Remove user {user_id} from collaborative organisation {co_id}?",
            abort=True,
        )
    with get_client() as client:
        co_api.remove_member(client, co_id, user_id)
    typer.echo(f"User {user_id} removed from collaborative organisation {co_id}.")

"""Workspace commands for the surf CLI.

Exposes CRUD and action operations on SURF Research Cloud workspaces via the
/workspaces/ API endpoints.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

from surf_cli.client import SurfClient

app = typer.Typer(help="Manage SURF Research Cloud workspaces.")


def _get_client() -> SurfClient:
    try:
        return SurfClient()
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _print_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2))


@app.command("list")
def list_workspaces(
    application_type: Optional[str] = typer.Option(
        None,
        "--application-type",
        "-t",
        help="Filter by type. Options: Compute, Storage, IP, Network.",
    ),
    by_owner: Optional[str] = typer.Option(
        None,
        "--by-owner",
        help="If 'true', return only workspaces owned by the authenticated user.",
    ),
    co_id: Optional[str] = typer.Option(None, "--co-id", help="Filter by collaborative organisation ID."),
    deleted: Optional[str] = typer.Option(None, "--deleted", help="Include deleted workspaces. Options: true, false."),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of results to return."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Search by workspace name."),
    offset: Optional[int] = typer.Option(None, "--offset", help="Offset for pagination."),
    status: Optional[str] = typer.Option(
        None,
        "--status",
        "-s",
        help=(
            "Filter by status. Options: creating, pausing, paused, resuming, running, "
            "failed, deleted, deleting, unknown, available, in-use, full, updating, "
            "unhealthy, rebooting, unaccounted."
        ),
    ),
    wallet_id: Optional[str] = typer.Option(None, "--wallet-id", "-w", help="Filter by wallet ID."),
) -> None:
    """List workspaces accessible to the authenticated user."""
    with _get_client() as client:
        data = client.get(
            "/workspaces/",
            application_type=application_type,
            by_owner=by_owner,
            co_id=co_id,
            deleted=deleted,
            limit=limit,
            name=name,
            offset=offset,
            status=status,
            wallet_id=wallet_id,
        )
    _print_json(data)


@app.command("get")
def get_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
) -> None:
    """Retrieve a workspace by ID."""
    with _get_client() as client:
        data = client.get(f"/workspaces/{workspace_id}/")
    _print_json(data)


@app.command("create")
def create_workspace(
    payload: str = typer.Argument(..., help="JSON payload for the workspace creation request."),
    application_type: str = typer.Option(
        "Compute",
        "--application-type",
        "-t",
        help="Content type variant to send. Options: Compute, Storage, IP, Network.",
    ),
) -> None:
    """Create a new workspace.

    PAYLOAD must be a JSON string matching the CreateComputeApplicationSchema (for Compute)
    or CreateApplicationSchema (for Storage, IP, Network).

    Example (Compute):
        surf workspace create '{...}' --application-type Compute
    """
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON payload: {exc}", err=True)
        raise typer.Exit(1) from exc

    with _get_client() as client:
        client._http.headers["Content-Type"] = f"application/json;{application_type}"
        data = client.post("/workspaces/", json=body)
    _print_json(data)


@app.command("update")
def update_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New workspace name."),
    end_time: Optional[str] = typer.Option(
        None,
        "--end-time",
        help="New end time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).",
    ),
) -> None:
    """Partially update a workspace (name and/or end_time)."""
    body: dict[str, str] = {}
    if name is not None:
        body["name"] = name
    if end_time is not None:
        body["end_time"] = end_time

    if not body:
        typer.echo("Provide at least --name or --end-time.", err=True)
        raise typer.Exit(1)

    with _get_client() as client:
        data = client.patch(f"/workspaces/{workspace_id}/", json=body)
    _print_json(data)


@app.command("delete")
def delete_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Delete a workspace by ID."""
    if not confirm:
        typer.confirm(f"Delete workspace {workspace_id}?", abort=True)
    with _get_client() as client:
        client.delete(f"/workspaces/{workspace_id}/")
    typer.echo(f"Workspace {workspace_id} deleted.")


@app.command("action")
def workspace_action(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    action_type: str = typer.Argument(
        ...,
        help="Action to perform. Options: pause, resume, reboot, update_nsgs, update_storages.",
    ),
    params: Optional[str] = typer.Option(
        None,
        "--params",
        "-p",
        help=(
            "JSON body for the action. Required for update_nsgs "
            '(e.g. \'{"network_security_group_rules": ["in tcp 22 22 0.0.0.0/0"]}\') '
            'and update_storages (e.g. \'{"storages": [{"id": "..."}]}\').'
        ),
    ),
) -> None:
    """Trigger a single action on a workspace."""
    body: object = {}
    if params is not None:
        try:
            body = json.loads(params)
        except json.JSONDecodeError as exc:
            typer.echo(f"Invalid JSON params: {exc}", err=True)
            raise typer.Exit(1) from exc

    with _get_client() as client:
        data = client.post(
            f"/workspaces/{workspace_id}/actions/{action_type}/",
            json=body,
        )
    _print_json(data)


@app.command("actions")
def workspace_actions(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    payload: str = typer.Argument(
        ...,
        help=(
            "JSON array of action objects, each with 'action' and optional 'parameters'. "
            'Example: \'[{"action": "pause"}, {"action": "resume"}]\''
        ),
    ),
) -> None:
    """Trigger a sequence of actions on a workspace (executed in order)."""
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON payload: {exc}", err=True)
        raise typer.Exit(1) from exc

    if not isinstance(body, list):
        typer.echo("Payload must be a JSON array of action objects.", err=True)
        raise typer.Exit(1)

    with _get_client() as client:
        data = client.post(f"/workspaces/{workspace_id}/actions/", json=body)
    _print_json(data)


@app.command("change-wallet")
def change_wallet(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    wallet_id: str = typer.Option(..., "--wallet-id", "-w", help="New wallet ID."),
    wallet_name: Optional[str] = typer.Option(None, "--wallet-name", help="New wallet name."),
) -> None:
    """Change the wallet associated with a workspace."""
    body: dict[str, str] = {"wallet_id": wallet_id}
    if wallet_name is not None:
        body["wallet_name"] = wallet_name

    with _get_client() as client:
        data = client.patch(f"/workspaces/{workspace_id}/change_wallet/", json=body)
    _print_json(data)


@app.command("claim-ownership")
def claim_ownership(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
) -> None:
    """Claim ownership of a workspace (WS admin only)."""
    with _get_client() as client:
        data = client.patch(f"/workspaces/{workspace_id}/claim_ownership/", json={})
    _print_json(data)


@app.command("logs")
def get_logs(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
) -> None:
    """Retrieve the logs for a workspace."""
    with _get_client() as client:
        response = client._http.get(f"/workspaces/{workspace_id}/logs/")
        response.raise_for_status()
        typer.echo(response.text)

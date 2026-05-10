"""Workspace commands for the surf CLI.

Exposes CRUD and action operations on SURF Research Cloud workspaces via the
/workspaces/ API endpoints.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Optional, Union

import typer

import surf_cli.api.workspaces as ws_api
from surf_cli.formatting import (
    OutputFormat,
    get_client,
    print_json,
    print_output,
    _to_serializable,
)
from surf_cli.models import (
    ActionRequestNsgsSchema,
    ActionRequestStorageSchema,
    AnyWorkspace,
    PaginatedComputeWorkspaceList,
    PaginatedIpWorkspaceList,
    PaginatedNetworkWorkspaceList,
    PaginatedStorageWorkspaceList,
    PatchedWorkspaceChangeWalletRequest,
    PatchedWorkspaceUpdate,
    WorkspaceActionsRequest,
)

app = typer.Typer(help="Manage SURF Research Cloud workspaces.")

_PAGINATED_TYPES = (
    PaginatedComputeWorkspaceList,
    PaginatedStorageWorkspaceList,
    PaginatedIpWorkspaceList,
    PaginatedNetworkWorkspaceList,
)


def _watch_loop(
    fetch: Callable[[], Any],
    interval: int,
    until_status: Optional[str],
    fmt: OutputFormat,
) -> None:
    """Poll *fetch* every *interval* seconds, printing results each iteration.

    Stops when the user interrupts (Ctrl-C) or when the response status field
    matches *until_status* (if provided).
    """
    try:
        while True:
            timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            typer.echo(f"--- {timestamp} ---", err=True)
            data = fetch()
            print_output(data, fmt)

            if until_status:
                reached = False
                if isinstance(data, _PAGINATED_TYPES):
                    reached = any(item.status == until_status for item in data.results)
                elif hasattr(data, "status"):
                    reached = data.status == until_status
                if reached:
                    break

            time.sleep(interval)
    except KeyboardInterrupt:
        pass


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
    co_id: Optional[str] = typer.Option(
        None, "--co-id", help="Filter by collaborative organisation ID."
    ),
    deleted: Optional[str] = typer.Option(
        None, "--deleted", help="Include deleted workspaces. Options: true, false."
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of results to return."
    ),
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
    wallet_id: Optional[str] = typer.Option(
        None, "--wallet-id", "-w", help="Filter by wallet ID."
    ),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
    watch: bool = typer.Option(False, "--watch", help="Poll for updates at a regular interval."),
    interval: int = typer.Option(
        5, "--interval", help="Polling interval in seconds (used with --watch)."
    ),
    until_status: Optional[str] = typer.Option(
        None,
        "--until-status",
        help="Stop polling when any workspace matches this status (used with --watch).",
    ),
) -> None:
    """List workspaces accessible to the authenticated user."""
    if limit is not None and limit <= 0:
        typer.echo("--limit must be a positive integer.", err=True)
        raise typer.Exit(1)
    if offset is not None and offset < 0:
        typer.echo("--offset must be a non-negative integer.", err=True)
        raise typer.Exit(1)

    def _fetch() -> Any:
        with get_client() as client:
            return ws_api.list_workspaces(
                client,
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

    _LIST_TABLE_COLUMNS = ("id", "name", "description", "status", "time_created", "time_deleted")

    def _for_display(data: Any) -> Any:
        if fmt != OutputFormat.table:
            return data
        raw = _to_serializable(data)
        if isinstance(raw, dict) and "results" in raw:
            raw = dict(raw)
            raw["results"] = [
                {k: row.get(k) for k in _LIST_TABLE_COLUMNS} for row in raw["results"]
            ]
        return raw

    if watch:
        _watch_loop(lambda: _for_display(_fetch()), interval, until_status, fmt)
    else:
        print_output(_for_display(_fetch()), fmt)


@app.command("get")
def get_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    fmt: OutputFormat = typer.Option(
        OutputFormat.json, "--format", "-f", help="Output format. Options: json, table, csv."
    ),
    watch: bool = typer.Option(
        False, "--watch", "-W", help="Poll for updates at a regular interval."
    ),
    interval: int = typer.Option(
        5, "--interval", help="Polling interval in seconds (used with --watch)."
    ),
    until_status: Optional[str] = typer.Option(
        None,
        "--until-status",
        help="Stop polling when the workspace reaches this status (used with --watch).",
    ),
) -> None:
    """Retrieve a workspace by ID."""

    def _fetch() -> Any:
        with get_client() as client:
            return ws_api.get_workspace(client, workspace_id)

    if watch:
        _watch_loop(_fetch, interval, until_status, fmt)
    else:
        print_output(_fetch(), fmt)


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

    with get_client() as client:
        result = ws_api.create_workspace(client, body, application_type)
    print_json(result)


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
    if name is None and end_time is None:
        typer.echo("Provide at least --name or --end-time.", err=True)
        raise typer.Exit(1)

    update = PatchedWorkspaceUpdate(name=name, end_time=end_time)

    with get_client() as client:
        result = ws_api.update_workspace(client, workspace_id, update)
    print_json(result)


@app.command("delete")
def delete_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Delete a workspace by ID."""
    if not confirm:
        typer.confirm(f"Delete workspace {workspace_id}?", abort=True)
    with get_client() as client:
        ws_api.delete_workspace(client, workspace_id)
    typer.echo(f"Workspace {workspace_id} deleted.")


_VALID_ACTION_TYPES = {"pause", "resume", "reboot", "update_nsgs", "update_storages"}


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
    if action_type not in _VALID_ACTION_TYPES:
        valid = ", ".join(sorted(_VALID_ACTION_TYPES))
        typer.echo(f"Invalid action_type '{action_type}'. Options: {valid}.", err=True)
        raise typer.Exit(1)

    request: Optional[Union[ActionRequestNsgsSchema, ActionRequestStorageSchema]] = None
    if params is not None:
        try:
            params_body = json.loads(params)
        except json.JSONDecodeError as exc:
            typer.echo(f"Invalid JSON params: {exc}", err=True)
            raise typer.Exit(1) from exc

        if action_type == "update_nsgs":
            request = ActionRequestNsgsSchema.model_validate(params_body)
        elif action_type == "update_storages":
            request = ActionRequestStorageSchema.model_validate(params_body)

    with get_client() as client:
        result = ws_api.workspace_action(client, workspace_id, action_type, request)
    print_json(result)


_VALID_ACTIONS = {
    "create",
    "delete",
    "pause",
    "purge",
    "reboot",
    "release",
    "resume",
    "update",
    "update_nsgs",
    "update_storages",
    "use",
}


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

    for item in body:
        if not isinstance(item, dict) or "action" not in item:
            typer.echo("Each action object must have an 'action' field.", err=True)
            raise typer.Exit(1)
        action_val = item["action"]
        if action_val not in _VALID_ACTIONS:
            valid = ", ".join(sorted(_VALID_ACTIONS))
            typer.echo(f"Invalid action '{action_val}'. Options: {valid}.", err=True)
            raise typer.Exit(1)

    actions = [WorkspaceActionsRequest.model_validate(item) for item in body]

    with get_client() as client:
        result = ws_api.workspace_actions(client, workspace_id, actions)
    print_json(result)


@app.command("change-wallet")
def change_wallet(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    wallet_id: str = typer.Option(..., "--wallet-id", "-w", help="New wallet ID."),
    wallet_name: Optional[str] = typer.Option(None, "--wallet-name", help="New wallet name."),
) -> None:
    """Change the wallet associated with a workspace."""
    request = PatchedWorkspaceChangeWalletRequest(wallet_id=wallet_id, wallet_name=wallet_name)
    with get_client() as client:
        result = ws_api.change_wallet(client, workspace_id, request)
    print_json(result)


@app.command("claim-ownership")
def claim_ownership(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
) -> None:
    """Claim ownership of a workspace (WS admin only)."""
    with get_client() as client:
        result = ws_api.claim_ownership(client, workspace_id)
    print_json(result)


@app.command("logs")
def get_logs(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
) -> None:
    """Retrieve the logs for a workspace."""
    with get_client() as client:
        text = ws_api.get_workspace_logs(client, workspace_id)
    typer.echo(text)


def _ssh_config_entry(
    workspace: AnyWorkspace,
    user: Optional[str],
    identity_file: Optional[str],
    port: int,
) -> Optional[str]:
    """Return an SSH config block for *workspace*, or None if no hostname is available."""
    resource_meta = workspace.resource_meta
    meta = workspace.meta

    hostname = None
    if resource_meta is not None:
        hostname = getattr(resource_meta, "ip", None) or getattr(
            resource_meta, "workspace_fqdn", None
        )
    if not hostname and meta is not None:
        hostname = getattr(meta, "workspace_fqdn", None)

    if not hostname:
        return None

    ws_name = workspace.name or workspace.id
    host_alias = "".join(c if c.isalnum() or c in "-_." else "-" for c in str(ws_name))

    effective_user = user
    if not effective_user and resource_meta is not None:
        effective_user = getattr(resource_meta, "instance_user", None)

    lines = [f"Host {host_alias}"]
    lines.append(f"    HostName {hostname}")
    if effective_user:
        lines.append(f"    User {effective_user}")
    lines.append(f"    Port {port}")
    if identity_file:
        lines.append(f"    IdentityFile {identity_file}")
    lines.append(f"    # Workspace ID: {workspace.id}")
    return "\n".join(lines)


@app.command("ssh-config")
def workspace_ssh_config(
    workspace_id: Optional[str] = typer.Argument(
        None,
        help="Workspace ID. If omitted, generate entries for all accessible workspaces.",
    ),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="SSH username to use."),
    identity_file: Optional[str] = typer.Option(
        None, "--identity-file", "-i", help="Path to SSH private key file."
    ),
    port: int = typer.Option(22, "--port", "-p", help="Default SSH port."),
    status_filter: Optional[str] = typer.Option(
        "running",
        "--status",
        "-s",
        help="Only include workspaces with this status. Pass empty string to include all.",
    ),
) -> None:
    """Generate SSH config entries for workspace(s).

    Outputs blocks ready to be appended to ~/.ssh/config. Workspaces without
    a reachable IP address in their metadata are silently skipped.

    Example usage:
        surf workspace ssh-config >> ~/.ssh/config
        surf workspace ssh-config ws-123
    """
    entries: list[str] = []

    with get_client() as client:
        if workspace_id:
            workspace = ws_api.get_workspace(client, workspace_id)
            entry = _ssh_config_entry(workspace, user, identity_file, port)
            if entry:
                entries.append(entry)
            else:
                typer.echo(
                    f"Workspace {workspace_id} has no IP address in its metadata.", err=True
                )
                raise typer.Exit(1)
        else:
            paginated = ws_api.list_workspaces(
                client, status=status_filter if status_filter else None
            )
            for ws in paginated.results:
                entry = _ssh_config_entry(ws, user, identity_file, port)
                if entry:
                    entries.append(entry)

    if not entries:
        typer.echo("No workspaces with SSH connectivity information found.", err=True)
        return

    typer.echo("\n\n".join(entries))

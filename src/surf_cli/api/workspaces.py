"""API functions for workspace operations."""

from __future__ import annotations

from typing import Any, Optional, Union

from surf_cli.client import SurfClient
from surf_cli.models import (
    ActionRequestNsgsSchema,
    ActionRequestStorageSchema,
    AnyWorkspace,
    ComputeWorkspace,
    CreateApplicationSchema,
    CreateComputeApplicationSchema,
    IpWorkspace,
    NetworkWorkspace,
    PaginatedComputeWorkspaceList,
    PaginatedIpWorkspaceList,
    PaginatedNetworkWorkspaceList,
    PaginatedStorageWorkspaceList,
    PatchedWorkspaceChangeWalletRequest,
    PatchedWorkspaceUpdate,
    StorageWorkspace,
    WorkspaceActionsRequest,
)

_PAGINATED_TYPES = (
    PaginatedComputeWorkspaceList,
    PaginatedStorageWorkspaceList,
    PaginatedIpWorkspaceList,
    PaginatedNetworkWorkspaceList,
)

_APP_TYPE_TO_WORKSPACE = {
    "Compute": ComputeWorkspace,
    "Storage": StorageWorkspace,
    "IP": IpWorkspace,
    "Network": NetworkWorkspace,
}

_APP_TYPE_TO_PAGINATED = {
    "Compute": PaginatedComputeWorkspaceList,
    "Storage": PaginatedStorageWorkspaceList,
    "IP": PaginatedIpWorkspaceList,
    "Network": PaginatedNetworkWorkspaceList,
}


def _detect_app_type(data: dict[str, Any]) -> str:
    meta = data.get("meta")
    if isinstance(meta, dict):
        app_type = meta.get("application_type")
        if app_type in _APP_TYPE_TO_WORKSPACE:
            return app_type
    return "Compute"


def _parse_workspace(data: dict[str, Any]) -> AnyWorkspace:
    app_type = _detect_app_type(data)
    model_cls = _APP_TYPE_TO_WORKSPACE[app_type]
    return model_cls.model_validate(data)


def _parse_paginated_workspaces(
    data: dict[str, Any],
) -> Union[
    PaginatedComputeWorkspaceList,
    PaginatedStorageWorkspaceList,
    PaginatedIpWorkspaceList,
    PaginatedNetworkWorkspaceList,
]:
    results = data.get("results", [])
    app_type = "Compute"
    if results and isinstance(results[0], dict):
        app_type = _detect_app_type(results[0])
    model_cls = _APP_TYPE_TO_PAGINATED[app_type]
    return model_cls.model_validate(data)


def list_workspaces(
    client: SurfClient,
    application_type: Optional[str] = None,
    by_owner: Optional[str] = None,
    co_id: Optional[str] = None,
    deleted: Optional[str] = None,
    limit: Optional[int] = None,
    name: Optional[str] = None,
    offset: Optional[int] = None,
    status: Optional[str] = None,
    wallet_id: Optional[str] = None,
) -> Union[
    PaginatedComputeWorkspaceList,
    PaginatedStorageWorkspaceList,
    PaginatedIpWorkspaceList,
    PaginatedNetworkWorkspaceList,
]:
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
    return _parse_paginated_workspaces(data)


def get_workspace(client: SurfClient, workspace_id: str) -> AnyWorkspace:
    data = client.get(f"/workspaces/{workspace_id}/")
    return _parse_workspace(data)


def create_workspace(
    client: SurfClient,
    payload: Union[CreateComputeApplicationSchema, CreateApplicationSchema, dict],
    application_type: str = "Compute",
) -> AnyWorkspace:
    if isinstance(payload, (CreateComputeApplicationSchema, CreateApplicationSchema)):
        body = payload.model_dump(exclude_none=True)
    else:
        body = payload
    data = client.post(
        "/workspaces/",
        json=body,
        content_type=f"application/json;{application_type}",
    )
    return _parse_workspace(data)


def update_workspace(
    client: SurfClient,
    workspace_id: str,
    update: PatchedWorkspaceUpdate,
) -> AnyWorkspace:
    data = client.patch(
        f"/workspaces/{workspace_id}/",
        json=update.model_dump(exclude_none=True),
    )
    return _parse_workspace(data)


def delete_workspace(client: SurfClient, workspace_id: str) -> None:
    client.delete(f"/workspaces/{workspace_id}/")


def workspace_action(
    client: SurfClient,
    workspace_id: str,
    action_type: str,
    params: Optional[Union[ActionRequestNsgsSchema, ActionRequestStorageSchema]] = None,
) -> AnyWorkspace:
    body: Any = {}
    if params is not None:
        body = params.model_dump(exclude_none=True)
    data = client.post(
        f"/workspaces/{workspace_id}/actions/{action_type}/",
        json=body,
        content_type=f"application/json;{action_type}",
    )
    return _parse_workspace(data)


def workspace_actions(
    client: SurfClient,
    workspace_id: str,
    actions: list[WorkspaceActionsRequest],
) -> AnyWorkspace:
    body = [a.model_dump(exclude_none=True) for a in actions]
    data = client.post(f"/workspaces/{workspace_id}/actions/", json=body)
    return _parse_workspace(data)


def change_wallet(
    client: SurfClient,
    workspace_id: str,
    request: PatchedWorkspaceChangeWalletRequest,
) -> AnyWorkspace:
    data = client.patch(
        f"/workspaces/{workspace_id}/change_wallet/",
        json=request.model_dump(exclude_none=True),
    )
    return _parse_workspace(data)


def claim_ownership(client: SurfClient, workspace_id: str) -> AnyWorkspace:
    data = client.patch(f"/workspaces/{workspace_id}/claim_ownership/", json={})
    return _parse_workspace(data)


def get_workspace_logs(client: SurfClient, workspace_id: str) -> str:
    return client.get_text(f"/workspaces/{workspace_id}/logs/")

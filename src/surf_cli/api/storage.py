"""API functions for storage operations."""

from __future__ import annotations

from typing import Any, Optional

from surf_cli.client import SurfClient


def list_storage(
    client: SurfClient,
    co_id: Optional[str] = None,
    limit: Optional[int] = None,
    name: Optional[str] = None,
    offset: Optional[int] = None,
    status: Optional[str] = None,
    wallet_id: Optional[str] = None,
) -> Any:
    return client.get(
        "/storage/",
        co_id=co_id,
        limit=limit,
        name=name,
        offset=offset,
        status=status,
        wallet_id=wallet_id,
    )


def get_storage(client: SurfClient, storage_id: str) -> Any:
    return client.get(f"/storage/{storage_id}/")


def create_storage(client: SurfClient, body: dict) -> Any:
    return client.post("/storage/", json=body)


def update_storage(client: SurfClient, storage_id: str, body: dict) -> Any:
    return client.patch(f"/storage/{storage_id}/", json=body)


def delete_storage(client: SurfClient, storage_id: str) -> None:
    client.delete(f"/storage/{storage_id}/")

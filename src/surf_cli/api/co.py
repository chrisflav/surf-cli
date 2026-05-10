"""API functions for collaborative organisation operations."""

from __future__ import annotations

from typing import Any, Optional

from surf_cli.client import SurfClient


def list_cos(
    client: SurfClient,
    limit: Optional[int] = None,
    name: Optional[str] = None,
    offset: Optional[int] = None,
) -> Any:
    return client.get("/co/", limit=limit, name=name, offset=offset)


def get_co(client: SurfClient, co_id: str) -> Any:
    return client.get(f"/co/{co_id}/")


def create_co(client: SurfClient, body: dict) -> Any:
    return client.post("/co/", json=body)


def update_co(client: SurfClient, co_id: str, body: dict) -> Any:
    return client.patch(f"/co/{co_id}/", json=body)


def delete_co(client: SurfClient, co_id: str) -> None:
    client.delete(f"/co/{co_id}/")


def list_members(
    client: SurfClient,
    co_id: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Any:
    return client.get(f"/co/{co_id}/members/", limit=limit, offset=offset)


def add_member(client: SurfClient, co_id: str, body: dict) -> Any:
    return client.post(f"/co/{co_id}/members/", json=body)


def remove_member(client: SurfClient, co_id: str, user_id: str) -> None:
    client.delete(f"/co/{co_id}/members/{user_id}/")

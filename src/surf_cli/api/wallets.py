"""API functions for wallet operations."""

from __future__ import annotations

from typing import Any, Optional

from surf_cli.client import SurfClient


def list_wallets(
    client: SurfClient,
    co_id: Optional[str] = None,
    limit: Optional[int] = None,
    name: Optional[str] = None,
    offset: Optional[int] = None,
) -> Any:
    return client.get("/wallets/", co_id=co_id, limit=limit, name=name, offset=offset)


def get_wallet(client: SurfClient, wallet_id: str) -> Any:
    return client.get(f"/wallets/{wallet_id}/")


def create_wallet(client: SurfClient, body: dict) -> Any:
    return client.post("/wallets/", json=body)


def update_wallet(client: SurfClient, wallet_id: str, body: dict) -> Any:
    return client.patch(f"/wallets/{wallet_id}/", json=body)


def delete_wallet(client: SurfClient, wallet_id: str) -> None:
    client.delete(f"/wallets/{wallet_id}/")

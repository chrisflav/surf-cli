"""API functions for catalog operations."""

from __future__ import annotations

from typing import Any, Optional

from surf_cli.client import SurfClient


def list_catalog(
    client: SurfClient,
    co_id: Optional[str] = None,
    limit: Optional[int] = None,
    name: Optional[str] = None,
    offset: Optional[int] = None,
    type_: Optional[str] = None,
) -> Any:
    return client.get(
        "/catalog/",
        co_id=co_id,
        limit=limit,
        name=name,
        offset=offset,
        type=type_,
    )


def get_catalog_item(client: SurfClient, item_id: str) -> Any:
    return client.get(f"/catalog/{item_id}/")

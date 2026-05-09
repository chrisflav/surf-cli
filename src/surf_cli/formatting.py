"""Output formatting utilities for the surf CLI.

Provides functions and types for rendering API responses in multiple formats
(JSON, table) using the rich library.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from surf_cli.client import SurfClient

console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    """Supported output formats for CLI commands."""

    json = "json"
    table = "table"


def get_client() -> SurfClient:
    """Create a SurfClient, exiting with an error if the token is missing."""
    try:
        return SurfClient()
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def print_json(data: object) -> None:
    """Print *data* as pretty-printed JSON."""
    typer.echo(json.dumps(data, indent=2))


def _build_table(rows: list[dict[str, Any]]) -> Table:
    """Build a rich Table from a list of dicts, using shared top-level keys as columns."""
    if not rows:
        return Table()

    columns = list(rows[0].keys())
    table = Table(show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*[_cell(row.get(col)) for col in columns])

    return table


def _cell(value: Any) -> str:
    """Convert a value to a table cell string."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


def print_table(data: Any) -> None:
    """Print *data* as a rich table.

    Supports:
    - A list of dicts → one row per dict.
    - A paginated response dict with a ``results`` key containing a list of dicts.
    - A single dict → two-column key/value table.
    - Any other value → falls back to JSON output.
    """
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        console.print(_build_table(data))
        return

    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list) and all(isinstance(item, dict) for item in results):
            console.print(_build_table(results))
            return

        # Single-object key/value table.
        table = Table(show_header=True, header_style="bold")
        table.add_column("Field")
        table.add_column("Value")
        for key, value in data.items():
            table.add_row(str(key), _cell(value))
        console.print(table)
        return

    print_json(data)


def print_output(data: Any, fmt: OutputFormat) -> None:
    """Dispatch to the appropriate formatter based on *fmt*."""
    if fmt == OutputFormat.table:
        print_table(data)
    else:
        print_json(data)

"""Output formatting utilities for the surf CLI.

Provides functions and types for rendering API responses in multiple formats
(JSON, table, CSV) using the rich library.
"""

from __future__ import annotations

import csv
import json
import sys
from enum import Enum
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from surf_cli.client import SurfClient
from surf_cli.state import state

console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    """Supported output formats for CLI commands."""

    json = "json"
    table = "table"
    csv = "csv"


def get_client() -> SurfClient:
    """Create a SurfClient, exiting with an error if the token is missing."""
    try:
        return SurfClient(verbose=state.verbose)
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


_TABLE_MAX_CELL_WIDTH = 40


def _cell(value: Any, max_width: int = _TABLE_MAX_CELL_WIDTH) -> str:
    """Convert a value to a table cell string, truncating to *max_width* chars."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value)
    else:
        text = str(value)
    if len(text) > max_width:
        return text[: max_width - 1] + "…"
    return text


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


def _csv_rows(data: Any) -> tuple[list[str], list[list[str]]]:
    """Extract (headers, rows) from *data* for CSV output."""
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        if not data:
            return [], []
        headers = list(data[0].keys())
        rows = [[_cell(item.get(h)) for h in headers] for item in data]
        return headers, rows

    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list) and all(isinstance(item, dict) for item in results):
            if not results:
                return [], []
            headers = list(results[0].keys())
            rows = [[_cell(item.get(h)) for h in headers] for item in results]
            return headers, rows

        # Single object → key/value pairs.
        headers = ["field", "value"]
        rows = [[str(key), _cell(value)] for key, value in data.items()]
        return headers, rows

    return [], []


def print_csv(data: Any) -> None:
    """Print *data* as CSV.

    Supports the same inputs as :func:`print_table`; falls back to JSON for
    scalar or unrecognised values.
    """
    headers, rows = _csv_rows(data)
    if not headers and not rows:
        print_json(data)
        return

    writer = csv.writer(sys.stdout)
    writer.writerow(headers)
    writer.writerows(rows)


def print_output(data: Any, fmt: OutputFormat) -> None:
    """Dispatch to the appropriate formatter based on *fmt*."""
    if fmt == OutputFormat.table:
        print_table(data)
    elif fmt == OutputFormat.csv:
        print_csv(data)
    else:
        print_json(data)

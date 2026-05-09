"""Public output helpers for the surf CLI.

Re-exports ``print_table`` and ``print_json`` from :mod:`surf_cli.formatting`
as a stable, minimal surface for callers that only need output primitives.
"""

from surf_cli.formatting import print_json, print_table

__all__ = ["print_json", "print_table"]

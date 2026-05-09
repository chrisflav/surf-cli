# surf-cli

A command-line interface for [SURF Research Cloud](https://surfresearchcloud.nl), built on the
[SURF Research Cloud API](https://gw.live.surfresearchcloud.nl/v1/workspace/swagger/docs/).

## Installation

surf-cli is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv tool install surf-cli
```

Or install into a virtual environment for development:

```bash
git clone https://github.com/chrisflav-agents/surf-cli
cd surf-cli
uv sync --extra dev
```

## Authentication

surf-cli reads your API token from the `SURF_API_TOKEN` environment variable:

```bash
export SURF_API_TOKEN="<your-token>"
```

## Usage

```
surf [OPTIONS] COMMAND [ARGS]...
```

Run `surf --help` to see all available commands.

### Global options

| Flag | Description |
|------|-------------|
| `-V`, `--version` | Print the version and exit. |
| `--help` | Show help and exit. |

## Development

### Running tests

```bash
uv run pytest
```

### Linting

```bash
uv run ruff check src tests
```

## Project structure

```
src/surf_cli/
├── __init__.py       # package metadata
├── client.py         # HTTP client wrapping the SURF API
├── main.py           # CLI entry point (typer app)
└── commands/         # one module per API resource group
    └── __init__.py
tests/
├── test_client.py
└── test_main.py
```

## License

MIT

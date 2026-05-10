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

surf-cli looks for an API token in the following order:

1. **Environment variable** – `SURF_API_TOKEN`
2. **Configuration file** – `~/.config/surf-cli/config.toml`

### Using the environment variable

```bash
export SURF_API_TOKEN="<your-token>"
```

### Using the configuration file

Save the token once with the `config set-token` command:

```bash
surf config set-token "<your-token>"
```

The token is written to `~/.config/surf-cli/config.toml` with permissions `0600`. Verify the current configuration with:

```bash
surf config show
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
| `--install-completion` | Install shell completion for the current shell and exit. |
| `--show-completion` | Show the shell completion script for the current shell and exit. |
| `--help` | Show help and exit. |

### Shell completion

surf-cli supports tab completion for bash, zsh, and fish. To install completion for your current shell:

```bash
surf --install-completion
```

To print the completion script without installing it (useful for custom setups):

```bash
surf --show-completion
```

After installing, restart your shell or source the updated RC file to activate completions.

### Output formats

Most read commands (`list`, `get`, `members`) accept a `-f` / `--format` option that controls how results are printed:

| Value | Description |
|-------|-------------|
| `json` | Pretty-printed JSON (default). |
| `table` | Formatted table rendered with [Rich](https://github.com/Textualize/rich). |

```bash
# JSON output (default)
surf workspace list

# Table output
surf workspace list --format table
surf catalog list -f table
```

Write commands (`create`, `update`, `delete`, `action`, etc.) always output JSON.

---

## Command groups

- [workspace](#workspace) — manage workspaces
- [catalog](#catalog) — browse the catalog
- [storage](#storage) — manage storage volumes
- [co](#co) — manage collaborative organisations
- [wallet](#wallet) — manage wallets

---

## workspace

Manage SURF Research Cloud workspaces.

```
surf workspace [COMMAND]
```

### workspace list

List workspaces accessible to the authenticated user.

```bash
surf workspace list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-t`, `--application-type TEXT` | Filter by type: `Compute`, `Storage`, `IP`, or `Network`. |
| `--by-owner TEXT` | Return only workspaces owned by the authenticated user (`true`/`false`). |
| `--co-id TEXT` | Filter by collaborative organisation ID. |
| `--deleted TEXT` | Include deleted workspaces (`true`/`false`). |
| `-l`, `--limit INTEGER` | Maximum number of results to return. |
| `-n`, `--name TEXT` | Search by workspace name. |
| `--offset INTEGER` | Pagination offset. |
| `-s`, `--status TEXT` | Filter by status (e.g. `running`, `paused`, `failed`). |
| `-w`, `--wallet-id TEXT` | Filter by wallet ID. |
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### workspace get

Get details of a specific workspace.

```bash
surf workspace get WORKSPACE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### workspace create

Create a new workspace from a JSON payload.

```bash
surf workspace create PAYLOAD [OPTIONS]
```

`PAYLOAD` must be a JSON string matching `CreateComputeApplicationSchema` (for `Compute`) or
`CreateApplicationSchema` (for other types).

| Option | Description |
|--------|-------------|
| `-t`, `--application-type TEXT` | Workspace type: `Compute` (default), `Storage`, `IP`, or `Network`. |

**Example:**
```bash
surf workspace create '{"name": "my-workspace", "co_id": "co-1", "wallet_id": "wallet-1", "catalog_item": "item-1"}'
```

### workspace update

Update a workspace's name or end time.

```bash
surf workspace update WORKSPACE_ID [OPTIONS]
```

At least one option is required.

| Option | Description |
|--------|-------------|
| `-n`, `--name TEXT` | New workspace name. |
| `--end-time TEXT` | New end time in ISO 8601 format (e.g. `2024-12-31T23:59:59Z`). |

### workspace delete

Delete a workspace.

```bash
surf workspace delete WORKSPACE_ID [--yes]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip the confirmation prompt. |

### workspace action

Perform a single action on a workspace.

```bash
surf workspace action WORKSPACE_ID ACTION_TYPE [OPTIONS]
```

Supported action types: `pause`, `resume`, `reboot`, `update_nsgs`, `update_storages`.

| Option | Description |
|--------|-------------|
| `-p`, `--params TEXT` | JSON body for the action (required for `update_nsgs` and `update_storages`). |

**Examples:**
```bash
# Pause a workspace
surf workspace action ws-123 pause

# Attach a storage volume
surf workspace action ws-123 update_storages --params '{"storages": [{"id": "st-456"}]}'

# Update network security group rules
surf workspace action ws-123 update_nsgs --params '{"network_security_group_rules": ["in tcp 22 22 0.0.0.0/0"]}'
```

### workspace actions

Perform a sequence of actions on a workspace in one call.

```bash
surf workspace actions WORKSPACE_ID PAYLOAD
```

`PAYLOAD` is a JSON array of action objects, each with an `action` key and an optional `parameters` key.

**Example:**
```bash
surf workspace actions ws-123 '[{"action": "pause"}, {"action": "resume"}]'
```

### workspace change-wallet

Move a workspace to a different wallet.

```bash
surf workspace change-wallet WORKSPACE_ID --wallet-id WALLET_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-w`, `--wallet-id TEXT` | (Required) New wallet ID. |
| `--wallet-name TEXT` | New wallet name (optional). |

### workspace claim-ownership

Claim ownership of a workspace (workspace admin only).

```bash
surf workspace claim-ownership WORKSPACE_ID
```

### workspace logs

Retrieve the logs for a workspace.

```bash
surf workspace logs WORKSPACE_ID
```

---

## catalog

Browse the SURF Research Cloud catalog (read-only).

```
surf catalog [COMMAND]
```

### catalog list

List available catalog items.

```bash
surf catalog list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--co-id TEXT` | Filter by collaborative organisation ID. |
| `-l`, `--limit INTEGER` | Maximum number of results to return. |
| `-n`, `--name TEXT` | Search by catalog item name. |
| `--offset INTEGER` | Pagination offset. |
| `-t`, `--type TEXT` | Filter by type: `Compute`, `Storage`, `IP`, or `Network`. |
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### catalog get

Get details of a specific catalog item.

```bash
surf catalog get ITEM_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

---

## storage

Manage SURF Research Cloud storage volumes.

```
surf storage [COMMAND]
```

### storage list

List storage volumes.

```bash
surf storage list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--co-id TEXT` | Filter by collaborative organisation ID. |
| `-l`, `--limit INTEGER` | Maximum number of results to return. |
| `-n`, `--name TEXT` | Search by storage volume name. |
| `--offset INTEGER` | Pagination offset. |
| `-s`, `--status TEXT` | Filter by status: `creating`, `available`, `in-use`, `full`, `updating`, `deleting`, `deleted`, `failed`, or `unknown`. |
| `-w`, `--wallet-id TEXT` | Filter by wallet ID. |
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### storage get

Get details of a specific storage volume.

```bash
surf storage get STORAGE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### storage create

Create a new storage volume from a JSON payload.

```bash
surf storage create PAYLOAD
```

**Example:**
```bash
surf storage create '{"name": "my-storage", "co_id": "co-1", "wallet_id": "wallet-1"}'
```

### storage update

Update a storage volume's name or end time.

```bash
surf storage update STORAGE_ID [OPTIONS]
```

At least one option is required.

| Option | Description |
|--------|-------------|
| `-n`, `--name TEXT` | New storage volume name. |
| `--end-time TEXT` | New end time in ISO 8601 format (e.g. `2024-12-31T23:59:59Z`). |

**Examples:**
```bash
surf storage update st-456 --name "renamed-storage"
surf storage update st-456 --end-time "2025-12-31T23:59:59Z"
```

### storage delete

Delete a storage volume.

```bash
surf storage delete STORAGE_ID [--yes]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip the confirmation prompt. |

**Example:**
```bash
surf storage delete st-456 --yes
```

---

## co

Manage SURF Research Cloud collaborative organisations (COs) and their members.

```
surf co [COMMAND]
```

### co list

List collaborative organisations.

```bash
surf co list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-l`, `--limit INTEGER` | Maximum number of results to return. |
| `-n`, `--name TEXT` | Search by collaborative organisation name. |
| `--offset INTEGER` | Pagination offset. |
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### co get

Get details of a specific collaborative organisation.

```bash
surf co get CO_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### co create

Create a new collaborative organisation from a JSON payload.

```bash
surf co create PAYLOAD
```

**Example:**
```bash
surf co create '{"name": "my-co", "description": "My collaborative organisation"}'
```

### co update

Update a collaborative organisation's name or description.

```bash
surf co update CO_ID [OPTIONS]
```

At least one option is required.

| Option | Description |
|--------|-------------|
| `-n`, `--name TEXT` | New name. |
| `-d`, `--description TEXT` | New description. |

**Examples:**
```bash
surf co update co-1 --name "Renamed CO"
surf co update co-1 --description "Updated description"
```

### co delete

Delete a collaborative organisation.

```bash
surf co delete CO_ID [--yes]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip the confirmation prompt. |

**Example:**
```bash
surf co delete co-1 --yes
```

### co members

List members of a collaborative organisation.

```bash
surf co members CO_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-l`, `--limit INTEGER` | Maximum number of results to return. |
| `--offset INTEGER` | Pagination offset. |
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

**Example:**
```bash
surf co members co-1 --format table
```

### co add-member

Add a user to a collaborative organisation.

```bash
surf co add-member CO_ID --user-id USER_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-u`, `--user-id TEXT` | (Required) User ID to add. |
| `-r`, `--role TEXT` | Role to assign: `member` (default) or `admin`. |

**Examples:**
```bash
surf co add-member co-1 --user-id user-42
surf co add-member co-1 --user-id user-42 --role admin
```

### co remove-member

Remove a user from a collaborative organisation.

```bash
surf co remove-member CO_ID USER_ID [--yes]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip the confirmation prompt. |

**Example:**
```bash
surf co remove-member co-1 user-42 --yes
```

---

## wallet

Manage SURF Research Cloud wallets (budget allocations).

```
surf wallet [COMMAND]
```

### wallet list

List wallets.

```bash
surf wallet list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--co-id TEXT` | Filter by collaborative organisation ID. |
| `-l`, `--limit INTEGER` | Maximum number of results to return. |
| `-n`, `--name TEXT` | Search by wallet name. |
| `--offset INTEGER` | Pagination offset. |
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### wallet get

Get details of a specific wallet.

```bash
surf wallet get WALLET_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f`, `--format TEXT` | Output format: `json` (default) or `table`. |

### wallet create

Create a new wallet from a JSON payload.

```bash
surf wallet create PAYLOAD
```

**Example:**
```bash
surf wallet create '{"name": "my-wallet", "co_id": "co-1"}'
```

### wallet update

Update a wallet's name or description.

```bash
surf wallet update WALLET_ID [OPTIONS]
```

At least one option is required.

| Option | Description |
|--------|-------------|
| `-n`, `--name TEXT` | New wallet name. |
| `-d`, `--description TEXT` | New wallet description. |

### wallet delete

Delete a wallet.

```bash
surf wallet delete WALLET_ID [--yes]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip the confirmation prompt. |

---

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
├── __init__.py           # package metadata
├── client.py             # HTTP client wrapping the SURF API
├── main.py               # CLI entry point (typer app)
└── commands/             # one module per API resource group
    ├── __init__.py
    ├── workspaces.py     # workspace commands
    ├── catalog.py        # catalog commands
    ├── storage.py        # storage commands
    ├── co.py             # collaborative organisation commands
    └── wallets.py        # wallet commands
tests/
├── conftest.py
├── test_client.py
├── test_main.py
├── test_workspaces.py
├── test_catalog.py
├── test_storage.py
├── test_co.py
└── test_wallets.py
```

## License

MIT

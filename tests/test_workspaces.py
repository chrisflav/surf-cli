"""Tests for workspace CLI commands."""

import json
from unittest.mock import patch

import httpx
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from surf_cli.client import TOKEN_ENV_VAR
from surf_cli.main import app

runner = CliRunner()


def _strip_separators(output: str) -> str:
    """Remove watch-mode separator lines (--- ... ---) from captured output."""
    return "\n".join(line for line in output.splitlines() if not line.startswith("---"))


WORKSPACE_ID = "ws-123"
BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"

SAMPLE_WORKSPACE = {
    "id": WORKSPACE_ID,
    "name": "My Workspace",
    "description": "A test workspace",
    "status": "running",
    "active": True,
    "deletable": True,
    "editable": True,
    "allowed_actions": ["pause", "resume"],
    "workspace_actions": [],
    "meta": {},
    "resource_meta": {},
    "end_time": "2025-12-31T00:00:00Z",
    "time_created": "2025-01-01T00:00:00Z",
    "time_deleted": None,
    "wallet_id": "wallet-1",
    "owner_id": "user-1",
    "co_id": "co-1",
}

PAGINATED_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [SAMPLE_WORKSPACE],
}


class TestListWorkspaces:
    def test_list_basic(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--format", "table"])
        assert result.exit_code == 0
        assert "━" in result.output

    def test_list_with_filters(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?application_type=Compute&status=running",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(
            app, ["workspace", "list", "--application-type", "Compute", "--status", "running"]
        )
        assert result.exit_code == 0

    def test_list_with_limit_offset(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?limit=10&offset=0",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--limit", "10", "--offset", "0"])
        assert result.exit_code == 0

    def test_list_invalid_limit(self) -> None:
        result = runner.invoke(app, ["workspace", "list", "--limit", "0"])
        assert result.exit_code == 1

    def test_list_negative_limit(self) -> None:
        result = runner.invoke(app, ["workspace", "list", "--limit", "-5"])
        assert result.exit_code == 1

    def test_list_negative_offset(self) -> None:
        result = runner.invoke(app, ["workspace", "list", "--offset", "-1"])
        assert result.exit_code == 1

    def test_list_by_owner(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?by_owner=true",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--by-owner", "true"])
        assert result.exit_code == 0

    def test_list_with_name_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?name=My+Workspace",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--name", "My Workspace"])
        assert result.exit_code == 0

    def test_list_with_co_id_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?co_id=co-1",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--co-id", "co-1"])
        assert result.exit_code == 0

    def test_list_with_wallet_id_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?wallet_id=wallet-1",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--wallet-id", "wallet-1"])
        assert result.exit_code == 0

    def test_list_with_deleted_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?deleted=true",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["workspace", "list", "--deleted", "true"])
        assert result.exit_code == 0

    def test_list_server_error(self, httpx_mock: HTTPXMock) -> None:
        # Register enough responses for the default retry count (3) plus the initial attempt.
        for _ in range(4):
            httpx_mock.add_response(
                url=f"{BASE_URL}/workspaces/",
                status_code=500,
                json={"detail": "Internal server error."},
            )
        result = runner.invoke(app, ["workspace", "list"])
        assert result.exit_code != 0

    def test_list_no_token(self, no_token: None) -> None:
        result = runner.invoke(app, ["workspace", "list"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestGetWorkspace:
    def test_get(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == WORKSPACE_ID

    def test_get_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == WORKSPACE_ID

    def test_get_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID, "--format", "table"])
        assert result.exit_code == 0
        assert WORKSPACE_ID in result.output

    def test_get_not_found(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            status_code=404,
        )
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID])
        assert result.exit_code != 0

    def test_get_auth_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            status_code=401,
            json={"detail": "Invalid token."},
        )
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID])
        assert result.exit_code != 0

    def test_get_no_token(self, no_token: None) -> None:
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestCreateWorkspace:
    def test_create(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/",
            method="POST",
            json=SAMPLE_WORKSPACE,
            status_code=201,
        )
        payload = json.dumps(
            {
                "co_id": "co-1",
                "wallet_id": "wallet-1",
                "name": "My Workspace",
                "description": "A test workspace",
                "end_time": "2025-12-31T00:00:00Z",
                "meta": {},
            }
        )
        result = runner.invoke(app, ["workspace", "create", payload])
        assert result.exit_code == 0

    def test_create_invalid_json(self) -> None:
        result = runner.invoke(app, ["workspace", "create", "{bad json}"])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output


class TestUpdateWorkspace:
    def test_update_name(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_WORKSPACE, "name": "New Name"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            method="PATCH",
            json=updated,
        )
        result = runner.invoke(app, ["workspace", "update", WORKSPACE_ID, "--name", "New Name"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "New Name"

    def test_update_end_time(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_WORKSPACE, "end_time": "2026-06-01T00:00:00Z"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            method="PATCH",
            json=updated,
        )
        result = runner.invoke(
            app,
            ["workspace", "update", WORKSPACE_ID, "--end-time", "2026-06-01T00:00:00Z"],
        )
        assert result.exit_code == 0

    def test_update_no_fields(self) -> None:
        result = runner.invoke(app, ["workspace", "update", WORKSPACE_ID])
        assert result.exit_code == 1
        assert "at least" in result.output


class TestDeleteWorkspace:
    def test_delete_with_confirm(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["workspace", "delete", WORKSPACE_ID, "--yes"])
        assert result.exit_code == 0
        assert WORKSPACE_ID in result.output

    def test_delete_abort(self) -> None:
        result = runner.invoke(app, ["workspace", "delete", WORKSPACE_ID], input="n\n")
        assert result.exit_code != 0


class TestWorkspaceAction:
    def test_pause(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/actions/pause/",
            method="POST",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "action", WORKSPACE_ID, "pause"])
        assert result.exit_code == 0

    def test_resume(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/actions/resume/",
            method="POST",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "action", WORKSPACE_ID, "resume"])
        assert result.exit_code == 0

    def test_reboot(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/actions/reboot/",
            method="POST",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "action", WORKSPACE_ID, "reboot"])
        assert result.exit_code == 0

    def test_update_nsgs(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/actions/update_nsgs/",
            method="POST",
            json=SAMPLE_WORKSPACE,
        )
        params = json.dumps({"network_security_group_rules": ["in tcp 22 22 0.0.0.0/0"]})
        result = runner.invoke(
            app,
            ["workspace", "action", WORKSPACE_ID, "update_nsgs", "--params", params],
        )
        assert result.exit_code == 0

    def test_update_storages(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/actions/update_storages/",
            method="POST",
            json=SAMPLE_WORKSPACE,
        )
        params = json.dumps({"storages": [{"id": "storage-1"}]})
        result = runner.invoke(
            app,
            ["workspace", "action", WORKSPACE_ID, "update_storages", "--params", params],
        )
        assert result.exit_code == 0

    def test_invalid_params_json(self) -> None:
        result = runner.invoke(
            app,
            ["workspace", "action", WORKSPACE_ID, "update_nsgs", "--params", "{bad}"],
        )
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output


class TestWorkspaceActions:
    def test_actions_sequence(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/actions/",
            method="POST",
            json=SAMPLE_WORKSPACE,
        )
        payload = json.dumps([{"action": "pause"}, {"action": "resume"}])
        result = runner.invoke(app, ["workspace", "actions", WORKSPACE_ID, payload])
        assert result.exit_code == 0

    def test_actions_invalid_json(self) -> None:
        result = runner.invoke(app, ["workspace", "actions", WORKSPACE_ID, "{bad json}"])
        assert result.exit_code == 1

    def test_actions_not_a_list(self) -> None:
        result = runner.invoke(app, ["workspace", "actions", WORKSPACE_ID, '{"action": "pause"}'])
        assert result.exit_code == 1
        assert "array" in result.output


class TestChangeWallet:
    def test_change_wallet(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_WORKSPACE, "wallet_id": "wallet-2"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/change_wallet/",
            method="PATCH",
            json=updated,
        )
        result = runner.invoke(
            app,
            ["workspace", "change-wallet", WORKSPACE_ID, "--wallet-id", "wallet-2"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["wallet_id"] == "wallet-2"

    def test_change_wallet_with_name(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/change_wallet/",
            method="PATCH",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(
            app,
            [
                "workspace",
                "change-wallet",
                WORKSPACE_ID,
                "--wallet-id",
                "wallet-2",
                "--wallet-name",
                "Budget 2026",
            ],
        )
        assert result.exit_code == 0


class TestClaimOwnership:
    def test_claim_ownership(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/claim_ownership/",
            method="PATCH",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "claim-ownership", WORKSPACE_ID])
        assert result.exit_code == 0


class TestGetLogs:
    def test_get_logs(self, httpx_mock: HTTPXMock) -> None:
        log_text = "2025-01-01 boot completed\n2025-01-02 shutdown"
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/logs/",
            text=log_text,
        )
        result = runner.invoke(app, ["workspace", "logs", WORKSPACE_ID])
        assert result.exit_code == 0
        assert "boot completed" in result.output

    def test_get_logs_not_found(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/logs/",
            status_code=404,
            json={"status": "Not Found", "message": "Logs not found"},
        )
        result = runner.invoke(app, ["workspace", "logs", WORKSPACE_ID])
        assert result.exit_code != 0


class TestWatchWorkspaceGet:
    def test_watch_exits_when_until_status_reached(self, httpx_mock: HTTPXMock) -> None:
        running_ws = {**SAMPLE_WORKSPACE, "status": "running"}
        httpx_mock.add_response(url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/", json=running_ws)
        with patch("surf_cli.commands.workspaces.time.sleep") as mock_sleep:
            result = runner.invoke(
                app,
                [
                    "workspace",
                    "get",
                    WORKSPACE_ID,
                    "--watch",
                    "--until-status",
                    "running",
                    "--interval",
                    "1",
                ],
            )
        assert result.exit_code == 0
        mock_sleep.assert_not_called()
        data = json.loads(_strip_separators(result.output))
        assert data["status"] == "running"

    def test_watch_polls_until_status_changes(self, httpx_mock: HTTPXMock) -> None:
        creating_ws = {**SAMPLE_WORKSPACE, "status": "creating"}
        running_ws = {**SAMPLE_WORKSPACE, "status": "running"}
        httpx_mock.add_response(url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/", json=creating_ws)
        httpx_mock.add_response(url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/", json=running_ws)
        with patch("surf_cli.commands.workspaces.time.sleep"):
            result = runner.invoke(
                app,
                [
                    "workspace",
                    "get",
                    WORKSPACE_ID,
                    "--watch",
                    "--until-status",
                    "running",
                    "--interval",
                    "1",
                ],
            )
        assert result.exit_code == 0
        # Output contains two pretty-printed JSON objects; parse them with a streaming decoder.
        decoder = json.JSONDecoder()
        raw = _strip_separators(result.output).strip()
        statuses = []
        idx = 0
        while idx < len(raw):
            try:
                obj, end = decoder.raw_decode(raw, idx)
                statuses.append(obj["status"])
                idx += end - idx
            except json.JSONDecodeError:
                idx += 1
        assert statuses == ["creating", "running"]

    def test_watch_keyboard_interrupt(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/", json=SAMPLE_WORKSPACE
        )

        def _raise_interrupt(seconds: int) -> None:
            raise KeyboardInterrupt

        with patch("surf_cli.commands.workspaces.time.sleep", side_effect=_raise_interrupt):
            result = runner.invoke(
                app,
                ["workspace", "get", WORKSPACE_ID, "--watch", "--interval", "1"],
            )
        assert result.exit_code == 0

    def test_watch_short_flag(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/", json=SAMPLE_WORKSPACE
        )
        with patch("surf_cli.commands.workspaces.time.sleep", side_effect=KeyboardInterrupt):
            result = runner.invoke(
                app,
                ["workspace", "get", WORKSPACE_ID, "-W", "--interval", "1"],
            )
        assert result.exit_code == 0

    def test_watch_no_token(self, no_token: None) -> None:
        result = runner.invoke(app, ["workspace", "get", WORKSPACE_ID, "--watch"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestWatchWorkspaceList:
    def test_watch_list_exits_when_until_status_reached(self, httpx_mock: HTTPXMock) -> None:
        response = {**PAGINATED_RESPONSE, "results": [{**SAMPLE_WORKSPACE, "status": "paused"}]}
        httpx_mock.add_response(url=f"{BASE_URL}/workspaces/", json=response)
        with patch("surf_cli.commands.workspaces.time.sleep") as mock_sleep:
            result = runner.invoke(
                app,
                ["workspace", "list", "--watch", "--until-status", "paused", "--interval", "1"],
            )
        assert result.exit_code == 0
        mock_sleep.assert_not_called()

    def test_watch_list_keyboard_interrupt(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/workspaces/", json=PAGINATED_RESPONSE)

        def _raise_interrupt(seconds: int) -> None:
            raise KeyboardInterrupt

        with patch("surf_cli.commands.workspaces.time.sleep", side_effect=_raise_interrupt):
            result = runner.invoke(
                app,
                ["workspace", "list", "--watch", "--interval", "1"],
            )
        assert result.exit_code == 0

    def test_watch_list_no_token(self, no_token: None) -> None:
        result = runner.invoke(app, ["workspace", "list", "--watch"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


SSH_WORKSPACE = {
    **SAMPLE_WORKSPACE,
    "name": "My SSH Workspace",
    "resource_meta": {"ip": "10.0.0.1"},
}

SSH_WORKSPACE_WITH_USER = {
    **SAMPLE_WORKSPACE,
    "name": "My SSH Workspace",
    "resource_meta": {"ip": "10.0.0.1", "instance_user": "surf"},
}


class TestSshConfig:
    def test_ssh_config_single_workspace(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SSH_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "ssh-config", WORKSPACE_ID])
        assert result.exit_code == 0
        assert "Host My-SSH-Workspace" in result.output
        assert "HostName 10.0.0.1" in result.output
        assert "Port 22" in result.output
        assert f"Workspace ID: {WORKSPACE_ID}" in result.output

    def test_ssh_config_single_workspace_with_user_option(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SSH_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "ssh-config", WORKSPACE_ID, "--user", "ubuntu"])
        assert result.exit_code == 0
        assert "User ubuntu" in result.output

    def test_ssh_config_single_workspace_user_from_meta(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SSH_WORKSPACE_WITH_USER,
        )
        result = runner.invoke(app, ["workspace", "ssh-config", WORKSPACE_ID])
        assert result.exit_code == 0
        assert "User surf" in result.output

    def test_ssh_config_single_workspace_with_identity_file(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SSH_WORKSPACE,
        )
        result = runner.invoke(
            app, ["workspace", "ssh-config", WORKSPACE_ID, "--identity-file", "~/.ssh/id_rsa"]
        )
        assert result.exit_code == 0
        assert "IdentityFile ~/.ssh/id_rsa" in result.output

    def test_ssh_config_single_workspace_custom_port(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SSH_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "ssh-config", WORKSPACE_ID, "--port", "2222"])
        assert result.exit_code == 0
        assert "Port 2222" in result.output

    def test_ssh_config_no_ip_address_exits_nonzero(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/{WORKSPACE_ID}/",
            json=SAMPLE_WORKSPACE,
        )
        result = runner.invoke(app, ["workspace", "ssh-config", WORKSPACE_ID])
        assert result.exit_code == 1

    def test_ssh_config_all_workspaces(self, httpx_mock: HTTPXMock) -> None:
        response = {"count": 1, "next": None, "previous": None, "results": [SSH_WORKSPACE]}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?status=running",
            json=response,
        )
        result = runner.invoke(app, ["workspace", "ssh-config"])
        assert result.exit_code == 0
        assert "Host My-SSH-Workspace" in result.output
        assert "HostName 10.0.0.1" in result.output

    def test_ssh_config_all_workspaces_no_status_filter(self, httpx_mock: HTTPXMock) -> None:
        response = {"count": 1, "next": None, "previous": None, "results": [SSH_WORKSPACE]}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/",
            json=response,
        )
        result = runner.invoke(app, ["workspace", "ssh-config", "--status", ""])
        assert result.exit_code == 0
        assert "Host My-SSH-Workspace" in result.output

    def test_ssh_config_all_workspaces_none_reachable(self, httpx_mock: HTTPXMock) -> None:
        response = {**PAGINATED_RESPONSE, "results": [SAMPLE_WORKSPACE]}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?status=running",
            json=response,
        )
        result = runner.invoke(app, ["workspace", "ssh-config"])
        assert result.exit_code == 0
        assert "No workspaces" in result.output

    def test_ssh_config_multiple_workspaces(self, httpx_mock: HTTPXMock) -> None:
        ws2 = {**SSH_WORKSPACE, "id": "ws-456", "name": "Second WS"}
        response = {"count": 2, "next": None, "previous": None, "results": [SSH_WORKSPACE, ws2]}
        httpx_mock.add_response(
            url=f"{BASE_URL}/workspaces/?status=running",
            json=response,
        )
        result = runner.invoke(app, ["workspace", "ssh-config"])
        assert result.exit_code == 0
        assert "My-SSH-Workspace" in result.output
        assert "Second-WS" in result.output

    def test_ssh_config_no_token(self, no_token: None) -> None:
        result = runner.invoke(app, ["workspace", "ssh-config"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output

"""Tests for storage CLI commands."""

import json

import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from surf_cli.client import TOKEN_ENV_VAR
from surf_cli.main import app

runner = CliRunner()

STORAGE_ID = "stor-789"
BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"

SAMPLE_STORAGE = {
    "id": STORAGE_ID,
    "name": "My Storage",
    "description": "A test storage volume.",
    "status": "available",
    "co_id": "co-1",
    "wallet_id": "wallet-1",
    "owner_id": "user-1",
    "time_created": "2025-01-01T00:00:00Z",
    "end_time": "2025-12-31T00:00:00Z",
}

PAGINATED_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [SAMPLE_STORAGE],
}



class TestListStorage:
    def test_list_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list", "--format", "table"])
        assert result.exit_code == 0
        assert "━" in result.output
        assert "stor-" in result.output

    def test_list_basic(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_with_name_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/?name=My+Storage",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list", "--name", "My Storage"])
        assert result.exit_code == 0

    def test_list_with_status_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/?status=available",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list", "--status", "available"])
        assert result.exit_code == 0

    def test_list_with_co_id_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/?co_id=co-1",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list", "--co-id", "co-1"])
        assert result.exit_code == 0

    def test_list_with_wallet_id_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/?wallet_id=wallet-1",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["storage", "list", "--wallet-id", "wallet-1"])
        assert result.exit_code == 0

    def test_list_with_pagination(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/?limit=5&offset=10",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(
            app, ["storage", "list", "--limit", "5", "--offset", "10"]
        )
        assert result.exit_code == 0

    def test_list_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["storage", "list"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestGetStorage:
    def test_get_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            json=SAMPLE_STORAGE,
        )
        result = runner.invoke(app, ["storage", "get", STORAGE_ID, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == STORAGE_ID

    def test_get_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            json=SAMPLE_STORAGE,
        )
        result = runner.invoke(app, ["storage", "get", STORAGE_ID, "--format", "table"])
        assert result.exit_code == 0
        assert STORAGE_ID in result.output

    def test_get(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            json=SAMPLE_STORAGE,
        )
        result = runner.invoke(app, ["storage", "get", STORAGE_ID])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == STORAGE_ID
        assert data["name"] == "My Storage"

    def test_get_not_found(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            status_code=404,
        )
        result = runner.invoke(app, ["storage", "get", STORAGE_ID])
        assert result.exit_code != 0

    def test_get_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["storage", "get", STORAGE_ID])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestCreateStorage:
    def test_create(self, httpx_mock: HTTPXMock) -> None:
        payload = {"name": "new-storage", "co_id": "co-1", "wallet_id": "wallet-1"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/",
            method="POST",
            json=SAMPLE_STORAGE,
        )
        result = runner.invoke(app, ["storage", "create", json.dumps(payload)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == STORAGE_ID

    def test_create_invalid_json(self) -> None:
        result = runner.invoke(app, ["storage", "create", "not-valid-json"])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    def test_create_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(
            app, ["storage", "create", '{"name": "x", "co_id": "co-1"}']
        )
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestUpdateStorage:
    def test_update_name(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_STORAGE, "name": "renamed-storage"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            method="PATCH",
            json=updated,
        )
        result = runner.invoke(
            app, ["storage", "update", STORAGE_ID, "--name", "renamed-storage"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "renamed-storage"

    def test_update_end_time(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_STORAGE, "end_time": "2026-06-01T00:00:00Z"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            method="PATCH",
            json=updated,
        )
        result = runner.invoke(
            app,
            ["storage", "update", STORAGE_ID, "--end-time", "2026-06-01T00:00:00Z"],
        )
        assert result.exit_code == 0

    def test_update_no_fields(self) -> None:
        result = runner.invoke(app, ["storage", "update", STORAGE_ID])
        assert result.exit_code == 1
        assert "--name" in result.output or "--end-time" in result.output

    def test_update_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(
            app, ["storage", "update", STORAGE_ID, "--name", "x"]
        )
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestDeleteStorage:
    def test_delete_with_confirm_flag(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["storage", "delete", STORAGE_ID, "--yes"])
        assert result.exit_code == 0
        assert STORAGE_ID in result.output

    def test_delete_prompt_abort(self) -> None:
        result = runner.invoke(app, ["storage", "delete", STORAGE_ID], input="n\n")
        assert result.exit_code != 0

    def test_delete_prompt_confirm(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/storage/{STORAGE_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["storage", "delete", STORAGE_ID], input="y\n")
        assert result.exit_code == 0

    def test_delete_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["storage", "delete", STORAGE_ID, "--yes"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output

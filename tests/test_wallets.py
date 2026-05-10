"""Tests for wallet CLI commands."""

import json

import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from surf_cli.client import TOKEN_ENV_VAR
from surf_cli.main import app

runner = CliRunner()

WALLET_ID = "wallet-789"
BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"

SAMPLE_WALLET = {
    "id": WALLET_ID,
    "name": "My Wallet",
    "description": "A test wallet",
    "co_id": "co-1",
    "time_created": "2025-01-01T00:00:00Z",
    "credits_used": 0,
    "credits_available": 1000,
}

PAGINATED_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [SAMPLE_WALLET],
}


class TestListWallets:
    def test_list_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["wallet", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["wallet", "list", "--format", "table"])
        assert result.exit_code == 0
        assert "━" in result.output
        assert "wallet-7" in result.output

    def test_list_basic(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["wallet", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_with_name_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/?name=My+Wallet", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["wallet", "list", "--name", "My Wallet"])
        assert result.exit_code == 0

    def test_list_with_co_id_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/?co_id=co-1", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["wallet", "list", "--co-id", "co-1"])
        assert result.exit_code == 0

    def test_list_with_pagination(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/wallets/?limit=5&offset=10", json=PAGINATED_RESPONSE
        )
        result = runner.invoke(app, ["wallet", "list", "--limit", "5", "--offset", "10"])
        assert result.exit_code == 0

    def test_list_invalid_limit(self) -> None:
        result = runner.invoke(app, ["wallet", "list", "--limit", "0"])
        assert result.exit_code == 1

    def test_list_negative_limit(self) -> None:
        result = runner.invoke(app, ["wallet", "list", "--limit", "-1"])
        assert result.exit_code == 1

    def test_list_negative_offset(self) -> None:
        result = runner.invoke(app, ["wallet", "list", "--offset", "-1"])
        assert result.exit_code == 1

    def test_list_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["wallet", "list"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestGetWallet:
    def test_get_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/{WALLET_ID}/", json=SAMPLE_WALLET)
        result = runner.invoke(app, ["wallet", "get", WALLET_ID, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == WALLET_ID

    def test_get_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/{WALLET_ID}/", json=SAMPLE_WALLET)
        result = runner.invoke(app, ["wallet", "get", WALLET_ID, "--format", "table"])
        assert result.exit_code == 0
        assert WALLET_ID in result.output

    def test_get(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/{WALLET_ID}/", json=SAMPLE_WALLET)
        result = runner.invoke(app, ["wallet", "get", WALLET_ID])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == WALLET_ID
        assert data["name"] == "My Wallet"

    def test_get_not_found(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/wallets/{WALLET_ID}/", status_code=404)
        result = runner.invoke(app, ["wallet", "get", WALLET_ID])
        assert result.exit_code != 0

    def test_get_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["wallet", "get", WALLET_ID])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestCreateWallet:
    def test_create(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/wallets/",
            method="POST",
            json=SAMPLE_WALLET,
            status_code=201,
        )
        payload = json.dumps({"name": "My Wallet", "co_id": "co-1"})
        result = runner.invoke(app, ["wallet", "create", payload])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == WALLET_ID

    def test_create_invalid_json(self) -> None:
        result = runner.invoke(app, ["wallet", "create", "not-valid-json"])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    def test_create_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["wallet", "create", '{"name": "x", "co_id": "co-1"}'])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestUpdateWallet:
    def test_update_name(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_WALLET, "name": "Renamed Wallet"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/wallets/{WALLET_ID}/", method="PATCH", json=updated
        )
        result = runner.invoke(app, ["wallet", "update", WALLET_ID, "--name", "Renamed Wallet"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Renamed Wallet"

    def test_update_description(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_WALLET, "description": "New description"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/wallets/{WALLET_ID}/", method="PATCH", json=updated
        )
        result = runner.invoke(
            app,
            ["wallet", "update", WALLET_ID, "--description", "New description"],
        )
        assert result.exit_code == 0

    def test_update_no_fields(self) -> None:
        result = runner.invoke(app, ["wallet", "update", WALLET_ID])
        assert result.exit_code == 1
        assert "--name" in result.output or "--description" in result.output

    def test_update_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["wallet", "update", WALLET_ID, "--name", "x"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestDeleteWallet:
    def test_delete_with_confirm_flag(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/wallets/{WALLET_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["wallet", "delete", WALLET_ID, "--yes"])
        assert result.exit_code == 0
        assert WALLET_ID in result.output

    def test_delete_prompt_abort(self) -> None:
        result = runner.invoke(app, ["wallet", "delete", WALLET_ID], input="n\n")
        assert result.exit_code != 0

    def test_delete_prompt_confirm(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/wallets/{WALLET_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["wallet", "delete", WALLET_ID], input="y\n")
        assert result.exit_code == 0

    def test_delete_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["wallet", "delete", WALLET_ID, "--yes"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output

"""Tests for collaborative organisation (CO) CLI commands."""

import json

import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from surf_cli.client import TOKEN_ENV_VAR
from surf_cli.main import app

runner = CliRunner()

CO_ID = "co-123"
USER_ID = "user-456"
BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"

SAMPLE_CO = {
    "id": CO_ID,
    "name": "My Organisation",
    "description": "A test collaborative organisation",
    "time_created": "2025-01-01T00:00:00Z",
}

PAGINATED_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [SAMPLE_CO],
}

SAMPLE_MEMBER = {
    "user_id": USER_ID,
    "role": "member",
    "time_created": "2025-01-01T00:00:00Z",
}

MEMBERS_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [SAMPLE_MEMBER],
}


class TestListCOs:
    def test_list_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["co", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["co", "list", "--format", "table"])
        assert result.exit_code == 0
        assert "━" in result.output
        assert "My Organisation" in result.output

    def test_list_basic(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["co", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_with_name_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/?name=My+Organisation", json=PAGINATED_RESPONSE
        )
        result = runner.invoke(app, ["co", "list", "--name", "My Organisation"])
        assert result.exit_code == 0

    def test_list_with_pagination(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/?limit=5&offset=10", json=PAGINATED_RESPONSE)
        result = runner.invoke(app, ["co", "list", "--limit", "5", "--offset", "10"])
        assert result.exit_code == 0

    def test_list_invalid_limit(self) -> None:
        result = runner.invoke(app, ["co", "list", "--limit", "0"])
        assert result.exit_code == 1

    def test_list_negative_limit(self) -> None:
        result = runner.invoke(app, ["co", "list", "--limit", "-1"])
        assert result.exit_code == 1

    def test_list_negative_offset(self) -> None:
        result = runner.invoke(app, ["co", "list", "--offset", "-1"])
        assert result.exit_code == 1

    def test_list_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "list"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestGetCO:
    def test_get_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", json=SAMPLE_CO)
        result = runner.invoke(app, ["co", "get", CO_ID, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == CO_ID

    def test_get_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", json=SAMPLE_CO)
        result = runner.invoke(app, ["co", "get", CO_ID, "--format", "table"])
        assert result.exit_code == 0
        assert CO_ID in result.output

    def test_get(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", json=SAMPLE_CO)
        result = runner.invoke(app, ["co", "get", CO_ID])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == CO_ID

    def test_get_not_found(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", status_code=404)
        result = runner.invoke(app, ["co", "get", CO_ID])
        assert result.exit_code != 0

    def test_get_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "get", CO_ID])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestCreateCO:
    def test_create(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/", method="POST", json=SAMPLE_CO, status_code=201
        )
        payload = json.dumps({"name": "My Organisation", "description": "A test CO"})
        result = runner.invoke(app, ["co", "create", payload])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == CO_ID

    def test_create_invalid_json(self) -> None:
        result = runner.invoke(app, ["co", "create", "{bad json}"])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    def test_create_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "create", '{"name": "x"}'])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestUpdateCO:
    def test_update_name(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_CO, "name": "New Name"}
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", method="PATCH", json=updated)
        result = runner.invoke(app, ["co", "update", CO_ID, "--name", "New Name"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "New Name"

    def test_update_description(self, httpx_mock: HTTPXMock) -> None:
        updated = {**SAMPLE_CO, "description": "Updated description"}
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", method="PATCH", json=updated)
        result = runner.invoke(
            app, ["co", "update", CO_ID, "--description", "Updated description"]
        )
        assert result.exit_code == 0

    def test_update_no_fields(self) -> None:
        result = runner.invoke(app, ["co", "update", CO_ID])
        assert result.exit_code == 1
        assert "at least" in result.output

    def test_update_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "update", CO_ID, "--name", "x"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestDeleteCO:
    def test_delete_with_confirm_flag(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", method="DELETE", status_code=204)
        result = runner.invoke(app, ["co", "delete", CO_ID, "--yes"])
        assert result.exit_code == 0
        assert CO_ID in result.output

    def test_delete_prompt_abort(self) -> None:
        result = runner.invoke(app, ["co", "delete", CO_ID], input="n\n")
        assert result.exit_code != 0

    def test_delete_prompt_confirm(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/", method="DELETE", status_code=204)
        result = runner.invoke(app, ["co", "delete", CO_ID], input="y\n")
        assert result.exit_code == 0

    def test_delete_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "delete", CO_ID, "--yes"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestListMembers:
    def test_list_members_format_json(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/members/", json=MEMBERS_RESPONSE)
        result = runner.invoke(app, ["co", "members", CO_ID, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_members_format_table(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/members/", json=MEMBERS_RESPONSE)
        result = runner.invoke(app, ["co", "members", CO_ID, "--format", "table"])
        assert result.exit_code == 0
        assert "━" in result.output
        assert USER_ID in result.output

    def test_list_members(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE_URL}/co/{CO_ID}/members/", json=MEMBERS_RESPONSE)
        result = runner.invoke(app, ["co", "members", CO_ID])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_members_with_pagination(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/{CO_ID}/members/?limit=5&offset=0",
            json=MEMBERS_RESPONSE,
        )
        result = runner.invoke(app, ["co", "members", CO_ID, "--limit", "5", "--offset", "0"])
        assert result.exit_code == 0

    def test_list_members_invalid_limit(self) -> None:
        result = runner.invoke(app, ["co", "members", CO_ID, "--limit", "0"])
        assert result.exit_code == 1

    def test_list_members_negative_limit(self) -> None:
        result = runner.invoke(app, ["co", "members", CO_ID, "--limit", "-1"])
        assert result.exit_code == 1

    def test_list_members_negative_offset(self) -> None:
        result = runner.invoke(app, ["co", "members", CO_ID, "--offset", "-1"])
        assert result.exit_code == 1

    def test_list_members_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "members", CO_ID])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestAddMember:
    def test_add_member(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/{CO_ID}/members/",
            method="POST",
            json=SAMPLE_MEMBER,
            status_code=201,
        )
        result = runner.invoke(app, ["co", "add-member", CO_ID, "--user-id", USER_ID])
        assert result.exit_code == 0

    def test_add_member_with_role(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/{CO_ID}/members/",
            method="POST",
            json={**SAMPLE_MEMBER, "role": "admin"},
            status_code=201,
        )
        result = runner.invoke(
            app,
            ["co", "add-member", CO_ID, "--user-id", USER_ID, "--role", "admin"],
        )
        assert result.exit_code == 0

    def test_add_member_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "add-member", CO_ID, "--user-id", USER_ID])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestRemoveMember:
    def test_remove_member_with_confirm_flag(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/{CO_ID}/members/{USER_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["co", "remove-member", CO_ID, USER_ID, "--yes"])
        assert result.exit_code == 0
        assert USER_ID in result.output

    def test_remove_member_prompt_abort(self) -> None:
        result = runner.invoke(app, ["co", "remove-member", CO_ID, USER_ID], input="n\n")
        assert result.exit_code != 0

    def test_remove_member_prompt_confirm(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/co/{CO_ID}/members/{USER_ID}/",
            method="DELETE",
            status_code=204,
        )
        result = runner.invoke(app, ["co", "remove-member", CO_ID, USER_ID], input="y\n")
        assert result.exit_code == 0

    def test_remove_member_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["co", "remove-member", CO_ID, USER_ID, "--yes"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output

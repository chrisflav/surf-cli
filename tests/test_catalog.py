"""Tests for catalog CLI commands."""

import json

import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from surf_cli.client import TOKEN_ENV_VAR
from surf_cli.main import app

runner = CliRunner()

ITEM_ID = "cat-456"
BASE_URL = "https://gw.live.surfresearchcloud.nl/v1/workspace"

SAMPLE_CATALOG_ITEM = {
    "id": ITEM_ID,
    "name": "Jupyter Notebook",
    "description": "Interactive computing environment.",
    "type": "Compute",
    "logo": "https://example.com/logo.png",
    "co_id": "co-1",
}

PAGINATED_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [SAMPLE_CATALOG_ITEM],
}



class TestListCatalog:
    def test_list_basic(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["catalog", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 1

    def test_list_with_name_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/?name=Jupyter",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["catalog", "list", "--name", "Jupyter"])
        assert result.exit_code == 0

    def test_list_with_type_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/?type=Compute",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["catalog", "list", "--type", "Compute"])
        assert result.exit_code == 0

    def test_list_with_co_id_filter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/?co_id=co-1",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["catalog", "list", "--co-id", "co-1"])
        assert result.exit_code == 0

    def test_list_with_pagination(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/?limit=5&offset=10",
            json=PAGINATED_RESPONSE,
        )
        result = runner.invoke(app, ["catalog", "list", "--limit", "5", "--offset", "10"])
        assert result.exit_code == 0

    def test_list_no_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(TOKEN_ENV_VAR, raising=False)
        result = runner.invoke(app, ["catalog", "list"])
        assert result.exit_code == 1
        assert TOKEN_ENV_VAR in result.output


class TestGetCatalogItem:
    def test_get(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/{ITEM_ID}/",
            json=SAMPLE_CATALOG_ITEM,
        )
        result = runner.invoke(app, ["catalog", "get", ITEM_ID])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == ITEM_ID
        assert data["name"] == "Jupyter Notebook"

    def test_get_not_found(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE_URL}/catalog/{ITEM_ID}/",
            status_code=404,
        )
        result = runner.invoke(app, ["catalog", "get", ITEM_ID])
        assert result.exit_code != 0

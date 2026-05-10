"""Tests for output formatting utilities."""

import json

import pytest
from typer.testing import CliRunner

from surf_cli.client import TOKEN_ENV_VAR
from surf_cli.formatting import (
    OutputFormat,
    _TABLE_MAX_CELL_WIDTH,
    _cell,
    print_csv,
    print_json,
    print_output,
    print_table,
)

runner = CliRunner()


@pytest.fixture(autouse=True)
def set_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TOKEN_ENV_VAR, "test-token")


class TestPrintJson:
    def test_prints_dict(self, capsys: pytest.CaptureFixture) -> None:
        print_json({"key": "value"})
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"key": "value"}

    def test_pretty_printed(self, capsys: pytest.CaptureFixture) -> None:
        print_json({"a": 1})
        captured = capsys.readouterr()
        assert "\n" in captured.out

    def test_prints_list(self, capsys: pytest.CaptureFixture) -> None:
        print_json([1, 2, 3])
        captured = capsys.readouterr()
        assert json.loads(captured.out) == [1, 2, 3]


class TestPrintTable:
    def test_list_of_dicts(self, capsys: pytest.CaptureFixture) -> None:
        rows = [{"id": "1", "name": "foo"}, {"id": "2", "name": "bar"}]
        print_table(rows)
        captured = capsys.readouterr()
        assert "id" in captured.out
        assert "name" in captured.out
        assert "foo" in captured.out
        assert "bar" in captured.out

    def test_paginated_response(self, capsys: pytest.CaptureFixture) -> None:
        data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": "ws-1", "name": "my workspace", "status": "running"}],
        }
        print_table(data)
        captured = capsys.readouterr()
        assert "ws-1" in captured.out
        assert "my workspace" in captured.out
        assert "running" in captured.out

    def test_single_dict(self, capsys: pytest.CaptureFixture) -> None:
        data = {"id": "ws-1", "name": "my workspace", "status": "running"}
        print_table(data)
        captured = capsys.readouterr()
        assert "id" in captured.out
        assert "ws-1" in captured.out
        assert "name" in captured.out
        assert "status" in captured.out

    def test_empty_list(self, capsys: pytest.CaptureFixture) -> None:
        print_table([])
        # Should not raise; empty table is rendered.

    def test_none_values_become_empty_string(self, capsys: pytest.CaptureFixture) -> None:
        print_table([{"id": "1", "end_time": None}])
        captured = capsys.readouterr()
        assert "id" in captured.out

    def test_nested_dict_serialized_as_json(self, capsys: pytest.CaptureFixture) -> None:
        print_table([{"id": "1", "meta": {"key": "value"}}])
        captured = capsys.readouterr()
        # Short enough not to be truncated
        assert '{"key": "value"}' in captured.out

    def test_long_value_truncated(self, capsys: pytest.CaptureFixture) -> None:
        long_val = "x" * (_TABLE_MAX_CELL_WIDTH + 20)
        print_table([{"id": "1", "desc": long_val}])
        captured = capsys.readouterr()
        assert long_val not in captured.out
        assert "…" in captured.out

    def test_value_at_max_width_not_truncated(self, capsys: pytest.CaptureFixture) -> None:
        exact_val = "y" * _TABLE_MAX_CELL_WIDTH
        print_table([{"id": "1", "desc": exact_val}])
        captured = capsys.readouterr()
        assert exact_val in captured.out
        assert "…" not in captured.out


class TestCell:
    def test_none_returns_empty(self) -> None:
        assert _cell(None) == ""

    def test_short_string_unchanged(self) -> None:
        assert _cell("hello") == "hello"

    def test_long_string_truncated(self) -> None:
        long_val = "a" * (_TABLE_MAX_CELL_WIDTH + 10)
        result = _cell(long_val)
        assert len(result) == _TABLE_MAX_CELL_WIDTH
        assert result.endswith("…")

    def test_exact_width_not_truncated(self) -> None:
        val = "b" * _TABLE_MAX_CELL_WIDTH
        assert _cell(val) == val

    def test_dict_truncated_when_long(self) -> None:
        big_dict = {"key": "v" * _TABLE_MAX_CELL_WIDTH}
        result = _cell(big_dict)
        assert len(result) == _TABLE_MAX_CELL_WIDTH
        assert result.endswith("…")

    def test_custom_max_width(self) -> None:
        result = _cell("hello world", max_width=5)
        assert result == "hell…"

    def test_fallback_to_json_for_scalar(self, capsys: pytest.CaptureFixture) -> None:
        print_table(42)
        captured = capsys.readouterr()
        assert "42" in captured.out


class TestPrintCsv:
    def test_list_of_dicts(self, capsys: pytest.CaptureFixture) -> None:
        rows = [{"id": "1", "name": "foo"}, {"id": "2", "name": "bar"}]
        print_csv(rows)
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "id,name"
        assert lines[1] == "1,foo"
        assert lines[2] == "2,bar"

    def test_paginated_response(self, capsys: pytest.CaptureFixture) -> None:
        data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": "ws-1", "name": "my workspace", "status": "running"}],
        }
        print_csv(data)
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "id,name,status"
        assert "ws-1" in lines[1]
        assert "my workspace" in lines[1]
        assert "running" in lines[1]

    def test_single_dict(self, capsys: pytest.CaptureFixture) -> None:
        data = {"id": "ws-1", "name": "my workspace"}
        print_csv(data)
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "field,value"
        assert lines[1] == "id,ws-1"
        assert "my workspace" in lines[2]

    def test_empty_list(self, capsys: pytest.CaptureFixture) -> None:
        print_csv([])
        # Empty list → no output; should not raise.

    def test_fallback_to_json_for_scalar(self, capsys: pytest.CaptureFixture) -> None:
        print_csv(42)
        captured = capsys.readouterr()
        assert "42" in captured.out

    def test_values_with_commas_are_quoted(self, capsys: pytest.CaptureFixture) -> None:
        print_csv([{"id": "1", "name": "foo, bar"}])
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert '"foo, bar"' in lines[1]

    def test_none_values_become_empty_string(self, capsys: pytest.CaptureFixture) -> None:
        print_csv([{"id": "1", "end_time": None}])
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "id,end_time"
        assert lines[1] == "1,"


class TestPrintOutput:
    def test_json_format(self, capsys: pytest.CaptureFixture) -> None:
        print_output({"key": "val"}, OutputFormat.json)
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"key": "val"}

    def test_table_format_list(self, capsys: pytest.CaptureFixture) -> None:
        print_output([{"id": "1", "name": "foo"}], OutputFormat.table)
        captured = capsys.readouterr()
        assert "foo" in captured.out

    def test_table_format_paginated(self, capsys: pytest.CaptureFixture) -> None:
        data = {"count": 1, "next": None, "previous": None, "results": [{"id": "1"}]}
        print_output(data, OutputFormat.table)
        captured = capsys.readouterr()
        assert "1" in captured.out

    def test_csv_format_list(self, capsys: pytest.CaptureFixture) -> None:
        print_output([{"id": "1", "name": "foo"}], OutputFormat.csv)
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "id,name"
        assert lines[1] == "1,foo"

    def test_csv_format_paginated(self, capsys: pytest.CaptureFixture) -> None:
        data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": "1", "name": "foo"}],
        }
        print_output(data, OutputFormat.csv)
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "id,name"
        assert lines[1] == "1,foo"


class TestOutputFormatOption:
    """Integration tests: ensure --format is accepted by commands."""

    def test_workspace_list_format_json(self, httpx_mock) -> None:
        from surf_cli.main import app

        httpx_mock.add_response(
            url="https://gw.live.surfresearchcloud.nl/v1/workspace/workspaces/",
            json={"count": 0, "next": None, "previous": None, "results": []},
        )
        result = runner.invoke(app, ["workspace", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 0

    def test_workspace_list_format_table(self, httpx_mock) -> None:
        from surf_cli.main import app

        httpx_mock.add_response(
            url="https://gw.live.surfresearchcloud.nl/v1/workspace/workspaces/",
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"id": "ws-1", "name": "test-ws", "status": "running"}],
            },
        )
        result = runner.invoke(app, ["workspace", "list", "--format", "table"])
        assert result.exit_code == 0
        assert "test-ws" in result.output

    def test_workspace_get_format_table(self, httpx_mock) -> None:
        from surf_cli.main import app

        httpx_mock.add_response(
            url="https://gw.live.surfresearchcloud.nl/v1/workspace/workspaces/ws-1/",
            json={"id": "ws-1", "name": "test-ws", "status": "running"},
        )
        result = runner.invoke(app, ["workspace", "get", "ws-1", "--format", "table"])
        assert result.exit_code == 0
        assert "test-ws" in result.output

    def test_workspace_list_format_csv(self, httpx_mock) -> None:
        from surf_cli.main import app

        httpx_mock.add_response(
            url="https://gw.live.surfresearchcloud.nl/v1/workspace/workspaces/",
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"id": "ws-1", "name": "test-ws", "status": "running"}],
            },
        )
        result = runner.invoke(app, ["workspace", "list", "--format", "csv"])
        assert result.exit_code == 0
        lines = result.output.splitlines()
        assert lines[0] == "id,name,status"
        assert "ws-1" in lines[1]
        assert "test-ws" in lines[1]

    def test_invalid_format_rejected(self, httpx_mock) -> None:
        from surf_cli.main import app

        result = runner.invoke(app, ["workspace", "list", "--format", "yaml"])
        assert result.exit_code != 0

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.rack.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestRackList:
    def test_rack_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "name": "Rack-A1", "size": "42", "description": "Main rack"},
            {"id": "2", "name": "Rack-B1", "size": "24", "description": "Small rack"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "rack", "list"])
        assert result.exit_code == 0
        assert "Rack-A1" in result.output
        assert "Rack-B1" in result.output

    def test_rack_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "rack", "list"])
        assert result.exit_code == 0
        assert "No racks found" in result.output

    def test_rack_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "name": "Zulu", "size": "42", "description": "Z"},
            {"id": "1", "name": "Alpha", "size": "24", "description": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "rack", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestRackShow:
    def test_rack_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "name": "Rack-A1", "size": "42",
        }
        result = runner.invoke(cli, ["--profile", "test", "rack", "show", "1"])
        assert result.exit_code == 0
        assert "Rack-A1" in result.output


class TestRackAdd:
    def test_rack_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Rack created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "rack", "add", "--name", "NewRack",
             "--size", "42", "--description", "Test rack"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_rack_add_with_location_and_row(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 4, "data": "Rack created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "rack", "add", "--name", "Rack-C1",
             "--location", "2", "--row", "A"],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["location"] == "2"
        assert call_data["row"] == "A"


class TestRackUpdate:
    def test_rack_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "rack", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/racks", 1, data={"name": "Renamed"}
        )

    def test_rack_update_size(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "rack", "update", "1", "--size", "48"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/racks", 1, data={"size": "48"}
        )

    def test_rack_update_location_row_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "rack", "update", "1",
             "--location", "5", "--row", "B", "--description", "Moved"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/racks", 1,
            data={"location": "5", "row": "B", "description": "Moved"}
        )


class TestRackDelete:
    def test_rack_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "rack", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

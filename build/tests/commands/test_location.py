from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.location.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestLocationList:
    def test_location_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "name": "DC-East", "address": "123 Main St", "description": "East DC"},
            {"id": "2", "name": "DC-West", "address": "456 Oak Ave", "description": "West DC"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "location", "list"])
        assert result.exit_code == 0
        assert "DC-East" in result.output
        assert "DC-West" in result.output

    def test_location_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "location", "list"])
        assert result.exit_code == 0
        assert "No locations found" in result.output

    def test_location_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "name": "Zulu", "address": "", "description": "Z"},
            {"id": "1", "name": "Alpha", "address": "", "description": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "location", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestLocationShow:
    def test_location_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "name": "DC-East", "address": "123 Main St",
        }
        result = runner.invoke(cli, ["--profile", "test", "location", "show", "1"])
        assert result.exit_code == 0
        assert "DC-East" in result.output


class TestLocationAdd:
    def test_location_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Location created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "location", "add", "--name", "New DC",
             "--address", "789 Elm St", "--description", "New datacenter"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_location_add_with_coords(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 4, "data": "Location created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "location", "add", "--name", "Geo DC",
             "--lat", "51.5", "--long", "-0.1"],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["lat"] == "51.5"
        assert call_data["long"] == "-0.1"


class TestLocationUpdate:
    def test_location_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "location", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/locations", 1, data={"name": "Renamed"}
        )

    def test_location_update_address_and_coords(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "location", "update", "1",
             "--address", "New St", "--lat", "52.0", "--long", "0.5"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/locations", 1,
            data={"address": "New St", "lat": "52.0", "long": "0.5"}
        )

    def test_location_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "location", "update", "1",
             "--description", "Updated DC"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/locations", 1, data={"description": "Updated DC"}
        )

    def test_location_update_address(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "location", "update", "1",
             "--address", "999 New St"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/locations", 1, data={"address": "999 New St"}
        )


class TestLocationDelete:
    def test_location_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "location", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

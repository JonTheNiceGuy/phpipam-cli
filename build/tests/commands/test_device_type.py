from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.device_type.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestDeviceTypeList:
    def test_device_type_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"tid": "1", "tname": "Switch", "tdescription": "Network switch"},
            {"tid": "2", "tname": "Router", "tdescription": "Network router"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "device-type", "list"])
        assert result.exit_code == 0
        assert "Switch" in result.output
        assert "Router" in result.output

    def test_device_type_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "device-type", "list"])
        assert result.exit_code == 0
        assert "No device types found" in result.output

    def test_device_type_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"tid": "2", "tname": "Zulu", "tdescription": "Z"},
            {"tid": "1", "tname": "Alpha", "tdescription": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "device-type", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestDeviceTypeShow:
    def test_device_type_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "tid": "1", "tname": "Switch", "tdescription": "Network switch",
        }
        result = runner.invoke(cli, ["--profile", "test", "device-type", "show", "1"])
        assert result.exit_code == 0
        assert "Switch" in result.output


class TestDeviceTypeAdd:
    def test_device_type_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Device type created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "device-type", "add", "--tname", "Firewall",
             "--tdescription", "Network firewall"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()


class TestDeviceTypeUpdate:
    def test_device_type_update_tname(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "device-type", "update", "1",
             "--tname", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/device_types", 1, data={"tname": "Renamed"}
        )

    def test_device_type_update_tdescription(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "device-type", "update", "1",
             "--tdescription", "New desc"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/device_types", 1, data={"tdescription": "New desc"}
        )


class TestDeviceTypeDelete:
    def test_device_type_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "device-type", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

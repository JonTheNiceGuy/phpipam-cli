from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.device.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestDeviceList:
    def test_device_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "hostname": "sw-core-01", "ip_addr": "10.0.0.1",
             "description": "Core switch"},
            {"id": "2", "hostname": "fw-edge-01", "ip_addr": "10.0.0.2",
             "description": "Edge firewall"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "device", "list"])
        assert result.exit_code == 0
        assert "sw-core-01" in result.output
        assert "fw-edge-01" in result.output

    def test_device_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "device", "list"])
        assert result.exit_code == 0
        assert "No devices found" in result.output

    def test_device_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "hostname": "zulu-sw", "ip_addr": "", "description": ""},
            {"id": "1", "hostname": "alpha-fw", "ip_addr": "", "description": ""},
        ]
        result = runner.invoke(cli, ["--profile", "test", "device", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "alpha-fw" in lines[0]
        assert "zulu-sw" in lines[1]


class TestDeviceShow:
    def test_device_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "hostname": "sw-core-01", "ip_addr": "10.0.0.1",
        }
        result = runner.invoke(cli, ["--profile", "test", "device", "show", "1"])
        assert result.exit_code == 0
        assert "sw-core-01" in result.output


class TestDeviceAdd:
    def test_device_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Device created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "device", "add", "--hostname", "new-sw-01",
             "--ip-addr", "10.0.0.3", "--description", "New switch"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_device_add_with_rack_and_location(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 4, "data": "Device created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "device", "add", "--hostname", "rack-sw-01",
             "--sections", "1;2", "--rack", "5", "--rack-start", "10",
             "--rack-size", "2", "--location", "3"],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["sections"] == "1;2"
        assert call_data["rack"] == "5"
        assert call_data["rack_start"] == "10"
        assert call_data["rack_size"] == "2"
        assert call_data["location"] == "3"


class TestDeviceUpdate:
    def test_device_update_hostname(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "device", "update", "1",
             "--hostname", "renamed-sw"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "devices", 1, data={"hostname": "renamed-sw"}
        )

    def test_device_update_ip_addr(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "device", "update", "1",
             "--ip-addr", "10.0.0.99"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "devices", 1, data={"ip_addr": "10.0.0.99"}
        )

    def test_device_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "device", "update", "1",
             "--description", "Updated desc"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "devices", 1, data={"description": "Updated desc"}
        )

    def test_device_update_rack_and_location(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "device", "update", "1",
             "--rack", "7", "--rack-start", "20", "--rack-size", "4",
             "--location", "2"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "devices", 1, data={
                "rack": "7", "rack_start": "20", "rack_size": "4",
                "location": "2",
            }
        )


class TestDeviceDelete:
    def test_device_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "device", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

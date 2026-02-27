from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.vrf.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestVrfList:
    def test_vrf_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"vrfId": "1", "name": "Global", "rd": "65000:1", "description": "Global VRF"},
            {"vrfId": "2", "name": "Customer-A", "rd": "65000:100", "description": "Customer A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "vrf", "list"])
        assert result.exit_code == 0
        assert "Global" in result.output
        assert "Customer-A" in result.output

    def test_vrf_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "vrf", "list"])
        assert result.exit_code == 0
        assert "No VRFs found" in result.output

    def test_vrf_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"vrfId": "2", "name": "Zulu", "rd": "65000:2", "description": "Z"},
            {"vrfId": "1", "name": "Alpha", "rd": "65000:1", "description": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "vrf", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestVrfShow:
    def test_vrf_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "vrfId": "1", "name": "Global", "rd": "65000:1", "description": "Global VRF",
        }
        result = runner.invoke(cli, ["--profile", "test", "vrf", "show", "1"])
        assert result.exit_code == 0
        assert "Global" in result.output


class TestVrfAdd:
    def test_vrf_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "VRF created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "vrf", "add", "--name", "NewVRF",
             "--rd", "65000:200", "--description", "Test VRF"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()


class TestVrfUpdate:
    def test_vrf_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "vrf", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "vrf", 1, data={"name": "Renamed"}
        )

    def test_vrf_update_rd(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "vrf", "update", "1", "--rd", "65000:999"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "vrf", 1, data={"rd": "65000:999"}
        )

    def test_vrf_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "vrf", "update", "1", "--description", "New desc"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "vrf", 1, data={"description": "New desc"}
        )


class TestVrfDelete:
    def test_vrf_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "vrf", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

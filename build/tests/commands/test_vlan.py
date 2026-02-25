from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.vlan.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestVlanList:
    def test_vlan_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 1, "number": "100", "name": "Management", "description": "Mgmt VLAN"},
            {"id": 2, "number": "200", "name": "Data", "description": "Data VLAN"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "vlan", "list"])
        assert result.exit_code == 0
        assert "100" in result.output
        assert "200" in result.output

    def test_vlan_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "vlan", "list"])
        assert result.exit_code == 0
        assert "No VLANs found" in result.output


class TestVlanShow:
    def test_vlan_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": 1,
            "number": "100",
            "name": "Management",
            "description": "Mgmt VLAN",
        }
        result = runner.invoke(
            cli, ["--profile", "test", "vlan", "show", "1"]
        )
        assert result.exit_code == 0
        assert "Management" in result.output


class TestVlanAdd:
    def test_vlan_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201,
            "success": True,
            "id": 3,
            "data": "VLAN created",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "vlan", "add",
                "--number", "300",
                "--name", "Guest",
                "--description", "Guest network",
            ],
        )
        assert result.exit_code == 0


class TestVlanUpdate:
    def test_vlan_update(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200,
            "success": True,
            "data": "VLAN updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "vlan", "update",
                "1",
                "--name", "Updated VLAN",
            ],
        )
        assert result.exit_code == 0

    def test_vlan_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200,
            "success": True,
            "data": "VLAN updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "vlan", "update",
                "1",
                "--description", "New VLAN desc",
            ],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "vlan", 1, data={"description": "New VLAN desc"}
        )


class TestVlanDelete:
    def test_vlan_delete(self, runner, mock_client):
        mock_client.delete.return_value = {
            "code": 200,
            "success": True,
            "data": "VLAN deleted",
        }
        result = runner.invoke(
            cli, ["--profile", "test", "vlan", "delete", "1"]
        )
        assert result.exit_code == 0

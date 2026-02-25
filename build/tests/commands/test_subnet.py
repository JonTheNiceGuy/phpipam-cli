from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.subnet.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestSubnetList:
    def test_subnet_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 1, "subnet": "10.0.0.0", "mask": "24", "description": "Office"},
            {"id": 2, "subnet": "192.168.1.0", "mask": "24", "description": "Lab"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0
        assert "10.0.0.0" in result.output
        assert "192.168.1.0" in result.output

    def test_subnet_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0


class TestSubnetShow:
    def test_subnet_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": 1,
            "subnet": "10.0.0.0",
            "mask": "24",
            "description": "Office",
            "sectionId": "1",
        }
        result = runner.invoke(cli, ["--profile", "test", "subnet", "show", "1"])
        assert result.exit_code == 0
        assert "10.0.0.0" in result.output


class TestSubnetAdd:
    def test_subnet_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201,
            "success": True,
            "id": 5,
            "data": "Subnet created",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "subnet", "add",
                "--subnet", "10.1.0.0",
                "--mask", "24",
                "--section-id", "1",
                "--description", "New net",
            ],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower() or "5" in result.output


class TestSubnetUpdate:
    def test_subnet_update(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200,
            "success": True,
            "data": "Subnet updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "subnet", "update",
                "1",
                "--description", "Updated desc",
            ],
        )
        assert result.exit_code == 0

    def test_subnet_update_mask(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200,
            "success": True,
            "data": "Subnet updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "subnet", "update",
                "1",
                "--mask", "25",
            ],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "subnets", 1, data={"mask": "25"}
        )


class TestSubnetDelete:
    def test_subnet_delete(self, runner, mock_client):
        mock_client.delete.return_value = {
            "code": 200,
            "success": True,
            "data": "Subnet deleted",
        }
        result = runner.invoke(
            cli, ["--profile", "test", "subnet", "delete", "1"]
        )
        assert result.exit_code == 0


class TestSubnetSearch:
    def test_subnet_search_cidr(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 1, "subnet": "10.0.0.0", "mask": "24", "description": "Office"}
        ]
        result = runner.invoke(
            cli, ["--profile", "test", "subnet", "search", "10.0.0.0/24"]
        )
        assert result.exit_code == 0
        assert "10.0.0.0" in result.output

    def test_subnet_search_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(
            cli, ["--profile", "test", "subnet", "search", "10.99.0.0/24"]
        )
        assert result.exit_code == 0
        assert "No subnets found" in result.output

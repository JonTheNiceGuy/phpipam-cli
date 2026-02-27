from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.l2domain.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestL2domainList:
    def test_l2domain_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 1, "name": "Default", "description": "Default L2 domain"},
            {"id": 2, "name": "DC-East", "description": "East datacenter"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "l2domain", "list"])
        assert result.exit_code == 0
        assert "Default" in result.output
        assert "DC-East" in result.output

    def test_l2domain_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "l2domain", "list"])
        assert result.exit_code == 0
        assert "No L2 domains found" in result.output

    def test_l2domain_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 2, "name": "Zebra", "description": "Z domain"},
            {"id": 1, "name": "Alpha", "description": "A domain"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "l2domain", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zebra" in lines[1]


class TestL2domainShow:
    def test_l2domain_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": 1, "name": "Default", "description": "Default L2 domain",
        }
        result = runner.invoke(cli, ["--profile", "test", "l2domain", "show", "1"])
        assert result.exit_code == 0
        assert "Default" in result.output


class TestL2domainAdd:
    def test_l2domain_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "L2 domain created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "l2domain", "add", "--name", "NewDomain",
             "--description", "Test"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()


class TestL2domainUpdate:
    def test_l2domain_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "l2domain", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "l2domains", 1, data={"name": "Renamed"}
        )

    def test_l2domain_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "l2domain", "update", "1",
             "--description", "New desc"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "l2domains", 1, data={"description": "New desc"}
        )


class TestL2domainDelete:
    def test_l2domain_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "l2domain", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

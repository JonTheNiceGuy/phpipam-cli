from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.nameserver.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestNameserverList:
    def test_nameserver_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "name": "Google DNS", "namesrv1": "8.8.8.8", "description": "Google"},
            {"id": "2", "name": "Cloudflare", "namesrv1": "1.1.1.1", "description": "CF"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "nameserver", "list"])
        assert result.exit_code == 0
        assert "Google DNS" in result.output
        assert "Cloudflare" in result.output

    def test_nameserver_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "nameserver", "list"])
        assert result.exit_code == 0
        assert "No nameservers found" in result.output

    def test_nameserver_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "name": "Zulu", "namesrv1": "9.9.9.9", "description": "Z"},
            {"id": "1", "name": "Alpha", "namesrv1": "1.1.1.1", "description": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "nameserver", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestNameserverShow:
    def test_nameserver_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "name": "Google DNS", "namesrv1": "8.8.8.8",
        }
        result = runner.invoke(cli, ["--profile", "test", "nameserver", "show", "1"])
        assert result.exit_code == 0
        assert "Google DNS" in result.output


class TestNameserverAdd:
    def test_nameserver_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Nameserver created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "nameserver", "add", "--name", "Custom DNS",
             "--namesrv1", "10.0.0.53", "--description", "Internal"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()


class TestNameserverUpdate:
    def test_nameserver_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nameserver", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/nameservers", 1, data={"name": "Renamed"}
        )

    def test_nameserver_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nameserver", "update", "1",
             "--description", "Updated"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/nameservers", 1, data={"description": "Updated"}
        )

    def test_nameserver_update_namesrv1(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nameserver", "update", "1",
             "--namesrv1", "10.0.0.54"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/nameservers", 1, data={"namesrv1": "10.0.0.54"}
        )


class TestNameserverDelete:
    def test_nameserver_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "nameserver", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

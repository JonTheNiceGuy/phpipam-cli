from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.nat.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestNatList:
    def test_nat_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "name": "Web NAT", "type": "source",
             "description": "Web server NAT"},
            {"id": "2", "name": "DB NAT", "type": "static",
             "description": "Database NAT"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "nat", "list"])
        assert result.exit_code == 0
        assert "Web NAT" in result.output
        assert "DB NAT" in result.output

    def test_nat_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "nat", "list"])
        assert result.exit_code == 0
        assert "No NAT rules found" in result.output

    def test_nat_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "name": "Zulu", "type": "source", "description": "Z"},
            {"id": "1", "name": "Alpha", "type": "static", "description": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "nat", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestNatShow:
    def test_nat_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "name": "Web NAT", "type": "source",
        }
        result = runner.invoke(cli, ["--profile", "test", "nat", "show", "1"])
        assert result.exit_code == 0
        assert "Web NAT" in result.output


class TestNatAdd:
    def test_nat_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "NAT created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "add", "--name", "New NAT",
             "--type", "source", "--description", "Test rule"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_nat_add_with_all_options(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 4, "data": "NAT created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "add", "--name", "Full NAT",
             "--type", "static", "--src", "10.0.0.0/24", "--dst", "192.168.0.0/24",
             "--src-port", "8080", "--dst-port", "80", "--device", "3"],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["src"] == "10.0.0.0/24"
        assert call_data["dst"] == "192.168.0.0/24"
        assert call_data["src_port"] == "8080"
        assert call_data["dst_port"] == "80"
        assert call_data["device"] == "3"

    def test_nat_add_invalid_type(self, runner, mock_client):
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "add", "--name", "Bad",
             "--type", "invalid"],
        )
        assert result.exit_code != 0


class TestNatUpdate:
    def test_nat_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "nat", 1, data={"name": "Renamed"}
        )

    def test_nat_update_type(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "update", "1", "--type", "static"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "nat", 1, data={"type": "static"}
        )

    def test_nat_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "update", "1",
             "--description", "Updated"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "nat", 1, data={"description": "Updated"}
        )

    def test_nat_update_src_dst_ports_device(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "nat", "update", "1",
             "--src", "10.0.0.0/8", "--dst", "172.16.0.0/12",
             "--src-port", "443", "--dst-port", "8443", "--device", "5"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "nat", 1, data={
                "src": "10.0.0.0/8", "dst": "172.16.0.0/12",
                "src_port": "443", "dst_port": "8443", "device": "5",
            }
        )


class TestNatDelete:
    def test_nat_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "nat", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

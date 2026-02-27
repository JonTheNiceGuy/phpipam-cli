from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.address.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestAddressList:
    def test_address_list_by_subnet(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 10, "ip": "10.0.0.1", "hostname": "web1", "description": "Web server"},
            {"id": 11, "ip": "10.0.0.2", "hostname": "db1", "description": "Database"},
        ]
        result = runner.invoke(
            cli, ["--profile", "test", "address", "list", "--subnet-id", "1"]
        )
        assert result.exit_code == 0
        assert "10.0.0.1" in result.output
        assert "10.0.0.2" in result.output

    def test_address_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(
            cli, ["--profile", "test", "address", "list", "--subnet-id", "1"]
        )
        assert result.exit_code == 0
        assert "No addresses found" in result.output


class TestAddressShow:
    def test_address_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": 10,
            "ip": "10.0.0.1",
            "hostname": "web1",
            "subnetId": "1",
            "description": "Web server",
        }
        result = runner.invoke(
            cli, ["--profile", "test", "address", "show", "10"]
        )
        assert result.exit_code == 0
        assert "10.0.0.1" in result.output


class TestAddressAdd:
    def test_address_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201,
            "success": True,
            "id": 42,
            "data": "Address created",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "address", "add",
                "--ip", "10.0.0.5",
                "--subnet-id", "1",
                "--hostname", "app1",
                "--description", "App server",
            ],
        )
        assert result.exit_code == 0

    def test_address_add_with_firewall_object(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 43, "data": "Address created",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "address", "add",
                "--ip", "10.0.0.6",
                "--subnet-id", "1",
                "--firewall-address-object", "fw-web-01",
            ],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["firewallAddressObject"] == "fw-web-01"


class TestAddressUpdate:
    def test_address_update(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200,
            "success": True,
            "data": "Address updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "address", "update",
                "10",
                "--hostname", "newname",
            ],
        )
        assert result.exit_code == 0

    def test_address_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200,
            "success": True,
            "data": "Address updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "address", "update",
                "10",
                "--description", "New desc",
            ],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "addresses", 10, data={"description": "New desc"}
        )

    def test_address_update_firewall_object(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200, "success": True, "data": "Address updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "address", "update",
                "10",
                "--firewall-address-object", "fw-db-01",
            ],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "addresses", 10, data={"firewallAddressObject": "fw-db-01"}
        )


class TestAddressDelete:
    def test_address_delete(self, runner, mock_client):
        mock_client.delete.return_value = {
            "code": 200,
            "success": True,
            "data": "Address deleted",
        }
        result = runner.invoke(
            cli, ["--profile", "test", "address", "delete", "10"]
        )
        assert result.exit_code == 0


class TestAddressSearch:
    def test_address_search_ip(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": 10, "ip": "10.0.0.1", "hostname": "web1", "description": "Web"}
        ]
        result = runner.invoke(
            cli, ["--profile", "test", "address", "search", "10.0.0.1"]
        )
        assert result.exit_code == 0
        assert "10.0.0.1" in result.output

    def test_address_search_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(
            cli, ["--profile", "test", "address", "search", "10.99.99.99"]
        )
        assert result.exit_code == 0
        assert "No addresses found" in result.output

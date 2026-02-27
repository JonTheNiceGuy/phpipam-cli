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
        mock_client.get.side_effect = lambda *args: {
            ("subnets",): [
                {"id": 1, "subnet": "10.0.0.0", "mask": "24", "sectionId": "1", "description": "Office"},
                {"id": 2, "subnet": "192.168.1.0", "mask": "24", "sectionId": "1", "description": "Lab"},
            ],
            ("sections",): [{"id": "1", "name": "Production"}],
        }[args]
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0
        assert "10.0.0.0" in result.output
        assert "192.168.1.0" in result.output

    def test_subnet_list_empty(self, runner, mock_client):
        mock_client.get.side_effect = lambda *args: {
            ("subnets",): [],
            ("sections",): [],
        }[args]
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0

    def test_subnet_list_sorted_by_section_then_ip_then_mask(self, runner, mock_client):
        mock_client.get.side_effect = lambda *args: {
            ("subnets",): [
                {"id": 1, "subnet": "192.168.1.0", "mask": "24", "sectionId": "2", "description": "ZLab"},
                {"id": 2, "subnet": "10.0.0.0", "mask": "16", "sectionId": "1", "description": "Wide"},
                {"id": 3, "subnet": "10.0.0.0", "mask": "24", "sectionId": "1", "description": "Narrow"},
                {"id": 4, "subnet": "172.16.0.0", "mask": "12", "sectionId": "1", "description": "Middle"},
            ],
            ("sections",): [
                {"id": "1", "name": "Alpha"},
                {"id": "2", "name": "Beta"},
            ],
        }[args]
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        # Alpha section first: 10.0.0.0/16, 10.0.0.0/24, 172.16.0.0/12
        # Beta section second: 192.168.1.0/24
        assert "10.0.0.0/16" in lines[0]
        assert "10.0.0.0/24" in lines[1]
        assert "172.16.0.0/12" in lines[2]
        assert "192.168.1.0/24" in lines[3]

    def test_subnet_list_mixed_ipv4_ipv6(self, runner, mock_client):
        mock_client.get.side_effect = lambda *args: {
            ("subnets",): [
                {"id": 1, "subnet": "2001:db8::", "mask": "32", "sectionId": "1", "description": "IPv6"},
                {"id": 2, "subnet": "10.0.0.0", "mask": "24", "sectionId": "1", "description": "IPv4"},
            ],
            ("sections",): [{"id": "1", "name": "Production"}],
        }[args]
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        # IPv4 sorts before IPv6 (version 4 < version 6)
        assert "10.0.0.0" in lines[0]
        assert "2001:db8::" in lines[1]

    def test_subnet_list_shows_section_name(self, runner, mock_client):
        mock_client.get.side_effect = lambda *args: {
            ("subnets",): [
                {"id": 1, "subnet": "10.0.0.0", "mask": "24", "sectionId": "1", "description": "Office"},
            ],
            ("sections",): [{"id": "1", "name": "Production"}],
        }[args]
        result = runner.invoke(cli, ["--profile", "test", "subnet", "list"])
        assert result.exit_code == 0
        assert "Production" in result.output


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

    def test_subnet_add_with_firewall_object(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 6, "data": "Subnet created",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "subnet", "add",
                "--subnet", "10.2.0.0",
                "--mask", "24",
                "--section-id", "1",
                "--firewall-address-object", "fw-net-office",
            ],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["firewallAddressObject"] == "fw-net-office"


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

    def test_subnet_update_firewall_object(self, runner, mock_client):
        mock_client.patch.return_value = {
            "code": 200, "success": True, "data": "Subnet updated",
        }
        result = runner.invoke(
            cli,
            [
                "--profile", "test",
                "subnet", "update",
                "1",
                "--firewall-address-object", "fw-net-lab",
            ],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "subnets", 1, data={"firewallAddressObject": "fw-net-lab"}
        )

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

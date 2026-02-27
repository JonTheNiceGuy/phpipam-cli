from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.circuit.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestCircuitList:
    def test_circuit_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "cid": "CIR-001", "status": "Active",
             "comment": "Primary link"},
            {"id": "2", "cid": "CIR-002", "status": "Inactive",
             "comment": "Backup link"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "circuit", "list"])
        assert result.exit_code == 0
        assert "CIR-001" in result.output
        assert "CIR-002" in result.output

    def test_circuit_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "circuit", "list"])
        assert result.exit_code == 0
        assert "No circuits found" in result.output

    def test_circuit_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "cid": "ZZZ-002", "status": "Active", "comment": ""},
            {"id": "1", "cid": "AAA-001", "status": "Active", "comment": ""},
        ]
        result = runner.invoke(cli, ["--profile", "test", "circuit", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "AAA-001" in lines[0]
        assert "ZZZ-002" in lines[1]


class TestCircuitShow:
    def test_circuit_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "cid": "CIR-001", "status": "Active",
        }
        result = runner.invoke(cli, ["--profile", "test", "circuit", "show", "1"])
        assert result.exit_code == 0
        assert "CIR-001" in result.output


class TestCircuitAdd:
    def test_circuit_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Circuit created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "add", "--cid", "CIR-003",
             "--provider", "1", "--status", "Active",
             "--comment", "New circuit"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_circuit_add_with_all_options(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 4, "data": "Circuit created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "add", "--cid", "CIR-004",
             "--provider", "1", "--capacity", "10G",
             "--device1", "5", "--location1", "3",
             "--device2", "6", "--location2", "4"],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["capacity"] == "10G"
        assert call_data["device1"] == "5"
        assert call_data["location1"] == "3"
        assert call_data["device2"] == "6"
        assert call_data["location2"] == "4"


class TestCircuitUpdate:
    def test_circuit_update_status(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "update", "1",
             "--status", "Inactive"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits", 1, data={"status": "Inactive"}
        )

    def test_circuit_update_comment(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "update", "1",
             "--comment", "Updated"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits", 1, data={"comment": "Updated"}
        )

    def test_circuit_update_cid_and_provider(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "update", "1",
             "--cid", "CIR-NEW", "--provider", "2"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits", 1, data={"cid": "CIR-NEW", "provider": "2"}
        )

    def test_circuit_update_capacity_and_devices(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "update", "1",
             "--capacity", "100G", "--device1", "10", "--location1", "3",
             "--device2", "11", "--location2", "4"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits", 1, data={
                "capacity": "100G", "device1": "10", "location1": "3",
                "device2": "11", "location2": "4",
            }
        )


class TestCircuitDelete:
    def test_circuit_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "circuit", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()


# --- Provider sub-commands ---


class TestProviderList:
    def test_provider_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "name": "Telco-A", "description": "Primary ISP"},
            {"id": "2", "name": "Telco-B", "description": "Backup ISP"},
        ]
        result = runner.invoke(
            cli, ["--profile", "test", "circuit", "provider", "list"]
        )
        assert result.exit_code == 0
        assert "Telco-A" in result.output
        assert "Telco-B" in result.output

    def test_provider_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(
            cli, ["--profile", "test", "circuit", "provider", "list"]
        )
        assert result.exit_code == 0
        assert "No providers found" in result.output

    def test_provider_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "name": "Zulu", "description": "Z"},
            {"id": "1", "name": "Alpha", "description": "A"},
        ]
        result = runner.invoke(
            cli, ["--profile", "test", "circuit", "provider", "list"]
        )
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestProviderShow:
    def test_provider_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "name": "Telco-A", "description": "Primary ISP",
        }
        result = runner.invoke(
            cli, ["--profile", "test", "circuit", "provider", "show", "1"]
        )
        assert result.exit_code == 0
        assert "Telco-A" in result.output


class TestProviderAdd:
    def test_provider_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Provider created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "provider", "add",
             "--name", "NewISP", "--description", "New provider"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()


class TestProviderUpdate:
    def test_provider_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "provider", "update", "1",
             "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits/providers", 1, data={"name": "Renamed"}
        )

    def test_provider_update_contact(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "provider", "update", "1",
             "--contact", "noc@example.com"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits/providers", 1, data={"contact": "noc@example.com"}
        )

    def test_provider_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "circuit", "provider", "update", "1",
             "--description", "Updated ISP"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "circuits/providers", 1, data={"description": "Updated ISP"}
        )


class TestProviderDelete:
    def test_provider_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "circuit", "provider", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

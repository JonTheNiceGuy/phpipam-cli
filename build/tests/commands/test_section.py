from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.section.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestSectionList:
    def test_section_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "name": "Production", "description": "Prod networks"},
            {"id": "2", "name": "Development", "description": "Dev networks"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "section", "list"])
        assert result.exit_code == 0
        assert "Production" in result.output
        assert "Development" in result.output

    def test_section_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "section", "list"])
        assert result.exit_code == 0
        assert "No sections found" in result.output

    def test_section_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "name": "Zulu", "description": "Z"},
            {"id": "1", "name": "Alpha", "description": "A"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "section", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestSectionShow:
    def test_section_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "name": "Production", "description": "Prod networks",
        }
        result = runner.invoke(cli, ["--profile", "test", "section", "show", "1"])
        assert result.exit_code == 0
        assert "Production" in result.output


class TestSectionAdd:
    def test_section_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Section created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "section", "add", "--name", "NewSection",
             "--description", "Test"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_section_add_with_master(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 4, "data": "Section created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "section", "add", "--name", "Child",
             "--master-section", "1"],
        )
        assert result.exit_code == 0
        mock_client.post.assert_called_once()
        call_data = mock_client.post.call_args
        assert call_data[1]["data"]["masterSection"] == "1"


class TestSectionUpdate:
    def test_section_update_name(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "section", "update", "1", "--name", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "sections", 1, data={"name": "Renamed"}
        )

    def test_section_update_description(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "section", "update", "1",
             "--description", "New desc"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "sections", 1, data={"description": "New desc"}
        )

    def test_section_update_master_section(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "section", "update", "1",
             "--master-section", "2"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "sections", 1, data={"masterSection": "2"}
        )


class TestSectionDelete:
    def test_section_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "section", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

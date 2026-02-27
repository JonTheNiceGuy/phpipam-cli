from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.tag.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestTagList:
    def test_tag_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "type": "Used", "bgcolor": "#f59c99", "fgcolor": "#000"},
            {"id": "2", "type": "Available", "bgcolor": "#a9cb9a", "fgcolor": "#000"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "tag", "list"])
        assert result.exit_code == 0
        assert "Used" in result.output
        assert "Available" in result.output

    def test_tag_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "tag", "list"])
        assert result.exit_code == 0
        assert "No tags found" in result.output

    def test_tag_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "type": "Zulu", "bgcolor": "#000", "fgcolor": "#fff"},
            {"id": "1", "type": "Alpha", "bgcolor": "#fff", "fgcolor": "#000"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "tag", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestTagShow:
    def test_tag_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "type": "Used", "bgcolor": "#f59c99", "fgcolor": "#000",
        }
        result = runner.invoke(cli, ["--profile", "test", "tag", "show", "1"])
        assert result.exit_code == 0
        assert "Used" in result.output


class TestTagAdd:
    def test_tag_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 5, "data": "Tag created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "tag", "add", "--type", "Reserved",
             "--bgcolor", "#ff0", "--fgcolor", "#000"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_tag_add_with_compress_and_locked(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 6, "data": "Tag created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "tag", "add", "--type", "Locked Tag",
             "--compress", "Yes", "--locked", "Yes"],
        )
        assert result.exit_code == 0
        call_data = mock_client.post.call_args[1]["data"]
        assert call_data["compress"] == "Yes"
        assert call_data["locked"] == "Yes"


class TestTagUpdate:
    def test_tag_update_type(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "tag", "update", "1", "--type", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/tags", 1, data={"type": "Renamed"}
        )

    def test_tag_update_bgcolor(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "tag", "update", "1", "--bgcolor", "#abc"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/tags", 1, data={"bgcolor": "#abc"}
        )

    def test_tag_update_fgcolor_compress_locked(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "tag", "update", "1",
             "--fgcolor", "#def", "--compress", "No", "--locked", "Yes"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/tags", 1,
            data={"fgcolor": "#def", "compress": "No", "locked": "Yes"}
        )


class TestTagDelete:
    def test_tag_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "tag", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

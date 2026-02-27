from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli
from ipam.client import PhpIpamClient, PhpIpamError


@pytest.fixture
def mock_authenticate():
    with patch("ipam.cli.PhpIpamClient.authenticate", return_value="fake-token-123"):
        yield


@pytest.fixture
def mock_authenticate_failure():
    with patch(
        "ipam.cli.PhpIpamClient.authenticate",
        side_effect=Exception("Invalid credentials"),
    ):
        yield


class TestCliBase:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PHPIPAM command line tool" in result.output

    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_has_profile_option(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--profile" in result.output

    def test_subcommand_groups_exist(self, runner):
        result = runner.invoke(cli, ["--help"])
        for cmd in ("subnet", "address", "vlan", "profile", "section",
                     "vrf", "l2domain", "device", "circuit", "nat",
                     "location", "rack", "nameserver", "tag",
                     "device-type", "customer"):
            assert cmd in result.output


class TestProfileCommands:
    def test_profile_help(self, runner):
        result = runner.invoke(cli, ["profile", "--help"])
        assert result.exit_code == 0
        assert "setup" in result.output
        assert "list" in result.output
        assert "show" in result.output
        assert "delete" in result.output

    def test_profile_setup(self, runner, config_file, mock_authenticate):
        result = runner.invoke(
            cli,
            ["profile", "setup", "--config-file", str(config_file)],
            input="myserver\nhttps://ipam.example.com\nmyapp\nadmin\nsecret\n",
        )
        assert result.exit_code == 0
        assert config_file.exists()

    def test_profile_list_empty(self, runner, config_file):
        result = runner.invoke(
            cli, ["profile", "list", "--config-file", str(config_file)]
        )
        assert result.exit_code == 0
        assert "No profiles" in result.output

    def test_profile_list_with_profiles(self, runner, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile srv1]\nurl = https://s1.com\napp_id = a1\ntoken = t1\n\n"
            "[profile srv2]\nurl = https://s2.com\napp_id = a2\ntoken = t2\n"
        )
        result = runner.invoke(
            cli, ["profile", "list", "--config-file", str(config_file)]
        )
        assert result.exit_code == 0
        assert "srv1" in result.output
        assert "srv2" in result.output

    def test_profile_show(self, runner, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile myserver]\n"
            "url = https://ipam.example.com\n"
            "app_id = myapp\n"
            "token = secret123\n"
        )
        result = runner.invoke(
            cli,
            ["profile", "show", "myserver", "--config-file", str(config_file)],
        )
        assert result.exit_code == 0
        assert "https://ipam.example.com" in result.output
        assert "myapp" in result.output

    def test_profile_show_not_found(self, runner, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text("")
        result = runner.invoke(
            cli,
            ["profile", "show", "nosuch", "--config-file", str(config_file)],
        )
        assert result.exit_code != 0

    def test_profile_delete(self, runner, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile myserver]\nurl = https://ipam.example.com\n"
        )
        result = runner.invoke(
            cli,
            [
                "profile",
                "delete",
                "myserver",
                "--config-file",
                str(config_file),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted" in result.output

    def test_profile_setup_auth_failure(self, runner, config_file, mock_authenticate_failure):
        result = runner.invoke(
            cli,
            ["profile", "setup", "--config-file", str(config_file)],
            input="myserver\nhttps://ipam.example.com\nmyapp\nadmin\nwrong\n",
        )
        assert result.exit_code != 0

    def test_profile_delete_not_found(self, runner, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text("[profile other]\nurl = https://other.com\n")
        result = runner.invoke(
            cli,
            ["profile", "delete", "nosuch", "--config-file", str(config_file)],
        )
        assert result.exit_code != 0


class TestCliErrorHandling:
    def test_disabled_module_shows_friendly_error(self, runner):
        with patch("ipam.commands.vlan.get_client") as mock_get:
            mock_get.return_value.get.side_effect = PhpIpamError(
                "invalid controller"
            )
            result = runner.invoke(
                cli, ["--profile", "test", "vlan", "list"]
            )
            assert result.exit_code != 0
            assert "not enabled" in result.output.lower()

    def test_api_error_shows_message(self, runner):
        with patch("ipam.commands.vlan.get_client") as mock_get:
            mock_get.return_value.get.side_effect = PhpIpamError(
                "subnet not found"
            )
            result = runner.invoke(
                cli, ["--profile", "test", "vlan", "list"]
            )
            assert result.exit_code != 0
            assert "subnet not found" in result.output


class TestCliProfileLoading:
    def test_successful_profile_load(self, runner, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile default]\n"
            "url = https://ipam.example.com\n"
            "app_id = myapp\n"
            "token = tok123\n"
        )
        with patch("ipam.cli.load_profile", return_value={
            "url": "https://ipam.example.com",
            "app_id": "myapp",
            "token": "tok123",
        }):
            result = runner.invoke(cli, ["subnet", "--help"])
            assert result.exit_code == 0

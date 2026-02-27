from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli
from ipam.client import PhpIpamError

pytestmark = pytest.mark.integration

# Mapping: (settings column, CLI command name, API controller path)
MODULE_MAP = [
    ("enableVRF", "vrf", "vrf"),
    ("enableNAT", "nat", "nat"),
    ("enableRACK", "rack", "tools/racks"),
    ("enableLocations", "location", "tools/locations"),
    ("enableCustomers", "customer", "tools/customers"),
    ("enableCircuits", "circuit", "circuits"),
]


class TestModuleDisabled:
    """Verify that disabling a phpIPAM module causes API errors."""

    @pytest.mark.parametrize(
        "settings_col,cli_cmd,api_path",
        MODULE_MAP,
        ids=[m[1] for m in MODULE_MAP],
    )
    def test_disabled_module_rejects_api_call(
        self, rwa_client, phpipam_service, toggle_module,
        settings_col, cli_cmd, api_path,
    ):
        toggle_module(settings_col, False)
        with pytest.raises(PhpIpamError):
            rwa_client.get(api_path)

    @pytest.mark.parametrize(
        "settings_col,cli_cmd,api_path",
        MODULE_MAP,
        ids=[m[1] for m in MODULE_MAP],
    )
    def test_re_enabled_module_works(
        self, rwa_client, phpipam_service, toggle_module,
        settings_col, cli_cmd, api_path,
    ):
        toggle_module(settings_col, False)
        toggle_module(settings_col, True)
        # Should not raise — module is re-enabled
        result = rwa_client.get(api_path)
        assert isinstance(result, (list, dict))


class TestModuleDisabledCliOutput:
    """Verify the CLI shows friendly errors for disabled modules."""

    @pytest.mark.parametrize(
        "settings_col,cli_cmd,api_path",
        MODULE_MAP,
        ids=[m[1] for m in MODULE_MAP],
    )
    def test_cli_shows_friendly_error(
        self, rwa_client, phpipam_service, toggle_module,
        settings_col, cli_cmd, api_path,
    ):
        toggle_module(settings_col, False)

        with patch("ipam.cli.load_profile", return_value={
            "url": phpipam_service,
            "app_id": "test_rwa",
            "token": rwa_client.token,
        }):
            runner = CliRunner(mix_stderr=False)
            result = runner.invoke(
                cli, ["--profile", "test", cli_cmd, "list"],
            )
            assert result.exit_code != 0
            assert "not enabled" in result.stderr.lower()

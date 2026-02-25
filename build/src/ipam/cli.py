import click

from ipam.client import PhpIpamClient
from ipam.config import (
    DEFAULT_CONFIG_PATH,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)
from ipam.commands.subnet import subnet
from ipam.commands.address import address
from ipam.commands.vlan import vlan


@click.group()
@click.version_option("0.1.0", prog_name="ipam")
@click.option(
    "--profile",
    default="default",
    envvar="IPAM_PROFILE",
    help="Profile name to use.",
)
@click.pass_context
def cli(ctx, profile):
    """PHPIPAM command line tool."""
    ctx.ensure_object(dict)
    ctx.obj = ctx.obj or {}

    # For subcommands that need the API client, load the profile.
    # Profile commands handle their own config access.
    if ctx.invoked_subcommand not in ("profile",):
        try:
            settings = load_profile(profile)
            ctx.obj = PhpIpamClient(
                url=settings["url"],
                app_id=settings["app_id"],
                token=settings["token"],
            )
        except (FileNotFoundError, KeyError):
            # Allow the command to proceed -- it will fail if it
            # actually needs the client (e.g. in tests with mocks).
            pass


cli.add_command(subnet)
cli.add_command(address)
cli.add_command(vlan)


# --- Profile management commands ---


@cli.group("profile")
def profile_group():
    """Manage connection profiles."""


@profile_group.command("setup")
@click.option(
    "--config-file",
    type=click.Path(),
    default=None,
    help="Config file path (default: ~/.ipam/config).",
)
def profile_setup(config_file):
    """Set up a new profile interactively."""
    from pathlib import Path

    cfg = Path(config_file) if config_file else DEFAULT_CONFIG_PATH

    name = click.prompt("Profile name")
    url = click.prompt("PHPIPAM URL")
    app_id = click.prompt("API App ID")
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True)

    try:
        token = PhpIpamClient.authenticate(url, app_id, username, password)
    except Exception as e:
        click.echo(f"Authentication failed: {e}", err=True)
        raise SystemExit(1)

    save_profile(name, {"url": url, "app_id": app_id, "token": token}, cfg)
    click.echo(f"Profile '{name}' saved.")


@profile_group.command("list")
@click.option(
    "--config-file",
    type=click.Path(),
    default=None,
    help="Config file path.",
)
def profile_list(config_file):
    """List all profiles."""
    from pathlib import Path

    cfg = Path(config_file) if config_file else DEFAULT_CONFIG_PATH
    names = list_profiles(cfg)
    if not names:
        click.echo("No profiles configured.")
        return
    for name in names:
        click.echo(f"  {name}")


@profile_group.command("show")
@click.argument("name")
@click.option(
    "--config-file",
    type=click.Path(),
    default=None,
    help="Config file path.",
)
def profile_show(name, config_file):
    """Show a profile's settings."""
    from pathlib import Path

    cfg = Path(config_file) if config_file else DEFAULT_CONFIG_PATH
    try:
        settings = load_profile(name, cfg)
    except (FileNotFoundError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    for key, value in settings.items():
        click.echo(f"  {key} = {value}")


@profile_group.command("delete")
@click.argument("name")
@click.option(
    "--config-file",
    type=click.Path(),
    default=None,
    help="Config file path.",
)
def profile_delete(name, config_file):
    """Delete a profile."""
    from pathlib import Path

    cfg = Path(config_file) if config_file else DEFAULT_CONFIG_PATH
    try:
        delete_profile(name, cfg)
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    click.echo(f"Deleted profile '{name}'.")

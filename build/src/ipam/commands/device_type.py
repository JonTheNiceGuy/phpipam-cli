import click

from ipam.helpers import get_client, format_output


@click.group("device-type")
def device_type():
    """Manage device types."""


@device_type.command("list")
@click.pass_context
def device_type_list(ctx):
    """List all device types."""
    client = get_client(ctx)
    data = client.get("tools/device_types")
    if not data:
        click.echo("No device types found.")
        return
    data.sort(key=lambda d: d.get("tname", "").lower())
    for d in data:
        click.echo(f"{d['tid']:>4}  {d.get('tname', ''):<30}  {d.get('tdescription', '')}")


@device_type.command("show")
@click.argument("device_type_id")
@click.pass_context
def device_type_show(ctx, device_type_id):
    """Show details of a device type."""
    client = get_client(ctx)
    data = client.get("tools/device_types", device_type_id)
    click.echo(format_output(data))


@device_type.command("add")
@click.option("--tname", required=True, help="Device type name")
@click.option("--tdescription", default="", help="Description")
@click.pass_context
def device_type_add(ctx, tname, tdescription):
    """Add a new device type."""
    client = get_client(ctx)
    payload = {"tname": tname, "tdescription": tdescription}
    result = client.post("tools/device_types", data=payload)
    click.echo(f"Device type created (id: {result['id']})")


@device_type.command("update")
@click.argument("device_type_id")
@click.option("--tname", default=None, help="Device type name")
@click.option("--tdescription", default=None, help="Description")
@click.pass_context
def device_type_update(ctx, device_type_id, tname, tdescription):
    """Update a device type."""
    client = get_client(ctx)
    payload = {}
    if tname is not None:
        payload["tname"] = tname
    if tdescription is not None:
        payload["tdescription"] = tdescription
    client.patch("tools/device_types", int(device_type_id), data=payload)
    click.echo("Device type updated.")


@device_type.command("delete")
@click.argument("device_type_id")
@click.pass_context
def device_type_delete(ctx, device_type_id):
    """Delete a device type."""
    client = get_client(ctx)
    client.delete("tools/device_types", int(device_type_id))
    click.echo("Device type deleted.")

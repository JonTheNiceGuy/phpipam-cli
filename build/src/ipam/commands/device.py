import click

from ipam.helpers import get_client, format_output


@click.group("device")
def device():
    """Manage devices."""


@device.command("list")
@click.pass_context
def device_list(ctx):
    """List all devices."""
    client = get_client(ctx)
    data = client.get("devices")
    if not data:
        click.echo("No devices found.")
        return
    data.sort(key=lambda d: d.get("hostname", "").lower())
    for d in data:
        click.echo(
            f"{d['id']:>4}  {d.get('hostname', ''):<30}  "
            f"{d.get('ip_addr', ''):<15}  {d.get('description', '')}"
        )


@device.command("show")
@click.argument("device_id")
@click.pass_context
def device_show(ctx, device_id):
    """Show details of a device."""
    client = get_client(ctx)
    data = client.get("devices", device_id)
    click.echo(format_output(data))


@device.command("add")
@click.option("--hostname", required=True, help="Device hostname")
@click.option("--ip-addr", default="", help="IP address")
@click.option("--description", default="", help="Description")
@click.option("--sections", default=None, help="Section IDs (semicolon-separated)")
@click.option("--rack", default=None, help="Rack ID")
@click.option("--rack-start", default=None, help="Rack start position")
@click.option("--rack-size", default=None, help="Rack size in U")
@click.option("--location", default=None, help="Location ID")
@click.pass_context
def device_add(ctx, hostname, ip_addr, description, sections, rack,
               rack_start, rack_size, location):
    """Add a new device."""
    client = get_client(ctx)
    payload = {
        "hostname": hostname, "ip_addr": ip_addr, "description": description,
    }
    if sections is not None:
        payload["sections"] = sections
    if rack is not None:
        payload["rack"] = rack
    if rack_start is not None:
        payload["rack_start"] = rack_start
    if rack_size is not None:
        payload["rack_size"] = rack_size
    if location is not None:
        payload["location"] = location
    result = client.post("devices", data=payload)
    click.echo(f"Device created (id: {result['id']})")


@device.command("update")
@click.argument("device_id")
@click.option("--hostname", default=None, help="Device hostname")
@click.option("--ip-addr", default=None, help="IP address")
@click.option("--description", default=None, help="Description")
@click.option("--rack", default=None, help="Rack ID")
@click.option("--rack-start", default=None, help="Rack start position")
@click.option("--rack-size", default=None, help="Rack size in U")
@click.option("--location", default=None, help="Location ID")
@click.pass_context
def device_update(ctx, device_id, hostname, ip_addr, description, rack,
                  rack_start, rack_size, location):
    """Update a device."""
    client = get_client(ctx)
    payload = {}
    if hostname is not None:
        payload["hostname"] = hostname
    if ip_addr is not None:
        payload["ip_addr"] = ip_addr
    if description is not None:
        payload["description"] = description
    if rack is not None:
        payload["rack"] = rack
    if rack_start is not None:
        payload["rack_start"] = rack_start
    if rack_size is not None:
        payload["rack_size"] = rack_size
    if location is not None:
        payload["location"] = location
    client.patch("devices", int(device_id), data=payload)
    click.echo("Device updated.")


@device.command("delete")
@click.argument("device_id")
@click.pass_context
def device_delete(ctx, device_id):
    """Delete a device."""
    client = get_client(ctx)
    client.delete("devices", int(device_id))
    click.echo("Device deleted.")

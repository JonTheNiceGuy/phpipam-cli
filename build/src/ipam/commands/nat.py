import click

from ipam.helpers import get_client, format_output


@click.group("nat")
def nat():
    """Manage NAT rules."""


@nat.command("list")
@click.pass_context
def nat_list(ctx):
    """List all NAT rules."""
    client = get_client(ctx)
    data = client.get("nat")
    if not data:
        click.echo("No NAT rules found.")
        return
    data.sort(key=lambda n: n.get("name", "").lower())
    for n in data:
        click.echo(
            f"{n['id']:>4}  {n.get('name', ''):<20}  "
            f"{n.get('type', ''):<12}  {n.get('description', '')}"
        )


@nat.command("show")
@click.argument("nat_id")
@click.pass_context
def nat_show(ctx, nat_id):
    """Show details of a NAT rule."""
    client = get_client(ctx)
    data = client.get("nat", nat_id)
    click.echo(format_output(data))


@nat.command("add")
@click.option("--name", required=True, help="NAT rule name")
@click.option("--type", "nat_type", required=True,
              type=click.Choice(["source", "static", "destination"]),
              help="NAT type")
@click.option("--src", default=None, help="Source")
@click.option("--dst", default=None, help="Destination")
@click.option("--src-port", default=None, help="Source port")
@click.option("--dst-port", default=None, help="Destination port")
@click.option("--device", default=None, help="Device ID")
@click.option("--description", default="", help="Description")
@click.pass_context
def nat_add(ctx, name, nat_type, src, dst, src_port, dst_port,
            device, description):
    """Add a new NAT rule."""
    client = get_client(ctx)
    payload = {"name": name, "type": nat_type, "description": description}
    if src is not None:
        payload["src"] = src
    if dst is not None:
        payload["dst"] = dst
    if src_port is not None:
        payload["src_port"] = src_port
    if dst_port is not None:
        payload["dst_port"] = dst_port
    if device is not None:
        payload["device"] = device
    result = client.post("nat", data=payload)
    click.echo(f"NAT rule created (id: {result['id']})")


@nat.command("update")
@click.argument("nat_id")
@click.option("--name", default=None, help="NAT rule name")
@click.option("--type", "nat_type", default=None,
              type=click.Choice(["source", "static", "destination"]),
              help="NAT type")
@click.option("--src", default=None, help="Source")
@click.option("--dst", default=None, help="Destination")
@click.option("--src-port", default=None, help="Source port")
@click.option("--dst-port", default=None, help="Destination port")
@click.option("--device", default=None, help="Device ID")
@click.option("--description", default=None, help="Description")
@click.pass_context
def nat_update(ctx, nat_id, name, nat_type, src, dst, src_port, dst_port,
               device, description):
    """Update a NAT rule."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if nat_type is not None:
        payload["type"] = nat_type
    if src is not None:
        payload["src"] = src
    if dst is not None:
        payload["dst"] = dst
    if src_port is not None:
        payload["src_port"] = src_port
    if dst_port is not None:
        payload["dst_port"] = dst_port
    if device is not None:
        payload["device"] = device
    if description is not None:
        payload["description"] = description
    client.patch("nat", int(nat_id), data=payload)
    click.echo("NAT rule updated.")


@nat.command("delete")
@click.argument("nat_id")
@click.pass_context
def nat_delete(ctx, nat_id):
    """Delete a NAT rule."""
    client = get_client(ctx)
    client.delete("nat", int(nat_id))
    click.echo("NAT rule deleted.")

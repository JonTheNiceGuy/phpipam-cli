import click

from ipam.helpers import get_client, format_output


@click.group("rack")
def rack():
    """Manage racks."""


@rack.command("list")
@click.pass_context
def rack_list(ctx):
    """List all racks."""
    client = get_client(ctx)
    data = client.get("tools/racks")
    if not data:
        click.echo("No racks found.")
        return
    data.sort(key=lambda r: r.get("name", "").lower())
    for r in data:
        click.echo(
            f"{r['id']:>4}  {r.get('name', ''):<30}  "
            f"size={r.get('size', '')}U  {r.get('description', '')}"
        )


@rack.command("show")
@click.argument("rack_id")
@click.pass_context
def rack_show(ctx, rack_id):
    """Show details of a rack."""
    client = get_client(ctx)
    data = client.get("tools/racks", rack_id)
    click.echo(format_output(data))


@rack.command("add")
@click.option("--name", required=True, help="Rack name")
@click.option("--size", default="", help="Rack size in U")
@click.option("--location", default=None, help="Location ID")
@click.option("--row", default=None, help="Row identifier")
@click.option("--description", default="", help="Description")
@click.pass_context
def rack_add(ctx, name, size, location, row, description):
    """Add a new rack."""
    client = get_client(ctx)
    payload = {"name": name, "size": size, "description": description}
    if location is not None:
        payload["location"] = location
    if row is not None:
        payload["row"] = row
    result = client.post("tools/racks", data=payload)
    click.echo(f"Rack created (id: {result['id']})")


@rack.command("update")
@click.argument("rack_id")
@click.option("--name", default=None, help="Rack name")
@click.option("--size", default=None, help="Rack size in U")
@click.option("--location", default=None, help="Location ID")
@click.option("--row", default=None, help="Row identifier")
@click.option("--description", default=None, help="Description")
@click.pass_context
def rack_update(ctx, rack_id, name, size, location, row, description):
    """Update a rack."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if size is not None:
        payload["size"] = size
    if location is not None:
        payload["location"] = location
    if row is not None:
        payload["row"] = row
    if description is not None:
        payload["description"] = description
    client.patch("tools/racks", int(rack_id), data=payload)
    click.echo("Rack updated.")


@rack.command("delete")
@click.argument("rack_id")
@click.pass_context
def rack_delete(ctx, rack_id):
    """Delete a rack."""
    client = get_client(ctx)
    client.delete("tools/racks", int(rack_id))
    click.echo("Rack deleted.")

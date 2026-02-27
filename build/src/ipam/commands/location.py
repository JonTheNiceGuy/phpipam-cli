import click

from ipam.helpers import get_client, format_output


@click.group("location")
def location():
    """Manage locations."""


@location.command("list")
@click.pass_context
def location_list(ctx):
    """List all locations."""
    client = get_client(ctx)
    data = client.get("tools/locations")
    if not data:
        click.echo("No locations found.")
        return
    data.sort(key=lambda l: l.get("name", "").lower())
    for l in data:
        click.echo(
            f"{l['id']:>4}  {l.get('name', ''):<30}  "
            f"{l.get('address', ''):<30}  {l.get('description', '')}"
        )


@location.command("show")
@click.argument("location_id")
@click.pass_context
def location_show(ctx, location_id):
    """Show details of a location."""
    client = get_client(ctx)
    data = client.get("tools/locations", location_id)
    click.echo(format_output(data))


@location.command("add")
@click.option("--name", required=True, help="Location name")
@click.option("--description", default="", help="Description")
@click.option("--address", default="", help="Street address")
@click.option("--lat", default=None, help="Latitude")
@click.option("--long", default=None, help="Longitude")
@click.pass_context
def location_add(ctx, name, description, address, lat, long):
    """Add a new location."""
    client = get_client(ctx)
    payload = {"name": name, "description": description, "address": address}
    if lat is not None:
        payload["lat"] = lat
    if long is not None:
        payload["long"] = long
    result = client.post("tools/locations", data=payload)
    click.echo(f"Location created (id: {result['id']})")


@location.command("update")
@click.argument("location_id")
@click.option("--name", default=None, help="Location name")
@click.option("--description", default=None, help="Description")
@click.option("--address", default=None, help="Street address")
@click.option("--lat", default=None, help="Latitude")
@click.option("--long", default=None, help="Longitude")
@click.pass_context
def location_update(ctx, location_id, name, description, address, lat, long):
    """Update a location."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if address is not None:
        payload["address"] = address
    if lat is not None:
        payload["lat"] = lat
    if long is not None:
        payload["long"] = long
    client.patch("tools/locations", int(location_id), data=payload)
    click.echo("Location updated.")


@location.command("delete")
@click.argument("location_id")
@click.pass_context
def location_delete(ctx, location_id):
    """Delete a location."""
    client = get_client(ctx)
    client.delete("tools/locations", int(location_id))
    click.echo("Location deleted.")

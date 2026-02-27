import click

from ipam.helpers import get_client, format_output


@click.group("vrf")
def vrf():
    """Manage VRFs."""


@vrf.command("list")
@click.pass_context
def vrf_list(ctx):
    """List all VRFs."""
    client = get_client(ctx)
    data = client.get("vrf")
    if not data:
        click.echo("No VRFs found.")
        return
    data.sort(key=lambda v: v.get("name", "").lower())
    for v in data:
        click.echo(
            f"{v['vrfId']:>4}  {v.get('name', ''):<20}  "
            f"{v.get('rd', ''):<15}  {v.get('description', '')}"
        )


@vrf.command("show")
@click.argument("vrf_id")
@click.pass_context
def vrf_show(ctx, vrf_id):
    """Show details of a VRF."""
    client = get_client(ctx)
    data = client.get("vrf", vrf_id)
    click.echo(format_output(data))


@vrf.command("add")
@click.option("--name", required=True, help="VRF name")
@click.option("--rd", default="", help="Route distinguisher")
@click.option("--description", default="", help="Description")
@click.pass_context
def vrf_add(ctx, name, rd, description):
    """Add a new VRF."""
    client = get_client(ctx)
    payload = {"name": name, "rd": rd, "description": description}
    result = client.post("vrf", data=payload)
    click.echo(f"VRF created (id: {result['id']})")


@vrf.command("update")
@click.argument("vrf_id")
@click.option("--name", default=None, help="VRF name")
@click.option("--rd", default=None, help="Route distinguisher")
@click.option("--description", default=None, help="Description")
@click.pass_context
def vrf_update(ctx, vrf_id, name, rd, description):
    """Update a VRF."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if rd is not None:
        payload["rd"] = rd
    if description is not None:
        payload["description"] = description
    client.patch("vrf", int(vrf_id), data=payload)
    click.echo("VRF updated.")


@vrf.command("delete")
@click.argument("vrf_id")
@click.pass_context
def vrf_delete(ctx, vrf_id):
    """Delete a VRF."""
    client = get_client(ctx)
    client.delete("vrf", int(vrf_id))
    click.echo("VRF deleted.")

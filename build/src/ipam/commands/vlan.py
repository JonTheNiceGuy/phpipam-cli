import click

from ipam.helpers import get_client, format_output


@click.group("vlan")
def vlan():
    """Manage VLANs."""


@vlan.command("list")
@click.pass_context
def vlan_list(ctx):
    """List all VLANs."""
    client = get_client(ctx)
    data = client.get("vlan")
    if not data:
        click.echo("No VLANs found.")
        return
    for v in data:
        click.echo(f"{v['id']:>4}  VLAN {v['number']}  {v.get('name', '')}  {v.get('description', '')}")


@vlan.command("show")
@click.argument("vlan_id")
@click.pass_context
def vlan_show(ctx, vlan_id):
    """Show details of a VLAN."""
    client = get_client(ctx)
    data = client.get("vlan", vlan_id)
    click.echo(format_output(data))


@vlan.command("add")
@click.option("--number", required=True, help="VLAN number")
@click.option("--name", required=True, help="VLAN name")
@click.option("--description", default="", help="Description")
@click.pass_context
def vlan_add(ctx, number, name, description):
    """Add a new VLAN."""
    client = get_client(ctx)
    payload = {
        "number": number,
        "name": name,
        "description": description,
    }
    result = client.post("vlan", data=payload)
    click.echo(f"VLAN created (id: {result['id']})")


@vlan.command("update")
@click.argument("vlan_id")
@click.option("--name", default=None, help="VLAN name")
@click.option("--description", default=None, help="Description")
@click.pass_context
def vlan_update(ctx, vlan_id, name, description):
    """Update a VLAN."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    client.patch("vlan", int(vlan_id), data=payload)
    click.echo("VLAN updated.")


@vlan.command("delete")
@click.argument("vlan_id")
@click.pass_context
def vlan_delete(ctx, vlan_id):
    """Delete a VLAN."""
    client = get_client(ctx)
    client.delete("vlan", int(vlan_id))
    click.echo("VLAN deleted.")

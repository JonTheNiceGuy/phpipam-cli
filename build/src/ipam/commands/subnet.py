import click

from ipam.helpers import get_client, format_output


@click.group("subnet")
def subnet():
    """Manage subnets."""


@subnet.command("list")
@click.pass_context
def subnet_list(ctx):
    """List all subnets."""
    client = get_client(ctx)
    data = client.get("subnets")
    if not data:
        click.echo("No subnets found.")
        return
    for s in data:
        click.echo(f"{s['id']:>4}  {s['subnet']}/{s['mask']}  {s.get('description', '')}")


@subnet.command("show")
@click.argument("subnet_id")
@click.pass_context
def subnet_show(ctx, subnet_id):
    """Show details of a subnet."""
    client = get_client(ctx)
    data = client.get("subnets", subnet_id)
    click.echo(format_output(data))


@subnet.command("add")
@click.option("--subnet", required=True, help="Subnet address (e.g. 10.0.0.0)")
@click.option("--mask", required=True, help="Subnet mask (e.g. 24)")
@click.option("--section-id", required=True, help="Section ID")
@click.option("--description", default="", help="Description")
@click.pass_context
def subnet_add(ctx, subnet, mask, section_id, description):
    """Add a new subnet."""
    client = get_client(ctx)
    payload = {
        "subnet": subnet,
        "mask": mask,
        "sectionId": section_id,
        "description": description,
    }
    result = client.post("subnets", data=payload)
    click.echo(f"Subnet created (id: {result['id']})")


@subnet.command("update")
@click.argument("subnet_id")
@click.option("--description", default=None, help="Description")
@click.option("--mask", default=None, help="Subnet mask")
@click.pass_context
def subnet_update(ctx, subnet_id, description, mask):
    """Update a subnet."""
    client = get_client(ctx)
    payload = {}
    if description is not None:
        payload["description"] = description
    if mask is not None:
        payload["mask"] = mask
    client.patch("subnets", int(subnet_id), data=payload)
    click.echo("Subnet updated.")


@subnet.command("delete")
@click.argument("subnet_id")
@click.pass_context
def subnet_delete(ctx, subnet_id):
    """Delete a subnet."""
    client = get_client(ctx)
    client.delete("subnets", int(subnet_id))
    click.echo("Subnet deleted.")


@subnet.command("search")
@click.argument("cidr")
@click.pass_context
def subnet_search(ctx, cidr):
    """Search subnets by CIDR (e.g. 10.0.0.0/24)."""
    client = get_client(ctx)
    data = client.get("subnets", "cidr", cidr)
    if not data:
        click.echo("No subnets found.")
        return
    for s in data:
        click.echo(f"{s['id']:>4}  {s['subnet']}/{s['mask']}  {s.get('description', '')}")
